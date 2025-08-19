# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""MMDetection object detection data class"""

import numpy as np
import os
import torch
from typing import Callable, Dict, List, Optional, Tuple

from azureml._common._error_definition import AzureMLError

from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException
from azureml.acft.image.components.finetune.common.augmentation.albumentations_augmentation import (
    AlbumentationsAugmentation as AlbumAugmentations,
)
from azureml.acft.image.components.finetune.common.constants.augmentation_constants import (
    AugmentationConfigFileNames,
)
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals, SettingParameters
)
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.mmdetection.common.dataset import (
    MmObjectDetectionDataset
)
from azureml.acft.image.components.finetune.common.data.runtime_detection_dataset_adapter import (
    get_object_detection_dataset
)
from azureml.acft.image.components.finetune.interfaces.azml_interface import AzmlDataInterface

from azureml.acft.image.components.finetune.mmdetection.common.model import DetectionConfigBuilder
from azureml.acft.image.components.finetune.common.mlflow.mmdet_utils import make_batch
from azureml.acft.image.components.finetune.common.mlflow.common_constants import MmDetectionDatasetLiterals
from azureml.acft.image.components.finetune.common.data.data_utils import filter_invalid_images
logger = get_logger_app(__name__)


class AzmlMMDImageDataClass(AzmlDataInterface):
    """Data Class for MMDetection Image Models"""

    def __init__(self, tokenizer=None, **kwargs) -> None:
        """Initialize the data class for MMDetection Image Models

        :param tokenizer: Tokenizer for the model
        :type tokenizer: Any
        :param kwargs: Keyword arguments
        :type kwargs: Dict

        returns: None
        rtype: None
        """

        self.apply_augmentations = kwargs.get(
            SettingLiterals.APPLY_AUGMENTATIONS, False
        )
        model_name_or_path = kwargs.get(SettingLiterals.MODEL_NAME_OR_PATH, None)
        self.model_preprocessing_param_dict = self._get_model_preprocessing_dict(model_name_or_path) \
            if model_name_or_path else {}
        if model_name_or_path is None:
            logger.info(
                f"{SettingLiterals.MODEL_NAME_OR_PATH} is not present in dataclass, "
                f"hence proceeding with default augmentations."
            )
        # Set the dataset classes
        self._set_dataset_classes(**kwargs)

        # copy the label mappings from train_dataset
        self._set_classes_metadata()

    def _get_model_preprocessing_dict(self, model_name_or_path: str) -> Dict:
        """ Read the model config and return the preprocessing pipeline dict

        :param model_name_or_path: Name/path of the mmdetection model
        :param type: str

        :return: MMdetcetion model configuration related to dataset preprocessing
                 such as transformations to apply.
        :rtype: Dict
        """
        config = DetectionConfigBuilder(model_name_or_path).build()
        return config

    def _get_train_valid_augmentation_transforms(
        self, **kwargs
    ) -> Tuple[Optional[Callable], Optional[Callable]]:
        """Get train and/or validation transforms

        :return: A tuple with train and validation transform
        :rtype: Tuple[Optional[Callable], Optional[Callable]]
        """

        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "..",
            "common/augmentation",
            AugmentationConfigFileNames.OD_IS_ALBUMENTATIONS_CONFIG,
        )
        augmentation_class_obj = AlbumAugmentations(
            config_path=config_path,
            model_preprocessing_params_dict=self.model_preprocessing_param_dict,
            **kwargs,
        )
        # Note/Todo: Output augmentation_class_obj.augmentations_dict to one of the output ports.
        valid_transform = augmentation_class_obj.get_valid_transform()

        # Get train and valid transforms
        if not self.apply_augmentations:
            return valid_transform, valid_transform

        train_transform = augmentation_class_obj.get_train_transform()
        return train_transform, valid_transform

    def _set_dataset_classes(
        self, **kwargs
    ) -> None:
        """Set dataset classes

        :return: None
        :rtype: None
        """
        (
            train_transform,
            valid_transform,
        ) = self._get_train_valid_augmentation_transforms(**kwargs)

        train_mltable_path = kwargs[SettingLiterals.TRAIN_MLTABLE_PATH]
        validation_mltable_path = kwargs.get(
            SettingLiterals.VALIDATION_MLTABLE_PATH, None
        )

        self.masks_required = bool(kwargs[SettingLiterals.TASK_NAME] == Tasks.MM_INSTANCE_SEGMENTATION)

        settings = {
            SettingLiterals.OUTPUT_DIR: kwargs.pop(SettingLiterals.OUTPUT_DIR, SettingParameters.DEFAULT_OUTPUT_DIR),
            SettingLiterals.USE_BG_LABEL: kwargs.pop(SettingLiterals.USE_BG_LABEL, False),
            SettingLiterals.IGNORE_DATA_ERRORS: kwargs.pop(SettingLiterals.IGNORE_DATA_ERRORS, True)
        }
        self.train_ds, self.validation_ds = get_object_detection_dataset(
            training_mltable=train_mltable_path,
            object_detection_dataset=MmObjectDetectionDataset,
            validation_mltable=validation_mltable_path,
            masks_required=self.masks_required,
            settings=settings
        )

        # set train transform
        self.train_ds.set_transform(transform=train_transform)
        if self.validation_ds:
            # set valid transform
            self.validation_ds.set_transform(transform=valid_transform)

    def _set_classes_metadata(self) -> None:
        """copy the label mappings from train_dataset"""
        dataset = self.train_ds.dataset
        self.label2id = {c: dataset.label_to_index_map(c) for c in dataset.classes}
        self.id2label = {v: k for k, v in self.label2id.items()}

    def get_train_dataset(self) -> MmObjectDetectionDataset:
        """get train dataset

        :return : train dataset
        :rtype: MmObjectDetectionDataset
        """
        return self.train_ds

    def get_validation_dataset(self) -> MmObjectDetectionDataset:
        """get validation dataset

        :return : validation dataset
        :rtype: MmObjectDetectionDataset
        """
        return self.validation_ds

    def object_detection_collate_func(self, examples: List[Dict[str, Dict]]) -> Dict[str, Dict]:
        """
        Collate function for MMDetection Object Detection/Instance Segmentation.

        :param examples: A list of dictionaries containing example data.
        :type examples: List[Dict[str, Dict]]

        :return: A dictionary containing batched data.
        :rtype: Dict[str, Dict]
        """
        # Filter out invalid examples
        valid_examples = filter_invalid_images(examples, MmDetectionDatasetLiterals.IMG)

        batched_images = make_batch([example[MmDetectionDatasetLiterals.IMG] for example in valid_examples])
        img_metas = [example[MmDetectionDatasetLiterals.IMG_METAS] for example in valid_examples]
        gt_bboxes = [example[MmDetectionDatasetLiterals.GT_BBOXES] for example in valid_examples]
        gt_labels = [example[MmDetectionDatasetLiterals.GT_LABELS] for example in valid_examples]
        gt_crowds = [example[MmDetectionDatasetLiterals.GT_CROWDS] for example in valid_examples]
        original_gtbboxes = [example[MmDetectionDatasetLiterals.ORIGINAL_GT_BBOXES] for example in valid_examples]
        # dummy_labels are added since hf_trainer expects same size tensors in
        # distributed gather step in evaluation loop
        dummy_labels = [torch.tensor(1)] * len(gt_labels)
        output = {
            MmDetectionDatasetLiterals.IMG: batched_images,
            MmDetectionDatasetLiterals.IMG_METAS: img_metas,
            MmDetectionDatasetLiterals.GT_BBOXES: gt_bboxes,
            MmDetectionDatasetLiterals.GT_LABELS: gt_labels,
            MmDetectionDatasetLiterals.GT_CROWDS: gt_crowds,
            MmDetectionDatasetLiterals.DUMMY_LABELS: dummy_labels,
            MmDetectionDatasetLiterals.ORIGINAL_GT_BBOXES: original_gtbboxes
        }

        if self.masks_required:
            gt_masks = [example[MmDetectionDatasetLiterals.GT_MASKS] for example in valid_examples]
            original_gtmasks = [example[MmDetectionDatasetLiterals.ORIGINAL_GT_MASKS] for example in valid_examples]
            output = {
                **output,
                MmDetectionDatasetLiterals.GT_MASKS: gt_masks,
                MmDetectionDatasetLiterals.ORIGINAL_GT_MASKS: original_gtmasks
            }

        return output

    def get_collation_function(
        self,
    ) -> Callable[[List[Dict[str, Dict]]], Dict[str, Dict]]:
        """
        Get the collate function for MMDetection Object Detection/Instance Segmentation.

        :return: A callable collate function.
        :rtype: Callable[[List[Dict[str, Dict]]], Dict[str, Dict]]
        """
        return self.object_detection_collate_func
