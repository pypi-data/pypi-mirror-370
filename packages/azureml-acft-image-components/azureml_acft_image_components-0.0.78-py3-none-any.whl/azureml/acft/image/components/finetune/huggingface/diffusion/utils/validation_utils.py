# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------
"""
validation utils
"""
import os
from argparse import Namespace

import azureml.mlflow
import mlflow
from azureml.acft.accelerator.utils.logging_utils import get_logger_app
from transformers.trainer import get_last_checkpoint

from azureml.acft.image.components.finetune.huggingface.diffusion.data.class_image_data import generate_class_images
from azureml.acft.image.components.finetune.huggingface.diffusion.models.constant import Literals
from azureml.acft.image.components.finetune.huggingface.diffusion.models.model import AzuremlStableDiffusionPipeline

logger = get_logger_app()


def sd_generate_validation_images(
    component_args: Namespace, azml_sd_pipeline: AzuremlStableDiffusionPipeline, num_class_images: int = None
):
    """Generate Images to last checkpoint for validation.

    :param component_args: args from the finetune component
    :type component_args: Namespace
    :param azml_sd_pipeline: AzureML stable diffusion pipeline, optional
    :type azml_sd_pipeline: AzuremlStableDiffusionPipeline
    """
    if not num_class_images:
        num_class_images = int(os.environ.get(Literals.NUM_VALIDATION_IMAGES, 0))
    if num_class_images <= 0:
        return
    last_checkpoint_folder = get_last_checkpoint(component_args.output_dir)
    validate_images_dir = os.path.join(last_checkpoint_folder, "generated_images")
    os.makedirs(validate_images_dir, exist_ok=True)
    generate_class_images(
        model_name_or_path=component_args.model_name_or_path,
        azml_sd_pipeline=azml_sd_pipeline,
        class_data_dir=validate_images_dir,
        class_prompt=component_args.instance_prompt,
        num_class_images=num_class_images,
        prior_generation_precision="fp32",
        sample_batch_size=min(component_args.sample_batch_size, num_class_images),
    )
    logger.info(f"generated {num_class_images} images at {validate_images_dir} for validation")
