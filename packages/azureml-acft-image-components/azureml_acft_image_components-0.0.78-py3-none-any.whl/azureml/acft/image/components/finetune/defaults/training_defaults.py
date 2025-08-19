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

"""Finetuning component logic for preparing training defaults."""

import os
import json
from typing import Optional, Union
from transformers import TrainingArguments

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.defaults.hf_trainer_defaults import (
    HFTrainerDefaults,
)
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.defaults.constants import (
    TrainingDefaultsConstants,
    NonHfTrainerDefaultsKeys,
)

logger = get_logger_app(__name__)


class TrainingDefaults(object):
    """This class contains the default values for the training arguments.

    Note: Defaults are stored in the dataclasses in the defaults folder.
    Defaults are selected based on the task and model architecture.
    Following is the order of selection:
    1. If user has provided the training arguments, then the user provided values are used.
    2. If the model architecture is supported, then the defaults are selected based on the model architecture.
    3. If the model architecture is not supported, then the defaults are selected based on the model family.
    4. If the model family is not supported, then the defaults are selected based on the task.
    5. If the task is not supported and the model architecture is not supported,
       then the Hugging Face defaults are provided.
    """

    def __init__(
        self,
        task: Optional[str] = None,
        model_name_or_path: Optional[Union[str, os.PathLike]] = None,
    ) -> None:
        """Constructor - This method initializes the trainingDefaults class.

        :param task: The task for which the training defaults are required.
        :type task: str
        :param model_name_or_path: The model name or path for which the training defaults are required.
        :type model_name_or_path: Union[str, os.PathLike]
        :return: None
        :rtype: None
        """
        self.task = task
        self.model_path = None
        self.model_name = None
        self.defaults_dict = None

        if model_name_or_path is not None and (
            os.path.isdir(model_name_or_path)
            or (os.path.isfile(model_name_or_path) and model_name_or_path.endswith(".py"))
        ):
            if os.path.isdir(model_name_or_path):
                self.model_path = model_name_or_path
            else:
                self.model_path = os.path.dirname(model_name_or_path)
            model_metadata_file = os.path.join(self.model_path, TrainingDefaultsConstants.MODEL_METADATA_FILE)
            data_dict = self._get_data_from_file(model_metadata_file)
            if data_dict is not None and TrainingDefaultsConstants.MODEL_NAME_KEY in data_dict:
                self.model_name = data_dict[TrainingDefaultsConstants.MODEL_NAME_KEY]
            else:
                logger.info("Unable to read model name from model metadata file.")
        elif model_name_or_path is not None:
            self.model_name = model_name_or_path

        # get the dataclass defaults based on the task and model family
        self.dataclass_defaults = self._get_training_defaults_dataclass()
        self.defaults_dict = self._get_dict_from_dataclass(self.dataclass_defaults)

        # If the model architecture is supported, then the defaults are selected based on the model architecture.
        if self.model_path is not None:
            model_defaults_file = os.path.join(self.model_path, TrainingDefaultsConstants.MODEL_DEFAULTS_FILE)
            model_defaults_dict = self._get_data_from_file(model_defaults_file)
            # take the union of dictionaries model defaults dict and defaults dict with precedence
            # given to model defaults dict
            if model_defaults_dict is not None:
                logger.info(f"Using the defaults from {TrainingDefaultsConstants.MODEL_DEFAULTS_FILE}")
                self.defaults_dict.update(model_defaults_dict)

        # validate and update the default dictionary
        self.defaults_dict = self._validate_and_update_defaults_dict(self.defaults_dict)

    @staticmethod
    def _get_data_from_file(file_path: str) -> dict:
        """This method returns the data from the file.

        :param file_path: The path to the file.
        :type file_path: str
        :return: The data from the file.
        :rtype: dict
        """
        data_dict = None
        if file_path is not None:
            # check if file is present and load the data
            if os.path.isfile(file_path):
                try:
                    with open(file_path) as json_file:
                        data_dict = json.load(json_file)
                except Exception as e:
                    logger.warning(f"Unable to read data from {file_path}. Error: {e}")
        return data_dict

    @staticmethod
    def _get_dict_from_dataclass(defaults_dataclass: object) -> dict:
        """This method returns the training arguments as a dictionary.

        :param defaults_dataclass: The training defaults dataclass.
        :type defaults_dataclass: object
        :return: The training arguments as a dictionary.
        :rtype: dict
        """

        training_args = {}
        for key, value in defaults_dataclass.__dict__.items():
            if key.startswith("_"):
                training_args[key[1:]] = value

        return training_args

    def _get_training_defaults_dataclass(self) -> object:
        """This method returns the training defaults dataclass.

        :return: The training defaults dataclass.
        :rtype: object
        """

        task_defaults = TrainingDefaultsConstants.TASK_TO_DATACLASS_MAPPING.get(self.task, HFTrainerDefaults)

        # get the model family defaults
        # identify the model family defaults or model families defaults from the model name
        # as single model could match to multiple model families depending on the task
        matched_model_families = TrainingDefaultsConstants.MODEL_NAME_TO_DATACLASS_MAPPING.get(self.model_name, None)

        if matched_model_families is None:
            # if model family is not supported, then use the task defaults
            model_family_defaults = task_defaults
        elif isinstance(matched_model_families, dict):
            # if model name matches to multiple model families, then use the task defaults
            # to identify the model family defaults
            model_family_defaults = matched_model_families.get(self.task, task_defaults)
        else:
            # if model name matches to single model family, then use the model family defaults
            model_family_defaults = matched_model_families

        return model_family_defaults()

    @staticmethod
    def _validate_and_update_defaults_dict(defaults_dict: dict) -> dict:
        """This method validates the default dictionary.

        :param defaults_dict: The default dictionary.
        :type defaults_dict: dict
        :return: The updated default dictionary.
        :rtype: dict
        """
        updated_defaults_dict = {}
        for key, value in defaults_dict.items():
            # check is key is present in TrainingArguments dataclass
            # and value has the same type as the dataclass attribute
            if key in NonHfTrainerDefaultsKeys.__dict__.values() or hasattr(TrainingArguments, key):
                # add key value in updated defaults dict
                updated_defaults_dict[key] = value
            else:
                # log warning if the key is not present in TrainingArguments dataclass
                logger.warning(f"{key} is not a valid training argument. It cannot be used for training defaults.")

        return updated_defaults_dict
