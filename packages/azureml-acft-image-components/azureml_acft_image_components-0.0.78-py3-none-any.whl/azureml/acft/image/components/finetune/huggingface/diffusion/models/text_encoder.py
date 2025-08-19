# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Create Text encoder."""

import os
from abc import ABC, abstractmethod
from typing import Union

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
from azureml.acft.image.components.finetune.common.constants.constants import SettingLiterals as CommonSettingLiterals
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingParameters as CommonSettingParameters,
)
from azureml.acft.image.components.finetune.huggingface.diffusion.models.default_model_settings import DefaultSettings
from transformers import AutoModel, PreTrainedModel

from .constant import Literals

logger = get_logger_app(__name__)


class AzmlTextEncoder(ABC):
    """Abstract base class for text encoders."""

    @classmethod
    @abstractmethod
    def get_text_encoder(cls, text_encoder_name_or_path: Union[str, os.PathLike], subfolder: str) -> "AzmlTextEncoder":
        """Get text encoder instance.

        :param text_encoder_name_or_path: Can be either HF repo id
        OR A path to a directory containing text encoder model
        :type text_encoder_name_or_path: Union[str, os.PathLike]
        :param subfolder: subfolder where text encoder is stored
        :type subfolder: str
        :return: TextEncoder instance
        :rtype: TextEncoder
        """
        pass


class CLIPTextModel(AzmlTextEncoder):
    """CLIPTextModel class."""

    @classmethod
    def get_text_encoder(cls, text_encoder_name_or_path: Union[str, os.PathLike], subfolder: str) -> "CLIPTextModel":
        """Get CLIPTextModel text encoder.

        :param text_encoder_name_or_path: Can be either HF repo id
        OR A path to a directory containing text encoder model
        :type text_encoder_name_or_path: Union[str, os.PathLike]
        :param subfolder: subfolder where text encoder is stored
        :type subfolder: str
        :return: CLIPTextModel instance
        :rtype: CLIPTextModel
        """
        from transformers import CLIPTextModel

        try:
            model = CLIPTextModel.from_pretrained(text_encoder_name_or_path, subfolder=subfolder)
        except Exception as ex:
            logger.warn(f"Encountered excption: {str(ex)}. Attempting to load model without specifying subfolder.")
            model = AutoModel.from_pretrained(text_encoder_name_or_path)
        return model


class T5EncoderModel(AzmlTextEncoder):
    """T5EncoderModel class."""

    @classmethod
    def get_text_encoder(cls, text_encoder_name_or_path: Union[str, os.PathLike], subfolder: str) -> "T5EncoderModel":
        """Get T5EncoderModel text encoder.

        :param text_encoder_name_or_path: Can be either HF repo id
        OR A path to a directory containing text encoder model
        :type text_encoder_name_or_path: Union[str, os.PathLike]
        :param subfolder: subfolder where text encoder is stored
        :type subfolder: str
        :return: T5EncoderModel instance
        :rtype: T5EncoderModel
        """
        from transformers import T5EncoderModel

        return T5EncoderModel.from_pretrained(text_encoder_name_or_path, subfolder=subfolder)


TEXT_ENCODER_MAPPING = {
    Literals.CLIP_TEXT_MODEL: CLIPTextModel,
    Literals.T5ENCODER_MODEL: T5EncoderModel,
}


class TextEncoderFactory:
    """Create supported Text encoder."""

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path=str, **text_encoder_args: dict) -> PreTrainedModel:
        """Get supported Text encoder.

        :param text_encoder_type: text encoder type
        :type text_encoder_type: str
        :param text_encoder_name_or_path: Can be either HF repo id
        OR A path to a directory containing text encoder model
        :type text_encoder_name_or_path: Union[str, os.PathLike]
        :param text_encoder_args: text encoder args, defaults to {}
        :type text_encoder_args: dict, optional
        :raises ACFTValidationException._with_error: Unsupported text encoder type
        :return: Text encoder instance
        :rtype: PreTrainedModel
        """
        text_encoder_type = text_encoder_args.get(Literals.TEXT_ENCODER_TYPE) or DefaultSettings.text_encoder_type
        text_encoder_name_or_path = text_encoder_args.get(Literals.TEXT_ENCODER_NAME) or hf_model_name_or_path
        subfolder = text_encoder_args.pop("text_encoder_subfolder", "text_encoder")
        try:
            text_encoder = TEXT_ENCODER_MAPPING[text_encoder_type].get_text_encoder(
                text_encoder_name_or_path, subfolder
            )
        except (TypeError, KeyError, OSError) as ex:
            try:
                logger.warn(f"Encountered excption: {str(ex)}. Attempting to load model using AutoModel.")
                text_encoder = AutoModel.from_pretrained(text_encoder_name_or_path)
            except Exception as exception:
                if text_encoder_type not in TEXT_ENCODER_MAPPING:
                    raise ACFTValidationException._with_error(
                        AzureMLError.create(
                            ACFTUserError,
                            pii_safe_message=f"Unsupported text encoder type: {text_encoder_type}."
                            f"Supported schedulers type: {list(TEXT_ENCODER_MAPPING.keys())}.",
                        ),
                    ) from exception
                raise

        return text_encoder
