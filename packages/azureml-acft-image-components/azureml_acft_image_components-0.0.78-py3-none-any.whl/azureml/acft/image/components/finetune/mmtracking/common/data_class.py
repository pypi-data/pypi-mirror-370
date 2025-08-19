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

from azureml.acft.image.components.finetune.common.augmentation.openmmlab_augmentation import (
    MmlabAugmentation,
)
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals, SettingParameters, VisionDatasetConstants
)
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.mmtracking.common.constants import (
    MmTrackingDatasetLiterals,
)
from azureml.acft.image.components.finetune.mmtracking.common.dataset import (
    MmTrackingDataset
)
from azureml.acft.image.components.finetune.common.data.data_utils import (
    get_dataset
)
from azureml.acft.image.components.finetune.interfaces.azml_interface import AzmlDataInterface

from azureml.acft.image.components.finetune.mmtracking.common.model import TrackingConfigBuilder

from azureml.acft.common_components.image.runtime_common.common import (
    utils,
    distributed_utils,
)

logger = get_logger_app(__name__)


class AzmlMMTImageDataClass(AzmlDataInterface):
    """Data Class for MMDetection Image Models"""

    def __init__(self, **kwargs) -> None:
        """Initialize the data class for MMDetection Image Models

        :param kwargs: Keyword arguments
        :type kwargs: Dict

        returns: None
        rtype: None
        """

        self.apply_augmentations = kwargs.get(
            SettingLiterals.APPLY_AUGMENTATIONS, False
        )
        image_width = kwargs.get(SettingLiterals.IMAGE_WIDTH)
        image_height = kwargs.get(SettingLiterals.IMAGE_HEIGHT)
        model_name_or_path = kwargs.get(SettingLiterals.MODEL_NAME_OR_PATH, None)
        self.model_preprocessing_param_dict = self._get_model_preprocessing_dict(model_name_or_path,
                                                                                 image_width, image_height) \
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

    def _get_model_preprocessing_dict(self, model_name_or_path: str, image_width: int, image_height: int) -> Dict:
        """ Read the model config and return the preprocessing pipeline dict

        :param model_name_or_path: Name/path of the mmdetection model
        :param type: str
        :param image_width: width of the image for data augmentation
        :param type: int
        :param image_height: height of the image for data augmentation
        :param type: int

        :return: MMdetcetion model configuration related to dataset preprocessing
                 such as transformations to apply.
        :rtype: Dict
        """
        config = (
            TrackingConfigBuilder(model_name_or_path)
            .set_image_scale((image_width, image_height))
            .build()
        )
        return config.data

    def _get_train_valid_augmentation_transforms(
        self, **kwargs
    ) -> Tuple[Optional[Callable], Optional[Callable]]:
        """Get train and/or validation transforms

        :return: A tuple with train and validation transform
        :rtype: Tuple[Optional[Callable], Optional[Callable]]
        """

        augmentation_class_obj = MmlabAugmentation(
            model_preprocessing_params_dict=self.model_preprocessing_param_dict,
            **kwargs,
        )
        # Note/Todo: Output augmentation_class_obj.augmentations_dict to one of the output ports.
        valid_transform = augmentation_class_obj.get_valid_transform()
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

        # for MOTS tasks which are not onboarded, we will need to have the masks check.
        # self.masks_required = bool(kwargs[SettingLiterals.TASK_NAME] == Tasks.MM_INSTANCE_SEGMENTATION)
        self.masks_required = False

        settings = {
            SettingLiterals.OUTPUT_DIR: kwargs.pop(SettingLiterals.OUTPUT_DIR, SettingParameters.DEFAULT_OUTPUT_DIR),
            SettingLiterals.USE_BG_LABEL: kwargs.pop(SettingLiterals.USE_BG_LABEL, False),
            SettingLiterals.IGNORE_DATA_ERRORS: kwargs.pop(SettingLiterals.IGNORE_DATA_ERRORS, True)
        }
        train_tabular_ds, valid_tabular_ds = get_dataset(
            training_mltable=train_mltable_path,
            validation_mltable=validation_mltable_path,
            settings=settings)
        train_images_df = self.get_images_df(train_tabular_ds)

        if valid_tabular_ds is not None:
            valid_images_df = self.get_images_df(valid_tabular_ds)
        else:
            train_images_df, valid_images_df = self.train_val_split(train_images_df)

        self.train_ds = MmTrackingDataset(train_images_df, is_train=True, load_as_video=False)
        self.validation_ds = MmTrackingDataset(valid_images_df, is_train=False, load_as_video=True)

        if self.train_ds.classes != self.validation_ds.classes:
            classes = set(self.train_ds.classes) | set(self.validation_ds.classes)
            self.train_ds.set_classes(classes)
            self.validation_ds.set_classes(classes)

        # set train transform
        self.train_ds.set_transform(transform=train_transform)
        # set valid transform
        self.validation_ds.set_transform(transform=valid_transform)

        # save images df
        master_process = distributed_utils.master_process()
        if master_process:
            utils._save_image_df(
                train_df=train_images_df,
                val_df=valid_images_df,
                output_dir=settings[SettingLiterals.OUTPUT_DIR],
                label_column_name=kwargs.get(SettingLiterals.LABEL_COLUMN_NAME, None),
            )

    def get_images_df(self, tabular_ds):
        """get image data frame from tabular dataset with local image file location
        """
        dataset_helper = tabular_ds.dataset_helper
        images_df = dataset_helper.images_df
        images_df["local_image_url"] = [dataset_helper.get_image_full_path(i) for i in images_df.index]

        if MmTrackingDatasetLiterals.VIDEO_DETAILS not in images_df.columns:
            raise ACFTDataException._with_error(
                AzureMLError.create(ACFTUserError,
                                    pii_safe_message="missing video_details data field"))

        def correct_format(video_details_dict):
            return MmTrackingDatasetLiterals.VIDEO_NAME in video_details_dict and \
                MmTrackingDatasetLiterals.FRAME_ID in video_details_dict and \
                isinstance(video_details_dict[MmTrackingDatasetLiterals.FRAME_ID], int)
        if not images_df[MmTrackingDatasetLiterals.VIDEO_DETAILS].apply(correct_format).all():
            raise ACFTDataException._with_error(
                AzureMLError.create(ACFTUserError,
                                    pii_safe_message="video_details should contain video_name, frame_id"))

        return images_df

    def train_val_split(self, train_df, **kwargs):
        """perform train, validation split on the train tabular dataset
        """
        number_of_samples = len(train_df)
        if number_of_samples == 1:
            logger.warning("Only one data point provided, will use this for both training and validation.")
            new_train_df, new_val_df = train_df.copy(), train_df.copy()
            return new_train_df, new_val_df

        # train test split
        validation_size = kwargs.pop(SettingLiterals.TRAIN_VAL_SPLIT_RATIO,
                                     VisionDatasetConstants.DEFAULT_VALIDATION_SIZE)
        split_point = int((1 - validation_size) * number_of_samples)
        new_train_df, new_val_df = train_df[:split_point], train_df[split_point:]
        new_val_df = new_val_df.reset_index(drop=True)

        # edit val df by split video name / frame id
        video_detail = new_val_df.loc[0][MmTrackingDatasetLiterals.VIDEO_DETAILS]
        split_video_name = video_detail[MmTrackingDatasetLiterals.VIDEO_NAME]
        split_frame_id = video_detail[MmTrackingDatasetLiterals.FRAME_ID]

        def edit_by_split_video(row):
            if row[MmTrackingDatasetLiterals.VIDEO_DETAILS][MmTrackingDatasetLiterals.VIDEO_NAME] == split_video_name:
                row[MmTrackingDatasetLiterals.VIDEO_DETAILS][MmTrackingDatasetLiterals.FRAME_ID] -= split_frame_id
            return row
        new_val_df = new_val_df.apply(edit_by_split_video, axis=1).head()
        return new_train_df, new_val_df

    def _set_classes_metadata(self) -> None:
        """copy the label mappings from train_dataset"""
        dataset = self.get_train_dataset()
        self.label2id = {c: dataset.class_name_to_id[c] for c in dataset.classes}
        self.id2label = {v: k for k, v in self.label2id.items()}

    def get_train_dataset(self) -> MmTrackingDataset:
        """get train dataset

        :return : train dataset
        :rtype: MmObjectDetectionDataset
        """
        return self.train_ds

    def get_validation_dataset(self) -> MmTrackingDataset:
        """get validation dataset

        :return : validation dataset
        :rtype: MmObjectDetectionDataset
        """
        return self.validation_ds

    def get_collation_function(
        self,
    ) -> Callable[[List[Dict[str, Dict]]], Dict[str, Dict]]:
        """
        collate function for MMDetection Object Detection/Instace Segmentation

        return: callable function
        rtype: Callable[[List[Dict[str, Dict]]], Dict[str, Dict]]
        """

        def tracking_collate_func(
            examples: List[Dict[str, Dict]]
        ) -> Dict[str, Dict]:

            # Filter out invalid examples
            valid_examples = [example for example in examples if example is not None]
            if len(valid_examples) != len(examples):
                if len(valid_examples) == 0:
                    raise ACFTDataException._with_error(
                        AzureMLError.create(ACFTUserError,
                                            pii_safe_message="All images in the current batch are invalid.")
                    )
                else:
                    num_invalid_examples = len(examples) - len(valid_examples)
                    logger.info(f"{num_invalid_examples} invalid images found.")
                    logger.info("Replacing invalid images with randomly selected valid images from the current batch")
                    new_example_indices = np.random.choice(np.arange(len(valid_examples)), num_invalid_examples)
                    for ind in new_example_indices:
                        # Padding the batch with valid examples
                        valid_examples.append(valid_examples[ind])

            pixel_values = torch.stack([example[MmTrackingDatasetLiterals.IMG] for example in valid_examples])
            img_metas = [example[MmTrackingDatasetLiterals.IMG_METAS] for example in valid_examples]
            gt_bboxes = [example[MmTrackingDatasetLiterals.GT_BBOXES] for example in valid_examples]
            gt_labels = [example[MmTrackingDatasetLiterals.GT_LABELS] for example in valid_examples]
            gt_crowds = [example[MmTrackingDatasetLiterals.GT_CROWDS] for example in valid_examples]
            original_bboxes = [example[MmTrackingDatasetLiterals.ORIGINAL_GT_BBOXES] for example in valid_examples]
            # dummy_labels are added since hf_trainer expects same size tensors in
            # distributed gather step in evaluation loop
            dummy_labels = [torch.tensor(1)] * len(gt_labels)
            output = {
                MmTrackingDatasetLiterals.IMG: pixel_values,
                MmTrackingDatasetLiterals.IMG_METAS: img_metas,
                MmTrackingDatasetLiterals.GT_BBOXES: gt_bboxes,
                MmTrackingDatasetLiterals.GT_LABELS: gt_labels,
                MmTrackingDatasetLiterals.GT_CROWDS: gt_crowds,
                MmTrackingDatasetLiterals.DUMMY_LABELS: dummy_labels,
                MmTrackingDatasetLiterals.ORIGINAL_GT_BBOXES: original_bboxes,
            }

            if MmTrackingDatasetLiterals.GT_INSTANCE_IDS in examples[0]:
                gt_instance_ids = [example[MmTrackingDatasetLiterals.GT_INSTANCE_IDS] for example in valid_examples]
                output[MmTrackingDatasetLiterals.GT_INSTANCE_IDS] = gt_instance_ids

            if self.masks_required:
                gt_masks = [example[MmTrackingDatasetLiterals.GT_MASKS] for example in valid_examples]
                output = {**output, MmTrackingDatasetLiterals.GT_MASKS: gt_masks}

            return output

        return tracking_collate_func
