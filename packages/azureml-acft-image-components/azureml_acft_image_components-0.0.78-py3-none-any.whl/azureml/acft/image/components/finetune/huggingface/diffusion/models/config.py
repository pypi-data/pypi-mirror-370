# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File containing HF config related functions"""


# https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

import os
from typing import Optional, Union

from azureml.acft.common_components import get_logger_app
from transformers import AutoConfig, PretrainedConfig

logger = get_logger_app(__name__)


class AzuremlAutoConfig(AutoConfig):
    """AzuremlAutoConfig class to handle the config related operations."""

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> PretrainedConfig:
        """Initialize the config from the pretrained model name or path."""
        apply_adjust = kwargs.pop("apply_adjust", True)
        logger.info(f"Initializing config with {kwargs}")
        config = super(AzuremlAutoConfig, cls).from_pretrained(
            hf_model_name_or_path,
            **kwargs,
        )

        return AzuremlAutoConfig.post_init(config) if apply_adjust else config

    @staticmethod
    def post_init(config: PretrainedConfig) -> PretrainedConfig:
        """Post init operations for the config."""
        _ = AzuremlAutoConfig.get_model_type(config)

        return config

    @staticmethod
    def get_model_type(
        config: Optional[PretrainedConfig] = None, hf_model_name_or_path: Optional[Union[str, os.PathLike]] = None
    ) -> str:
        """Get model type from the config or model_name_or_path."""
        # PreTrainedConfig has an attribute model_type
        if config is not None:
            return getattr(config, "model_type")
        elif hf_model_name_or_path is not None:
            config = super(AzuremlAutoConfig, AzuremlAutoConfig).from_pretrained(hf_model_name_or_path)
            return getattr(config, "model_type")
        else:
            raise ValueError("Pretrained config or model_name_or_path should be present")
