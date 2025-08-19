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

"""AzureML ACFT Image Components package - finetuning component interfaces."""

import torch.nn as nn

from abc import ABC
from datasets import Dataset as DatasetsDataset
from torch.utils.data import Dataset as TorchDataset, IterableDataset as TorchIterableDataset
from transformers import PreTrainedTokenizerBase, TrainerCallback, PreTrainedModel
from typing import Union, Callable, Dict, Any, List, Tuple


class AzmlPreprocessInterface(ABC):
    """Interface for preprocessing the input data"""

    def preprocess(self) -> None:
        """Process and encode the input data"""
        pass

    def find_classes(
        self,
        train_file_path_or_data: Union[str, DatasetsDataset],
        validation_file_path_or_data: Union[str, DatasetsDataset]
    ) -> List[str]:
        """Identify and save the class names from train and validation files"""
        pass

    def copy_meta_data_files(self) -> None:
        """
        [Optional] Since the preprocessing for video datasets happen dynamically, the meta data files
        needs to be available during finetuning

        This function should implement the logic of copying the input metadata files to output directory
        """
        pass


class AzmlFinetuneInterface(ABC):
    """Interface for finetuning the model"""
    def get_finetune_args(self) -> Dict[str, Any]:
        """
        Args and Trainer args for finetune

        def sample_get_finetune_args():

            # ft args
            custom_ft_args = {}
            class_names_load_path = <file saved at end of preprocessing>
            with open(class_names_load_path, 'r') as rptr:
                custom_finetune_args["class_names"] = json.load(rptr)
                custom_finetune_args["num_labels"] = len(custom_finetune_args["class_names"])


            return custom_ft_args
        """
        pass

    def get_custom_trainer_functions(self) -> Dict[str, Callable]:
        """
        Customizable methods for trainer class

        1. train sampler
            from torch.utils.data import Sampler
            def custom_train_sampler(train_dataset: Dataset, world_size: int) -> Sampler:
                ...
        2. validation sampler
            from torch.utils.data import Sampler
            def custom_validation_sampler(eval_dataset: Dataset, world_size: int) -> Sampler:
                ...
        3. optimizer
            def custom_optimizer(model: Union[PreTrainedModel, nn.Module], **kwargs):
                # kwargs are optimizer args
                ...

        return value sample
        ===================
        from ..constants.constants import HfTrainerMethodsConstants
        return {
            'HfTrainerMethodsConstants.AzmlTrainSampler': custom_train_sampler,
            ...
        }

        """
        pass


class AzmlInferenceInterface(ABC):
    """Interface for inference"""
    def get_inference_args(self) -> Dict[str, Any]:
        """
        Args and Trainer args for inference

        def sample_get_inference_args():

            # inference args
            custom_inference_args = {}
            class_names_load_path = <file saved at end of preprocessing>
            with open(class_names_load_path, 'r') as rptr:
                custom_finetune_args["class_names"] = json.load(rptr)
                custom_finetune_args["num_labels"] = len(custom_finetune_args["class_names"])

            # trainer args
            custom_trainer_args = {'remove_unused_columns': False}

            return custom_inference_args, custom_trainer_args
        """
        pass

    def get_custom_trainer_functions(self) -> Dict[str, Callable]:
        """
        Customizable methods for trainer class

        1. train sampler
            from torch.utils.data import Sampler
            def custom_train_sampler(train_dataset: Dataset, world_size: int) -> Sampler:
                ...
        2. validation sampler
            from torch.utils.data import Sampler
            def custom_validation_sampler(eval_dataset: Dataset, world_size: int) -> Sampler:
                ...
        3. optimizer
            def custom_optimizer(model: Union[PreTrainedModel, nn.Module], **kwargs):
                # kwargs are optimizer args
                ...

        return value sample
        ===================
        from ..constants.constants import HfTrainerMethodsConstants
        return {
            'HfTrainerMethodsConstants.AzmlTrainSampler': custom_train_sampler,
            ...
        }

        """
        pass


class AzmlDataInterface(ABC):
    """Interface for data"""
    def get_train_dataset(self) -> Union[TorchDataset, TorchIterableDataset, DatasetsDataset]:
        """Train dataset example for DatasetsDataset

        from datasets import load_dataset
        file_format = "json"
        train_file_jsonl = "train.jsonl"
        remove_columns = ["list", "of", "columns", "to", "remove"]
        train_ds = load_dataset(file_format, data_files={'tmp': train_file_jsonl}, split="tmp",
                                remove_columns=remove_columns)
        """
        pass

    def get_validation_dataset(self) -> Union[TorchDataset, TorchIterableDataset, DatasetsDataset]:
        """Validation dataset for DatasetsDataset

        from datasets import load_dataset
        file_format = "json"
        validation_file_jsonl = "train.jsonl"
        remove_columns = ["list", "of", "columns", "to", "remove"]
        valid_ds = load_dataset(file_format, data_files={'tmp': validation_file_jsonl}, split="tmp",
                                remove_columns=remove_columns)
        """
        pass

    def get_test_dataset(self) -> Union[TorchDataset, TorchIterableDataset, DatasetsDataset]:
        """Test dataset for DatasetsDataset

        from datasets import load_dataset
        file_format = "json"
        test_file_jsonl = "train.jsonl"
        remove_columns = ["list", "of", "columns", "to", "remove"]
        test_ds = load_dataset(file_format, data_files={'tmp': test_file_jsonl}, split="tmp",
                               remove_columns=remove_columns)
        """
        pass

    def get_collation_function(self) -> Callable:
        """
        Collation function

        Sample collator function for video classification
        -------------------------------------------------
        Say model forward expectes `pixel_values` and `labels` in the collated examples

        import torch
        examples_batch = [{'pixel_values': np.ndarray, 'label': int}, ...]
        def sample_collator_func(examples_batch):
            # collate all the examples in the batch
            pixel_values = torch.stack([example['pixel_values'] for example in examples_batch])
            if label in examples_batch[0]:
                # format the label column
                labels = ...
                return {'pixel_values': pixel_values, 'labels': labels}
            else:
                # test dataset might not contain the label column
                return {'pixel_values': pixel_values}
        """
        pass


class AzmlTokenizerInterface(ABC):
    """Interface for tokenizer."""
    @classmethod
    def from_pretrained(cls, model_name_or_path: str, **kwargs) -> PreTrainedTokenizerBase:
        """
        Use a custom name for `model_name_or_path` so that the name won't conflict with the
        existing set of variables in kwargs

        For instance if the onboarded model family is `nebula`, a better signature for `from_pretrained` could be
            def from_pretrained(cls, nebula_model_name_or_path, **kwargs):
                ...
        """
        pass

    def save_pretrained(self, **kwargs) -> None:
        """
        The `save_pretrained` is already implemented for HF models but if you are writing a custom model,
        this function needs to be implemented mandatorily

        This function should contain the logic of saving the already loaded tokenizer
        """
        pass


class AzmlTextEncoderInterface(ABC):
    """Interface for text enocder."""
    @classmethod
    def from_pretrained(cls, model_name_or_path: str, **kwargs) -> PreTrainedTokenizerBase:
        """
        Use a custom name for `model_name_or_path` so that the name won't conflict with the
        existing set of variables in kwargs

        For instance if the onboarded model family is `nebula`, a better signature for `from_pretrained` could be
            def from_pretrained(cls, nebula_model_name_or_path, **kwargs):
                ...
        """
        pass

    def save_pretrained(self, **kwargs) -> None:
        """
        The `save_pretrained` is already implemented for HF models but if you are writing a custom model,
        this function needs to be implemented mandatorily

        This function should contain the logic of saving the already loaded tokenizer
        """
        pass


class AzmlModelInterface(ABC):
    """Interface for model."""
    @classmethod
    def from_pretrained(cls, model_name_or_path: str, **kwargs) -> Union[PreTrainedModel, nn.Module]:
        """
        Use a custom name for `model_name_or_path` so that the name won't conflict with the
        existing set of variables in kwargs

        For instance if the onboarded model family is `nebula`, a better signature for `from_pretrained` could be
            def from_pretrained(cls, nebula_model_name_or_path, **kwargs):
                ...
        """
        pass

    def save_pretrained(self, **kwargs) -> None:
        """
        The `save_pretrained` is already implemented for HF models but if you are writing a custom model,
        this function needs to be implemented mandatorily

        This function should contain the logic of saving the finetuned model
        """
        pass


# NOTE Using normal classes instead of dataclasses to have mutable object for class variables
class AzmlTrainerClassesInterface:
    """Interface for trainer classes."""

    def __init__(self) -> None:
        """Initialize trainer classes"""

        self.preprocess_cls: AzmlPreprocessInterface = None
        self.finetune_cls: AzmlFinetuneInterface = None
        self.inference_cls: AzmlInferenceInterface = None
        self.text_encoder_cls: AzmlTextEncoderInterface = None
        self.data_cls: AzmlDataInterface = None
        self.tokenizer_cls: AzmlTokenizerInterface = None
        self.model_cls: AzmlModelInterface = None
        self.callbacks: List[TrainerCallback] = []
        self.metrics_function: Callable = None
        self.predict_function: Callable = None
