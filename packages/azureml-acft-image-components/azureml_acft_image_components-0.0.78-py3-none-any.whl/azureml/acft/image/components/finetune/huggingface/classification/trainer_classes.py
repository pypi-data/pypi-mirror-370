# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Hf image classification trainer classes."""

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.huggingface.classification.data_cls import AzmlHfImageDataInterface
from azureml.acft.image.components.finetune.huggingface.classification.finetune_cls import (
    AzmlHfImageClsFinetune,
)
from azureml.acft.image.components.finetune.huggingface.classification.inference_cls import (
    AzmlImageClsInference,
    SaveMlflowModel,
    calculate_metrics,
)
from azureml.acft.image.components.finetune.huggingface.common.hf_image_interfaces import (
    AzmlHfImageConfig,
    AzmlHfImageFeatureExtractor,
    AzmlHfImageModel,
)
from azureml.acft.image.components.finetune.interfaces.azml_interface import AzmlTrainerClassesInterface

logger = get_logger_app(__name__)


class ImageClassificationTrainerClasses(AzmlTrainerClassesInterface):
    """Trainer classes for Hf Image classification - Multi-class and Multi-label."""

    def __init__(self):
        """init function for ImageClassificationTrainerClasses"""
        super().__init__()
        self.finetune_cls = AzmlHfImageClsFinetune
        self.inference_cls = AzmlImageClsInference
        self.tokenizer_cls = AzmlHfImageFeatureExtractor
        self.model_cls = AzmlHfImageModel
        self.dataset_cls = AzmlHfImageDataInterface
        self.config_cls = AzmlHfImageConfig
        self.callbacks = [SaveMlflowModel]
        self.metrics_function = calculate_metrics
