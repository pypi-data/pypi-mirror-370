# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image finetune component - base dataset."""

from __future__ import annotations

import pandas as pd

from abc import abstractmethod, ABC
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from typing import Dict, Optional, Tuple

from azureml._common._error_definition.azureml_error import AzureMLError

from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException

from azureml.acft.image.components.finetune.common.constants.constants import (
    VisionDatasetConstants,
    ImageDataFrameConstants,
)
from azureml.acft.image.components.finetune.common.data.download_manager import (
    DownloadManager,
)


class BaseDataset(ABC, Dataset):
    """Base dataset class that provides additional functionalities on torch.utils.Dataset.

    Inheriting classes should call the base constructor.
    """

    def __init__(
        self,
        mltable_path: Optional[str] = None,
        images_df: Optional[pd.DataFrame] = None,
        data_dir: Optional[str] = None,
        image_column_name: str = ImageDataFrameConstants.DEFAULT_IMAGE_COLUMN_NAME,
        label_column_name: str = ImageDataFrameConstants.DEFAULT_LABEL_COLUMN_NAME,
    ) -> None:

        """Constructor - This reads the MLTable and creates pytorch dataset with whe help of Dataset Helper class.
        If data frame and download directory is provided, this will directly create pytorch dataset.

        :param mltable_data: azureml MLTable path.
        :type mltable_data: str
        :param images_df: Pandas dataframe from Aml dataset.
        :type images_df: Pandas dataframe
        :param data_dir: image folder for downloaded images.
        :type data_dir: str
        :param image_column_name: image url column for dataframe.
        :type image_column_name: str
        :param label_column_name: label column for dataframe.
        :type label_column_name: str
        """
        super().__init__()
        self.label2id = dict()
        self.id2label = dict()

        if images_df is not None:
            # images df and download directory is available
            if data_dir is None:
                raise ACFTDataException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message="data_dir cannot be None if image_df is specified.",
                    )
                )
            self.images_df = images_df
            self.data_dir = data_dir
            self.image_column_name = image_column_name
            self.label_column_name = label_column_name

        else:
            # create dataframe from mltable and download the images
            self.download_manager = DownloadManager(mltable_path)
            self.images_df = self.download_manager._images_df
            self.data_dir = self.download_manager._data_dir
            self.image_column_name = self.download_manager._image_column_name
            self.label_column_name = self.download_manager._label_column_name

    @abstractmethod
    def __len__(self):
        """Implement __len__ method for corresponding derived class."""
        pass

    @abstractmethod
    def __getitem__(self, index):
        """Implement __getitem__ method for corresponding derived class."""
        pass

    @abstractmethod
    def set_classes_metadata(self, all_labels_to_id: Dict[str, int] = None):
        """Set metadata for corresponding derived class."""
        pass

    @abstractmethod
    def validate_image_dataframe(self):
        """Validate loaded image dataframe."""
        pass

    def train_val_split(
        self, valid_portion: int = VisionDatasetConstants.DEFAULT_VALIDATION_SIZE
    ) -> Tuple[BaseDataset, BaseDataset]:
        """Splits a dataset into two datasets, one for training and one for validation.

        :param valid_portion: (optional) Portion of dataset to use for validation.
        :type valid_portion: Float between 0.0 and 1.0
        :return: Two base Dataset objects containing the split data.
        :rtype: BaseDataset, BaseDataset
        """

        train, val = train_test_split(self.images_df, test_size=valid_portion)
        return self._clone_dataset(train), self._clone_dataset(val)

    def _clone_dataset(self, images_df: pd.DataFrame) -> BaseDataset:
        """Create a copy of a dataset but with the specified image dataframe.

        :param images_df: Labeled dataset DataFrame.
        :type images_df: pandas.DataFrame
        :return: The copy of the BaseDataset.
        :rtype: BaseDataset
        """

        return self.__class__(
            images_df=images_df,
            data_dir=self.data_dir,
            image_column_name=self.image_column_name,
            label_column_name=self.label_column_name,
        )
