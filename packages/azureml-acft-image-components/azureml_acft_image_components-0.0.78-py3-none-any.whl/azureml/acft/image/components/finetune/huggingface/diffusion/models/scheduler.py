# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Create Noise scheduler."""

import importlib
from typing import Dict, List, Optional, Union

from azureml.acft.common_components import get_logger_app
from diffusers import DiffusionPipeline
from diffusers.schedulers import KarrasDiffusionSchedulers

from azureml.acft.image.components.common.utils import get_input_params_name
from azureml.acft.image.components.finetune.common.trainer.train_helper import get_typesafe_value
from azureml.acft.image.components.finetune.huggingface.diffusion.models.constant import Literals
from azureml.acft.image.components.finetune.huggingface.diffusion.models.default_model_settings import DefaultSettings

logger = get_logger_app(__name__)


def filter_params(params: Dict, allowed_params: List[str], scheduler_name: str) -> Dict[str, any]:
    """Filter parameters based on allowed parameters for particular scheduler constructor.

    :param params: parameters
    :type params: Dict
    :param allowed_params: allowed parameters for scheduler
    :type allowed_params: List[str]
    :param scheduler_name: scheduler name
    :type scheduler_name: str
    :return: filtered parameters
    :rtype: Dict[str, any]
    """
    ignored_params = set(params.keys()) - set(allowed_params)
    if ignored_params:
        logger.warning(f"Ignored params while creating {scheduler_name}: {ignored_params}")
    return {k: v for k, v in params.items() if k in allowed_params}


def prepare_scheduler_parameters(config: Dict, scheduler_args: Dict) -> None:
    """Override scheduler parameters.

    :param config: scheduler config
    :type config: Dict
    :param scheduler_args: scheduler user arguments
    :type scheduler_args: dict
    """
    extra_params_string = scheduler_args.pop(Literals.EXTRA_NOISE_SCHEDULER_ARGS, None)
    params = {}
    if extra_params_string:
        params = [item.split("=") for item in extra_params_string.split(";")]
        params = {key.strip(): get_typesafe_value(value.strip()) for key, value in params}

    for key, val in scheduler_args.items():
        if val and key.startswith("noise_scheduler") and key != "noise_scheduler_name":
            key = key.replace("noise_scheduler_", "")
            params[key] = val
    config.update(params)


class DDPMScheduler:
    """Create denoising diffusion probabilistic models scheduler."""

    @classmethod
    def get_scheduler(cls, hf_model_name_or_path: str, **scheduler_args) -> "DDPMScheduler":
        """Get Denoising diffusion probabilistic models (DDPM) scheduler.

        :param hf_model_name_or_path: huggingface model name or path
        :type hf_model_name_or_path: str
        :param scheduler_args: scheduler arguments, defaults to {}
        :type scheduler_args: dict, optional
        :return: DDPMScheduler instance
        :rtype: DDPMScheduler
        """
        from diffusers import DDPMScheduler

        config = DDPMScheduler.load_config(hf_model_name_or_path, subfolder=DefaultSettings.scheduler_folder)
        prepare_scheduler_parameters(config, scheduler_args)

        allowed_params = get_input_params_name(DDPMScheduler)
        kwargs = filter_params(config, allowed_params, "DDPMScheduler")
        return DDPMScheduler(**kwargs)


class DPMSolverMultistepScheduler:
    """Create Diffusion probabilistic models multistep scheduler."""

    @classmethod
    def get_scheduler(cls, hf_model_name_or_path: str, **scheduler_args) -> "DPMSolverMultistepScheduler":
        """Get DPMSolverMultistepScheduler.

        :param hf_model_name_or_path: huggingface model name or path
        :type hf_model_name_or_path: str
        :param scheduler_args: scheduler arguments, defaults to {}
        :type scheduler_args: dict, optional
        :return: DPMSolverMultistepScheduler instance
        :rtype: DPMSolverMultistepScheduler
        """
        from diffusers import DPMSolverMultistepScheduler

        config = DPMSolverMultistepScheduler.load_config(
            hf_model_name_or_path, subfolder=DefaultSettings.scheduler_folder
        )
        prepare_scheduler_parameters(config, scheduler_args)

        allowed_params = get_input_params_name(DPMSolverMultistepScheduler)
        kwargs = filter_params(config, allowed_params, "DPMSolverMultistepScheduler")
        # Temporary hack to assign default value from class for prediction_type.
        # Assigning different value than default causing following problem in forward pass of model.
        # PNDM scheduler don't have `get_velocity` method.
        kwargs.pop(Literals.PREDICTION_TYPE, None)
        return DPMSolverMultistepScheduler(**kwargs)


class PNDMScheduler:
    """Create Probabilistic noise diffusion models scheduler."""

    @classmethod
    def get_scheduler(cls, hf_model_name_or_path: str, **scheduler_args) -> "PNDMScheduler":
        """Get Probabilistic noise diffusion models scheduler.

        :param hf_model_name_or_path: huggingface model name or path
        :type hf_model_name_or_path: str
        :param scheduler_args: scheduler arguments, defaults to {}
        :type scheduler_args: dict, optional
        :return: PNDMScheduler instance
        :rtype: PNDMScheduler
        """
        from diffusers import PNDMScheduler

        config = PNDMScheduler.load_config(hf_model_name_or_path, subfolder=DefaultSettings.scheduler_folder)
        prepare_scheduler_parameters(config, scheduler_args)

        allowed_params = get_input_params_name(PNDMScheduler)
        kwargs = filter_params(config, allowed_params, "PNDMScheduler")
        # Temporary hack to assign default value from class for prediction_type.
        # Assigning different value than default causing following problem in forward pass of model.
        # PNDM scheduler don't have `get_velocity` method.
        kwargs.pop(Literals.PREDICTION_TYPE, None)
        return PNDMScheduler(**kwargs)


SCHEDULER_MAPPING = {
    KarrasDiffusionSchedulers.DPMSolverMultistepScheduler.name: DPMSolverMultistepScheduler,
    KarrasDiffusionSchedulers.DDPMScheduler.name: DDPMScheduler,
    KarrasDiffusionSchedulers.PNDMScheduler.name: PNDMScheduler,
}


class NoiseSchedulerFactory:
    """Factory class to create noise scheduler."""

    @classmethod
    def load_scheduler_info_from_model(cls, model_path) -> List[str]:
        """Load scheduler config from model folder.

        :param model_path: model path
        :type model_path: str
        :return: scheduler config
        :rtype: List[str]
        """
        config = DiffusionPipeline.load_config(model_path)
        return config.get(DefaultSettings.scheduler_folder, None)

    @classmethod
    def create_noise_scheduler(cls, hf_model_name_or_path: str, **scheduler_args: dict) -> KarrasDiffusionSchedulers:
        """Create noise scheduler.

        If scheduler name is not provided, it will attempt to load scheduler config from model folder.
        If scheduler name is provided, it will create scheduler using parameters formed by default model parameters,
        user parameters and extra user parameters with priority default parameters < extra params string < user params.

        :param hf_model_name_or_path: huggingface model name or path
        :type hf_model_name_or_path: str
        :param scheduler_args: scheduler arguments
        :type scheduler_args: dict
        :raises ACFTValidationException._with_error: Unsupported scheduler type
        :return: Scheduler instance
        :rtype: KarrasDiffusionSchedulers
        """
        scheduler_name = scheduler_args.get(Literals.NOISE_SCHEDULER_NAME, None)
        if scheduler_name and scheduler_name in SCHEDULER_MAPPING:
            scheduler = SCHEDULER_MAPPING[scheduler_name].get_scheduler(hf_model_name_or_path, **scheduler_args)
            return scheduler
        else:
            logger.info("Attempting to load noise schduler config from model folder.")
            scheduler_config = NoiseSchedulerFactory.load_scheduler_info_from_model(hf_model_name_or_path)
            module = importlib.import_module(scheduler_config[0])
            scheduler_class = getattr(module, scheduler_config[1])
            return scheduler_class.from_pretrained(hf_model_name_or_path, subfolder=DefaultSettings.scheduler_folder)
