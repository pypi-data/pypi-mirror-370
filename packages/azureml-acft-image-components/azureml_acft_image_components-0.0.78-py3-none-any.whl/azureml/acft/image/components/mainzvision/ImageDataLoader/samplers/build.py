# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging

import torch

from .class_aware_sampler import (
    ClassAwareDistributedSampler,
    ClassAwareAverageSampler,
    ClassAwareMedianSampler,
)
from .distributed_chunk_sampler import DistributedChunkSampler
from .ra_sampler import RASampler

logger = logging.getLogger(__name__)


def build_sampler(cfg, dataset, is_train, shuffle):
    if is_train and cfg["DATASET"]["SAMPLER"] == "repeated_aug":
        logger.info("=> use repeated aug sampler")
        sampler = RASampler(dataset, shuffle=shuffle)
    elif is_train and cfg["DATASET"]["SAMPLER"] == "class_aware":
        logger.info("=> use class aware sampler")
        if isinstance(cfg["DATASET"]["NUM_SAMPLES_CLASS"], int):
            sampler = ClassAwareDistributedSampler(
                dataset,
                num_samples_cls=cfg["DATASET"]["NUM_SAMPLES_CLASS"],
                shuffle=shuffle,
            )
        elif cfg["TRAIN"]["NUM_SAMPLES_CLASS"] == "average":
            sampler = ClassAwareAverageSampler(dataset, shuffle=shuffle)
        elif cfg["TRAIN"]["NUM_SAMPLES_CLASS"] == "median":
            sampler = ClassAwareMedianSampler(dataset, shuffle=shuffle)
        else:
            raise ValueError(
                "Unrecognized setting of TRAIN.NUM_SAMPLES_CLASS: %s"
                % cfg["DATASET"]["NUM_SAMPLES_CLASS"]
            )
    elif is_train and cfg["DATASET"]["SAMPLER"] == "chunk":
        logger.info("=> use chunk sampler")
        chunk_sizes = (
            dataset.get_chunk_sizes() if hasattr(dataset, "get_chunk_sizes") else None
        )
        sampler = DistributedChunkSampler(
            dataset,
            shuffle=shuffle,
            chunk_sizes=chunk_sizes,
            prefetch=cfg["DATASET"].get("PREFETCH", 1),
        )
    else:
        logger.info("=> use PyTorch distributed sampler")
        sampler = torch.utils.data.distributed.DistributedSampler(
            dataset, shuffle=shuffle
        )

    return sampler
