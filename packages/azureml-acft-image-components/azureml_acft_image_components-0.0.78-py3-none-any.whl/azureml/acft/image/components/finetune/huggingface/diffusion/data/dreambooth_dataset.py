# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Diffusion Dataset."""

import os
from pathlib import Path
from typing import Callable, Dict, List

import albumentations
import numpy as np
import torch
import torchvision
from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
from azureml.acft.image.components.finetune.common.constants.augmentation_constants import (
    AlbumentationParamNames,
    TorchvisionParamNames,
)
from azureml.acft.image.components.finetune.common.constants.constants import ImageDataItemLiterals
from azureml.acft.image.components.finetune.huggingface.diffusion.models.constant import Literals
from PIL import Image
from PIL.ImageOps import exif_transpose
from torch.utils.data import Dataset
from torchvision import transforms
from transformers import PreTrainedTokenizer

logger = get_logger_app(__name__)


class DreamBoothDataset(Dataset):
    """A dataset to prepare the instance and class images with the prompts for fine-tuning the model.

    It pre-processes the images and the tokenizes prompts.
    """

    SUPPORTED_TRANSFORM_LIB_NAME_MAPPING = {
        albumentations.core.composition.Compose: AlbumentationParamNames.LIB_NAME,
        torchvision.transforms.Compose: TorchvisionParamNames.LIB_NAME,
    }

    def __init__(
        self,
        instance_data_root: str,
        instance_prompt: str,
        tokenizer: PreTrainedTokenizer,
        class_data_root: str = None,
        class_prompt: str = None,
        tokenizer_max_length: int = None,
        num_class_images: int = None,
        encoder_hidden_states: torch.Tensor = None,
        class_prompt_encoder_hidden_states: torch.Tensor = None,
        transform: List[callable] = None,
    ) -> None:
        """Dream Booth training Dataset constructor.

        :param instance_data_root: Path to the instance images root directory.
        :type instance_data_root: str
        :param instance_prompt: Prompt for the instance images with special placeholder.
        :type instance_prompt: str
        :param tokenizer: Tokenizer to tokenize the prompt.
        :type tokenizer: PreTrainedTokenizer
        :param class_data_root: Path to the class images root directory.
        :type class_data_root: str
        :param class_prompt: Prompt for the class images.
        :type class_prompt: str
        :param tokenizer_max_length: Maximum length of the tokenizer.
        :type tokenizer_max_length: int
        :param num_class_images: Number of class images to use.
        :type num_class_images: int
        :param encoder_hidden_states: Hidden states for the encoder.
        :type encoder_hidden_states: torch.Tensor
        :param class_prompt_encoder_hidden_states: Hidden states for the class prompt encoder.
        :type class_prompt_encoder_hidden_states: torch.Tensor
        :param transform: List of transformations to apply to the images.
        :type transform: List[callable]
        """
        self.instance_data_root = Path(instance_data_root)
        if not self.instance_data_root.exists():
            raise ACFTValidationException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=f"Instance {self.instance_data_root} images root doesn't exists.",
                ),
            )
        self.instance_prompt = instance_prompt
        self.instance_images_path = [
            path
            for path in self.instance_data_root.iterdir()
            if os.path.splitext(path)[-1] in [".jpeg", ".jpg", ".png"]
        ]
        self.num_instance_images = len(self.instance_images_path)
        self._length = self.num_instance_images

        self.tokenizer = tokenizer
        self.tokenizer_max_length = tokenizer_max_length

        self.class_data_root = class_data_root
        if class_data_root is not None:
            self.class_data_root = Path(class_data_root)
            self.class_images_path = [
                path
                for path in self.class_data_root.iterdir()
                if os.path.splitext(path)[-1] in [".jpeg", ".jpg", ".png"]
            ]
            if num_class_images is not None:
                self.num_class_images = min(len(self.class_images_path), num_class_images)
            else:
                self.num_class_images = len(self.class_images_path)
            self._length = max(self.num_class_images, self._length)
            self.class_prompt = class_prompt

        self.encoder_hidden_states = encoder_hidden_states
        self.class_prompt_encoder_hidden_states = class_prompt_encoder_hidden_states
        self.transform = None
        self._set_transform(transform)

    def __len__(self) -> int:
        """Return the length of the dataset.

        :return: Length of the dataset.
        :rtype: int
        """
        return self._length

    def __getitem__(self, index: int) -> Dict[str, torch.Tensor]:
        """Get the item at the specified index.

        :param index: Index of the item.
        :type index: int
        :return: Dictionary containing the instance, class images, prompts ids and attention mask.
        :rtype: Dict[str, torch.Tensor]
        """
        example = {}
        instance_image = Image.open(self.instance_images_path[index % self.num_instance_images])
        instance_image = exif_transpose(instance_image)

        if not instance_image.mode == "RGB":
            instance_image = instance_image.convert("RGB")
        if self.transform is not None:
            example[Literals.INSTANCE_IMAGES] = self._apply_transform(image=np.array(instance_image))

        if self.encoder_hidden_states is not None:
            example[Literals.INSTANCE_PROMPT_IDS] = self.encoder_hidden_states
        else:
            text_inputs = tokenize_prompt(
                self.tokenizer, self.instance_prompt, tokenizer_max_length=self.tokenizer_max_length
            )
            example[Literals.INSTANCE_PROMPT_IDS] = text_inputs.input_ids
            example[Literals.INSTANCE_ATTENTION_MASK] = text_inputs.attention_mask

        if self.class_data_root:
            class_image = Image.open(self.class_images_path[index % self.num_class_images])
            class_image = exif_transpose(class_image)

            if not class_image.mode == "RGB":
                class_image = class_image.convert("RGB")

            example[Literals.CLASS_IMAGES] = (
                self._apply_transform(image=np.array(class_image)) if self.transform else np.array(class_image)
            )

            if self.class_prompt_encoder_hidden_states is not None:
                example[Literals.CLASS_PROMPT_IDS] = self.class_prompt_encoder_hidden_states
            else:
                class_text_inputs = tokenize_prompt(
                    self.tokenizer, self.class_prompt, tokenizer_max_length=self.tokenizer_max_length
                )
                example[Literals.CLASS_PROMPT_IDS] = class_text_inputs.input_ids
                example[Literals.CLASS_ATTENTION_MASK] = class_text_inputs.attention_mask
        return example

    def _set_transform(self, transform: Callable) -> None:
        """Set transform to the specified transform.

        :param transform: Transform to apply to the images.
        :type transform: Callable
        """
        self.transform = transform

        # check supported augmentation transforms
        self._check_supported_transform_type()

        # Get augmentation library name
        self._set_augmentation_library_name_from_transform()

        # Prepare an apply transform factory
        self._set_apply_transform_factory()

    def _check_supported_transform_type(self) -> None:
        """Check supported transform type.

        :return: None
        :rtype: None
        """
        # Check for supported augmentation transform
        if self.transform and not any(
            [
                isinstance(self.transform, supported_transform)
                for supported_transform in self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys()
            ]
        ):
            logger.error(
                f"{type(self.transform)} is not supported. Only"
                f" {list( self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys())} are supported for now."
            )
            raise NotImplementedError(
                f"{type(self.transform)} is not supported. "
                f"Only {list( self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys())} are supported for now."
            )

    def _set_augmentation_library_name_from_transform(self):
        """Extract augmentation library name based on the transform and set it."""
        # Get augmentation library name
        for supported_transform in self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys():
            if isinstance(self.transform, supported_transform):
                self.augmentation_lib_name = self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING[supported_transform]
                break

    def _set_apply_transform_factory(self):
        """Prepare apply_transoform factory."""
        # Prepare an apply transform factory
        self.apply_transform_factory = {
            AlbumentationParamNames.LIB_NAME: self._albumentations_apply_transform,
            TorchvisionParamNames.LIB_NAME: self._torchvision_apply_transform,
        }

    def _albumentations_apply_transform(self, image: np.ndarray) -> np.ndarray:
        """Apply albumentations transform.

        :param image: Input image
        :type image: np.ndarray
        :return: An image with transform applied, if transform type is supported. Otherwise, raise error.
        :rtype: np.ndarray
        """
        return self.transform(image=image)[ImageDataItemLiterals.ALBUMENTATIONS_IMAGE_KEY]

    def _torchvision_apply_transform(self, image: np.ndarray) -> np.ndarray:
        """Apply torchvision transform.

        :param image: Input image
        :type image: np.ndarray
        :return: An image with transform applied, if transform type is supported. Otherwise, raise error.
        :rtype: np.ndarray
        """
        return self.transform(image)

    def _apply_transform(self, image: np.ndarray) -> np.ndarray:
        """Apply transform.

        :param image: Input image
        :type image: np.ndarray
        :return: An image with transform applied, if transform type is supported. Otherwise, raise error.
        :rtype: np.ndarray
        """
        return self.apply_transform_factory[self.augmentation_lib_name](image=image)


def tokenize_prompt(tokenizer: PreTrainedTokenizer, prompt: str, tokenizer_max_length: int = None) -> List[str]:
    """Tokenize the prompt using the tokenizer and return the tokenized inputs.

    :param tokenizer: Tokenizer to tokenize the prompt.
    :type tokenizer: PreTrainedTokenizer
    :param prompt: Prompt to tokenize.
    :type prompt: str
    :param tokenizer_max_length: Maximum length of the tokenizer.
    :type tokenizer_max_length: int
    :return: Tokenized inputs.
    :rtype: List[str]
    """
    if tokenizer_max_length is not None:
        max_length = tokenizer_max_length
    else:
        max_length = tokenizer.model_max_length

    text_inputs = tokenizer(
        prompt,
        truncation=True,
        padding="max_length",
        max_length=max_length,
        return_tensors="pt",
    )

    return text_inputs
