# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Hf text-to-image finetune class."""

import os
from argparse import Namespace
from typing import Any, Dict

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.common.constants.constants import SettingLiterals, SettingParameters
from azureml.acft.image.components.finetune.huggingface.diffusion.models.constant import Literals
from azureml.acft.image.components.finetune.huggingface.diffusion.models.model import AzuremlStableDiffusionPipeline
from azureml.acft.image.components.finetune.huggingface.diffusion.utils.validation_utils import (
    sd_generate_validation_images,
)
from azureml.acft.image.components.finetune.interfaces.azml_interface import AzmlFinetuneInterface
from transformers import TrainerCallback, TrainerControl, TrainerState, TrainingArguments
from transformers.modeling_utils import unwrap_model

logger = get_logger_app(__name__)


class AzmlHfTextToImageFinetune(AzmlFinetuneInterface):
    """Hf image classification finetune class."""

    def __init__(self, params: Dict[str, Any]) -> None:
        """
        :param params: parameters used for training
        :type params: dict
        """
        super().__init__()
        self.params = params

    def get_finetune_args(self) -> Dict[str, Any]:
        """custom args for text to image finetuning

        :return: dictionary of custom args which are not supported by core
                 and needed for text-to-image models
        :rtype: Dict[str, Any]
        """
        custom_args_dict = {}
        lora_config = "unet.*to_q|unet.*to_v|unet.*to_out.0|unet.*add_k_proj|unet.*add_v_proj"
        if Literals.TRAIN_TEXT_ENCODER in self.params and self.params[Literals.TRAIN_TEXT_ENCODER]:
            lora_config += "|text_encoder.*q_proj|text_encoder.*k_proj|text_encoder.*v_proj|text_encoder.*out_proj"

        custom_args_dict.update({"lora_target_modules": lora_config})
        custom_args_dict[SettingLiterals.REMOVE_UNUSED_COLUMNS] = SettingParameters.REMOVE_UNUSED_COLUMNS
        custom_args_dict["dataloader_pin_memory"] = False
        # This is workaround to pass number of validation image in on log callback.
        os.environ[Literals.NUM_VALIDATION_IMAGES] = str(self.params[Literals.NUM_VALIDATION_IMAGES])
        return custom_args_dict

    def get_custom_trainer_functions(self) -> Dict[str, Any]:
        """Customizable methods for trainer class

        :return: dictionary of custom trainer methods needed for text-to-image models
        :rtype: Dict[str, Any]
        """
        return {}


class GenerateImages(TrainerCallback):
    """Hf image classification save mlflow model callback."""

    def on_save(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs) -> None:
        """Callback called at the end of training.
        :param args: training arguments
        :type args: TrainingArguments (transformers.TrainingArguments)
        :param state: trainer state
        :type state: TrainerState (transformers.TrainerState)
        :param control: trainer control
        :type control: TrainerControl (transformers.TrainerControl)
        :param kwargs: keyword arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """
        model = kwargs[Literals.MODEL]
        model = unwrap_model(model)

        azml_sd_pipeline = AzuremlStableDiffusionPipeline(
            unet=model.unet,
            vae=model.vae,
            text_encoder=model.text_encoder,
            noise_scheduler=model.noise_scheduler,
            tokenizer=model.tokenizer,
            hf_model_name_or_path=model.hf_model_name_or_path,
            precision=16 if args.fp16 else 32,
        )

        sd_generate_validation_images(
            azml_sd_pipeline=azml_sd_pipeline,
            component_args=Namespace(
                **{
                    Literals.MODEL_NAME_OR_PATH: model.hf_model_name_or_path,
                    Literals.INSTANCE_PROMPT: kwargs["train_dataloader"].dataset.instance_prompt,
                    SettingLiterals.OUTPUT_DIR: args.output_dir,
                    Literals.MODEL_NAME_OR_PATH: model.hf_model_name_or_path,
                    Literals.SAMPLE_BATCH_SIZE: args.per_device_train_batch_size,
                }
            ),
        )
