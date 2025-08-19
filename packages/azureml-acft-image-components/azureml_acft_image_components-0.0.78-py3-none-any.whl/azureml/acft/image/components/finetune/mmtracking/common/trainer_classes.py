# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""MMDetection trainer classes."""

from azureml.acft.common_components import get_logger_app

from azureml.acft.image.components.finetune.interfaces.azml_interface import (
    AzmlTrainerClassesInterface,
)
from azureml.acft.image.components.finetune.mmtracking.common.data_class import AzmlMMTImageDataClass
from azureml.acft.image.components.finetune.mmtracking.common.inference import (
    SaveMlflowModel,
    TrackingInference,
)
from azureml.acft.image.components.finetune.mmtracking.common.model import (
    TrackingModel,
    TrackingConfigBuilder,
)
from azureml.acft.image.components.finetune.mmtracking.common.trainer_arguments import (
    TrackingTrainerArguments,
)
from azureml.acft.image.components.finetune.mmtracking.common.metrics import (
    calculate_tracking_metrics
)

logger = get_logger_app(__name__)


class TrackingTrainer(AzmlTrainerClassesInterface):
    """MM Detection trainer classes."""
    def __init__(self):
        """ All required classes for training the object detection model using ACFT trainer """
        super().__init__()
        self.dataset_cls = AzmlMMTImageDataClass
        # MMDetection framework don't have tokenizer. Preprocessing is handled in augmentation.
        self.tokenizer_cls = None
        self.model_cls = TrackingModel

        self.finetune_cls = TrackingTrainerArguments
        self.config_cls = TrackingConfigBuilder
        self.callbacks = [SaveMlflowModel]
        self.metrics_function = calculate_tracking_metrics
        self.inference_cls = TrackingInference
