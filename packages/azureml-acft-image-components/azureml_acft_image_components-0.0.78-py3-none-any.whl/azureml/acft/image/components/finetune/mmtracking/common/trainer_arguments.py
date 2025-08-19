# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""MMTracking trainer arguments"""

from typing import Any, Dict
from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.mmdetection.common.trainer_arguments import (
    DetectionTrainerArguments,
)

logger = get_logger_app(__name__)


class TrackingTrainerArguments(DetectionTrainerArguments):
    """MM Detection trainer arguments."""
    def __init__(self, params: Dict[str, Any]) -> None:
        """
        :param params: parameters used for training
        :type params: dict
        """
        super().__init__(params)
