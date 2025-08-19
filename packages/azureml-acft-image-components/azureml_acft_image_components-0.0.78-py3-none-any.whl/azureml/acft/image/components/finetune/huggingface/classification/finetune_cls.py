# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Hf image classification finetune class."""

from typing import Any, Dict
from functools import partial

from transformers.training_args import OptimizerNames
from azureml.acft.accelerator.constants import HfTrainerMethodsConstants
from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.common.constants.constants import SettingLiterals, SettingParameters
from azureml.acft.image.components.finetune.huggingface.common.constants import (
    HfImageInterfaceConstants,
    HfImageModelConstants,
    HfProblemType,
)
from azureml.acft.image.components.finetune.interfaces.azml_interface import AzmlFinetuneInterface
from azureml.acft.image.components.finetune.common.trainer.train_helper import get_custom_optimizer

logger = get_logger_app(__name__)


class AzmlHfImageClsFinetune(AzmlFinetuneInterface):
    """Hf image classification finetune class."""

    def __init__(self, params: Dict[str, Any]) -> None:
        """
        :param params: parameters used for training
        :type params: dict
        """
        super().__init__()
        self.params = params

    def get_finetune_args(self) -> Dict[str, Any]:
        """custom args for image classification finetuning

        :return: dictionary of custom args which are not supported by core
                 and needed for image models
        :rtype: Dict[str, Any]
        """

        custom_args_dict = {}
        # Add Hf tokenizer and model classses
        custom_args_dict[HfImageInterfaceConstants.HF_IMAGE_MODEL_CLS] = HfImageModelConstants.HF_IMAGE_AUTO_MODEL_CLS

        if self.params[SettingLiterals.TASK_NAME] == Tasks.HF_MULTI_LABEL_IMAGE_CLASSIFICATION:
            custom_args_dict[SettingLiterals.PROBLEM_TYPE] = HfProblemType.MULTI_LABEL_CLASSIFICATION
        else:
            custom_args_dict[SettingLiterals.PROBLEM_TYPE] = HfProblemType.SINGLE_LABEL_CLASSIFICATION

        custom_args_dict[SettingLiterals.REMOVE_UNUSED_COLUMNS] = SettingParameters.REMOVE_UNUSED_COLUMNS

        return custom_args_dict

    def get_custom_trainer_functions(self) -> Dict[str, Any]:
        """Customizable methods for trainer class

        :return: dictionary of custom trainer methods needed for image models
        :rtype: Dict[str, Any]
        """
        if self.params.get(SettingLiterals.OPTIMIZER, None) == OptimizerNames.SGD \
           and self.params.get(SettingLiterals.EXTRA_OPTIMIZER_ARGS, None):
            sgd_optimizer = partial(get_custom_optimizer,
                                    optimizer_name=self.params[SettingLiterals.OPTIMIZER],
                                    extra_optim_args=self.params[SettingLiterals.EXTRA_OPTIMIZER_ARGS],
                                    weight_decay=self.params.get(SettingLiterals.WEIGHT_DECAY, 0.0))

            return {HfTrainerMethodsConstants.AZUREML_OPTIMIZER: sgd_optimizer}
        return {}
