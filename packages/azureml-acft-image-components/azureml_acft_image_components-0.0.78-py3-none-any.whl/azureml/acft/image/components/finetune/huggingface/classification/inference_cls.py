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

"""Hf image classification Inference and evaluation related classes."""

from typing import Any, Dict
from transformers import EvalPrediction, TrainerCallback, TrainerControl, TrainerState, TrainingArguments

import numpy as np
import torch

from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore
from azureml.metrics import compute_metrics
from azureml.metrics import constants as metrics_constants
from azureml.metrics import list_metrics

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.common.constants.constants import InferenceParameters, SettingLiterals
from azureml.acft.image.components.finetune.huggingface.common.constants import HfProblemType
from azureml.acft.image.components.finetune.interfaces.azml_interface import AzmlInferenceInterface

logger = get_logger_app(__name__)


def calculate_metrics(eval_pred: EvalPrediction, **kwargs) -> Dict:
    """
    compute and return metrics for Image classification tasks

    :param eval_pred: eval_pred containing predictions and labels
    :type eval_pred: EvalPrediction (transformers.EvalPrediction)
    :return: Dictionary containing all metrics.
    :rtype: Dict
    """
    # To Do: After mmclassification is implemented, check if we can reuse part of this

    problem_type = kwargs.get(SettingLiterals.PROBLEM_TYPE)
    multi_label = problem_type == HfProblemType.MULTI_LABEL_CLASSIFICATION
    predictions, labels = eval_pred

    if multi_label:
        # source: https://jesusleal.io/2021/04/21/Longformer-multilabel-classification/
        # first, apply sigmoid on predictions which are of shape (batch_size, num_labels)
        sigmoid = torch.nn.Sigmoid()
        probs = sigmoid(torch.Tensor(predictions)).numpy()
        # threshold: threshold for multi_label_classification
        threshold = kwargs.get(SettingLiterals.PROB_THRESHOLD, InferenceParameters.DEFAULT_PROB_THRESHOLD)
        y_pred = np.zeros(probs.shape)
        # next, use threshold to turn them into integer predictions
        y_pred[np.where(probs >= threshold)] = 1
    else:
        soft_max = torch.nn.Softmax(dim=1)
        probs = soft_max(torch.Tensor(predictions)).numpy()
        y_pred = np.argmax(probs, axis=1)
    y_true = labels

    # get the list of supported metrics
    metrics_list = list_metrics(task_type=metrics_constants.Tasks.CLASSIFICATION, multilabel=multi_label)

    # finally, compute metrics
    metrics = compute_metrics(
        task_type=metrics_constants.Tasks.CLASSIFICATION,
        multilabel=multi_label,
        y_test=y_true,
        y_pred_proba=probs,
        y_pred=y_pred,
        metrics=metrics_list,
    )

    return_metrics = metrics['metrics']
    return_metrics.update(metrics['artifacts'])
    return return_metrics


class AzmlImageClsInference(AzmlInferenceInterface):
    """Hf image classification Inference and evaluation related class."""

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
    """Hf image classification save mlflow model callback."""

    def on_train_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs) -> None:
        """Callback called at the end of training.
        :param args: training arguments
        :type args: TrainingArguments (transformers.TrainingArguments)
        :param state: trainer state
        :type state: TrainerState (transformers.TrainerState)
        :param control: trainer control
        :type control: TrainerControl (transformers.TrainerControl)
        :param kwargs: keyword arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """
        # save_as_mlflow_model arg is not reaching to the callback,
        # so we have implemented this functionality in finetune_runner.py
        pass
