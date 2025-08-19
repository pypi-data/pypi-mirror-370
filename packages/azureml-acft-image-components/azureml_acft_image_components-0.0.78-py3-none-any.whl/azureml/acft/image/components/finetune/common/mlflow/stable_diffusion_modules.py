# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File containing HF model related functions."""


from __future__ import annotations
from typing import Any, Dict, List, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F
from diffusers.training_utils import compute_snr
from diffusers import AutoencoderKL, DDPMScheduler, StableDiffusionPipeline, UNet2DConditionModel
from diffusers.schedulers import KarrasDiffusionSchedulers
from transformers import CLIPTextModel
from transformers import AutoTokenizer, PreTrainedTokenizer
from common_constants import SDLiterals, SDPredictionType, SDDataLiterals, SDSettingParameters, TrainingLiterals
import importlib


def import_scheduler(scheduler_name: str) -> KarrasDiffusionSchedulers:
    """
    Import the scheduler from the diffusers module.

    :param scheduler_name: Name of the scheduler to import
    :type scheduler_name: str
    :return: The scheduler class
    :rtype: KarrasDiffusionSchedulers
    """
    try:
        # Import the diffusers module
        diffusers = importlib.import_module("diffusers")
        scheduler = getattr(diffusers, scheduler_name)
        return scheduler
    except AttributeError as e:
        raise ValueError(f"Scheduler named '{scheduler_name}' not found: {e}")
    except ImportError as e:
        raise ImportError(f"Failed to import the diffusers module: {e}")


class AzuremlStableDiffusionPipeline(nn.Module):
    """AzuremlStableDiffusionPipeline class to handle the diffusion pipeline related operations."""

    def __init__(
        self,
        unet: UNet2DConditionModel,
        vae: AutoencoderKL,
        text_encoder: CLIPTextModel,
        noise_scheduler: DDPMScheduler,
        tokenizer: PreTrainedTokenizer,
        hf_model_name_or_path: str,
        revision: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize Azureml stable diffusion pipeline class.

        :param unet: UNet2DConditionModel model
        :type unet: UNet2DConditionModel
        :param vae: AutoencoderKL model
        :type vae: AutoencoderKL
        :param text_encoder: CLIPTextModel model
        :type text_encoder: CLIPTextModel
        :param noise_scheduler: DDPMScheduler model
        :type noise_scheduler: DDPMScheduler
        :param tokenizer: PreTrainedTokenizer model
        :type tokenizer: PreTrainedTokenizer
        :param hf_model_name_or_path: HF model name or path
        :type hf_model_name_or_path: str
        :param revision: Revision, defaults to None
        :type revision: Optional[str], optional
        :param weight_dtype: Weight dtype, defaults to torch.float32
        :type weight_dtype: torch.dtype, optional
        """
        super().__init__()

        self.unet = unet
        self.vae = vae  # require_grad set to False
        self.text_encoder = text_encoder  # require_grad set to False
        self.noise_scheduler = noise_scheduler
        self.hf_model_name_or_path = hf_model_name_or_path
        self.revision = revision
        self.tokenizer = tokenizer

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> "AzuremlStableDiffusionPipeline":
        """Get Azureml stable difffusion pipeline pretrained model.

        :param hf_model_name_or_path: HF model name or path
        :type hf_model_name_or_path: str
        :param kwargs: Additional arguments
        :type kwargs: Dict
        :return: AzuremlStableDiffusion Pipeline
        :rtype: AzuremlStableDiffusionPipeline
        """
        _ = kwargs.get(SDLiterals.NON_EMA_REVISION, None)
        revision = kwargs.get(SDLiterals.REVISION, None)
        # load vae
        vae = AutoencoderKL.from_pretrained(hf_model_name_or_path, subfolder=SDLiterals.VAE, revision=revision)
        # load unet
        unet: UNet2DConditionModel = UNet2DConditionModel.from_pretrained(
            hf_model_name_or_path, subfolder=SDLiterals.UNET, revision=revision
        )
        # load scheduler
        # DDPMScheduler is default scheduler
        scheduler_type = kwargs.pop(SDLiterals.SCHEDULER_TYPE, SDSettingParameters.DEFAULT_SCHEDULER)
        scheduler_name_or_path = kwargs.pop(SDLiterals.SCHEDULER_PATH, SDLiterals.SCHEDULER)
        noise_scheduler = import_scheduler(scheduler_type).from_pretrained(scheduler_name_or_path)

        # load tokenizer
        tokenizer_name_or_path = kwargs.pop(SDLiterals.TOKENIZER_NAME_OR_PATH, hf_model_name_or_path)
        subfolder = kwargs.pop(SDLiterals.TOKENIZER_SUBFOLDER, SDLiterals.TOKENIZER)
        tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=tokenizer_name_or_path,
            subfolder=subfolder,
            **kwargs,
        )
        # load text encoder
        subfolder = kwargs.pop(SDLiterals.TEXT_ENCODER_SUBFOLDER, SDLiterals.TEXT_ENCODER)
        text_encoder_name_or_path = kwargs.pop(SDLiterals.TEXT_ENCODER, hf_model_name_or_path)
        text_encoder_type = kwargs.get(SDLiterals.TEXT_ENCODER_TYPE, SDLiterals.CLIP_TEXT_MODEL)
        if text_encoder_type == SDLiterals.CLIP_TEXT_MODEL:
            from transformers import CLIPTextModel

            text_encoder = CLIPTextModel.from_pretrained(text_encoder_name_or_path, subfolder=subfolder)
        else:
            from transformers import T5EncoderModel

            text_encoder = T5EncoderModel.from_pretrained(text_encoder_name_or_path, subfolder=subfolder)

        # freeze all weights
        vae.requires_grad_(False)
        unet.requires_grad_(False)
        text_encoder.requires_grad_(False)

        return cls(
            unet=unet,
            vae=vae,
            noise_scheduler=noise_scheduler,
            tokenizer=tokenizer,
            text_encoder=text_encoder,
            hf_model_name_or_path=hf_model_name_or_path,
            revision=revision,
            **kwargs,
        )
