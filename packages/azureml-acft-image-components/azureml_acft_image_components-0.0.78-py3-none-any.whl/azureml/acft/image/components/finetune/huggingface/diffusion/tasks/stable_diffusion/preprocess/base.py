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

"""Base class for stable diffusion preprocess task."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field

from ....constants.constants import AzuremlConstants, PreprocessArgsTemplate
from ....constants.constants import Tasks, MLFlowHFFlavourTasks
from ....constants.constants import STRING_DTYPES

from ....utils.data_utils import AzuremlDataset
from ....utils.validation_utils import AzuremlValidatorMixin

from transformers.tokenization_utils_base import PreTrainedTokenizerBase

from azureml.acft.accelerator.utils.logging_utils import get_logger_app
from azureml.acft.accelerator.utils.error_handling.exceptions import ValidationException
from azureml.acft.accelerator.utils.error_handling.error_definitions import ValidationError
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore

import torch


logger = get_logger_app()


@dataclass
class StableDiffusionPreprocessArgs(PreprocessArgsTemplate):
    """Stable Diffusion Preprocess Args"""
    # Specify the defaults for all new attributes of StableDiffusionPreprocessArgs +
    # inhertied attributes from PreprocessArgsTemplate here.
    # Otherwise, there will be issues related to ordering of default and
    # non-default attributes

    # extra args
    # Makesure the extra args don't overlap with names of PreprocessArgs Template
    image_column: str = field(default="image")
    caption_column: str = field(default="text")
    resolution: Optional[int] = field(default=512)
    center_crop: Optional[str] = field(default=None)
    random_flip: Optional[str] = field(default=None)
    revision: Optional[str] = field(default=None)
    #
    problem_type: Optional[str] = field(default="stable_diffusion")
    task_name: str = field(default=Tasks.STABLE_DIFFUSION)
    placeholder_label_column: str = field(default="caption_column")
    metric_for_best_model: str = field(default="loss")
    greater_is_better: bool = field(default=False)
    mlflow_task_type: str = field(default=MLFlowHFFlavourTasks.STABLE_DIFFUSION)

    def __post_init__(self):
        """Post init function to set the defaults for the mutable arguments"""
        # setting the defaults for mutable arguments will cause issue in case of multiple class
        # initializations. so, placeholders are set here
        self.placeholder_required_columns = ["image_column", "caption_column"]
        self.placeholder_required_column_dtypes = [STRING_DTYPES, STRING_DTYPES]
        #
        if self.placeholder_required_columns is not None:
            for idx, col_name in enumerate(self.placeholder_required_columns):
                decoded_arg = getattr(self, col_name, None)
                if decoded_arg is not None:
                    self.required_columns.append(decoded_arg)
                    self.required_column_dtypes.append(self.placeholder_required_column_dtypes[idx])

        self.label_column = getattr(self, self.placeholder_label_column)


class StableDiffusionDataset(AzuremlDataset, AzuremlValidatorMixin):
    """Stable Diffusion Dataset class to handle the dataset related operations"""
    def __init__(
        self,
        path_or_dict: Union[str, Path],
        dataset_args: Optional[Dict[str, Any]] = None,
        required_columns: Optional[List[str]] = None,
        required_column_dtypes: Optional[List[List[str]]] = None,
        label_column: Optional[str] = None,
        label_column_optional: bool = False,
        # data_format: str = "json",
        tokenizer: Optional[PreTrainedTokenizerBase] = None,
        dataset_split_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Stable Diffusion Dataset class to handle the dataset related operations"""
        # following arguments are needed
        # resolution
        # center_crop
        # randon_flip
        # tokenizer

        # required_columns, required_column_dtypes are made optional to support loading the dataset
        # without the need for validation

        # initialize the dataset class
        super().__init__(
            path_or_dict,
            label_column=label_column,
            label_column_optional=label_column_optional,
            # data_format=data_format,
            dataset_split_kwargs=dataset_split_kwargs,
        )

        # initialze the validator mixin class
        super(AzuremlDataset, self).__init__(
            required_columns=required_columns, required_column_dtypes=required_column_dtypes
        )

        self.dataset_args = dataset_args
        self.tokenizer = tokenizer

    def get_collation_function(self) -> Optional[Callable]:
        """Collation function"""

        def collate_fn(examples):
            pixel_values = torch.stack([example["pixel_values"] for example in examples])
            pixel_values = pixel_values.to(memory_format=torch.contiguous_format).float()
            input_ids = torch.stack([example["input_ids"] for example in examples])
            return {"pixel_values": pixel_values, "input_ids": input_ids}

        return collate_fn

    def update_dataset_columns_with_prefix(self):
        """Update the image_column and caption_column with prefix"""
        if self.dataset_args is not None:
            self.dataset_args["image_column"] = (
                AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["image_column"]
            )
            if self.dataset_args["caption_column"] is not None:
                self.dataset_args["caption_column"] = (
                    AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["caption_column"]
                )

        return super().update_dataset_columns_with_prefix()

    def encode_dataset(self, class_names_train_plus_valid: Optional[List[str]] = None):
        """
        datasets: HuggingFace datasets object
        tokenizer: HuggingFace tokenizer
        kwargs: max_seq_length, pad_to_max_length, sentence1_key, sentence2_key, label_key

        https://github.com/huggingface/notebooks/blob/main/examples/text_classification.ipynb
        """
        pass

    def stable_diffusion_data_filter(self):
        """Remove the examples that contain null data. specific to stable diffusion task"""

        if self.dataset_args is None:
            logger.info(f"Dataset args is {self.dataset_args}. Skipping stable diffusion data filter")
            return

        # apply singlelabel specific data filter
        if self.label_column is None:
            logger.info("label key is not present. skipping stable diffusion specific data filter")
            return

        # filter examples with empty image_column
        # dataset_args is not None at this point
        # filter_lambda = lambda example: (example[self.dataset_args["image_column"]] != "")  # type: ignore
        pre_filter_rows = self.dataset.num_rows
        self.dataset = self.dataset.filter(lambda example: (example[self.dataset_args["image_column"]] != ""))
        post_filter_rows = self.dataset.num_rows
        logger.info(
            f"StableDiffusion data filter | before example count: {pre_filter_rows} |"
            f"after example count: {post_filter_rows}"
        )
        if post_filter_rows == 0:
            raise ValidationException._with_error(
                AzureMLError.create(
                    ValidationError, error=f"Found no examples after data preprocessing for {self.path_or_dict}"
                )
            )

    def validate(self):
        """Validate the dataset"""
        # Remove the extra columns and match the remaining columns
        self.remove_extra_columns()
        self.match_columns()

        # filter data
        # null filter
        self.remove_null_examples()
        # remove examples with empty sentence1 or sentence2
        self.stable_diffusion_data_filter()

        # check dtypes
        self.check_column_dtypes()
