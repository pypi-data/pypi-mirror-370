# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image finetune component - classification dataset."""

import albumentations
import os

import numpy as np
import pandas as pd

from PIL import Image
from typing import Any, Callable, Dict, Optional

from azureml._common._error_definition.azureml_error import AzureMLError

from azureml.acft.common_components.utils.logging_utils import get_logger_app
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException

from azureml.acft.image.components.finetune.common.constants.augmentation_constants import (
    AlbumentationParamNames,
)
from azureml.acft.image.components.finetune.common.constants.constants import (
    ImageDataFrameConstants,
    ImageDataItemLiterals,
)
from azureml.acft.image.components.finetune.common.data.base_dataset import (
    BaseDataset,
)


logger = get_logger_app(__name__)


class ImageClassificationDataset(BaseDataset):
    """Image Classification Dataset for HF"""

    SUPPORTED_TRANSFORM_LIB_NAME_MAPPING = {
        albumentations.core.composition.Compose: AlbumentationParamNames.LIB_NAME
    }

    def __init__(
        self,
        mltable_path: Optional[str] = None,
        images_df: Optional[pd.DataFrame] = None,
        data_dir: Optional[str] = None,
        image_column_name: str = ImageDataFrameConstants.DEFAULT_IMAGE_COLUMN_NAME,
        label_column_name: str = ImageDataFrameConstants.DEFAULT_LABEL_COLUMN_NAME,
    ) -> None:

        """Constructor - This reads the MLTable and creates Classification dataset, if data frame and download
        directory is provided, this will directly create pytorch dataset.

        :param mltable_data: azureml MLTable path.
        :type mltable_data: str
        :param images_df: Pandas dataframe from Aml dataset.
        :type images_df: Pandas dataframe
        :param data_dir: image folder for downloaded images.
        :type data_dir: str
        :param image_column_name: image stream column for dataframe.
        :type image_column_name: str
        :param label_column_name: label column for dataframe.
        :type label_column_name: str
        """
        super().__init__(
            mltable_path=mltable_path,
            images_df=images_df,
            data_dir=data_dir,
            image_column_name=image_column_name,
            label_column_name=label_column_name,
        )

        # set default value for multilabel and transform flag
        self.multilabel = False
        self.transform = None
        # validate loaded dataframe
        self.validate_image_dataframe()

    def __len__(self) -> int:
        """return length of the dataset"""
        return len(self.images_df)

    def set_multilabel(self, multilabel: bool) -> None:
        """Set multilabel flag for  image classification multilabel task

        :param multilabel: flag for multilabel image classification.
        :type multilabel: bool
        """
        self.multilabel = multilabel

    def set_transform(self, transform: Callable) -> None:
        """Set transform to the specified transform"""
        self.transform = transform

        # check supported augmentation transforms
        self._check_supported_transform_type()

        # Get augmentation library name
        self._set_augmentation_library_name_from_transform()

        # Prepare an apply transform factory
        self._set_apply_transform_factory()

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
            logger.error(f"{type(self.transform)} is not supported. Only"
                         f" {list( self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys())} are supported for now.")
            raise NotImplementedError(
                f"{type(self.transform)} is not supported. "
                f"Only {list( self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys())} are supported for now."
            )

    def _set_augmentation_library_name_from_transform(self):
        """Extract augmentation library name based on the transform and set it."""
        # Get augmentation library name
        for supported_transform in self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys():
            if isinstance(self.transform, supported_transform):
                self.augmentation_lib_name = self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING[
                    supported_transform
                ]
                break

    def _set_apply_transform_factory(self):
        """Prepare apply_transoform factory."""
        # Prepare an apply transform factory
        self.apply_transform_factory = {
            AlbumentationParamNames.LIB_NAME: self._albumentations_apply_transform
        }

    def _albumentations_apply_transform(self, image: np.ndarray) -> np.ndarray:
        """Apply albumentations transform

        :param image: Input image
        :type image: np.ndarray

        :return: An image with transform applied, if transform type is supported. Otherwise, raise error.
        :rtype: np.ndarray
        """
        return self.transform(image=image)[
            ImageDataItemLiterals.ALBUMENTATIONS_IMAGE_KEY
        ]

    def set_classes_metadata(self, all_labels_to_id: Dict[str, int] = None) -> None:
        """Set metadata for Image Classification
        Provide all_labels_to_id from training dataset to make a
        superset of labels from training and validation dataset.

        :param all_labels_to_id: all id to label dict from training dataset
        :type all_labels_to_id: Dict[str, int]
        """

        labels = self.images_df[self.label_column_name]
        if self.multilabel:
            classes = set()
            for label in labels:
                for item in label:
                    classes.add(item)
        else:
            classes = set(labels)
        # Use sorted class names for reproducibility
        classes = sorted(list(classes))

        if all_labels_to_id is None:
            self.id2label = {k: v for k, v in enumerate(classes)}
            self.label2id = {v: k for k, v in enumerate(classes)}
        else:
            all_label_classes = set(all_labels_to_id)
            superset_classes = all_label_classes.union(classes)
            # Use sorted class names for reproducibility
            superset_classes = sorted(list(superset_classes))
            self.id2label = {k: v for k, v in enumerate(superset_classes)}
            self.label2id = {v: k for k, v in enumerate(superset_classes)}

    def _apply_transform(self, image: np.ndarray) -> np.ndarray:
        """Apply transform

        :param image: Input image
        :type image: np.ndarray

        :return: An image with transform applied, if transform type is supported. Otherwise, raise error.
        :rtype: np.ndarray
        """
        return self.apply_transform_factory[self.augmentation_lib_name](image=image)

    def __getitem__(self, index: int) -> Dict[str, Any]:
        """Get item from the dataset

        :param index: index of the item
        :type index: int

        :return: (transformed) item
        :rtype: Dict[str, Any]
        """
        # read the image from dataframe
        rel_path = self.images_df[self.image_column_name].iloc[index]
        image_path = os.path.join(self.data_dir, str(rel_path))
        image = Image.open(image_path).convert("RGB")

        # read the label from dataframe
        label = self.images_df[self.label_column_name].iloc[index]

        if self.transform is not None:
            image = self._apply_transform(image=np.array(image))

        example = {
            ImageDataItemLiterals.DEFAULT_IMAGE_KEY: np.asarray(image),
            ImageDataItemLiterals.DEFAULT_LABEL_KEY: label,
        }
        return example

    def validate_image_dataframe(self) -> None:
        """Validate image classification dataframe."""
        if self.images_df.empty:
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message="Image dataframe should not be empty.")
            )
        if self.label_column_name not in self.images_df.columns:
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=f"{self.label_column_name} is not present in image dataframe.")
            )

        if self.image_column_name not in self.images_df.columns:
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=f"{self.image_column_name} is not present in image dataframe.")
            )
