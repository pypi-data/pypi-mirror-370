# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image finetune component - augmentation config utils."""

import inspect
import os
import yaml

from types import ModuleType
from typing import List

from azureml.acft.image.components.finetune.common.mlflow.custom_augmentations import albumentations
from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.factory.mappings import MODEL_FAMILY_CLS
from azureml.acft.image.components.finetune.common.constants.augmentation_constants import AugmentationConfigKeys
from azureml.acft.image.components.finetune.common.mlflow.common_constants import AlbumentationParameterNames
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals
)
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.common.augmentation.model_preproc_extractor import (
    HfModelPreProcExtractor,
    ModelPreProcExtractor,
    MMDModelPreProcExtractor
)
from azureml.acft.image.components.finetune.common.mlflow.augmentation_helper import (
    load_augmentation_dict_from_config
)

logger = get_logger_app(__name__)


def get_augmentation_library(augmentation_library_name: str) -> ModuleType:
    """ Get Augmentation lib corresponding to augmentation_library_name used in config file

    :param augmentation_function_name: name of augmentaion library
    :type augmentation_function_name: string

    :return: augmentation library used, for example albumentations, kornia, torchvision
    :rtype: ModuleType
    """
    AUGMENTATION_LIB_NAME_TO_LIB_MAPPING = {"albumentations": albumentations}

    if augmentation_library_name not in AUGMENTATION_LIB_NAME_TO_LIB_MAPPING.keys():
        logger.error(
            f"{augmentation_library_name} not in supported libraries - {AUGMENTATION_LIB_NAME_TO_LIB_MAPPING.keys()}"
        )
        raise NotImplementedError(
            f"{augmentation_library_name} not in supported libraries - {AUGMENTATION_LIB_NAME_TO_LIB_MAPPING.keys()}"
        )
    return AUGMENTATION_LIB_NAME_TO_LIB_MAPPING[augmentation_library_name]


def get_model_preproc_extractor(
    augmentation_library_name: str,
    model_preprocessing_params_dict: dict,
    model_family: MODEL_FAMILY_CLS,
) -> ModelPreProcExtractor:
    """ Get model preprocessing extractor for specific frameworks.

    :param augmentation_library_name: Name of augmentation library from config
    :type augmentation_library_name: str
    :param model_preprocessing_params_dict:
            models's preprocessing parameters dict
            - HF: image_processor.to_dict() from preprocess_config.json
            - Other Framwork: dict containing preprocessing params
            - Other approaches: dict containing preprocessing param,
                key:value pairs in dict to be used for preparing transforms.
    :type model_preprocessing_params_dict: dict
    :param model_family: Model family
    :type model_family: str

    :return: model preprocessing params extractor
    :rtype: ModelPreProcExtractor
    """
    if model_family == MODEL_FAMILY_CLS.HUGGING_FACE_IMAGE:
        return HfModelPreProcExtractor(
            model_preprocessing_params=model_preprocessing_params_dict,
            augmentation_library_name=augmentation_library_name,
        )
    elif model_family == MODEL_FAMILY_CLS.MMDETECTION_IMAGE:
        return MMDModelPreProcExtractor(
            model_preprocessing_params=model_preprocessing_params_dict,
            augmentation_library_name=augmentation_library_name,
        )
    else:
        logger.error(
            f"Model Preprocessing Params Extractor is not yet implemented for {model_family}."
        )
        raise NotImplementedError(
            f"Model Preprocessing Params Extractor is not yet implemented for "
            f"{model_family}."
        )


def validate_transform_function_and_parameter_names(
    augmentation_library: ModuleType,
    augmentation_function_name: str,
    augmentation_function_param_names_list: List[str],
) -> None:
    """ Validates the augmentation function names and their parameters as per the used augmentation library

    :param augmentation_library: augmentation library used, for example albumentations, kornia, torchvision
    :type augmentation_library: ModuleType
    :param augmentation_function_name: name of augmentaion function
    :type augmentation_function_name: string
    :param augmentation_function_param_names_list: list of parameter names for given
           augmentation_function_name as specified in config
    :type augmentation_function_param_names_list: List[str]

    :return: None
    :rtype: None
    """

    # Ensure that the function is present in the library
    if not hasattr(augmentation_library, augmentation_function_name):
        logger.error(
            f"{augmentation_function_name} is not present in {augmentation_library.__name__}."
        )
        raise NameError(
            f"{augmentation_function_name} is not present in {augmentation_library.__name__}."
        )

    # Get list of expected parameters for a function
    expected_func_param_names_list = list(
        inspect.signature(
            getattr(augmentation_library, augmentation_function_name)
        ).parameters
    )

    # Assert all specified parameters in yaml are in acceptable parameters for the function
    assert all(
        [
            incoming_param_name in expected_func_param_names_list
            for incoming_param_name in augmentation_function_param_names_list
        ]
    ), (
        f"{augmentation_function_name}, expected: {expected_func_param_names_list}, "
        f"got: {augmentation_function_param_names_list}"
    )


def get_task_image_label_params_dict(phase_name: str, task_params_dict: dict) -> dict:
    """ Get the image and label related task params from task input.

    :param phase_name: Name of the phase - train/valid.
    :type phase_name: str
    :param task_params_dict: A dictionary containing task input param names and their values.
    :type task_params_dict: dict

    :return: A dictionary of required task image/label related params for the given phase.
    rtype: dict
    """
    # Get input params dictionary
    input_image_label_dict = {}
    if task_params_dict[SettingLiterals.TASK_NAME] in [
        Tasks.HF_MULTI_CLASS_IMAGE_CLASSIFICATION, Tasks.HF_MULTI_LABEL_IMAGE_CLASSIFICATION
    ]:
        input_image_label_dict = {
            **input_image_label_dict,
            SettingLiterals.IMAGE_HEIGHT: task_params_dict.get(
                SettingLiterals.IMAGE_HEIGHT, None
            ),
            SettingLiterals.IMAGE_WIDTH: task_params_dict.get(
                SettingLiterals.IMAGE_WIDTH, None
            ),
        }
    elif task_params_dict[SettingLiterals.TASK_NAME] in [
        Tasks.MM_OBJECT_DETECTION, Tasks.MM_INSTANCE_SEGMENTATION
    ]:
        input_image_label_dict = {
            **input_image_label_dict,
            SettingLiterals.IMAGE_MIN_SIZE: task_params_dict.get(
                SettingLiterals.IMAGE_MIN_SIZE, None
            ),
            SettingLiterals.IMAGE_MAX_SIZE: task_params_dict.get(
                SettingLiterals.IMAGE_MAX_SIZE, None
            ),
        }
    # Returning same for train and validation case, to be updated as per need later
    if phase_name == AugmentationConfigKeys.TRAINING_PHASE_KEY:
        return input_image_label_dict
    else:
        return input_image_label_dict


def update_augmentation_dict_with_model_preproc_config(
    config_path, model_preprocessing_params_dict, **task_params
):
    """ Get the augmentation dictionary from augmentation-config updated with the model
    preprocessing param values.

    :param config_path: Augmentation config's path - if config file used;
            None, otherwise
    :type config_path: string
    :param model_preprocessing_params_dict: models's preprocessing parameters dict
            - HF: image_processor.to_dict() from preprocess_config.json
            - Other Framwork: dict containing preprocessing params
            - Other approaches: dict containing preprocessing param,
                key:value pairs in dict to be used for preparing transforms.
    :type model_preprocessing_params_dict: dict
    :param task_params: A dictionary containing task input param names and their values.
    :type task_params: dict

    :return: augmentation config dictionary containing function name, updated function param's values
                & values for train and valid
            {
                "train": [{"function_name": {function_param_name: value, ...}, ...}],
                "valid": [{"function_name": {function_param_name: value, ...}, ...}],
            }
    :rtype: dict
    """
    # Load the config dict
    augmentation_dict = load_augmentation_dict_from_config(config_path=config_path)

    # Get augmentation library name
    augmentation_library_name = augmentation_dict[
        AugmentationConfigKeys.AUGMENTATION_LIBRARY_NAME
    ]

    # Get augmentation library
    augmentation_library = get_augmentation_library(
        augmentation_library_name=augmentation_library_name
    )

    # Get model family preprocessing extractor
    model_preproc_extractor = get_model_preproc_extractor(
        augmentation_library_name=augmentation_library_name,
        model_preprocessing_params_dict=model_preprocessing_params_dict,
        model_family=task_params[SettingLiterals.MODEL_FAMILY],
    )

    # Prepare task's image and label related input for train and validation phases to update config
    task_image_label_params_dict = {
        AugmentationConfigKeys.TRAINING_PHASE_KEY: get_task_image_label_params_dict(
            phase_name=AugmentationConfigKeys.TRAINING_PHASE_KEY,
            task_params_dict=task_params,
        ),
        AugmentationConfigKeys.VALIDATION_PHASE_KEY: get_task_image_label_params_dict(
            phase_name=AugmentationConfigKeys.VALIDATION_PHASE_KEY,
            task_params_dict=task_params,
        ),
    }

    # Get the updated augmentation config dictionary
    updated_augmentation_dict = {
        AugmentationConfigKeys.AUGMENTATION_LIBRARY_NAME: augmentation_library_name
    }
    for phase_key in [
        AugmentationConfigKeys.TRAINING_PHASE_KEY,
        AugmentationConfigKeys.VALIDATION_PHASE_KEY,
    ]:
        if phase_key not in augmentation_dict.keys():
            logger.info(
                f"{phase_key} is not present in the Augmentation config. Skipping processing for it."
            )
            continue

        updated_augmentation_dict[phase_key] = []

        for augmentation_dict_item in augmentation_dict[phase_key]:
            augmentation_function_name = list(augmentation_dict_item.keys())[0]
            augmentation_function_params_dict = augmentation_dict_item[augmentation_function_name]
            result_dict = {
                augmentation_function_name: augmentation_function_params_dict
            }

            # Update aug params, if needed
            update_fn_params = {
                AugmentationConfigKeys.FUNC_NAME: augmentation_function_name,
                AugmentationConfigKeys.FUNC_PARAMS_DICT: augmentation_function_params_dict,
                AugmentationConfigKeys.PHASE_NAME: phase_key,
                AugmentationConfigKeys.TASK_PARAM_DICT: task_image_label_params_dict[phase_key]
            }
            if AlbumentationParameterNames.TRANSFORMS_KEY in result_dict[augmentation_function_name].keys():
                # Processing the transformations such as OneOf, SomeOf etc which contains child transformations
                augmentation_function_params_update = {AlbumentationParameterNames.TRANSFORMS_KEY: []}
                for transform in result_dict[augmentation_function_name][AlbumentationParameterNames.TRANSFORMS_KEY]:
                    tfms_name = list(transform.keys())[0]
                    default_param_dict = transform[tfms_name]
                    update_fn_params[AugmentationConfigKeys.FUNC_NAME] = tfms_name
                    update_fn_params[AugmentationConfigKeys.FUNC_PARAMS_DICT] = default_param_dict
                    updated_params_dict = model_preproc_extractor.extract_augmentation_params_dict(**update_fn_params)
                    augmentation_function_params_update[AlbumentationParameterNames.TRANSFORMS_KEY].append({
                        tfms_name: {**default_param_dict, **updated_params_dict}
                    })
            else:
                augmentation_function_params_update = \
                    model_preproc_extractor.extract_augmentation_params_dict(**update_fn_params)

            # Update parameters in the dict
            result_dict[augmentation_function_name] = {
                **result_dict[augmentation_function_name],
                **augmentation_function_params_update
            }
            updated_augmentation_dict[phase_key].append(result_dict)

            # Validate the augmentation parameters
            validate_transform_function_and_parameter_names(
                augmentation_library=augmentation_library,
                augmentation_function_name=augmentation_function_name,
                augmentation_function_param_names_list=list(
                    result_dict[augmentation_function_name].keys()
                ),
            )
            # Validate the parameters for compositional transforms such as OneOf, SomeOf etc.
            if AlbumentationParameterNames.TRANSFORMS_KEY in result_dict[augmentation_function_name].keys():
                for transform in result_dict[augmentation_function_name][AlbumentationParameterNames.TRANSFORMS_KEY]:
                    tfms_name = list(transform.keys())[0]
                    validate_transform_function_and_parameter_names(
                        augmentation_library=augmentation_library,
                        augmentation_function_name=tfms_name,
                        augmentation_function_param_names_list=list(
                            transform[tfms_name].keys()
                        )
                    )

    return updated_augmentation_dict
