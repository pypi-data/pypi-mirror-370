# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import absolute_import
from __future__ import division

from __future__ import print_function

import logging
from typing import Callable, Tuple, Union
from PIL import ImageFile
import torch.utils.data as data
from .languages.prompt_engineering import prompt_engineering
from vision_datasets import DatasetHub, Usages, ManifestDataset
from vision_datasets.pytorch import TorchDataset

ImageFile.LOAD_TRUNCATED_IMAGES = True

logger = logging.getLogger(__name__)


class VDImageTextDataset(data.Dataset):
    """
    This class is intended for encapsulating Image/Text pair data for contrastive learning described in
    the following paper, support image text pairs and supervised CLASSIFICATION data
    """

    def __init__(
        self,
        dataset_name,
        dataset_json,
        blob_container,
        local_dir,
        is_train,
        n_few_shot=None,
        few_shot_rnd_seed=0,
        transform: Callable = None,
        tokenize: Callable = None,
        context_length: int = 77,
    ):
        self.transform = transform
        self.tokenize = tokenize
        self._chunk_sizes = None
        self.context_length = context_length

        usage = (
            [Usages.TRAIN_PURPOSE, Usages.VAL_PURPOSE]
            if is_train
            else Usages.TEST_PURPOSE
        )
        self._dataset = DatasetHub(dataset_json).create_manifest_dataset(
            container_sas=blob_container,
            local_dir=local_dir,
            name=dataset_name,
            usage=usage,
        )
        if n_few_shot and is_train:
            self._dataset = ManifestDataset(
                self._dataset.dataset_info,
                self._dataset.dataset_manifest.sample_few_shots_subset_greedy(
                    n_few_shot, few_shot_rnd_seed
                ),
                dataset_resources=self._dataset.dataset_resources,
            )
            logger.info(
                f"""Constructing {n_few_shot} few shot dataset with random seed {few_shot_rnd_seed},
                vision-datasets for {dataset_name}, with usage {usage}, len {len(self._dataset)}."""
            )
        else:
            logger.info(
                f"Construct vision-datasets for {dataset_name}, with usage {usage}, len {len(self._dataset)}"
            )

    def get_chunk_sizes(self):
        return self._chunk_sizes

    def __getitem__(self, index: Union[int, Tuple[int, int]]):
        if index is None:
            import torch

            return (
                torch.tensor([], dtype=torch.float32),
                torch.tensor([], dtype=torch.int64),
                torch.tensor([], dtype=torch.int64),
            )

        img, target, _ = self._dataset[index]

        txt = prompt_engineering(" ".join([self._dataset.labels[i] for i in target]))

        if self.transform:
            img = self.transform(img)

        tokens = (
            self.tokenize(
                txt,
                padding="max_length",
                truncation=True,
                max_length=self.context_length,
                return_tensors="pt",
            )
            if self.tokenize
            else txt
        )

        tokens["input_ids"].squeeze_()
        tokens["attention_mask"].squeeze_()

        return img, tokens, target[0]

    def __len__(self):
        return len(self._dataset)

    def spawn(self, n_images, rnd_seed=0):
        self._dataset = ManifestDataset(
            self._dataset.dataset_info,
            self._dataset.dataset_manifest.sample_subset(n_images, True, rnd_seed),
            dataset_resources=self._dataset.dataset_resources,
        )


class MultiClassTorchDatasetWrapper(TorchDataset):
    def __getitem__(self, index):
        from inspect import signature

        if len(signature(self.transform).parameters) == 1:
            if isinstance(index, int):
                image, target, idx_str = self.dataset[index]
                image = self.transform(image)
                return image, target
            else:
                return [
                    self.transform(img)
                    + (
                        target,
                        idx,
                    )
                    for img, target, idx in self.dataset[index]
                ]
        else:
            if isinstance(index, int):
                image, target, idx_str = super().__getitem__(index)
                return image, target[0]
            else:
                return [
                    (img, target) for img, target, idx in super().__getitem__(index)
                ]

    def spawn(self, n_images, rnd_seed=0):
        self.dataset = ManifestDataset(
            self.dataset.dataset_info,
            self.dataset.dataset_manifest.sample_subset(n_images, True, rnd_seed),
            dataset_resources=self.dataset.dataset_resources,
        )
