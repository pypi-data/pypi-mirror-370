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
"""Finetune component for Stable Diffusion"""

import json
from pathlib import Path
from typing import Any, Union, Dict, List, Optional, Tuple
from functools import partial

import torch
import torch.nn as nn
from torchvision import transforms

from azureml.acft.accelerator.finetune import AzuremlFinetuneArgs, AzuremlDatasetArgs
from azureml.acft.accelerator.finetune import AzuremlTrainer
from azureml.acft.accelerator.constants import HfTrainerType
from azureml.acft.common_components.model_selector.constants import ModelSelectorConstants

from ..preprocess.base import StableDiffusionDataset
from ..preprocess.preprocess_for_finetune import StableDiffusionPreprocessForFinetune
from ....diffusion_auto.tokenizer import AzuremlCLIPTokenizer
from ....diffusion_auto.model import AzuremlStableDiffusionPipeline
from ....constants.constants import SaveFileConstants, MLFlowHFFlavourConstants, Tasks
from ....utils.mlflow_utils import SaveMLflowModelCallback

from transformers import PreTrainedTokenizerBase

from azureml.acft.accelerator.finetune import get_logger_app


logger = get_logger_app(name="Stable Diffusion Logger")


class StableDiffusionFinetune:
    """Stable Diffusion Finetune class to handle the finetune related operations"""
    def __init__(self, finetune_params: Dict[str, Any]) -> None:
        """Stable Diffusion Finetune class to handle the finetune related operations"""
        # finetune params is finetune component args + args saved as part of preprocess
        self.finetune_params = finetune_params

        logger.info(f"Task name: {Tasks.STABLE_DIFFUSION}")

        self.finetune_params["remove_unused_columns"] = False
        self.finetune_params["label_names"] = ["pixel_values"]

        # set log_metrics_at_root=False to not to log to parent
        self.finetune_params["log_metrics_at_root"] = False

        # if :param `resume_from_checkpoint` is set to True
        #   - only load the weights using config while creating model object
        #   - update the `resume_from_checkpoint` to the model_name_or_path to load the model, and optimizer and
        #     scheduler states if exist
        if (
            self.finetune_params.pop("resume_from_checkpoint", False)
            and isinstance(self.finetune_params["model_name_or_path"], Path)
            and self.finetune_params["model_name_or_path"].is_dir()
        ):
            self.finetune_params["resume_from_checkpoint"] = self.finetune_params["model_name_or_path"]

    def _get_finetune_args(self, model_type: Optional[str] = None) -> AzuremlFinetuneArgs:
        self.finetune_params["model_type"] = model_type
        azml_trainer_finetune_args = AzuremlFinetuneArgs(
            self.finetune_params,
            trainer_type=HfTrainerType.DEFAULT,
        )

        return azml_trainer_finetune_args

    def _load_dataset(
        self,
        path_or_dict: Union[str, Path],
        tokenizer: Optional[PreTrainedTokenizerBase] = None,
        dataset_split_kwargs: Optional[Dict[str, Any]] = None,
    ):
        stablediffusion_ds = StableDiffusionDataset(path_or_dict, tokenizer=tokenizer)
        new_ds = stablediffusion_ds.dataset.with_transform(
            partial(
                StableDiffusionPreprocessForFinetune.preprocess_train_data,
                **self.finetune_params,
                dataset_split_kwargs=dataset_split_kwargs,
            )
        )
        stablediffusion_ds.dataset = new_ds
        return stablediffusion_ds

    def _get_dataset_args(self, tokenizer: Optional[PreTrainedTokenizerBase] = None) -> AzuremlDatasetArgs:
        self.finetune_params["tokenizer"] = tokenizer

        # set dataset split args
        train_dataset_split_kwargs = None
        validation_dataset_split_kwargs = None

        if not self.finetune_params["validation_data_path"]:
            self.finetune_params["validation_data_path"] = self.finetune_params["train_data_path"]
            train_dataset_split_kwargs = {
                "train_size": 1 - self.finetune_params["validation_split"],
                "shuffle": False,
            }
            validation_dataset_split_kwargs = {
                "test_size": self.finetune_params["validation_split"],
                "shuffle": False,
            }

        train_ds = self._load_dataset(
            Path(self.finetune_params["train_data_path"]),
            tokenizer=tokenizer,
            dataset_split_kwargs=train_dataset_split_kwargs,
        )
        validation_ds = self._load_dataset(
            Path(self.finetune_params["validation_data_path"]),
            tokenizer=tokenizer,
            dataset_split_kwargs=validation_dataset_split_kwargs,
        )
        azml_trainer_dataset_args = AzuremlDatasetArgs(
            train_dataset=train_ds.dataset,
            validation_dataset=validation_ds.dataset,
            data_collator=train_ds.get_collation_function(),
        )

        return azml_trainer_dataset_args

    def _load_model(self) -> Tuple[nn.Module, Union[str, None], Union[List[str], None]]:
        model_params = {
            "revision": None,
            "non_ema_revision": None,
        }

        model = AzuremlStableDiffusionPipeline.from_pretrained(
            self.finetune_params["model_name_or_path"],
            **model_params,
        )

        model_type = None
        new_initalized_layers = None

        return model, model_type, new_initalized_layers

    def _get_tokenizer(self) -> PreTrainedTokenizerBase:
        """This method loads the tokenizer as is w/o any modifications to it"""

        tokenizer_params = {
            "revision": None,
            # "task_name": self.finetune_params["task_name"],
        }

        return AzuremlCLIPTokenizer.from_pretrained(self.finetune_params["preprocess_output"], **tokenizer_params)

    def finetune(self) -> None:
        """Finetune the model with the given dataset and trainer args"""
        self.finetune_params["model_name_or_path"] = str(self.finetune_params["model_name_or_path"])

        # configure MLflow save callback
        mlflow_infer_params_file_path = Path(
            self.finetune_params["preprocess_output"], MLFlowHFFlavourConstants.INFERENCE_PARAMS_SAVE_NAME_WITH_EXT
        )
        base_model_asset_id = self.finetune_params.get("model_asset_id", None)
        base_model_task = self.finetune_params.get(ModelSelectorConstants.BASE_MODEL_TASK, None)

        save_mlflow_callback = SaveMLflowModelCallback(
            mlflow_infer_params_file_path=mlflow_infer_params_file_path,
            mlflow_model_save_path=self.finetune_params["mlflow_model_folder"],
            mlflow_task_type=self.finetune_params["mlflow_task_type"],
            model_name=self.finetune_params["model_name"],
            model_name_or_path=self.finetune_params["model_name_or_path"],
            base_model_asset_id=base_model_asset_id,
            base_model_task=base_model_task,
            **{"mlflow_ft_conf": self.finetune_params.get("mlflow_ft_conf", {})},
        )

        model, model_type, new_initialized_params = self._load_model()
        tokenizer = self._get_tokenizer()
        trainer = AzuremlTrainer(
            finetune_args=self._get_finetune_args(model_type),
            dataset_args=self._get_dataset_args(tokenizer),
            model=model,
            tokenizer=tokenizer,
            metric_func=None,
            new_initalized_layers=new_initialized_params,
            custom_trainer_callbacks=[save_mlflow_callback],
        )

        # Torch barrier is used to complete the training on a distributed setup
        # Use callbacks for adding steps to be done at the end of training
        # NOTE Avoid adding any logic after trainer.train()
        # Test the distributed scenario in case you add any logic beyond trainer.train()
        trainer.train()

        # save files only once by Rank-0 process
        if trainer.hf_trainer.args.should_save:
            # save finetune args
            Path(self.finetune_params["pytorch_model_folder"]).mkdir(exist_ok=True, parents=True)
            finetune_args_path = Path(
                self.finetune_params["pytorch_model_folder"], SaveFileConstants.FINETUNE_ARGS_SAVE_PATH
            )
            self.finetune_params.pop("tokenizer", None)
            with open(finetune_args_path, "w") as rptr:
                json.dump(self.finetune_params, rptr, indent=2)
