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
Base runner
"""

from abc import ABC, abstractmethod

from .diffusion_auto.config import AzuremlAutoConfig
from .constants.constants import Tasks

from azureml.acft.accelerator.utils.logging_utils import get_logger_app
from azureml.acft.accelerator.utils.error_handling.exceptions import ValidationException, LLMException
from azureml.acft.accelerator.utils.error_handling.error_definitions import (
    ModelIncompatibleWithTask,
)
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore


logger = get_logger_app()


STABLE_DIFFUSION_SUPPORTED_MODELS = [
    "CompVis/stable-diffusion-v1-4",
]


class BaseRunner(ABC):
    """Base Runner"""
    def check_model_task_compatibility(self, model_name_or_path: str, task_name: str) -> None:
        """
        Check if the given model supports the given task in the case of Hugging Face Models
        """
        # TODO: check model compatability
        # supported_model_types = TASK_SUPPORTED_MODEL_TYPES_MAP[task_name]
        # model_type = AzuremlAutoConfig.get_model_type(hf_model_name_or_path=model_name_or_path)

        # if model_type not in supported_model_types:
        #     raise ValidationException._with_error(
        #         AzureMLError.create(
        #             ModelIncompatibleWithTask, TaskName=task_name, ModelName=model_name_or_path
        #         )
        #     )
        pass

    @abstractmethod
    def run_preprocess_for_finetune(self, *args, **kwargs) -> None:
        """Run preprocess for finetune"""
        pass

    @abstractmethod
    def run_finetune(self, *args, **kwargs) -> None:
        """Run finetune"""
        pass

    @abstractmethod
    def run_preprocess_for_infer(self, *args, **kwargs) -> None:
        """Run preprocess for infer"""
        pass

    def run_modelselector(self, **kwargs) -> None:
        """
        Downloads model from azureml-preview registry if present
        Prepares model for continual finetuning
        Save model selector args
        """
        pass
