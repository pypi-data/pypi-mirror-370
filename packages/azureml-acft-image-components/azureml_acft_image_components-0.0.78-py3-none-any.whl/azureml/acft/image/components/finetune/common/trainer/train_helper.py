# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Common Training Helper methods"""

import ast
import inspect
import os
import shutil
from typing import List, Union
import torch

from transformers.trainer_pt_utils import get_parameter_names
from transformers.pytorch_utils import ALL_LAYERNORM_LAYERS
from transformers.training_args import OptimizerNames

from azureml.acft.common_components import get_logger_app
from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.common_components.utils.error_handling.error_definitions import (
    ACFTUserError, ACFTSystemError)
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException
from azureml.acft.image.components.finetune.common.constants.constants import SettingLiterals

logger = get_logger_app(__name__)


def get_typesafe_value(value: str) -> Union[str, bool, int, float]:
    """
    Convert the value from string type to the actual type
    :param value: value to be converted
    :type value: str
    """
    try:
        return ast.literal_eval(value)
    except ValueError:
        return value


def get_custom_optimizer(model,
                         learning_rate,
                         optimizer_name="sgd",
                         extra_optim_args=None,
                         weight_decay=0.0) -> torch.optim.Optimizer:
    """
    Get torch optimizer with custom arguments
    :param model: model to be trained
    :type model: torch.nn.Module
    :param learning_rate: learning rate for the optimizer
    :type learning_rate: float
    :param extra_optim_args: custom arguments for the optimizer, defaults to None
    :type extra_optim_args: str, optional
    :param weight_decay: Weight Decay for the optimizer
    :type weight_decay: float
    :return: torch optimizer intialized with optim_args
    :rtype: torch.optim.Optimizer
    """
    optim_args_dict = {}
    optim_args_dict[SettingLiterals.LR] = learning_rate
    optim_args_dict[SettingLiterals.WEIGHT_DECAY] = weight_decay
    if extra_optim_args:
        logger.info(f"Processing Custom optimizer arguments: {extra_optim_args}")
        for mapping in extra_optim_args.replace(" ", "").split(";"):
            if not mapping or mapping == '=':
                continue
            elif "=" in mapping:
                logger.info(f"Argument: {mapping}")
                try:
                    key, value = mapping.split("=")
                    if value:
                        optim_args_dict[key] = get_typesafe_value(value)
                    else:
                        msg = f"No value found for parameter {key}, hence ignoring it."
                        logger.warning(msg)
                except ValueError:
                    msg = "Please make sure to seperate values by semi-colon. No value found"
                    raise ACFTDataException._with_error(
                        AzureMLError.create(ACFTUserError, pii_safe_message=msg))
            else:
                msg = f"Ignoring optimization argument: {mapping}, since no value is provided" \
                      f" for the argument: {mapping}. Please use '=' operator to separate key and value." \
                      "For e.g. 'momentum=0.9;nesterov=False'."
                logger.warning(msg)
    optim_args_dict[SettingLiterals.PARAMS] = get_model_parameters(
        model, optim_args_dict[SettingLiterals.WEIGHT_DECAY])

    if optimizer_name == OptimizerNames.SGD:
        optimizer_class = torch.optim.SGD
    else:
        msg = f"No custom optimizer implemented for {optimizer_name}"
        raise ACFTDataException._with_error(AzureMLError.create(ACFTSystemError, pii_safe_message=msg))
    expected_arg_list = list(
        inspect.signature(
            getattr(optimizer_class, "__init__")
        ).parameters
    )
    # Exclude self from the list of expected parameters
    expected_arg_list = expected_arg_list[1:] if expected_arg_list[0] == "self" else expected_arg_list
    invalid_argument_list = []
    for arg_key in optim_args_dict.keys():
        if arg_key not in expected_arg_list:
            invalid_argument_list.append(arg_key)
    if invalid_argument_list:
        msg = f"Found invalid argument(s) in extra_optim_args for {optimizer_name}: {invalid_argument_list}, " \
              f"hence ignoring them. Valid arguments are {expected_arg_list}." \
              "We will only use valid arguments for the optimizer."
        logger.warning(msg)

        # Remove the invalid arguments from optim_args.
        for invalid_arg in invalid_argument_list:
            optim_args_dict.pop(invalid_arg)
        msg = f"Using {optimizer_name} optimizer with following arguments. extra_optim_args = {optim_args_dict}."

    return optimizer_class(**optim_args_dict)


def get_model_parameters(opt_model, weight_decay=0.0) -> List:
    """
    Get model parameters for the optimizer
    :param opt_model: model to be optimized
    :type opt_model: torch.nn.Module
    :param weight_decay: weight decay for the optimizer
    :type weight_decay: float
    :return: model parameters for the optimizer
    :rtype: list
    """
    decay_parameters = get_parameter_names(opt_model, ALL_LAYERNORM_LAYERS)
    decay_parameters = [name for name in decay_parameters if "bias" not in name]
    optimizer_grouped_parameters = [
        {
            SettingLiterals.PARAMS: [
                p for n, p in opt_model.named_parameters() if (n in decay_parameters and p.requires_grad)
            ],
            SettingLiterals.WEIGHT_DECAY: weight_decay,
        },
        {
            SettingLiterals.PARAMS: [
                p for n, p in opt_model.named_parameters() if (n not in decay_parameters and p.requires_grad)
            ],
            SettingLiterals.WEIGHT_DECAY: 0.0,
        },
    ]
    return optimizer_grouped_parameters


def save_pytorch_model(job_output_dir: str, pytorch_model_folder: str) -> None:
    """Save the best model checkpoint to pytorch model folder
    :param job_output_dir: job's output directory
    :type job_output_dir: str
    :param pytorch_model_folder: pytorch model folder
    :type pytorch_model_folder: str
    :return: None
    :rtype: None
    """
    os.makedirs(pytorch_model_folder, exist_ok=True)

    for filename in os.listdir(job_output_dir):
        file_path = os.path.join(job_output_dir, filename)
        if os.path.isfile(file_path) and (not filename.endswith(".log")) and (not filename.endswith(".csv")):
            shutil.copy2(file_path, pytorch_model_folder)
    logger.info("Pytorch model saved successfully.")
