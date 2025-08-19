# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image finetune component - runtime classification dataset."""

from __future__ import annotations
import json
import numpy as np
import albumentations
from torch import Tensor
from typing import cast, Tuple, Dict, Callable
import pandas as pd
from azureml.automl.core.shared.constants import MLTableLiterals, MLTableDataLabel
from azureml.acft.image.components.finetune.common.constants.augmentation_constants import (
    AlbumentationParamNames,
)
from azureml.acft.image.components.finetune.common.constants.constants import (
    ImageDataItemLiterals,
)
from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.common.utils import get_workspace
from azureml.acft.image.components.finetune.common.constants.constants import (
    VisionDatasetConstants,
    SettingLiterals,
    SettingParameters,
)
from azureml.acft.common_components.image.runtime_common.common import (
    utils,
    distributed_utils,
)
from azureml.acft.common_components.image.runtime_common.common.aml_dataset_base_wrapper import (
    AmlDatasetBaseWrapper,
)
from azureml.acft.common_components.image.runtime_common.classification.io.read.dataset_wrappers import (
    AmlDatasetWrapper,
)


logger = get_logger_app(__name__)


class HfClassificationDatasetRuntimeWrapper(AmlDatasetWrapper):
    """
    This is a wrapper on runtime classification AmlDatasetWrapper that adds functionality
    to make it suitable for HF trainer.
    """

    SUPPORTED_TRANSFORM_LIB_NAME_MAPPING = {albumentations.core.composition.Compose: AlbumentationParamNames.LIB_NAME}

    def __init__(self, *args, **kwargs):
        """Initialize the dataset wrapper"""
        self.transform = None
        super().__init__(*args, **kwargs)

    def __getitem__(self, index: int) -> Tuple[Tensor, dict]:
        """Convert output of AmlDatasetWrapper get item to make it generalized and usable in components

        :param index: Index of object
        :type index: int
        :return: Image tensor in de-normalized form [0-255], training labels
        :rtype: Tuple[Tensor, dict]
        """
        image, training_labels = super().__getitem__(index)

        if image is None:
            logger.info("Image was not found for a data point in the batch, the data point is marked as invalid.")
            return None
        if training_labels is None:
            logger.info(
                "Labels were not found for a data point in the batch, the data point is marked as invalid."
            )
            return None

        if self.transform is not None:
            image = self._apply_transform(image=np.array(image))

        example = {
            ImageDataItemLiterals.DEFAULT_IMAGE_KEY: np.asarray(image),
            ImageDataItemLiterals.DEFAULT_LABEL_KEY: training_labels,
        }
        return example

    def _check_supported_transform_type(self) -> None:
        """Check supported transform type

        :return: None
        :rtype: None
        """
        # Check for supported augmentation transform
        if self.transform and not any(
            [
                isinstance(self.transform, supported_transform)
                for supported_transform in self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys()
            ]
        ):
            logger.error(
                f"{type(self.transform)} is not supported. Only"
                f" {list( self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys())} are supported for now."
            )
            raise NotImplementedError(
                f"{type(self.transform)} is not supported. "
                f"Only {list( self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys())} are supported for now."
            )

    def _set_augmentation_library_name_from_transform(self):
        """Extract augmentation library name based on the transform and set it."""
        # Get augmentation library name
        for supported_transform in self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys():
            if isinstance(self.transform, supported_transform):
                self.augmentation_lib_name = self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING[supported_transform]
                break

    def _set_apply_transform_factory(self):
        """Prepare apply_transoform factory."""
        # Prepare an apply transform factory
        self.apply_transform_factory = {AlbumentationParamNames.LIB_NAME: self._albumentations_apply_transform}

    def _albumentations_apply_transform(self, image: np.ndarray) -> np.ndarray:
        """Apply albumentations transform

        :param image: Input image
        :type image: np.ndarray

        :return: An image with transform applied, if transform type is supported. Otherwise, raise error.
        :rtype: np.ndarray
        """
        return self.transform(image=image)[ImageDataItemLiterals.ALBUMENTATIONS_IMAGE_KEY]

    def _apply_transform(self, image: np.ndarray) -> np.ndarray:
        """Apply transform

        :param image: Input image
        :type image: np.ndarray

        :return: An image with transform applied, if transform type is supported. Otherwise, raise error.
        :rtype: np.ndarray
        """
        return self.apply_transform_factory[self.augmentation_lib_name](image=image)

    def set_transform(self, transform: Callable) -> None:
        """Set transform to the specified transform"""
        self.transform = transform

        # check supported augmentation transforms
        self._check_supported_transform_type()

        # Get augmentation library name
        self._set_augmentation_library_name_from_transform()

        # Prepare an apply transform factory
        self._set_apply_transform_factory()

    def clone_dataset(self, images_df: pd.DataFrame) -> HfClassificationDatasetRuntimeWrapper:
        """Create a copy of a dataset but with the specified image dataframe.

        :param images_df: Labeled dataset DataFrame.
        :type images_df: pandas.DataFrame
        :return: The copy of the HfClassificationDatasetRuntimeWrapper.
        :rtype: HfClassificationDatasetRuntimeWrapper
        """

        return HfClassificationDatasetRuntimeWrapper(
            images_df=images_df,
            label_column_name=self._label_column_name,
            ignore_data_errors=self._ignore_data_errors,
            data_dir=self._data_dir,
            multilabel=self._multilabel,
            stream_image_files=self._stream_image_files,
        )


def _combine_mltables(training_mltable: str, validation_mltable: str) -> str:
    """Combine mltables to make single mltable to pass in get_tabular_dataset
    :param training_mltable: The training mltable path
    :type training_mltable: str
    :param validation_mltable: The validation mltable path
    :type validation_mltable: str
    :return: mltable in serialized json format
    :rtype: str
    """

    mltable = {MLTableDataLabel.TrainData.value: {MLTableLiterals.MLTABLE_RESOLVEDURI: training_mltable}}
    if validation_mltable is not None:
        mltable[MLTableDataLabel.ValidData.value] = {MLTableLiterals.MLTABLE_RESOLVEDURI: validation_mltable}
    return json.dumps(mltable)


def get_classification_dataset(
    training_mltable: str,
    settings: Dict = {},
    validation_mltable: str = None,
    multi_label: bool = False,
) -> Tuple[HfClassificationDatasetRuntimeWrapper, HfClassificationDatasetRuntimeWrapper]:
    """
    Return training and validation dataset for classification task from mltable
    :param training_mltable: The training mltable path
    :type training_mltable: str
    :param settings: Settings dictionary
    :type settings: Dict
    :param validation_mltable: The validation mltable path
    :type validation_mltable: str
    :param multi_label: True if multi label classification, False otherwise
    :type multi_label: bool
    :return: Training dataset, validation dataset
    :rtype: Tuple[HfClassificationDatasetRuntimeWrapper, HfClassificationDatasetRuntimeWrapper]
    """

    mltable = _combine_mltables(training_mltable, validation_mltable)

    dataset_wrapper: AmlDatasetBaseWrapper = cast(AmlDatasetBaseWrapper, AmlDatasetWrapper)

    ws = get_workspace()
    train_tabular_ds, validation_tabular_ds = utils.get_tabular_dataset(settings=settings, mltable_json=mltable)

    utils.download_or_mount_image_files(
        settings=settings,
        train_ds=train_tabular_ds,
        validation_ds=validation_tabular_ds,
        dataset_class=dataset_wrapper,
        workspace=ws,
    )

    validation_size = settings.get(
        SettingLiterals.TRAIN_VAL_SPLIT_RATIO,
        VisionDatasetConstants.DEFAULT_VALIDATION_SIZE,
    )
    output_directory = settings.get(SettingLiterals.OUTPUT_DIR, SettingParameters.DEFAULT_OUTPUT_DIR)
    ignore_data_errors = settings.get(SettingLiterals.IGNORE_DATA_ERRORS, True)
    label_column_name = settings.get(SettingLiterals.LABEL_COLUMN_NAME, None)
    stream_image_files = settings.get(SettingLiterals.STREAM_IMAGE_FILES, False)
    master_process = distributed_utils.master_process()

    train_dataset_wrapper = HfClassificationDatasetRuntimeWrapper(
        train_tabular_ds,
        multilabel=multi_label,
        label_column_name=label_column_name,
        ignore_data_errors=ignore_data_errors,
        stream_image_files=stream_image_files,
    )
    if validation_tabular_ds is None:
        (
            train_dataset_wrapper,
            valid_dataset_wrapper,
        ) = train_dataset_wrapper.train_val_split(validation_size)
    else:
        valid_dataset_wrapper = HfClassificationDatasetRuntimeWrapper(
            validation_tabular_ds,
            multilabel=multi_label,
            label_column_name=label_column_name,
            ignore_data_errors=ignore_data_errors,
            stream_image_files=stream_image_files,
        )

    if master_process:
        utils._save_image_df(
            train_df=train_dataset_wrapper._images_df,
            val_df=valid_dataset_wrapper._images_df,
            output_dir=output_directory,
            label_column_name=label_column_name,
        )

    if valid_dataset_wrapper.labels != train_dataset_wrapper.labels:
        all_labels = list(set(valid_dataset_wrapper.labels + train_dataset_wrapper.labels))
        train_dataset_wrapper.reset_labels(all_labels)
        valid_dataset_wrapper.reset_labels(all_labels)

    logger.info(
        f"# train images: {len(train_dataset_wrapper)}, # validation images: {len(valid_dataset_wrapper)}, \
        # labels: {train_dataset_wrapper.num_classes}"
    )

    return (
        train_dataset_wrapper,
        valid_dataset_wrapper,
    )
