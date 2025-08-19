# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import math
import torch
from torch.utils.data import Sampler
import torch.distributed as dist
import random
import logging
import threading

logger = logging.getLogger(__name__)


def pre_fetch(fn_fetch, index):
    logger.debug(f"Pre-loading file index: {index} ...")
    fn_fetch(index)
    logger.debug(f"Pre-loading ended file index: {index} ...")


class DistributedChunkSampler(Sampler):
    def __init__(
        self,
        dataset,
        chunk_sizes=None,
        num_replicas=None,
        rank=None,
        shuffle=True,
        shuffle_chunk=True,
        prefetch=1,
    ):
        if num_replicas is None:
            try:
                num_replicas = dist.get_world_size()
            except Exception:
                num_replicas = torch.cuda.device_count()
        if rank is None:
            try:
                rank = dist.get_rank()
            except Exception:
                rank = torch.cuda.current_device()
        if chunk_sizes is None:
            logger.info(
                "[DistributedChunkSampler] No chunk size specified. Reduce to normal distributed sampler."
            )
            chunk_sizes = [len(dataset)]
        if torch.cuda.is_available():
            self.gpus_per_node = torch.cuda.device_count()
        self.dataset = dataset
        self.num_replicas = num_replicas  # num of GPUs
        if self.num_replicas < self.gpus_per_node:
            # this makes the sampler work on a 1 node job using less GPUs than the node has
            self.gpus_per_node = self.num_replicas
        self.rank = rank  # GPU id
        self.chunk_sizes = chunk_sizes
        self.min_chunk_size = min(self.chunk_sizes) - (
            min(self.chunk_sizes) % self.gpus_per_node
        )
        # logging.info("[DistributedChunkSampler] min chunk size: %s", self.min_chunk_size)
        self.epoch = 0
        self.local_sample_idx = 0
        self.global_sample_idx = 0
        num_nodes = int(self.num_replicas / self.gpus_per_node)
        assert (
            len(self.chunk_sizes) >= num_nodes
        ), f"Too few chunk files ({len(self.chunk_sizes)}) vs {num_nodes} machines for data parallel."
        if len(self.chunk_sizes) % num_nodes != 0:
            logger.warning(
                f"""The {len(self.chunk_sizes)} tsv chunk files
                cannot be evenly distributed to the {num_nodes} machines."""
                f" {len(self.chunk_sizes) % num_nodes} chunks will be ignored in each epoch."
            )
        self.num_samples = int(
            math.ceil(
                (len(self.chunk_sizes) // num_nodes * num_nodes * self.min_chunk_size)
                * 1.0
                / self.num_replicas
            )
        )  # num of samples per GPU
        self.total_size = self.num_samples * self.num_replicas
        logger.info(
            "\n[DistributedChunkSampler]"
            "\n\t rank: {}"
            "\n\t num_replicas: {}"
            "\n\t gpus_per_node: {}"
            "\n\t chunk_sizes: {}"
            "\n\t num_samples per gpu: {}"
            "\n\t total size: {}".format(
                rank,
                self.num_replicas,
                self.gpus_per_node,
                self.chunk_sizes,
                self.num_samples,
                self.total_size,
            )
        )
        self.shuffle = shuffle
        self.shuffle_chunk = shuffle_chunk
        self.prefetch = max(prefetch, 1)
        self.indices = None

    def _shuffle_chunk_elements(self, chunk_indices):
        """
        Generate randomly shuffled indices chunk-by-chunk.
        The generated indices are randomized in both chunk- and instance-level.

        Example::
        Input:
            chunk_size: [100, 100, 100, 100, 100]
            accum_chunk_sizes: [0, 100, 200, 300, 400, 500]
            chunk_indices: [1, 3, 2, 5, 4]
        Output:
            [12, 47, 29, ...
            283, 247, 212, ...
            192, 148, 183, ...
            482, 457, 431, ...
            314, 367, 352, ...]
        """
        accum_chunk_sizes = [0]
        for size in self.chunk_sizes:
            accum_chunk_sizes += [accum_chunk_sizes[-1] + size]

        # In case that the data size is greater than local cache (e.g., blobfuse),
        # reverse the order of consuming data between epochs to reduce the impact of cache miss.
        num_nodes = int(self.num_replicas / self.gpus_per_node)
        num_tsvs = int(len(chunk_indices) / num_nodes)
        if self.epoch % 2:
            for i in range(num_nodes):
                chunk_indices[i * num_tsvs: (i + 1) * num_tsvs] = chunk_indices[
                    i * num_tsvs: (i + 1) * num_tsvs
                ][::-1]

        logger.info(
            "\n[DistributedChunkSampler]"
            "\n\t epoch: {}"
            "\n\t chunk indices: {}".format(self.epoch, chunk_indices)
        )

        node_idx = int(self.rank / self.gpus_per_node)

        indices = []
        for idx in range(len(chunk_indices)):
            shuffled_chunk_elements = list(
                range(
                    accum_chunk_sizes[chunk_indices[idx] - 1],
                    accum_chunk_sizes[chunk_indices[idx]],
                )
            )
            random.shuffle(shuffled_chunk_elements)
            shuffled_chunk_elements = shuffled_chunk_elements[: self.min_chunk_size]
            if self.global_sample_idx < len(indices) + len(shuffled_chunk_elements):
                # insert tsv file index for pre-loading, skip the last tsv files
                if (idx + self.prefetch) < num_tsvs * (node_idx + 1):
                    shuffled_chunk_elements[0] = (
                        shuffled_chunk_elements[0],
                        chunk_indices[min(idx + self.prefetch, len(chunk_indices) - 1)]
                        - 1,
                        False,
                    )
                    logger.debug(
                        f"idx = {idx}, shuffled_chunk_elements[0] = {shuffled_chunk_elements[0]}"
                    )
                if self.global_sample_idx >= len(indices):
                    shuffled_chunk_elements[1] = (
                        shuffled_chunk_elements[1],
                        chunk_indices[idx] - 1,
                        True,
                    )
                    logger.debug(
                        f"idx = {idx}, shuffled_chunk_elements[1] = {shuffled_chunk_elements[1]}"
                    )
                    for i in range(1, self.prefetch):
                        if idx + i < num_tsvs * (node_idx + 1):
                            shuffled_chunk_elements[i + 1] = (
                                shuffled_chunk_elements[i + 1],
                                chunk_indices[min(idx + i, len(chunk_indices) - 1)] - 1,
                                False,
                            )
                            logger.debug(
                                f"idx = {idx}, shuffled_chunk_elements[{i+1}] = {shuffled_chunk_elements[i+1]}"
                            )
            indices += shuffled_chunk_elements

        return indices

    def __iter__(self):
        for i, item in enumerate(self.indices):
            if isinstance(item, tuple):
                index = item[0]
                index_chunk = item[1]
                if item[2]:
                    pre_fetch(self.dataset.fetch_blob, index_chunk)
                else:
                    x = threading.Thread(
                        target=pre_fetch,
                        args=(self.dataset.fetch_blob, index_chunk),
                        daemon=True,
                    )
                    x.start()
            else:
                index = item
            # local_sample_idx may be larger than self.num_samples due to multitask data smoothing
            # recurrently use the data if it is the case
            if i >= self.local_sample_idx % self.num_samples:
                logger.debug(
                    f"Sample [{i}]: {index}, local_sample_idx: {self.local_sample_idx}"
                )
                self.local_sample_idx += 1
                yield index
            else:
                logger.debug(
                    f"Skip sample [{i}]: {index}, local_sample_idx: {self.local_sample_idx}"
                )
                yield None

    def __len__(self):
        return self.num_samples

    def set_epoch(self, epoch):
        # Deterministically shuffle based on epoch
        self.epoch = epoch
        random.seed(self.epoch)

        if self.shuffle:
            chunk_indices = list(range(1, len(self.chunk_sizes) + 1))
            if self.shuffle_chunk:
                random.shuffle(chunk_indices)
            self.indices = self._shuffle_chunk_elements(chunk_indices)
        else:
            self.indices = list(range(len(self.dataset)))
        self.indices = self.indices[: self.total_size]

        assert (
            len(self.indices) == self.total_size
        ), "indices: {} vs total_size: {}".format(len(self.indices), self.total_size)

        # Subsample
        rank = self.rank % self.gpus_per_node
        node_idx = int(self.rank / self.gpus_per_node)
        logger.info(
            "[DistributedChunkSampler] global rank/local rank/node_idx: %d/%d/%d",
            self.rank,
            rank,
            node_idx,
        )
        idx_start = self.gpus_per_node * node_idx * self.num_samples
        idx_end = self.gpus_per_node * (node_idx + 1) * self.num_samples
        self.indices = self.indices[idx_start:idx_end]
        logger.debug(
            f"[DistributedChunkSampler] node sample range: indices[{idx_start}:{idx_end}]"
        )
        idx_start = rank
        idx_end = self.num_samples * self.gpus_per_node
        idx_step = self.gpus_per_node
        self.indices = self.indices[idx_start:idx_end:idx_step]
        logger.debug(
            f"[DistributedChunkSampler] rank sample range: indices[{idx_start}:{idx_end}:{idx_step}]"
        )

        assert (
            len(self.indices) == self.num_samples
        ), "indices: {} vs num_samples: {}".format(len(self.indices), self.num_samples)

    def set_sample_idx(self, local_sample_idx):
        rank = self.rank % self.gpus_per_node
        node_idx = int(self.rank / self.gpus_per_node)
        self.local_sample_idx = local_sample_idx
        # local_sample_idx may be larger than self.num_samples due to multitask data smoothing
        # recurrently use the data if it is the case
        self.global_sample_idx = (
            self.num_samples * self.gpus_per_node * node_idx
            + self.gpus_per_node * (local_sample_idx % self.num_samples)
            + rank
        )
        logger.info(
            f"""Resuming from local sample
            {self.local_sample_idx%self.num_samples} or global sample {self.global_sample_idx} ..."""
        )

    def get_sample_idx(self):
        return self.local_sample_idx
