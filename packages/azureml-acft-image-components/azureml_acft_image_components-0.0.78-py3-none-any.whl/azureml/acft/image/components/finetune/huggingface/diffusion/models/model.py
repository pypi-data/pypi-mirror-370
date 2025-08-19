# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File containing HF model related functions."""


from __future__ import annotations

import os
import shutil
from typing import Any, Dict, Optional
from collections import OrderedDict

import torch
import torch.nn as nn
import torch.nn.functional as F
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore
from azureml.acft.common_components import ModelSelectorConstants, get_logger_app
from azureml.acft.common_components.utils.constants import MlflowMetaConstants
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTSystemError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTSystemException
from azureml.acft.image.components.finetune.common.constants.constants import SettingLiterals as CommonSettingLiterals
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingParameters as CommonSettingParameters,
)
from azureml.acft.image.components.finetune.huggingface.diffusion.models.constant import (
    DataLiterals,
    Literals,
    PredictionType,
    SettingParameters,
)
from azureml.acft.image.components.finetune.huggingface.diffusion.models.default_model_settings import DefaultSettings
from azureml.acft.image.components.finetune.huggingface.diffusion.models.scheduler import NoiseSchedulerFactory
from azureml.acft.image.components.finetune.huggingface.diffusion.models.text_encoder import (
    TextEncoderFactory,
    AzmlTextEncoder,
)
from azureml.acft.image.components.finetune.huggingface.diffusion.models.tokenizer import TokenizerFactory
from diffusers import AutoencoderKL, DDPMScheduler, StableDiffusionPipeline, UNet2DConditionModel
from diffusers.training_utils import compute_snr
from transformers import CLIPTextModel, PreTrainedTokenizer
from transformers.trainer import get_last_checkpoint
from transformers.utils.peft_utils import ADAPTER_CONFIG_NAME, ADAPTER_SAFE_WEIGHTS_NAME, ADAPTER_WEIGHTS_NAME

logger = get_logger_app(__name__)


class AzuremlAutoEncoderKL:
    """File containing HF model related functions."""

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> AutoencoderKL:
        """Load Azureml AutoencoderKL pretrained model.

        :param hf_model_name_or_path: HF model name or path
        :type hf_model_name_or_path: str
        :param kwargs: Additional arguments
        :type kwargs: Dict
        :return: AutoencoderKL model
        :rtype: AutoencoderKL
        """
        revision = kwargs[Literals.REVISION]
        vae = AutoencoderKL.from_pretrained(hf_model_name_or_path, subfolder=Literals.VAE, revision=revision)
        return vae


class AzuremlUNet2DConditionModel:
    """Azueml UNet2DConditionModel class to handle the UNet2DConditionModel related operations."""

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> UNet2DConditionModel:
        """Load Azureml Unet2DCondition model.

        :param hf_model_name_or_path: HF model name or path
        :type hf_model_name_or_path: str
        :param kwargs: Additional arguments
        :type kwargs: Dict
        :return: UNet2DConditionModel model
        :rtype: UNet2DConditionModel
        """
        revision = kwargs[Literals.NON_EMA_REVISION]
        unet = UNet2DConditionModel.from_pretrained(hf_model_name_or_path, subfolder=Literals.UNET, revision=revision)
        return unet


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

        self.metadata = kwargs.get(ModelSelectorConstants.MODEL_METADATA, {})
        self.class_labels_conditioning = kwargs.get(Literals.CLASS_LABELS_CONDITIONING, SettingParameters.TIMESTEPS)
        self.precision = kwargs.get(CommonSettingLiterals.PRECISION, CommonSettingParameters.DEFAULT_PRECISION)
        self.pre_compute_text_embeddings = kwargs.get(Literals.PRE_COMPUTE_TEXT_EMBEDDINGS, True)
        self.snr_gamma = kwargs.get(Literals.SNR_GAMMA, True)
        self.with_prior_preservation = kwargs.get(Literals.WITH_PRIOR_PRESERVATION, True)
        self.offset_noise = kwargs.get(Literals.OFFSET_NOISE, True)
        self.text_encoder_use_attention_mask = kwargs.get(Literals.TEXT_ENCODER_USE_ATTENTION_MASK, True)
        self.prior_loss_weight = kwargs.get(Literals.PRIOR_LOSS_WEIGHT, SettingParameters.DEFAULT_PRIOR_LOSS_WEIGHT)
        self.apply_lora = kwargs.get(CommonSettingLiterals.APPLY_LORA, False)
        # add bf16 support
        self.weight_dtype = torch.float16 if self.precision == 16 else torch.float32

    def forward(self, **data):
        """Model forward pass for training and validation mode.

        :param data: Input data to model
        :type data: Dict
        :return: A dictionary of loss components in training mode OR Tuple of dictionary of predicted and ground
        labels in validation mode
        :rtype: Dict[str, Any] in training mode; Tuple[Tensor, Tensor] in validation mode;

        """
        if self.unet.training is False:
            return torch.tensor(0.0, device=self.unet.device, dtype=self.weight_dtype)

        input_ids = data.get(DataLiterals.INPUT_IDS, None)
        pixel_values = data.get(DataLiterals.PIXEL_VALUES, None)
        attention_mask = data.get(DataLiterals.ATTENTION_MASK, None)

        if self.vae is not None:
            # Convert images to latent space
            model_input = self.vae.encode(pixel_values).latent_dist.sample()
            model_input = model_input * self.vae.config.scaling_factor
        else:
            model_input = pixel_values

        # Sample noise that we'll add to the model input
        if self.offset_noise:
            noise = torch.randn_like(model_input) + 0.1 * torch.randn(
                model_input.shape[0], model_input.shape[1], 1, 1, device=model_input.device
            )
        else:
            noise = torch.randn_like(model_input)
        batch_size, channels, height, width = model_input.shape
        # Sample a random timestep for each image
        timesteps = torch.randint(
            0, self.noise_scheduler.config.num_train_timesteps, (batch_size,), device=model_input.device
        )
        timesteps = timesteps.long()

        # Add noise to the model input according to the noise magnitude at each timestep
        # (this is the forward diffusion process)
        noisy_model_input = self.noise_scheduler.add_noise(model_input, noise, timesteps)

        # Get the text embedding for conditioning
        if self.pre_compute_text_embeddings:
            encoder_hidden_states = input_ids
        else:
            encoder_hidden_states = AzuremlStableDiffusionPipeline.encode_prompt(
                text_encoder=self.text_encoder,
                input_ids=input_ids,
                attention_mask=attention_mask,
                text_encoder_use_attention_mask=self.text_encoder_use_attention_mask,
            )

        if self.unet.config.in_channels == channels * 2:
            noisy_model_input = torch.cat([noisy_model_input, noisy_model_input], dim=1)

        if self.class_labels_conditioning == SettingParameters.TIMESTEPS:
            class_labels = timesteps
        else:
            class_labels = None

        # Predict the noise residual
        model_pred = self.unet(
            sample=noisy_model_input,
            timestep=timesteps,
            encoder_hidden_states=encoder_hidden_states,
            class_labels=class_labels,
            return_dict=False,
        )[0]

        # if model predicts variance, throw away the prediction. we will only train on the
        # simplified training objective. This means that all schedulers using the fine tuned
        # model must be configured to use one of the fixed variance variance types.
        if model_pred.shape[1] == 6:
            model_pred, _ = torch.chunk(model_pred, 2, dim=1)

        # Get the target for loss depending on the prediction type
        if self.noise_scheduler.config.prediction_type == PredictionType.EPSILON:
            target = noise
        elif self.noise_scheduler.config.prediction_type == PredictionType.V_PREDICTION:
            target = self.noise_scheduler.get_velocity(model_input, noise, timesteps)
        else:
            error_string = f"Unknown prediction type {self.noise_scheduler.config.prediction_type}"
            raise ACFTSystemException._with_error(AzureMLError.create(ACFTSystemError, pii_safe_message=error_string))

        if self.with_prior_preservation:
            # Chunk the noise and model_pred into two parts and compute the loss on each part separately.
            model_pred, model_pred_prior = torch.chunk(model_pred, 2, dim=0)
            target, target_prior = torch.chunk(target, 2, dim=0)

            # Compute instance loss
            loss = F.mse_loss(model_pred.float(), target.float(), reduction="mean")

            # Compute prior loss
            prior_loss = F.mse_loss(model_pred_prior.float(), target_prior.float(), reduction="mean")

            # Add the prior loss to the instance loss.
            loss = loss + self.prior_loss_weight * prior_loss
        else:
            loss = F.mse_loss(model_pred.float(), target.float(), reduction="mean")

        # # Todo: Uncomment the below piece of code post validating snr_gamma
        # # Compute instance loss
        # if self.snr_gamma is None:
        #     loss = F.mse_loss(model_pred.float(), target.float(), reduction="mean")
        # else:
        #     # Compute loss-weights as per Section 3.4 of https://arxiv.org/abs/2303.09556.
        #     # Since we predict the noise instead of x_0, the original formulation is slightly changed.
        #     # This is discussed in Section 4.2 of the same paper.
        #     snr = compute_snr(self.noise_scheduler, timesteps)
        #     base_weight = torch.stack([snr, self.snr_gamma * torch.ones_like(timesteps)], dim=1).min(dim=1)[0] / snr
        #     if self.noise_scheduler.config.prediction_type == PredictionType.V_PREDICTION:
        #         # Velocity objective needs to be floored to an SNR weight of one.
        #         mse_loss_weights = base_weight + 1
        #     else:
        #         # Epsilon and sample both use the same loss weights.
        #         mse_loss_weights = base_weight
        #     loss = F.mse_loss(model_pred.float(), target.float(), reduction="none")
        #     loss = loss.mean(dim=list(range(1, len(loss.shape)))) * mse_loss_weights
        #     loss = loss.mean()
        # if self.with_prior_preservation:
        #     # Add the prior loss to the instance loss.
        #     loss = loss + self.prior_loss_weight * prior_loss

        return loss, model_pred

    @classmethod
    def from_pretrained(
        cls, hf_model_name_or_path: str, weight_dtype: torch.dtype = None, **kwargs
    ) -> "AzuremlStableDiffusionPipeline":
        """Get Azureml stable difffusion pipeline pretrained model.

        :param hf_model_name_or_path: HF model name or path
        :type hf_model_name_or_path: str
        :param kwargs: Additional arguments
        :type kwargs: Dict
        :return: AzuremlStableDiffusion Pipeline
        :rtype: AzuremlStableDiffusionPipeline
        """
        _ = kwargs.get(Literals.NON_EMA_REVISION, None)
        revision = kwargs.get(Literals.REVISION, None)
        precision = kwargs.get(CommonSettingLiterals.PRECISION, CommonSettingParameters.DEFAULT_PRECISION)
        if weight_dtype is None:
            weight_dtype = torch.float16 if precision == 16 else torch.float32
        device = torch.device(Literals.CUDA if torch.cuda.is_available() else Literals.CPU)

        # set the vae, noise_scheduler and text encoder
        # freezing the weights for vae and text_encoder
        vae = AzuremlAutoEncoderKL.from_pretrained(
            hf_model_name_or_path, revision=revision, weight_dtype=weight_dtype, device=device
        )

        unet: UNet2DConditionModel = AzuremlUNet2DConditionModel.from_pretrained(
            hf_model_name_or_path, non_ema_revision=revision, weight_dtype=weight_dtype, device=device, **kwargs
        )

        noise_scheduler = NoiseSchedulerFactory.create_noise_scheduler(hf_model_name_or_path, **kwargs)

        tokenizer_name_or_path = kwargs.pop(Literals.TOKENIZER_NAME_OR_PATH, hf_model_name_or_path)
        tokenizer_name_or_path = tokenizer_name_or_path or hf_model_name_or_path
        tokenizer = TokenizerFactory.from_pretrained(tokenizer_name_or_path, **kwargs)

        train_text_encoder = kwargs.get(Literals.TRAIN_TEXT_ENCODER, False)
        text_encoder = kwargs.pop(CommonSettingLiterals.TEXT_ENCODER, None)
        if not text_encoder:
            text_encoder = TextEncoderFactory().from_pretrained(
                hf_model_name_or_path, weight_dtype=weight_dtype, **kwargs
            )

        azml_sd_pipeline = cls(
            unet=unet,
            vae=vae,
            noise_scheduler=noise_scheduler,
            tokenizer=tokenizer,
            text_encoder=text_encoder,
            hf_model_name_or_path=hf_model_name_or_path,
            **kwargs,
        )

        AzuremlStableDiffusionPipeline._prepare_pipeline_for_training(
            azml_sd_pipeline, weight_dtype, device, train_text_encoder
        )

        return azml_sd_pipeline

    def _prepare_pipeline_for_training(
        azml_sd_pipeline: "AzuremlStableDiffusionPipeline",
        weight_dtype: torch.dtype,
        device: str,
        train_text_encoder: bool,
    ) -> None:
        """Prepare the pipeline for training by setting appropriate data type and gradient calculation.

        :param azml_sd_pipeline: Azureml Stable Diffusion Pipeline
        :type azml_sd_pipeline: AzuremlStableDiffusionPipeline
        :param weight_dtype: model weight data type
        :type weight_dtype: torch.dtype
        :param device: device type to move model to
        :type device: str
        :param train_text_encoder: Flag to train text encoder
        :type train_text_encoder: bool
        """
        azml_sd_pipeline.vae.requires_grad_(False)
        azml_sd_pipeline.unet.requires_grad_(True)
        if train_text_encoder:
            azml_sd_pipeline.text_encoder.requires_grad_(True)
        else:
            azml_sd_pipeline.text_encoder.requires_grad_(False)
        # for now, not manually casting. leaving it hf trainer to autocast
        # To validate while testing the component
        azml_sd_pipeline.vae.to(device, dtype=torch.float32)
        azml_sd_pipeline.text_encoder.to(device, dtype=torch.float32)
        azml_sd_pipeline.unet.to(device, dtype=torch.float32)

    def save_pretrained(self, output_dir: str, state_dict: Optional[Dict[str, Any]] = None) -> None:
        """Save the model to the output directory.

        :param output_dir: Output directory
        :type output_dir: str
        :param state_dict: State dictionary, defaults to None
        :type state_dict: Optional[Dict[str, Any]], optional
        """

        base_model_asset_id = self.metadata.get(MlflowMetaConstants.BASE_MODEL_ASSET_ID, "")
        is_input_model_from_azure_registry = (
            base_model_asset_id.startswith("azureml") if base_model_asset_id else False
        )
        if self.apply_lora and is_input_model_from_azure_registry:
            # last checkpoint has to be changed to best once we have metrics enabled
            last_checkpoint_folder = get_last_checkpoint(output_dir)
            for filename in [ADAPTER_WEIGHTS_NAME, ADAPTER_SAFE_WEIGHTS_NAME, ADAPTER_CONFIG_NAME]:
                lora_file = os.path.join(last_checkpoint_folder, filename)
                if os.path.isfile(lora_file):
                    shutil.copy(lora_file, output_dir)
        # whole pipeline is dumped so as to support continual finetuning.
        # For Lora FT, These are lora merged weights.
        pipeline = StableDiffusionPipeline.from_pretrained(
            self.hf_model_name_or_path,
            text_encoder=self.text_encoder,
            vae=self.vae,
            unet=self.unet,
            scheduler=self.noise_scheduler,
        )
        pipeline.save_pretrained(output_dir)

    @staticmethod
    def encode_prompt(
        text_encoder: AzmlTextEncoder,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        text_encoder_use_attention_mask: bool = False,
    ) -> torch.Tensor:
        """Encode the prompt using the text encoder and return the embeddings.

        :param text_encoder: The text encoder.
        :type text_encoder: AzmlTextEncoder
        :param input_ids: The input ids for the prompt.
        :type input_ids: torch.Tensor
        :param attention_mask: The attention mask for the prompt.
        :type attention_mask: torch.Tensor
        :param text_encoder_use_attention_mask: Whether to use the attention mask.
        :type text_encoder_use_attention_mask: bool
        :return: The embeddings for the prompt.
        :rtype: torch.Tensor
        """
        text_input_ids = input_ids.to(text_encoder.device)

        if text_encoder_use_attention_mask:
            attention_mask = attention_mask.to(text_encoder.device)
        else:
            attention_mask = None

        prompt_embeds = text_encoder(
            text_input_ids,
            attention_mask=attention_mask,
            return_dict=False,
        )
        prompt_embeds = prompt_embeds[0]

        return prompt_embeds

    @property
    def config(self) -> str:
        """Config property."""
        return OrderedDict()
