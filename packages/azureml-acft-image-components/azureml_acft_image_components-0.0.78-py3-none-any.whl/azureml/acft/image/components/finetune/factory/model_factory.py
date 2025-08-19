# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Fetching and validating models."""

import importlib

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.error_handling.error_definitions import ModelFamilyNotSupported
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.factory.mappings import (
    MODEL_FAMILY_CLS,
    MODEL_FAMILY_MODULE_IMPORT_PATH_MAP
)


logger = get_logger_app(__name__)


class ModelFactory:
    """Class for fetching and returning model."""

    def __init__(self, model_family: MODEL_FAMILY_CLS, model_id: str,
                 task_name: str=Tasks.HF_MULTI_CLASS_IMAGE_CLASSIFICATION,
                 model_metadata: dict={}):
        """
        init function for ModelFactory
        """
        if model_family not in MODEL_FAMILY_MODULE_IMPORT_PATH_MAP:
            raise ACFTValidationException._with_error(
                AzureMLError.create(
                    ModelFamilyNotSupported,
                    model_family=model_family,
                    supported_model_families=list(MODEL_FAMILY_MODULE_IMPORT_PATH_MAP.keys())
                )
            )

        # Load the module
        try:
            module = importlib.import_module(MODEL_FAMILY_MODULE_IMPORT_PATH_MAP[model_family])
        except ImportError as e:
            logger.error(f"Unable to import the module. model family: {model_family}. Error: {e}")
            raise ImportError(f"Unable to import the module. model family: {model_family}. Error: {e}")

        # Set the model factory output
        trainer_classes_obj = getattr(module, "TrainerClasses")(model_family, model_id, task_name, model_metadata)
        self.trainer_classes = trainer_classes_obj.get_trainer_classes_mapping()

    @property
    def get_trainer_classes(self):
        """Get trainer classes."""
        return self.trainer_classes
