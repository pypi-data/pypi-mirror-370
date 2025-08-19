# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Download manager helper class for reading AzureML MLTable"""

import os
import tempfile
import time
from typing import cast

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.core import Dataset as AmlDataset
from azureml.core import Run
from azureml.core.run import _OfflineRun
from azureml.core.workspace import Workspace
from azureml.data.abstract_dataset import AbstractDataset
from azureml.dataprep import ExecutionError
from azureml.dataprep.api.engineapi.typedefinitions import FieldType
from azureml.exceptions import UserErrorException

from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError, ACFTSystemError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException, ACFTSystemException

from azureml.acft.image.components.common.utils import get_workspace
from azureml.acft.image.components.finetune.common.constants.constants import (
    ImageDataFrameConstants,
)

logger = get_logger_app(__name__)


class DownloadManager:
    """A helper class that reads MLTable, download images and prepares the dataframe"""

    def __init__(
        self,
        mltable_data: str,
        ignore_data_errors: bool = False,
        image_column_name: str = ImageDataFrameConstants.DEFAULT_IMAGE_COLUMN_NAME,
        download_files: bool = True,
    ):

        """Constructor - This reads the MLTable and downloads the images that it contains.

        :param mltable_data: azureml MLTable path
        :type mltable_data: str
        :param ignore_data_errors: Setting this ignores and files in the dataset that fail to download.
        :type ignore_data_errors: bool
        :param image_column_name: The column name for the image file.
        :type image_column_name: str
        :param download_files: Flag to download files or not.
        :type download_files: bool
        """
        self._dataset = DownloadManager._get_dataset_from_mltable(mltable_data)

        self._data_dir = DownloadManager._get_data_dir()

        self._image_column_name = DownloadManager._get_image_column_name(
            self._dataset, image_column_name
        )
        self._label_column_name = DownloadManager._get_label_column_name(
            self._dataset, ImageDataFrameConstants.DEFAULT_LABEL_COLUMN_NAME
        )

        if download_files:
            DownloadManager._download_image_files(
                self._dataset, self._image_column_name
            )

        self._images_df = self._dataset.to_pandas_dataframe()

        # drop rows for which images are not downloaded
        if download_files and ignore_data_errors:
            missing_file_indices = []
            for index in self._images_df.index:
                full_path = self._get_image_full_path(index)
                if not os.path.exists(full_path):
                    missing_file_indices.append(index)
                    logger.warning("File not found. Since ignore_data_errors is True, this file will be ignored.")
            self._images_df.drop(missing_file_indices, inplace=True)
            self._images_df.reset_index(inplace=True, drop=True)

    @staticmethod
    def _get_dataset_from_mltable(mltable_path: str) -> AbstractDataset:
        """Get dataset from mltable.

        :param mltable_path: MLTable containing dataset URI
        :type mltable_path: str
        :param workspace: workspace object
        :type workspace: azureml.core.Workspace
        :return: The dataset corresponding to given label.
        :rtype: AbstractDataset
        """

        dataset = None
        if mltable_path is None:
            raise ACFTDataException._with_error(
                AzureMLError.create(ACFTUserError, pii_safe_message="Mltable path is not provided.")
            )
        else:
            try:
                dataset = DownloadManager._load_abstract_dataset(mltable_path)
            except (UserErrorException, ValueError) as e:
                msg = f"MLTable input is invalid. {e}"
                raise ACFTDataException._with_error(
                    AzureMLError.create(ACFTUserError, pii_safe_message=msg)
                ) from e
            except Exception as e:
                msg = f"Error in loading MLTable. {e}"
                raise ACFTSystemException._with_error(
                    AzureMLError.create(ACFTSystemError, pii_safe_message=msg)
                ) from e

        return dataset

    @staticmethod
    def _load_abstract_dataset(mltable_path: str) -> AbstractDataset:
        """Get abstract dataset  from mltable.

        :param mltable_path: MLTable containing dataset URI
        :type mltable_path: str
        :return: The dataset corresponding to given label.
        :rtype: AbstractDataset
        """
        ws = get_workspace()
        return AbstractDataset._load(mltable_path, ws)

    def _get_image_full_path(self, index: int) -> str:
        """Return the full local path for an image.

        :param index: index
        :type index: int
        :return: Full path for the local image file
        :rtype: str
        """
        rel_path = self._images_df[self._image_column_name].iloc[index]
        abs_path = os.path.join(self._data_dir, str(rel_path))
        return abs_path

    @staticmethod
    def _get_data_dir() -> str:
        """Get the data directory to download the image files to.

        :return: Data directory path
        :type: str
        """
        return tempfile.gettempdir()

    @staticmethod
    def _get_column_name(
        ds: AmlDataset, parent_column_property: str, default_value: str
    ) -> str:
        """Get the column name by inspecting AmlDataset properties.
        Return default_column_name if not found in properties.

        :param ds: Aml Dataset object
        :type ds: TabularDataset
        :param parent_column_property: parent column property of the AmlDataset
        :type parent_column_property: str
        :param default_value: default value to return
        :type default_value: str
        :return: column name
        :rtype: str
        """
        if parent_column_property not in ds._properties:
            return default_value
        else:
            image_property = ds._properties[parent_column_property]
            if ImageDataFrameConstants.COLUMN_PROPERTY in image_property:
                return cast(
                    str, image_property[ImageDataFrameConstants.COLUMN_PROPERTY]
                )
            lower_column_property = ImageDataFrameConstants.COLUMN_PROPERTY.lower()
            if lower_column_property in image_property:
                return cast(str, image_property[lower_column_property])

    @staticmethod
    def _get_image_column_name(ds: AmlDataset, default_image_column_name: str) -> str:
        """Get the image column name by inspecting AmlDataset properties.
        Return default_image_column_name if not found in properties.

        :param ds: Aml Dataset object
        :type ds: TabularDataset
        :param default_image_column_name: default value to return
        :type default_image_column_name: str
        :return: Image column name
        :rtype: str
        """
        return DownloadManager._get_column_name(
            ds, ImageDataFrameConstants.IMAGE_COLUMN_PROPERTY, default_image_column_name
        )

    @staticmethod
    def _get_label_column_name(ds: AmlDataset, default_label_column_name: str) -> str:
        """Get the label column name by inspecting AmlDataset properties.
        Return default_label_column_name if not found in properties.

        :param ds: Aml Dataset object
        :type ds: TabularDataset
        :param default_label_column_name: default value to return
        :type default_label_column_name: str
        :return: Label column name
        :rtype: str
        """
        return DownloadManager._get_column_name(
            ds, ImageDataFrameConstants.LABEL_COLUMN_PROPERTY, default_label_column_name
        )

    @staticmethod
    def _download_image_files(ds, image_column_name: str) -> None:
        """Helper method to download dataset files.

        :param ds: Aml Dataset object
        :type ds: TabularDataset
        :param image_column_name: The column name for the image file.
        :type image_column_name: str
        """
        DownloadManager._validate_image_column(ds, image_column_name)
        logger.info("Start downloading image files")
        start_time = time.perf_counter()
        data_dir = DownloadManager._get_data_dir()
        try:
            ds.download(
                stream_column=image_column_name,
                target_path=data_dir,
                ignore_not_found=True,
                overwrite=True,
            )
        except (ExecutionError, UserErrorException) as e:
            msg = f"Could not download dataset files. Please check the logs for more details. Error Code: {e}"
            raise ACFTDataException._with_error(
                AzureMLError.create(ACFTUserError, pii_safe_message=msg)
            ) from e

        logger.info(
            f"Downloading image files took {time.perf_counter() - start_time:.2f} seconds"
        )

    @staticmethod
    def _validate_image_column(ds: AmlDataset, image_column_name: str) -> None:
        """Helper method to validate if image column is present in dataset, and it's type is STREAM.

        :param ds: Aml Dataset object
        :type ds: TabularDataset
        :param image_column_name: The column name for the image file.
        :type image_column_name: str
        """
        dtypes = ds._dataflow.dtypes
        if image_column_name not in dtypes:
            msg = f"Image URL column '{image_column_name}' is not present in the dataset."
            raise ACFTDataException._with_error(
                AzureMLError.create(ACFTUserError, pii_safe_message=msg)
            )
        image_column_dtype = dtypes.get(image_column_name)
        if image_column_dtype != FieldType.STREAM:
            msg = f"The data type of image URL column '{image_column_name}' is {image_column_dtype.name}, " \
                  f"but it should be {FieldType.STREAM.name}."

            raise ACFTDataException._with_error(
                AzureMLError.create(ACFTUserError, pii_safe_message=msg)
            )
