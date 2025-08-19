# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image Components package - finetuning component MMTracking."""

import os
import json
from typing import Union

from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore
from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.error_handling.error_definitions import TaskNotSupported
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException

from azureml.acft.image.components.finetune.factory.mappings import MODEL_FAMILY_CLS
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.mmtracking.common.trainer_classes import (
    TrackingTrainer,
)

logger = get_logger_app(__name__)


class TrainerClasses:
    """Trainer classes."""
    def __init__(
        self,
        model_family: MODEL_FAMILY_CLS,
        model_name_or_path: Union[str, os.PathLike],
        task_name: Tasks,
        model_metadata: dict = None,
    ) -> None:
        """
        :param model_family: related model_family to which current task belongs
        :type model_family: azureml.acft.accelerator.mappings.MODEL_FAMILY_CLS
        :param model_name_or_path: Hugging face image model name or path
        :type model_name_or_path: Union[str, os.PathLike]
        :param task_name: related task_name
        :type task_name: azureml.acft.accelerator.constants.task_definitions.Tasks
        """
        self.model_family = model_family
        self.task_name = task_name
        self.model_name_or_path = model_name_or_path
        self.model_metadata = model_metadata

    def get_trainer_classes_mapping(self):
        """get trainer class based on task_name"""
        if self.task_name in [
            Tasks.MM_MULTI_OBJECT_TRACKING,
        ]:
            return TrackingTrainer
        else:
            raise ACFTValidationException._with_error(
                AzureMLError.create(TaskNotSupported,
                                    TaskName=self.task_name))
