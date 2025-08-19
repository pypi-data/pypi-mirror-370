# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image Components package - finetuning component MMDetection."""

import os
import json
from typing import Union

from mmengine import Config
from mmdet.apis import init_detector
from mmdet.models.detectors.two_stage import TwoStageDetector

from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore
from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.model_selector.constants import (
    ModelRepositoryURLs
)
from azureml.acft.common_components.utils.error_handling.error_definitions import (
    TaskNotSupported,
    ModelIncompatibleWithTask,
    InvalidData,
    NotSupported,
    ValidationError
)
from azureml.acft.common_components.utils.error_handling.exceptions import (
    ACFTValidationException,
    ACFTSystemException
)

from azureml.acft.image.components.finetune.factory.mappings import MODEL_FAMILY_CLS
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.common.mlflow.common_utils import get_current_device
from azureml.acft.image.components.finetune.mmdetection.common.trainer_classes import (
    DetectionTrainer,
)
from azureml.acft.image.components.finetune.mmdetection.common.constants import (
    MmDetectionModelLiterals
)
from azureml.acft.image.components.finetune.common.mlflow.common_constants import MmDetectionDatasetLiterals

from azureml.acft.image.components.model_selector.constants import MMDSupportedTasks
from azureml.acft.common_components.model_selector.constants import (
    ModelSelectorConstants
)

logger = get_logger_app(__name__)

MMDTaskMap = {
    MMDSupportedTasks.OBJECT_DETECTION: Tasks.MM_OBJECT_DETECTION,
    MMDSupportedTasks.INSTANCE_SEGMENTATION: Tasks.MM_INSTANCE_SEGMENTATION,
}


class TrainerClasses:
    """Trainer classes."""
    def __init__(
        self,
        model_family: MODEL_FAMILY_CLS,
        model_name_or_path: Union[str, os.PathLike],
        task_name: Tasks,
        model_metadata: dict = {},
    ) -> None:
        """
        :param model_family: related model_family to which current task belongs
        :type model_family: azureml.acft.accelerator.mappings.MODEL_FAMILY_CLS
        :param model_name_or_path: Hugging face image model name or path
        :type model_name_or_path: Union[str, os.PathLike]
        :param task_name: related task_name
        :type task_name: azureml.acft.accelerator.constants.task_definitions.Tasks
        :param model_metafile_path: path to model metadata file
        :type model_metafile_path: str
        """
        self.model_family = model_family
        self.task_name = task_name
        self.model_name_or_path = model_name_or_path
        self.model_metadata = model_metadata
        self._is_finetuning_supported()

    def get_trainer_classes_mapping(self):
        """get trainer class based on task_name"""
        if self.task_name in [
            Tasks.MM_OBJECT_DETECTION,
            Tasks.MM_INSTANCE_SEGMENTATION,
        ]:
            return DetectionTrainer
        else:
            raise ACFTValidationException._with_error(
                AzureMLError.create(TaskNotSupported,
                                    TaskName=self.task_name))

    def _is_finetuning_supported(self):
        """check if model is supported for current task"""

        model_tasks = [MMDTaskMap[task.lower()] for task in
                       self.model_metadata[ModelSelectorConstants.FINETUNING_TASKS]]
        model_name = self.model_name_or_path.split("/")[-1][:-3]

        # raise if selected task is not in model tasks
        if self.task_name not in model_tasks:
            error_str = f"Model {self.model_name_or_path} is not compatible with task {self.task_name}. "\
                        f"Provided Model supports these tasks: {model_tasks}."
            logger.error(error_str)

            raise ACFTValidationException._with_error(
                AzureMLError.create(ModelIncompatibleWithTask,
                                    pii_safe_message=error_str,
                                    ModelName=model_name,
                                    TaskName=self.task_name))

        try:
            config = Config.fromfile(self.model_name_or_path)
        except Exception as e:
            error_str = f"Error while reading config file for model {model_name}."
            logger.error(error_str + f"Error: {e}")
            raise ACFTValidationException._with_error(
                AzureMLError.create(ValidationError, error=error_str))

        teacher_config = config.model.get(MmDetectionModelLiterals.TEACHER_CONFIG)
        if teacher_config:
            error_str = "Teacher models are not yet supported for image finetuning tasks "
            logger.error(error_str)
            raise ACFTValidationException._with_error(
                AzureMLError.create(NotSupported,
                                    ModelName=model_name,
                                    scenario_name=error_str))
        try:
            model = init_detector(config, device=get_current_device())
        except Exception as e:
            error_str = f"Error while initializing model {model_name}. {e}"
            logger.error(error_str)
            raise ACFTValidationException._with_error(
                AzureMLError.create(ValidationError,
                                    error=error_str))
        # semantic segmentation is not yet supported.
        with_semantic = hasattr(model, MmDetectionModelLiterals.ROI_HEAD)\
            and hasattr(model.roi_head, MmDetectionModelLiterals.WITH_SEMANTIC)\
            and model.roi_head.with_semantic
        with_panoptic = (hasattr(model, MmDetectionModelLiterals.WITH_SEMANTIC) and model.with_semantic)\
            and (hasattr(model, MmDetectionModelLiterals.PANOPTIC_HEAD))
        if with_semantic or with_panoptic:
            error_str = f"Model-{model_name} with semantic/panoptic segmentation is not yet supported"\
                        "for image finetuning tasks."
            logger.error(error_str)
            raise ACFTValidationException._with_error(
                AzureMLError.create(ValidationError, error=error_str))

        # Models like fast rcnn needs a proposal file to be sent along since it doesn't
        # have a rpn network. They are currently not supported for finetuning.
        if isinstance(model, TwoStageDetector) and \
           hasattr(model, MmDetectionModelLiterals.WITH_RPN) and not model.with_rpn:
            error_str = "Two-stage models without rpn are not yet supported."\
                        f"please select other models from {ModelRepositoryURLs.MMDETECTION} for finetuning."
            logger.error(error_str)
            raise ACFTValidationException._with_error(
                AzureMLError.create(ValidationError, error=error_str))

        return
