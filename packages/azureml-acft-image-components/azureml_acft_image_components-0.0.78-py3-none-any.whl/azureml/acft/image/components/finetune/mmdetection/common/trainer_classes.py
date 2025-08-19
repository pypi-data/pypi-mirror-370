# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""MMDetection trainer classes."""

from azureml.acft.common_components import get_logger_app

from azureml.acft.image.components.finetune.interfaces.azml_interface import (
    AzmlTrainerClassesInterface,
)
from azureml.acft.image.components.finetune.mmdetection.common.data_class import AzmlMMDImageDataClass
from azureml.acft.image.components.finetune.mmdetection.common.inference import (
    SaveMlflowModel,
    DetectionInference,
    MMDetectionMessageHubUpdateCallback,
)
from azureml.acft.image.components.finetune.mmdetection.common.model import (
    DetectionModel,
    DetectionConfigBuilder,
)
from azureml.acft.image.components.finetune.mmdetection.common.trainer_arguments import (
    DetectionTrainerArguments,
)
from azureml.acft.image.components.finetune.mmdetection.common.metrics import (
    calculate_detection_metrics,
)

logger = get_logger_app(__name__)


class DetectionTrainer(AzmlTrainerClassesInterface):
    """MM Detection trainer classes."""
    def __init__(self):
        """ All required classes for training the object detection model using ACFT trainer """
        super().__init__()
        self.dataset_cls = AzmlMMDImageDataClass
        # MMDetection framework don't have tokenizer. Preprocessing is handled in augmentation.
        self.tokenizer_cls = None
        self.model_cls = DetectionModel

        self.finetune_cls = DetectionTrainerArguments
        self.config_cls = DetectionConfigBuilder
        self.callbacks = [SaveMlflowModel, MMDetectionMessageHubUpdateCallback]
        self.metrics_function = calculate_detection_metrics
        self.inference_cls = DetectionInference
