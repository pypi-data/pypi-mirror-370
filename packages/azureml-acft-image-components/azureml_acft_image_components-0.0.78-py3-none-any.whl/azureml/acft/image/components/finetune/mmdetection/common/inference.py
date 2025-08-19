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

"""MMDetection image OD and IS Inference related classes"""

from typing import Dict, Any
from transformers import (
    TrainerCallback,
    TrainingArguments,
    TrainerState,
    TrainerControl,
)
from mmengine import MessageHub
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals,
)
from azureml.acft.image.components.finetune.interfaces.azml_interface import (
    AzmlInferenceInterface,
)


class DetectionInference(AzmlInferenceInterface):
    """Inference class for MMDetection image OD and IS tasks"""

    def __init__(self, params: Dict[str, Any]) -> None:
        """
        :param params: parameters used for inference
        :type params: dict
        :param trainer_classes_cls: trainer interface class
        :type trainer_classes_cls: AzmlTrainerClassesInterface
        """
        self.inference_params = params

    # other required methods to be implemented as part of mlflow_save task.


class SaveMlflowModel(TrainerCallback):
    """MMDetection image OD and IS save mlflow model callback."""

    # finetune-core has implemented save mlflow model directly in the driver without an interface and
    # they are using mlflow.hftransformers flavor. Till the interface is exposed we can have a TrainerCallback
    # on_train_end and save the mlflow model
    def on_train_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs) -> None:
        """Callback called at the end of training.
        :param args: training arguments
        :type args: TrainingArguments (transformers.TrainingArguments)
        :param state: trainer state
        :type state: TrainerState (transformers.TrainerState)
        :param control: trainer control
        :type control: TrainerControl (transformers.TrainerControl)
        :param kwargs: additional arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """
        if not getattr(args, SettingLiterals.SAVE_AS_MLFLOW_MODEL, False):
            return

        raise NotImplementedError()


class MMDetectionMessageHubUpdateCallback(TrainerCallback):
    """MMDetection image OD and IS message hub update callback class."""

    # messagehub for MMD is not available in finetune-core. This is a placeholder to update the epoch
    # information in the messagehub. Please add any other training details in MessageHub as needed.
    def on_epoch_begin(self, args, state, control, **kwargs) -> None:
        """Callback called at the beginning of each epoch.
        :param args: training arguments
        :type args: TrainingArguments (transformers.TrainingArguments)
        :param state: trainer state
        :type state: TrainerState (transformers.TrainerState)
        :param control: trainer control
        :type control: TrainerControl (transformers.TrainerControl)
        :param kwargs: additional arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """
        # Get the current instance of MessageHub
        message_hub = MessageHub.get_current_instance()
        # Update the epoch information in MessageHub
        message_hub.update_info("epoch", state.epoch)
