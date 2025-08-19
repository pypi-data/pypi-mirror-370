# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------

"""Hf image classification data class."""

import os
import numpy as np
import torch

from typing import Any, Callable, Dict, List, Optional, Tuple
from transformers.image_processing_utils import BaseImageProcessor

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.common.augmentation.albumentations_augmentation import (
    AlbumentationsAugmentation as AlbumAugmentations,
)
from azureml.acft.image.components.finetune.common.constants.augmentation_constants import (
    AugmentationConfigFileNames,
)
from azureml.acft.image.components.finetune.common.constants.constants import (
    ImageDataItemLiterals,
    SettingLiterals,
    SettingParameters,
    VisionDatasetConstants,
)
from azureml.acft.image.components.finetune.common.data.base_dataset import (
    BaseDataset,
)
from azureml.acft.image.components.finetune.huggingface.common.constants import (
    HfProblemType,
)
from azureml.acft.image.components.finetune.interfaces.azml_interface import AzmlDataInterface

from azureml.acft.image.components.finetune.common.data.runtime_classification_dataset import (
    get_classification_dataset,
)
from azureml.acft.image.components.finetune.common.data.data_utils import filter_invalid_images

logger = get_logger_app(__name__)


class AzmlHfImageDataInterface(AzmlDataInterface):
    """Data interface for Hf Image Models"""

    def __init__(self, tokenizer: BaseImageProcessor, **kwargs) -> None:
        """
        :param tokenizer: hugging face feature extractor for image models
        :type tokenizer: BaseImageProcessor
        """
        self.image_processor = tokenizer
        self.model_preprocessing_param_dict = self.image_processor.to_dict()

        self.multi_label = kwargs[SettingLiterals.PROBLEM_TYPE] == HfProblemType.MULTI_LABEL_CLASSIFICATION

        self.train_mltable_path = kwargs[SettingLiterals.TRAIN_MLTABLE_PATH]
        self.validation_mltable_path = kwargs.get(SettingLiterals.VALIDATION_MLTABLE_PATH, None)
        self.apply_augmentations = kwargs.get(SettingLiterals.APPLY_AUGMENTATIONS, False)

        # Set the dataset classes
        self._set_dataset_classes(**kwargs)

        # copy the label mappings from train_dataset
        self._set_classes_metadata()

    def _get_train_valid_augmentation_transforms(self, **kwargs) -> Tuple[Optional[Callable], Optional[Callable]]:
        """Get train and/or validation transforms

        :return: A tuple with train and validation transform
        :rtype: Tuple[Optional[Callable], Optional[Callable]]
        """
        train_transform, valid_transform = None, None

        logger.info(f"Feature Extractor config as dict: {self.model_preprocessing_param_dict}")

        # Note/Todo: read config_path from the params once the option is open to user.
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "..",
            "common/augmentation",
            AugmentationConfigFileNames.CLASSIFICATION_ALBUMENTATIONS_CONFIG,
        )
        augmentation_class_obj = AlbumAugmentations(
            config_path=config_path,
            model_preprocessing_params_dict=self.model_preprocessing_param_dict,
            **kwargs,
        )
        # Note/Todo: Output augmentation_class_obj.augmentations_dict to one of the output ports.

        # Get valid transforms
        valid_transform = augmentation_class_obj.get_valid_transform()

        if not self.apply_augmentations:
            # If no augmentations are applied, we only want to apply the validation transformations.
            return valid_transform, valid_transform

        # Get train transforms
        train_transform = augmentation_class_obj.get_train_transform()
        return train_transform, valid_transform

    def _set_dataset_classes(self, **kwargs) -> None:
        """Set dataset classes

        :return: None
        :rtype: None
        """
        (
            train_transform,
            valid_transform,
        ) = self._get_train_valid_augmentation_transforms(**kwargs)

        settings = {
            SettingLiterals.OUTPUT_DIR: kwargs.pop(SettingLiterals.OUTPUT_DIR, SettingParameters.DEFAULT_OUTPUT_DIR),
            SettingLiterals.IGNORE_DATA_ERRORS: kwargs.pop(SettingLiterals.IGNORE_DATA_ERRORS, True),
        }
        self.train_ds, self.validation_ds = get_classification_dataset(
            training_mltable=self.train_mltable_path,
            validation_mltable=self.validation_mltable_path,
            multi_label=self.multi_label,
            settings=settings,
        )

        # set train transform
        self.train_ds.set_transform(transform=train_transform)
        # set valid transform
        self.validation_ds.set_transform(transform=valid_transform)

    def _set_classes_metadata(self) -> None:
        """copy the label mappings from train_dataset"""

        self.label2id = self.train_ds.label_to_index_map
        self.id2label = {v: k for k, v in self.label2id.items()}

    def get_train_dataset(self) -> BaseDataset:
        """get train dataset

        :return : train dataset
        :rtype: BaseDataset
        """
        return self.train_ds

    def get_validation_dataset(self) -> BaseDataset:
        """get validation dataset

        :return : validation dataset
        :rtype: BaseDataset
        """
        return self.validation_ds

    def image_classification_collate_func(self, data_list: List[Dict[str, Any]]) -> Dict[str, torch.tensor]:
        """
        Collate function for image classification.

        :param data_list: A list of dictionaries with image and label keys.
        :type data_list: List[Dict[str, Any]]

        :return: A dictionary with images and labels.
        :rtype: Dict[str, torch.Tensor]
        """
        valid_data_list = filter_invalid_images(data_list, ImageDataItemLiterals.DEFAULT_IMAGE_KEY)
        if self.multi_label:
            labels = np.zeros((len(data_list), len(self.label2id)), dtype=np.float64)
            for idx, data in enumerate(valid_data_list):
                for label in data[ImageDataItemLiterals.DEFAULT_LABEL_KEY]:
                    labels[idx][label] = 1
        else:
            labels = np.array(
                [data[ImageDataItemLiterals.DEFAULT_LABEL_KEY] for data in valid_data_list],
                dtype=np.int64,
            )
        labels_tensor = torch.tensor(labels)

        images = [data[ImageDataItemLiterals.DEFAULT_IMAGE_KEY] for data in valid_data_list]

        output_dict = dict()

        def to_tensor_fn(img):
            # Converting to torch tensor(CHW format) from numpy array(HWC format)
            return torch.from_numpy(img.transpose(2, 0, 1)).to(dtype=torch.float)

        output_dict[ImageDataItemLiterals.HF_PIXEL_VALUES_KEY] = torch.stack([to_tensor_fn(img) for img in images])
        output_dict.update({ImageDataItemLiterals.HF_LABELS_KEY: labels_tensor})
        return output_dict

    def get_collation_function(
        self,
    ) -> Callable[[List[Dict[str, Any]]], Dict[str, torch.tensor]]:
        """
        Get the collate function for Hugging Face image classification.

        :return: A callable collate function.
        :rtype: Callable[[List[Dict[str, Any]]], Dict[str, torch.Tensor]]
        """

        return self.image_classification_collate_func
