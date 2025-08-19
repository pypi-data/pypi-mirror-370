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

"""Preprocess for finetune component for stable diffusion task."""

from pathlib import Path
from argparse import Namespace
from dataclasses import asdict

import json

from .base import StableDiffusionPreprocessArgs, StableDiffusionDataset
from ....diffusion_auto.config import AzuremlAutoConfig
from ....diffusion_auto.tokenizer import AzuremlCLIPTokenizer
from ....constants.constants import Tasks, DatasetSplit, SaveFileConstants, MLFlowHFFlavourConstants

from azureml.acft.accelerator.utils.logging_utils import get_logger_app
from azureml.acft.accelerator.utils.error_handling.exceptions import ValidationException
from azureml.acft.accelerator.utils.error_handling.error_definitions import InvalidDataset, InvalidLabel
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore

from transformers.tokenization_utils_base import PreTrainedTokenizerBase

from torchvision import transforms
import numpy as np
import random


from typing import Any, Dict, List


logger = get_logger_app()


def str2bool(arg):
    """String to boolean conversion function."""
    if not arg:
        return False
    arg = arg.lower()
    if arg in ["true", "1"]:
        return True
    elif arg in ["false", "0"]:
        return False
    else:
        raise ValueError(f"Invalid argument {arg} to while converting string to boolean")


class StableDiffusionPreprocessForFinetune:
    """Stable Diffusion Preprocess for Finetune component."""
    def __init__(self, component_args: Namespace, preprocess_args: StableDiffusionPreprocessArgs) -> None:
        """Stable Diffusion Preprocess for Finetune component."""
        # component args is combined args of
        #  - preprocess component args
        #  - model_name arg from model selector
        #  - newly constructed model_name_or_path
        self.component_args = component_args
        self.preprocess_args = preprocess_args

        logger.info(f"Task name: {Tasks.STABLE_DIFFUSION}")

        self.model_type = (
            None  # AzuremlAutoConfig.get_model_type(hf_model_name_or_path=component_args.model_name_or_path)
        )
        logger.info(self.preprocess_args)

        self.tokenizer = self._init_tokenizer()

    def _init_tokenizer(self) -> PreTrainedTokenizerBase:
        """Initialize the tokenizer and set the model max length for the tokenizer if not already set"""

        tokenizer_params = {
            "task_name": Tasks.STABLE_DIFFUSION,
            "apply_adjust": True,
            "revision": self.preprocess_args.revision,
        }

        return AzuremlCLIPTokenizer.from_pretrained(self.component_args.model_name_or_path, **tokenizer_params)

    @staticmethod
    def preprocess_train_data(
        examples: Dict[str, Any], image_column: str = "image", caption_column: str = "text", **kwargs
    ) -> Dict[str, Any]:
        """Preprocess the training data for stable diffusion task."""
        # Preprocessing the datasets.
        # We need to tokenize input captions and transform the images.
        def tokenize_captions(is_train=True):
            captions = []
            for caption in examples[caption_column]:
                if isinstance(caption, str):
                    captions.append(caption)
                elif isinstance(caption, (List, np.ndarray)):
                    # take a random caption if there are multiple
                    captions.append(random.choice(caption) if is_train else caption[0])
                else:
                    raise ValueError(
                        f"Caption column `{caption_column}` should contain either strings or lists of strings."
                    )
            inputs = tokenizer(
                captions,
                max_length=tokenizer.model_max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            return inputs.input_ids

        # Preprocessing the datasets.
        resolution = int(kwargs["resolution"])
        center_crop = str2bool(kwargs["center_crop"])
        random_flip = str2bool(kwargs["random_flip"])
        tokenizer = kwargs["tokenizer"]
        # logger.info(f"Resolution: {resolution} | dtype: {type(resolution)}")
        train_transforms = transforms.Compose(
            [
                transforms.Resize(resolution, interpolation=transforms.InterpolationMode.BILINEAR),
                transforms.CenterCrop(resolution) if center_crop else transforms.RandomCrop(resolution),
                transforms.RandomHorizontalFlip() if random_flip else transforms.Lambda(lambda x: x),
                transforms.ToTensor(),
                transforms.Normalize([0.5], [0.5]),
            ]
        )
        images = [image.convert("RGB") for image in examples[image_column]]
        examples["pixel_values"] = [train_transforms(image) for image in images]
        examples["input_ids"] = tokenize_captions()
        return examples

    def preprocess(self) -> None:
        """
        Preprocess the raw dataset
        """

        # load, validate and encode the datasets are handled in finetune component

        # Save
        # 1. Arguments
        # 2. tokenizer
        # 3. mlflow inference data

        # 1. Arguments: save the preprocess args, model_type, encoded datasets
        preprocess_args = vars(self.component_args)
        preprocess_args.update(vars(self.preprocess_args))
        # add the model path
        preprocess_args["model_type"] = self.model_type
        preprocess_args_save_path = Path(self.component_args.output_dir, SaveFileConstants.PREPROCESS_ARGS_SAVE_PATH)
        preprocess_args["model_name_or_path"] = str(preprocess_args["model_name_or_path"])
        logger.info(f"Saving the preprocess args to {preprocess_args_save_path}")
        with open(preprocess_args_save_path, "w") as fp:
            json.dump(preprocess_args, fp, indent=2)

        # 2. tokenizer
        self.tokenizer.save_pretrained(str(Path.joinpath(Path(self.component_args.output_dir, "tokenizer"))))

        # 3. save the mlflow inference params
        # TODO - Add MlFlow params
        # save_key = MLFlowHFFlavourConstants.INFERENCE_PARAMS_SAVE_KEY
        # save_data = {
        #     save_key: self.encode_params
        # }
        # mlflow_inference_params_save_path = Path(
        #     self.component_args.output_dir, MLFlowHFFlavourConstants.INFERENCE_PARAMS_SAVE_NAME_WITH_EXT)
        # logger.info(f"Saving the mlflow inference params at {mlflow_inference_params_save_path}")
        # with open(mlflow_inference_params_save_path, 'w') as wptr:
        #     json.dump(save_data, wptr)
