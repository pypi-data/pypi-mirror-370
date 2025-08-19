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

"""MMDetection image OD and IS evaluation related functions."""

from transformers import EvalPrediction
from typing import Dict
from azureml.acft.image.components.finetune.common.mlflow.common_constants import MetricsLiterals


def calculate_tracking_metrics(eval_prediction: EvalPrediction, **kwargs) -> Dict:
    """
    compute and return metrics for Multi Object Tracking task
    :param eval_prediction: eval_prediction containing predictions and labels
    :type eval_prediction: Huggingface EvalPrediction
    :param kwargs: A dictionary of additional configuration parameters including the metric
    computer method.
    :type kwargs: dict
    :return: Dictionary containing all metrics.
    :rtype: Dict
    """
    metrics_computer = kwargs[MetricsLiterals.METRICS_COMPUTER]
    # Calculate metrics at the end of the epoch
    metrics = metrics_computer.aggregate_compute()[MetricsLiterals.METRICS]
    # Reset the metric computation after batch is over.
    metrics_computer.reset()

    return metrics
