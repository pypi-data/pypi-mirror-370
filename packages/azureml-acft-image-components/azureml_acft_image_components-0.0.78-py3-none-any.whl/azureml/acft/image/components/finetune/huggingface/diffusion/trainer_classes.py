# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Hf text-to-image trainer classes."""

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.huggingface.diffusion.data.data_cls import AzmlHfImageDataInterface
from azureml.acft.image.components.finetune.huggingface.diffusion.finetune_cls import (
    AzmlHfTextToImageFinetune,
    GenerateImages,
)
from azureml.acft.image.components.finetune.huggingface.diffusion.models.model import AzuremlStableDiffusionPipeline
from azureml.acft.image.components.finetune.huggingface.diffusion.models.text_encoder import TextEncoderFactory
from azureml.acft.image.components.finetune.huggingface.diffusion.models.tokenizer import TokenizerFactory
from azureml.acft.image.components.finetune.interfaces.azml_interface import AzmlTrainerClassesInterface

logger = get_logger_app(__name__)


class SDTextToImageTrainerClasses(AzmlTrainerClassesInterface):
    """Trainer classes for Hf Text-To-Image."""

    def __init__(self):
        """init function for TextToImage TrainerClasses"""
        super().__init__()
        self.finetune_cls = AzmlHfTextToImageFinetune
        self.tokenizer_cls = TokenizerFactory
        self.model_cls = AzuremlStableDiffusionPipeline
        self.dataset_cls = AzmlHfImageDataInterface
        self.text_encoder_cls = TextEncoderFactory
        self.callbacks = [GenerateImages]
