# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Generate class images if prior preservation is enabled"""
import os
from pathlib import Path

import azureml.mlflow
import mlflow
import torch
from accelerate import Accelerator
from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.common_components import get_logger_app

# this is needed to handle mlflow tracking uri which startswith azureml
from azureml.acft.common_components.image.runtime_common.common import distributed_utils
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
from diffusers import DiffusionPipeline
from huggingface_hub.utils import insecure_hashlib
from torch.utils.data import DataLoader
from tqdm import tqdm

from azureml.acft.image.components.finetune.common.mlflow.common_utils import get_current_device
from azureml.acft.image.components.finetune.huggingface.diffusion.constants.defaults import DataDefaults
from azureml.acft.image.components.finetune.huggingface.diffusion.data.prompt_dataset import get_prompt_dataloader
from azureml.acft.image.components.finetune.huggingface.diffusion.models.constant import Literals
from azureml.acft.image.components.finetune.huggingface.diffusion.models.model import AzuremlStableDiffusionPipeline

logger = get_logger_app(__name__)


class ClassImageGenerator:
    """Generate class images if prior preservation is enabled."""

    def __init__(
        self,
        pretrained_model_name_or_path: str = None,
        azml_sd_pipeline: AzuremlStableDiffusionPipeline = None,
        prior_generation_precision: str = "fp32",
        seed: int = 42,
        dataloader_num_workers: int = 0,
        **kwargs,
    ):
        """Create class image generator with stable diffusion pipeline and settings.

        :param pretrained_model_name_or_path: pretrained model name or path, optional
        :type pretrained_model_name_or_path: str
        :param azml_sd_pipeline: AzureML stable diffusion pipeline, optional
        :type azml_sd_pipeline: AzuremlStableDiffusionPipeline
        :param prior_generation_precision: precision for prior generation, default is "fp32"
        :type prior_generation_precision: str
        :param seed: seed for random number generation, default is 42
        :type seed: int
        :param dataloader_num_workers: number of workers for dataloader, default is 0
        :type dataloader_num_workers: int
        """
        self.pretrained_model_name_or_path = pretrained_model_name_or_path
        self.prior_generation_precision = prior_generation_precision
        self.seed = seed
        self.dataloader_num_workers = dataloader_num_workers
        self.azml_sd_pipeline = azml_sd_pipeline
        self.kwargs = kwargs
        self._del_pipeline = False
        if self.pretrained_model_name_or_path is None and self.azml_sd_pipeline is None:
            raise ACFTValidationException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message="pretrained_model_name_or_path and azml_sd_pipeline both can not be None.",
                ),
            )

    @property
    def torch_dtype(self) -> torch.dtype:
        """Get torch dtype based on precision.

        :return: torch dtype
        :rtype: torch.dtype
        """
        device = get_current_device()
        torch_dtype = torch.float16 if device.type == "cuda" else torch.float32
        if self.prior_generation_precision == "fp32":
            torch_dtype = torch.float32
        elif self.prior_generation_precision == "fp16":
            torch_dtype = torch.float16
        elif self.prior_generation_precision == "bf16":
            torch_dtype = torch.bfloat16
        return torch_dtype

    def _get_current_image_count(self, class_image_dir: str) -> int:
        """Get count of images present in class image directory.

        :param class_image_dir: class image directory
        :type class_image_dir: str
        :return: count of images present in class image directory
        :rtype: int
        """
        class_images_dir = Path(class_image_dir)
        if not class_images_dir.exists():
            class_images_dir.mkdir(parents=True)
        return len(list(class_images_dir.iterdir()))

    def _load_pipeline(self) -> DiffusionPipeline:
        """Load diffusion pipeline from azureml stable diffusion pipeline.

        :return: diffusion pipeline from HF
        :rtype: DiffusionPipeline
        """
        self.kwargs[Literals.WEIGHT_DTYPE] = self.torch_dtype

        if self.azml_sd_pipeline is None:
            pipeline = DiffusionPipeline.from_pretrained(self.pretrained_model_name_or_path, dtype=self.torch_dtype)
            # If pipeline is created in this method, then delete it after use.
            self._del_pipeline = True
        else:
            pipeline = DiffusionPipeline.from_pretrained(
                self.pretrained_model_name_or_path,
                text_encoder=self.azml_sd_pipeline.text_encoder,
                vae=self.azml_sd_pipeline.vae,
                unet=self.azml_sd_pipeline.unet,
                tokenizer=self.azml_sd_pipeline.tokenizer,
                scheduler=self.azml_sd_pipeline.noise_scheduler,
            )

        pipeline.set_progress_bar_config(disable=True)
        return pipeline

    def run_pipeline(self, dataloader: DataLoader, class_image_dir: str, cur_class_images: int = 0) -> None:
        """Run pipeline to generate class images on master process.

        :param dataloader: dataloader to generate class images
        :type dataloader: DataLoader
        :param class_image_dir: directory to save class images
        :type class_image_dir: str
        :param cur_class_images: current class images, default is 0
        :type cur_class_images: int
        """
        if not distributed_utils.master_process():
            return
        try:
            pipeline = self._load_pipeline()
            accelerator = Accelerator()
            sample_dataloader = accelerator.prepare(dataloader)
            pipeline.to(accelerator.device)
            for example in tqdm(
                sample_dataloader, desc="Generating class images", disable=not accelerator.is_local_main_process
            ):
                with torch.no_grad():
                    images = pipeline(example["prompt"]).images

                for i, image in enumerate(images):
                    hash_image = insecure_hashlib.sha1(image.tobytes()).hexdigest()
                    image_filename = os.path.join(
                        class_image_dir, f"{example['index'][i] + cur_class_images}-{hash_image}.jpg"
                    )
                    image.save(image_filename)
        finally:
            if self._del_pipeline:
                del pipeline
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                self._del_pipeline = False

    def generate_class_images(
        self,
        class_image_dir: str,
        class_prompt: str,
        class_image_count: int,
        batch_size: int,
    ) -> bool:
        """Generate class images.

        :param class_image_dir: directory to save class images
        :type class_image_dir: str
        :param class_prompt: prompt to generate class images
        :type class_prompt: str
        :param class_image_count: number of class images to generate
        :type class_image_count: int
        :param batch_size: batch size, default is 1
        :type batch_size: int

        :return: True if class images are to be generated. False otherwise.
        """
        cur_class_images = self._get_current_image_count(class_image_dir)
        num_new_images = class_image_count - cur_class_images
        if num_new_images > 0:
            logger.info(f"Number of class images to sample: {num_new_images}.")
            dataloader = get_prompt_dataloader(class_prompt, num_new_images, batch_size)

            self.run_pipeline(dataloader, class_image_dir, cur_class_images)
            return True
        else:
            logger.warning(
                f"{class_image_count} images are already present in the folder {class_image_dir}. "
                "No new images are generated."
            )
            return False


def generate_class_images(
    model_name_or_path: str,
    class_prompt: str,
    class_data_dir=DataDefaults.CLASS_DATA_DIR,
    num_class_images=DataDefaults.NUM_CLASS_IMAGES,
    prior_generation_precision=DataDefaults.PRIOR_GENERATION_PRECISION,
    dataloader_num_workers=DataDefaults.DATALOADER_WORKERS,
    sample_batch_size=DataDefaults.SAMPLE_BATCH_SIZE,
    upload_images_as_artifacts=False,
    **kwargs,
) -> None:
    """Generate class images for prior preservation.

    :param model_name_or_path: The model name or path.
    :type model_name_or_path: str
    :param class_prompt: prompt to generate class images
    :type class_prompt: str
    :param class_data_dir: directory to save class images
    :type class_data_dir: str
    :param num_class_images: number of class images to generate
    :type num_class_images: int
    :param prior_generation_precision: precision for prior generation, default is "fp32"
    :type prior_generation_precision: str
    :param dataloader_num_workers: number of workers for dataloader, default is 0
    :type dataloader_num_workers: int
    :param sample_batch_size: batch size, default is 1
    :type sample_batch_size: int
    :param upload_images_as_artifacts: upload images as artifacts, default is False
    :type upload_images_as_artifacts: bool
    """
    if not class_prompt:
        raise ACFTValidationException._with_error(
            AzureMLError.create(
                ACFTUserError,
                pii_safe_message="Class prompt is required for prior preservation.",
            ),
        )

    have_generate_class_images = ClassImageGenerator(
        pretrained_model_name_or_path=model_name_or_path,
        prior_generation_precision=prior_generation_precision,
        dataloader_num_workers=dataloader_num_workers,
        **kwargs,
    ).generate_class_images(class_data_dir, class_prompt, num_class_images, sample_batch_size)

    if upload_images_as_artifacts:
        if have_generate_class_images:
            if distributed_utils.master_process():
                mlflow.log_artifacts(class_data_dir, artifact_path=DataDefaults.CLASS_DATA_DIR)
                logger.info("Class images are uploaded as artifacts in mlflow.")
        else:
            logger.info("No new class images are generated. Therefore, not uploading any images as artifacts.")
