# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Hf diffusion data class."""

import gc
from typing import Any, Callable, Dict, List, Optional

import torch
import torch.utils.checkpoint
from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
from azureml.acft.image.components.finetune.common.data.base_dataset import BaseDataset
from azureml.acft.image.components.finetune.huggingface.diffusion.constants.defaults import DataDefaults
from azureml.acft.image.components.finetune.huggingface.diffusion.data.class_image_data import ClassImageGenerator
from azureml.acft.image.components.finetune.huggingface.diffusion.data.dreambooth_dataset import (
    DreamBoothDataset,
    tokenize_prompt,
)
from azureml.acft.image.components.finetune.huggingface.diffusion.models.constant import DataLiterals, Literals
from azureml.acft.image.components.finetune.huggingface.diffusion.models.model import AzuremlStableDiffusionPipeline
from azureml.acft.image.components.finetune.huggingface.diffusion.models.text_encoder import AzmlTextEncoder
from azureml.acft.image.components.finetune.huggingface.diffusion.models.tokenizer import PreTrainedTokenizer
from azureml.acft.image.components.finetune.interfaces.azml_interface import AzmlDataInterface
from torchvision import transforms

logger = get_logger_app(__name__)


class AzmlHfImageDataInterface(AzmlDataInterface):
    """Data interface for Hf Image Models."""

    def __init__(
        self,
        tokenizer: PreTrainedTokenizer,
        text_encoder: AzmlTextEncoder,
        **kwargs
    ) -> None:
        """Initialize the data interface for stable diffusion Image Models.

        :param tokenizer: hugging face feature extractor for image models
        :type tokenizer: PreTrainedTokenizer
        :param text_encoder: text encoder
        :type text_encoder: AzmlTextEncoder
        :param azml_sd_pipeline: AzureML stable diffusion pipeline
        :type azml_sd_pipeline: AzuremlStableDiffusionPipeline
        :param kwargs: additional arguments such as train_mltable_path (mandetory)
        """
        self.num_class_images = kwargs.get(Literals.NUM_CLASS_IMAGES, DataDefaults.NUM_CLASS_IMAGES)
        self.class_data_dir = kwargs.get(Literals.CLASS_DATA_DIR, DataDefaults.CLASS_DATA_DIR)
        self.class_prompt = kwargs.get(Literals.CLASS_PROMPT, None)
        self.with_prior_preservation = kwargs.get(Literals.WITH_PRIOR_PRESERVATION, True)

        # Dataset and DataLoaders creation:'
        self.instance_prompt = kwargs.get(Literals.INSTANCE_PROMPT, None)
        self.pre_compute_text_embeddings = kwargs.get(Literals.PRE_COMPUTE_TEXT_EMBEDDINGS, True)
        self.text_encoder_use_attention_mask = kwargs.get(Literals.TEXT_ENCODER_USE_ATTENTION_MASK, False)
        self.instance_data_dir = kwargs[Literals.TRAIN_MLTABLE_PATH]
        self.tokenizer_max_length = kwargs.get(Literals.TOKENIZER_MAX_LENGTH, None)
        self.tokenizer = tokenizer

        self.size = kwargs.get(Literals.RESOLUTION, 512)
        self.center_crop = kwargs.get(Literals.CENTER_CROP, True)
        self.random_flip = kwargs.get(Literals.RANDOM_FLIP, True)

        self.pre_computed_encoder_hidden_states = None
        self.pre_computed_class_prompt_encoder_hidden_states = None
        if self.pre_compute_text_embeddings:
            self._pre_encode_prompt(tokenizer, text_encoder)

    def _get_train_augmentation_transforms(self) -> Optional[Callable]:
        """Get the train augmentation transforms.

        :return: The train augmentation transforms.
        :rtype: Optional[Callable]
        """
        train_transforms = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Resize(self.size, interpolation=transforms.InterpolationMode.BILINEAR),
                transforms.CenterCrop(self.size) if self.center_crop else transforms.RandomCrop(self.size),
                transforms.RandomHorizontalFlip() if self.random_flip else transforms.Lambda(lambda x: x),
                transforms.Normalize([0.5], [0.5]),
            ]
        )
        return train_transforms

    def _pre_encode_prompt(self, tokenizer: PreTrainedTokenizer, text_encoder: AzmlTextEncoder) -> torch.Tensor:
        """Pre-encode the prompt.

        :param tokenizer: The tokenizer.
        :type tokenizer: PreTrainedTokenizer
        :param text_encoder: The text encoder.
        :type text_encoder: AzmlTextEncoder
        :return: The prompt embeddings.
        :rtype: torch.Tensor
        """
        def compute_text_embeddings(prompt: str) -> torch.Tensor:
            """Compute the text embeddings.

            :param prompt: The prompt.
            :type prompt: str
            :return: The embeddings.
            :rtype: torch.Tensor
            """
            with torch.no_grad():
                text_inputs = tokenize_prompt(tokenizer, prompt, tokenizer_max_length=self.tokenizer_max_length)
                prompt_embeds = AzuremlStableDiffusionPipeline.encode_prompt(
                    text_encoder,
                    text_inputs.input_ids,
                    text_inputs.attention_mask,
                    text_encoder_use_attention_mask=self.text_encoder_use_attention_mask,
                )

            return prompt_embeds

        self.pre_computed_encoder_hidden_states = compute_text_embeddings(self.instance_prompt)

        if self.class_prompt is not None:
            self.pre_computed_class_prompt_encoder_hidden_states = compute_text_embeddings(self.class_prompt)

        gc.collect()
        torch.cuda.empty_cache()

    def get_train_dataset(self) -> BaseDataset:
        """Get train dataset.

        :return : train dataset
        :rtype: BaseDataset
        """
        self.train_dataset = DreamBoothDataset(
            instance_data_root=self.instance_data_dir,
            instance_prompt=self.instance_prompt,
            class_data_root=self.class_data_dir if self.with_prior_preservation else None,
            class_prompt=self.class_prompt,
            num_class_images=self.num_class_images,
            tokenizer=self.tokenizer,
            encoder_hidden_states=self.pre_computed_encoder_hidden_states,
            class_prompt_encoder_hidden_states=self.pre_computed_class_prompt_encoder_hidden_states,
            transform=self._get_train_augmentation_transforms(),
        )
        return self.train_dataset

    def get_validation_dataset(self) -> BaseDataset:
        """Get validation dataset.

        :return : validation dataset
        :rtype: BaseDataset
        """
        # dummy validation num_images, since no compute metrics is being called.
        num_class_images = 1
        return DreamBoothDataset(
            instance_data_root=self.instance_data_dir,
            instance_prompt=self.instance_prompt,
            class_data_root=self.class_data_dir if self.with_prior_preservation else None,
            class_prompt=self.class_prompt,
            num_class_images=num_class_images,
            tokenizer=self.tokenizer,
            encoder_hidden_states=self.pre_computed_encoder_hidden_states,
            class_prompt_encoder_hidden_states=self.pre_computed_class_prompt_encoder_hidden_states,
            transform=self._get_train_augmentation_transforms(),
        )

    def get_collation_function(
        self,
    ) -> Callable[[List[Dict[str, Any]]], Dict[str, torch.Tensor]]:
        """Get the collate function.

        :return: A callable collate function.
        :rtype: Callable[[List[Dict[str, Any]]], Dict[str, torch.Tensor]]
        """
        return collate_fn


def collate_fn(examples: List[Dict], with_prior_preservation: bool = True) -> Dict[str, torch.Tensor]:
    """Get collate function for the diffusion dataset.

    :param examples: The examples to collate.
    :type examples: List[Dict[str, Any]]
    :param with_prior_preservation: Whether to include the prior preservation.
    :type with_prior_preservation: bool
    :return: The collated batch.
    :rtype: Dict[str, torch.Tensor]
    """
    has_attention_mask = Literals.INSTANCE_ATTENTION_MASK in examples[0]

    input_ids = [example[Literals.INSTANCE_PROMPT_IDS] for example in examples]
    pixel_values = [example[Literals.INSTANCE_IMAGES] for example in examples]

    if has_attention_mask:
        attention_mask = [example[Literals.INSTANCE_ATTENTION_MASK] for example in examples]

    if len(examples) > 0 and Literals.CLASS_PROMPT_IDS in examples[0]:
        input_ids += [example[Literals.CLASS_PROMPT_IDS] for example in examples]
        pixel_values += [example[Literals.CLASS_IMAGES] for example in examples]

        if has_attention_mask:
            attention_mask += [example[Literals.CLASS_ATTENTION_MASK] for example in examples]

    pixel_values = torch.stack(pixel_values)
    pixel_values = pixel_values.to(memory_format=torch.contiguous_format).float()

    input_ids = torch.cat(input_ids, dim=0)

    batch = {
        DataLiterals.INPUT_IDS: input_ids,
        DataLiterals.PIXEL_VALUES: pixel_values,
    }

    if has_attention_mask:
        attention_mask = torch.cat(attention_mask, dim=0)
        batch[DataLiterals.ATTENTION_MASK] = attention_mask

    return batch
