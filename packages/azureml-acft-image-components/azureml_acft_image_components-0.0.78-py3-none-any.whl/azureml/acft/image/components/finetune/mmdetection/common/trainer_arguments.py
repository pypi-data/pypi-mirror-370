# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""MMDetection trainer arguments"""

from typing import Any, Dict
from functools import partial

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals,
    SettingParameters,
)

from transformers.training_args import OptimizerNames
from transformers import TrainingArguments
from azureml.acft.accelerator.constants import HfTrainerMethodsConstants
from azureml.acft.image.components.finetune.interfaces.azml_interface import (
    AzmlFinetuneInterface,
)
from azureml.acft.image.components.finetune.common.mlflow.common_constants import MmDetectionDatasetLiterals
from azureml.acft.image.components.finetune.defaults.constants import HFTrainerDefaultsKeys
from azureml.acft.image.components.finetune.common.trainer.train_helper import get_custom_optimizer

logger = get_logger_app(__name__)


class DetectionTrainerArguments(AzmlFinetuneInterface):
    """MM Detection trainer arguments."""
    def __init__(self, params: Dict[str, Any]) -> None:
        """
        :param params: parameters used for training
        :type params: dict
        """
        super().__init__()
        self.params = params

    def get_finetune_args(self) -> Dict[str, Any]:
        """custom args for MM detection tasks (OD and IS)

        :return: dictionary of custom args which are not supported by core
                 and needed for image models
        :rtype: Dict[str, Any]
        """
        custom_args_dict = {
            SettingLiterals.REMOVE_UNUSED_COLUMNS: SettingParameters.REMOVE_UNUSED_COLUMNS,
            # dummy_labels are added since hf_trainer expects same size tensors in
            # distributed gather step in evaluation loop
            SettingLiterals.LABEL_NAMES: [MmDetectionDatasetLiterals.DUMMY_LABELS],
        }

        if hasattr(TrainingArguments, HFTrainerDefaultsKeys.SAVE_SAFETENSORS):
            custom_args_dict[HFTrainerDefaultsKeys.SAVE_SAFETENSORS] = False

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
