# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Mlflow save utils."""

# Note: Make Sure not add any imports from image package as this is being
# used in evaluate-mlflow pacakge for testing.
import mlflow
import os
import shutil
import torch
import transformers
from argparse import Namespace

from mlflow.models import infer_signature
from mlflow.transformers import generate_signature_output
from transformers.image_processing_utils import BaseImageProcessor
from transformers.modeling_utils import PreTrainedModel
from transformers.trainer import get_last_checkpoint
from transformers.utils.peft_utils import ADAPTER_CONFIG_NAME, ADAPTER_SAFE_WEIGHTS_NAME, ADAPTER_WEIGHTS_NAME
from typing import Dict, Optional, List, Any

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.common_components import get_logger_app, ModelSelectorDefaults
from azureml.acft.common_components.utils.error_handling.error_definitions import TaskNotSupported
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
try:
    from azureml.acft.image.components.common.utils import get_random_base64_decoded_image
except Exception:
    # imported in evaluate-mlflow uts. Not needed for od/is uts.
    get_random_base64_decoded_image = None
from mlflow.models.signature import ModelSignature
from mlflow.types.schema import ColSpec, Schema, ParamSchema, ParamSpec

from mmdet_mlflow_model_wrapper import ImagesMLFlowModelWrapper as DetImagesMLFlowModelWrapper
from mmtrack_mlflow_model_wrapper import ImagesMLFlowModelWrapper as TrackImagesMLFlowModelWrapper
from stable_diffusion_mlflow_model_wrapper import StableDiffusionMLflowWrapper

from common_constants import (
    AugmentationConfigKeys,
    Tasks,
    MLFlowSchemaLiterals,
    MLflowLiterals,
    MLflowMetadataLiterals,
    MMDetLiterals,
    SDLiterals,
    SDSettingParameters,
    TrainingDefaultsConstants,
    TrainingLiterals
)
from mlflow.utils.requirements_utils import _get_pinned_requirement


logger = get_logger_app(__name__)


def get_mlflow_signature(task_type: str) -> ModelSignature:
    """
    Return mlflow model signature with input and output schema given the input task type.

    :param task_type: Task type used in training.
    :type task_type: str
    :return: mlflow model signature.
    :rtype: mlflow.models.signature.ModelSignature
    """
    if task_type == Tasks.MM_MULTI_OBJECT_TRACKING:
        input_schema = Schema(
            [
                ColSpec(
                    MLFlowSchemaLiterals.INPUT_COLUMN_VIDEO_DATA_TYPE,
                    MLFlowSchemaLiterals.INPUT_COLUMN_VIDEO,
                )
            ]
        )
    elif task_type == Tasks.HF_SD_TEXT_TO_IMAGE:
        input_schema = Schema(inputs=[
            ColSpec(name=MLFlowSchemaLiterals.INPUT_COLUMN_PROMPT,
                    type=MLFlowSchemaLiterals.INPUT_COLUMN_PROMPT_DATA_TYPE,)
        ])
    else:
        input_schema = Schema(
            [
                ColSpec(
                    MLFlowSchemaLiterals.INPUT_COLUMN_IMAGE_DATA_TYPE,
                    MLFlowSchemaLiterals.INPUT_COLUMN_IMAGE,
                )
            ]
        )

    # For classification
    if task_type in [
        Tasks.HF_MULTI_CLASS_IMAGE_CLASSIFICATION,
        Tasks.HF_MULTI_LABEL_IMAGE_CLASSIFICATION,
    ]:

        output_schema = Schema(
            [
                ColSpec(
                    MLFlowSchemaLiterals.OUTPUT_COLUMN_DATA_TYPE,
                    MLFlowSchemaLiterals.OUTPUT_COLUMN_PROBS,
                ),
                ColSpec(
                    MLFlowSchemaLiterals.OUTPUT_COLUMN_DATA_TYPE,
                    MLFlowSchemaLiterals.OUTPUT_COLUMN_LABELS,
                ),
            ]
        )

    # for object detection and instance segmentation and multi-object tracking mlflow signature remains same
    elif task_type in [
        Tasks.MM_OBJECT_DETECTION,
        Tasks.MM_INSTANCE_SEGMENTATION,
        Tasks.MM_MULTI_OBJECT_TRACKING,
    ]:
        output_schema = Schema(
            [
                ColSpec(
                    MLFlowSchemaLiterals.OUTPUT_COLUMN_DATA_TYPE,
                    MLFlowSchemaLiterals.OUTPUT_COLUMN_BOXES,
                ),
            ]
        )
    elif task_type == Tasks.HF_SD_TEXT_TO_IMAGE:
        output_schema = Schema(inputs=[
            ColSpec(name=MLFlowSchemaLiterals.INPUT_COLUMN_PROMPT,
                    type=MLFlowSchemaLiterals.INPUT_COLUMN_PROMPT_DATA_TYPE,),
            ColSpec(name=MLFlowSchemaLiterals.OUTPUT_COLUMN_IMAGE,
                    type=MLFlowSchemaLiterals.OUTPUT_COLUMN_IMAGE_TYPE),
            ColSpec(name=MLFlowSchemaLiterals.OUTPUT_COLUMN_NSFW_FLAG,
                    type=MLFlowSchemaLiterals.OUTPUT_COLUMN_NSFW_FLAG_TYPE,),
        ])

    else:
        raise ACFTValidationException._with_error(
            AzureMLError.create(TaskNotSupported, TaskName=task_type)
        )

    params_schema = None
    if task_type == Tasks.HF_SD_TEXT_TO_IMAGE:
        params_schema = ParamSchema(
            [
                ParamSpec(SDLiterals.HEIGHT, SDSettingParameters.HEIGHT_DTYPE, SDSettingParameters.HEIGHT),
                ParamSpec(SDLiterals.WIDTH, SDSettingParameters.WIDTH_DTYPE, SDSettingParameters.WIDTH),
                ParamSpec(
                    SDLiterals.NUM_INFERENCE_STEPS,
                    SDSettingParameters.NUM_INFERENCE_STEPS_DTYPE,
                    SDSettingParameters.NUM_INFERENCE_STEPS,
                ),
                ParamSpec(
                    SDLiterals.GUIDANCE_SCALE,
                    SDSettingParameters.GUIDANCE_SCALE_DTYPE,
                    SDSettingParameters.GUIDANCE_SCALE,
                ),
                ParamSpec(
                    SDLiterals.NEGATIVE_PROMPT,
                    SDSettingParameters.NEGATIVE_PROMPT_DTYPE,
                    SDSettingParameters.NEGATIVE_PROMPT,
                    (-1,),
                ),
                ParamSpec(
                    SDLiterals.NUM_IMAGES_PER_PROMPT,
                    SDSettingParameters.NUM_IMAGES_PER_PROMPT_DTYPE,
                    SDSettingParameters.NUM_IMAGES_PER_PROMPT,
                ),
            ]
        )

    return ModelSignature(inputs=input_schema, outputs=output_schema, params=params_schema)


def get_extra_pip_requirements(task_name: str) -> List[str]:
    """ Return extra pip packages required to loading the model in mlflow.
    :param task_name: Task name used in training.
    :type task_name: str
    :return: extra pip packages.
    :rtype: List[str]
    """
    extra_packages_list = []
    extra_package_names = []
    if task_name in [Tasks.HF_MULTI_CLASS_IMAGE_CLASSIFICATION,
                     Tasks.HF_MULTI_LABEL_IMAGE_CLASSIFICATION]:
        extra_package_names = [("torchvision", ">=0.0.14")]
    for (package_name, default_version) in extra_package_names:
        try:
            # Take the pinned version from the current environment if available
            # else use the default version provided.
            package_with_version = _get_pinned_requirement(package_name)
            extra_packages_list.append(package_with_version)
        except ModuleNotFoundError:
            msg = f"Failed to get requirement for {package_name} in the current environment. \
                Pinning the default version {default_version} for {package_name}."
            logger.info(msg)
            extra_packages_list.append(f"{package_name}{default_version}")

    return extra_packages_list


def _save_mmdet_mlflow_model(
    model_output_dir: str,
    mlflow_output_dir: str,
    options: Dict[str, Any],
    model_name: str,
    task_type: str,
    metadata: dict
) -> None:
    """
    Save the mmdetection model in mlflow format.

    :param model_output_dir: Output directory where the HF trainer model files are stored.
    :type model_output_dir: str
    :param mlflow_output_dir: Output directory where mlflow model will be stored.
    :type mlflow_output_dir: str
    :param options: Dictionary of MLflow settings/wrappers for model saving process.
    :type options: Dict
    :param model_name: Name of the model.
    :type model_name: str
    :param task_type: Task type used in training.
    :type task_type: str
    :param metadata: metadata to be added to MLmodel file
    :type metadata: dict
    :return: None
    """

    config_path = os.path.join(model_output_dir, model_name + ".py")
    model_weights_path = os.path.join(model_output_dir, ModelSelectorDefaults.MODEL_CHECKPOINT_FILE_NAME)
    augmentations_path = os.path.join(model_output_dir, AugmentationConfigKeys.OUTPUT_AUG_FILENAME)
    metafile_path = os.path.join(model_output_dir, MMDetLiterals.METAFILE_PATH + ".json")
    model_defaults_path = os.path.join(model_output_dir, TrainingDefaultsConstants.MODEL_DEFAULTS_FILE)
    artifacts_dict = {
        MMDetLiterals.CONFIG_PATH : config_path,
        MMDetLiterals.WEIGHTS_PATH : model_weights_path,
        MMDetLiterals.AUGMENTATIONS_PATH: augmentations_path,
        MMDetLiterals.METAFILE_PATH: metafile_path,
    }
    if os.path.isfile(model_defaults_path):
        artifacts_dict[MMDetLiterals.MODEL_DEFAULTS_PATH] = model_defaults_path

    files_to_include_mmd = ['common_constants.py', 'common_utils.py', 'mmdet_mlflow_model_wrapper.py',
                            'mmdet_modules.py', 'mmdet_utils.py', 'augmentation_helper.py',
                            'custom_augmentations.py']
    files_to_include_mmt = ['common_constants.py', 'common_utils.py', 'mmtrack_mlflow_model_wrapper.py',
                            'mmtrack_module.py', 'mmtrack_utils.py']
    if task_type == Tasks.MM_OBJECT_DETECTION:
        files_to_include = files_to_include_mmd
    if task_type == Tasks.MM_INSTANCE_SEGMENTATION:
        files_to_include_mmd.append('masktools.py')
        files_to_include = files_to_include_mmd
    if task_type == Tasks.MM_MULTI_OBJECT_TRACKING:
        files_to_include = files_to_include_mmt
    directory = os.path.dirname(__file__)
    code_path = [os.path.join(directory, x) for x in files_to_include]

    logger.info(f"Saving mlflow pyfunc model to {mlflow_output_dir}.")

    pip_requirements = None
    conda_env = None
    if task_type == Tasks.MM_OBJECT_DETECTION:
        pip_requirements = os.path.join(os.path.dirname(__file__), "mmdet-od-requirements.txt")
    elif task_type == Tasks.MM_INSTANCE_SEGMENTATION:
        pip_requirements = os.path.join(os.path.dirname(__file__), "mmdet-is-requirements.txt")
    elif task_type == Tasks.MM_MULTI_OBJECT_TRACKING:
        conda_env = os.path.join(os.path.dirname(__file__), "mmtrack-mot-conda.yaml")

    try:
        mlflow.pyfunc.save_model(
            path=mlflow_output_dir,
            python_model=options[MLFlowSchemaLiterals.WRAPPER],
            artifacts=artifacts_dict,
            pip_requirements=pip_requirements,
            conda_env=conda_env,
            signature=options[MLFlowSchemaLiterals.SCHEMA_SIGNATURE],
            code_path=code_path,
            metadata=metadata
        )
        logger.info("Saved mlflow model successfully.")
    except Exception as e:
        logger.error(f"Failed to save the mlflow model {str(e)}")
        raise Exception(f"failed to save the mlflow model {str(e)}")


def save_mmdet_mlflow_pyfunc_model(
    task_type: str,
    model_output_dir: str,
    mlflow_output_dir: str,
    model_name: str,
    metadata: dict,
) -> None:
    """
    Save the mlflow model.

    :param task_type: Task type used in training.
    :type task_type: str
    :param model_output_dir: Output directory where the HF trainer model files are stored.
    :type model_output_dir: str
    :param mlflow_output_dir: Output directory where mlflow model will be stored.
    :type mlflow_output_dir: str
    :param model_name: Name of the model.
    :type model_name: str
    :param metadata: metadata to be added to MLmodel file
    :type metadata: dict
    """

    logger.info("Saving the model in MLFlow format.")
    if task_type == Tasks.MM_MULTI_OBJECT_TRACKING:
        mlflow_model_wrapper = TrackImagesMLFlowModelWrapper(task_type=task_type)
    else:
        mlflow_model_wrapper = DetImagesMLFlowModelWrapper(task_type=task_type)

    # Upload files to artifact store
    mlflow_options = {
        MLFlowSchemaLiterals.WRAPPER: mlflow_model_wrapper,
        MLFlowSchemaLiterals.SCHEMA_SIGNATURE: get_mlflow_signature(task_type),
    }
    _save_mmdet_mlflow_model(
        model_output_dir=model_output_dir,
        mlflow_output_dir=mlflow_output_dir,
        options=mlflow_options or {},
        model_name=model_name,
        task_type=task_type,
        metadata=metadata
    )


def hf_save_as_mlflow_model(component_args: Namespace,
                            model: PreTrainedModel,
                            image_processor: BaseImageProcessor,
                            metadata: dict):
    """
    save hugging face mlflow

    :param component_args: args from the finetune component
    :type component_args: Namespace
    :param model: transformers model object
    :type model: PreTrainedModel
    :param image_processor: transformers image processor object
    :type image_processor: BaseImageProcessor
    :param metadata: metadata to be added to MLmodel file
    :type metadata: dict
    """
    output_model_metafile_path = os.path.join(component_args.output_dir,
                                              ModelSelectorDefaults.MODEL_METADATA_PATH)
    output_model_defaults_path = os.path.join(component_args.output_dir,
                                              ModelSelectorDefaults.MODEL_DEFAULTS_PATH)
    code_paths = []
    if os.path.isfile(output_model_defaults_path):
        code_paths.append(output_model_defaults_path)
    if os.path.isfile(output_model_metafile_path):
        code_paths.append(output_model_metafile_path)
    transformers_model = {"model": model, "image_processor": image_processor}
    # float16 models won't work when model is on cpu. hence converting
    # the model to float32 for generating the signature.
    vision_model = transformers.pipeline(
        task="image-classification",
        model=model.to(torch.float32),
        image_processor=image_processor,
    )

    img_str = get_random_base64_decoded_image()
    signature = infer_signature(
        img_str, generate_signature_output(vision_model, img_str),
    )
    req_file = os.path.join(os.path.dirname(__file__), "hf-cls-requirements.txt")
    # mlflow 2.12.1 checks for "task"" key
    metadata.update({"task": "image-classification"})
    mlflow.transformers.save_model(
        transformers_model=transformers_model,
        path=component_args.mlflow_model_folder,
        code_paths=code_paths,
        signature=signature,
        metadata=metadata,
        task=Tasks.HF_MULTI_CLASS_IMAGE_CLASSIFICATION,
        pip_requirements=req_file,
    )


def _save_sd_text_to_image_mlflow_model(
    model_output_dir: str,
    mlflow_output_dir: str,
    options: Dict[str, Any],
    metadata: dict,
    apply_lora: bool
) -> None:
    """
    Save the Stable Diffusion text-to-image model in mlflow format.

    :param model_output_dir: Output directory where the HF trainer model files are stored.
    :type model_output_dir: str
    :param mlflow_output_dir: Output directory where mlflow model will be stored.
    :type mlflow_output_dir: str
    :param options: Dictionary of MLflow settings/wrappers for model saving process.
    :type options: Dict
    :param metadata: metadata to be added to MLmodel file
    :type metadata: dict
    :param apply_lora: flag to enable lora training
    :type apply_lora: bool
    :return: None
    """
    # create a temp directory to save the model artifacts
    saved_model_path = os.path.join(os.path.dirname(model_output_dir), MLflowLiterals.SAVED_MODEL_PATH)
    os.makedirs(saved_model_path, exist_ok=True)

    if apply_lora:
        # save only lora weight files and scheduler config
        last_checkpoint_folder = get_last_checkpoint(model_output_dir)
        for filename in [ADAPTER_WEIGHTS_NAME, ADAPTER_SAFE_WEIGHTS_NAME, ADAPTER_CONFIG_NAME]:
            lora_file = os.path.join(last_checkpoint_folder, filename)
            if os.path.isfile(lora_file):
                shutil.copy(lora_file, saved_model_path)
        # copy the scheduler folder to temp folder
        for item in os.listdir(model_output_dir):
            source = os.path.join(model_output_dir, item)
            destination = os.path.join(saved_model_path, item)
            if item.startswith(SDLiterals.SCHEDULER):
                if os.path.isdir(source):
                    shutil.copytree(source, destination)
    else:
        # Copy everything from model_output_dir to saved_model_path except for the 'checkpoint' folder
        for item in os.listdir(model_output_dir):
            source = os.path.join(model_output_dir, item)
            destination = os.path.join(saved_model_path, item)
            if os.path.isdir(source) and item.startswith(TrainingLiterals.CHECKPOINT):
                continue  # Skip the 'checkpoint' folder
            if os.path.isdir(source):
                if os.path.exists(destination):  # Check if the destination directory exists
                    shutil.rmtree(destination)  # Remove it if it does
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)

    artifacts_dict = {
        MLflowLiterals.MODEL_DIR: saved_model_path,
    }
    metadata[MLflowMetadataLiterals.APPLY_LORA] = apply_lora
    metadata.pop(MLflowMetadataLiterals.AZUREML_BASE_IMAGE, None)
    files_to_include = [
        "common_constants.py",
        "common_utils.py",
        "stable_diffusion_mlflow_model_wrapper.py",
        "stable_diffusion_modules.py",
    ]

    directory = os.path.dirname(__file__)
    code_path = [os.path.join(directory, x) for x in files_to_include]

    logger.info(f"Saving mlflow pyfunc model to {mlflow_output_dir}.")

    pip_requirements = None
    conda_env = None
    conda_env = os.path.join(os.path.dirname(__file__), "sd-text-to-image-conda.yaml")

    try:
        mlflow.pyfunc.save_model(
            path=mlflow_output_dir,
            python_model=options[MLFlowSchemaLiterals.WRAPPER],
            artifacts=artifacts_dict,
            pip_requirements=pip_requirements,
            conda_env=conda_env,
            signature=options[MLFlowSchemaLiterals.SCHEMA_SIGNATURE],
            code_path=code_path,
            metadata=metadata
        )
        logger.info("Saved mlflow model successfully.")
    except Exception as e:
        logger.error(f"Failed to save the mlflow model {str(e)}")
        raise Exception(f"failed to save the mlflow model {str(e)}")


def save_sd_text_to_image_mlflow_pyfunc_model(
    task_type: str,
    model_output_dir: str,
    mlflow_output_dir: str,
    metadata: dict,
    apply_lora: bool = False,
) -> None:
    """
    Save the mlflow model.

    :param task_type: Task type used in training.
    :type task_type: str
    :param model_output_dir: Output directory where the HF trainer model files are stored.
    :type model_output_dir: str
    :param mlflow_output_dir: Output directory where mlflow model will be stored.
    :type mlflow_output_dir: str
    :param metadata: metadata to be added to MLmodel file
    :type metadata: dict
    :param apply_lora: flag to enable lora training
    :type apply_lora: bool
    """

    logger.info("Saving the model in MLFlow format.")
    mlflow_model_wrapper = StableDiffusionMLflowWrapper(task_type=task_type)
    # Upload files to artifact store
    mlflow_options = {
        MLFlowSchemaLiterals.WRAPPER: mlflow_model_wrapper,
        MLFlowSchemaLiterals.SCHEMA_SIGNATURE: get_mlflow_signature(task_type),
    }
    _save_sd_text_to_image_mlflow_model(
        model_output_dir=model_output_dir,
        mlflow_output_dir=mlflow_output_dir,
        options=mlflow_options or {},
        metadata=metadata,
        apply_lora=apply_lora
    )
