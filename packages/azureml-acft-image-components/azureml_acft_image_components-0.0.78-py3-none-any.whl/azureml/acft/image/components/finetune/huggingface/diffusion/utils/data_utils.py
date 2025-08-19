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

"""
data utils
"""

from pathlib import Path
from typing import Optional, List, Union, Dict, Any

from abc import ABC, abstractmethod

from datasets.load import load_dataset
from datasets import Sequence, Value, ClassLabel
from datasets.arrow_dataset import Dataset

from azureml.acft.accelerator.utils.logging_utils import get_logger_app
from azureml.acft.accelerator.utils.error_handling.exceptions import ValidationException
from azureml.acft.accelerator.utils.error_handling.error_definitions import PathNotFound, ValidationError
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore

from ..constants.constants import AzuremlConstants


logger = get_logger_app()


class AzuremlDataset(ABC):
    """
    All the logic related to data can be a part of this class or the subclass inheriting this
    1. loading and saving the dataset
    2. data wrangling
    3. data collation function
    4. data augmentation (TBD)
    """

    VALID_DATA_FORMATS = ["json", "csv", "parquet"]

    def __init__(
        self,
        path_or_dict: Union[str, Path, Dict],
        label_column: Optional[str] = None,
        label_column_optional: bool = False,
        # data_format: str = "json",
        dataset_split_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        :param label_column
            The column in self.dataset to be used as label_column. Setting this value to None makes some of
            the attributes / methods invalid
                :attr `class_names` calculates the class_names of the label_column
                :method `convert_label_column_using_classlabel` converts the label column to `dataset.ClassLabel`
                format
        :param label_column_optional
            The :param `label_column` can be initialized to None in some known cases. Alternatively, if you are unsure
            whether the column exists or not, you can use the :param `label_column_optional` which will check for the
            existance of label_column after loading the dataset
        :param data_format
            Supported data_formats are json, csv, parquet
            NOTE Set the data_format to `json` for handling both json and json lines files.
        :param path_or_dict
            The input can be a path or dictionary which will be converted to `datasets.Dataset` format. The path can
            be of type str or Path. There is currently no restriction on the dictionary format
        """

        # datasets-2.3.2 library doesn't go well with Path; so converting to str
        if isinstance(path_or_dict, Path):
            self.path_or_dict = str(path_or_dict)
        else:
            self.path_or_dict = path_or_dict

        self.label_column = label_column
        # self.data_format = data_format
        self.label_column_optional = label_column_optional

        self.dataset_split_kwargs = dataset_split_kwargs

        # load the dataset
        self.dataset = self.load(self.dataset_split_kwargs)

    def load(
        self,
        dataset_split_kwargs: Optional[Dict[str, Any]] = None,
    ) -> Union[Dataset, None]:
        """
        1. Loads the dataset
        2. kwargs
            data_format - json, csv, mltable
            dataset_type - could be dataset or torch
            sample_size
                0.1 - 1.0 percentage of data to load
                1 - len(dataset) number of samples to load
        3. Handle loading dataset from S3 URI, Azure blob store
        """

        if isinstance(self.path_or_dict, str):
            # check if file exists
            if not Path(self.path_or_dict).is_dir():
                raise ValidationException._with_error(AzureMLError.create(PathNotFound, path=self.path_or_dict))

            # check if the file format is supported
            try:
                ds = load_dataset("imagefolder", data_dir=self.path_or_dict, split="train")
                logger.info("dataset loaded")
            except Exception as e:
                raise ValidationException._with_error(
                    AzureMLError.create(ValidationError, error=f"Error while loading the dataset: {e}")
                )

            if dataset_split_kwargs:
                logger.info(f"Splitting dataset with {dataset_split_kwargs}")
                try:
                    ds_dict = ds.train_test_split(**dataset_split_kwargs)
                    if "test_size" in dataset_split_kwargs:
                        return ds_dict["test"]
                    elif "train_size" in dataset_split_kwargs:
                        return ds_dict["train"]
                    else:
                        logger.warning("Wrong split args, using the whole dataset")
                except Exception as ex:
                    logger.warning(f"Unable to split dataset, using the whole dataset. Error: {str(ex)}")

            return ds

        raise ValidationException._with_error(AzureMLError.create(PathNotFound, path=self.path_or_dict))

    def update_dataset_columns_with_prefix(self) -> None:
        """
        Add the dataset column prefix to the dataset. The prefix is added only to the 1st level of columns
        and not done recursively

        The `self.label_column` will be updated with prefix along with dataset columns
        """
        self.dataset = self.dataset.rename_columns(
            {col: AzuremlConstants.DATASET_COLUMN_PREFIX + col for col in self.dataset.column_names}
        )

        # update the label column
        if self.label_column is not None:
            self.label_column = AzuremlConstants.DATASET_COLUMN_PREFIX + self.label_column

    def get_collation_function(self) -> None:
        """
        used for data collation during training. The default behaviour is implemented here
        None => no dynamic padding happens during training
        """
        return None

    @abstractmethod
    def encode_dataset(self) -> None:
        """
        tokenize the dataset which is task dependent and needs to be implemented by the subclass
        """
        pass
