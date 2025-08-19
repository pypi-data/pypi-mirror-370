# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tokenizer factory."""

import os
from typing import Union

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.huggingface.diffusion.models.constant import \
    Literals
from transformers import AutoTokenizer, PreTrainedTokenizer

logger = get_logger_app(__name__)


class TokenizerFactory:
    """Tokenizer factory."""

    SUPPORTED_TOKENIZER_NAMES = [Literals.OPENAI_CLIP_VIT_LARGE_PATCH14]

    @classmethod
    def from_pretrained(
        cls, tokenizer_name_or_path: Union[str, os.PathLike], **tokenizer_args: dict
    ) -> PreTrainedTokenizer:
        """Create tokenizer.

        :param tokenizer_name_or_path: Can be either HF repo id OR A path to a directory containing tokenizer
        :type tokenizer_name_or_path: Union[str, os.PathLike]
        :param tokenizer_args: tokenizer arguments, defaults to {}
        :type tokenizer_args: dict, optional
        :raises ACFTValidationException._with_error: Unsupported tokenizer
        :return: Pre trained tokenizer.
        :rtype: PreTrainedTokenizer
        """
        try:
            use_fast = tokenizer_args.pop("use_fast", False)
            subfolder = tokenizer_args.pop("tokenizer_subfolder", "tokenizer")

            return AutoTokenizer.from_pretrained(
                pretrained_model_name_or_path=tokenizer_name_or_path,
                use_fast=use_fast,
                subfolder=subfolder,
                **tokenizer_args,
            )
        except OSError as ex:
            logger.warning(
                f"Error while creating tokenizer: {ex}. " "Attempting to load tokenizer without specifying subfolder."
            )
            return AutoTokenizer.from_pretrained(
                pretrained_model_name_or_path=tokenizer_name_or_path,
                use_fast=use_fast,
                **tokenizer_args,
            )
