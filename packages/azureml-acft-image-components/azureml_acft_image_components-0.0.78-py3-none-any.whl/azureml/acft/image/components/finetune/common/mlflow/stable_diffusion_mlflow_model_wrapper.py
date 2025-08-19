# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Contains MLFlow pyfunc wrapper for stable diffusion models.

Has methods to load the model and predict.
"""

from diffusers import StableDiffusionPipeline
import mlflow
import yaml
import os
import pandas as pd
from peft import PeftModel
import torch
from typing import Optional, Any, Dict, List
from stable_diffusion_modules import AzuremlStableDiffusionPipeline
from common_constants import (
    Tasks,
    MLflowLiterals,
    MLFlowSchemaLiterals,
    DatatypeLiterals,
    MLflowMetadataLiterals,
    SDLiterals,
    TrainingLiterals,
)
from common_utils import image_to_base64, get_sd_scheduler_type, save_image


class StableDiffusionMLflowWrapper(mlflow.pyfunc.PythonModel):
    """MLflow model wrapper for stable diffusion models."""

    def __init__(self, task_type: str) -> None:
        """Initialize model parameters for converting Huggingface StableDifusion model to mlflow.

        :param task_type: Task type used in training.
        :type task_type: str
        """
        super().__init__()
        self._pipe = None
        self.batch_output_folder = None
        self._task_type = task_type

    def load_context(self, context: mlflow.pyfunc.PythonModelContext) -> None:
        """
        Load a MLflow model with pyfunc.load_model().

        :param context: MLflow context containing artifacts that the model can use for inference
        :type context: mlflow.pyfunc.PythonModelContext
        """

        self.batch_output_folder = os.getenv(TrainingLiterals.BATCH_OUTPUT_PATH, default=False)
        self.fp16_inference = os.getenv(TrainingLiterals.FP16_INFERENCE, default=False)
        torch_dtype = torch.float16 if self.fp16_inference else torch.float32
        if self._task_type == Tasks.HF_SD_TEXT_TO_IMAGE:
            try:
                _map_location = "cuda" if torch.cuda.is_available() else "cpu"
                model_dir = context.artifacts[MLflowLiterals.MODEL_DIR]
                mlmodel_path = os.path.join(os.path.dirname(os.path.dirname(model_dir)), MLflowLiterals.MODEL_FILE)
                with open(mlmodel_path, "r") as file:
                    mlmodel_data = yaml.safe_load(file)
                model_metadata = mlmodel_data[MLflowMetadataLiterals.METADATA]
                self.apply_lora = model_metadata.get(MLflowMetadataLiterals.APPLY_LORA, False)
                if self.apply_lora:
                    # only lora weights are saved in mlflow model, download base model and merge weights
                    self.base_model_name = model_metadata.get(MLflowMetadataLiterals.BASE_MODEL_NAME)
                    self.scheduler_path = os.path.join(model_dir, SDLiterals.SCHEDULER)
                    self.scheduler_type = get_sd_scheduler_type(self.scheduler_path)
                    # load base model from hugging face and provide scheduler from saved finetuned configs
                    base_model = AzuremlStableDiffusionPipeline.from_pretrained(
                        self.base_model_name, scheduler_type=self.scheduler_type, scheduler_path=self.scheduler_path
                    )
                    model = PeftModel.from_pretrained(base_model, model_dir, device_map="auto")
                    model = model.merge_and_unload()
                    print("Merged base model and adapter weights successfully.")

                    self._pipe = StableDiffusionPipeline.from_pretrained(
                        self.base_model_name,
                        unet=model.unet,
                        text_encoder=model.text_encoder,
                        scheduler=model.noise_scheduler,
                        torch_dtype=torch_dtype,
                    )
                else:
                    self._pipe = StableDiffusionPipeline.from_pretrained(model_dir, torch_dtype=torch_dtype)
                self._pipe.to(_map_location)
                print("Model loaded successfully")
            except Exception as e:
                print("Failed to load the the model.")
                print(e)
                raise
        else:
            raise ValueError(f"invalid task type {self._task_type}")

    def predict(
        self,
        context: mlflow.pyfunc.PythonModelContext,
        input_data: pd.DataFrame,
        params: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """
        Perform inference on the input data.

        :param context: MLflow context containing artifacts that the model can use for inference
        :type context: mlflow.pyfunc.PythonModelContext
        :param input_data: Pandas DataFrame with a column name ["prompt"] having text
                           input for which image has to be generated.
        :type input_data: pd.DataFrame
        :return: Pandas dataframe with input text prompts, their corresponding generated images and NSFW flag.
                 Images in form of base64 string.
        :param params: Additional parameters for inference.
        :type params: Optional[Dict[str, Any]]
        :rtype: pd.DataFrame
        """
        text_prompts = input_data[MLFlowSchemaLiterals.INPUT_COLUMN_PROMPT].tolist()
        params[SDLiterals.NEGATIVE_PROMPT] = (
            None if params[SDLiterals.NEGATIVE_PROMPT] == "" else params[SDLiterals.NEGATIVE_PROMPT]
        )
        num_images_per_prompt = (
            params[SDLiterals.NUM_IMAGES_PER_PROMPT] if SDLiterals.NUM_IMAGES_PER_PROMPT in params else 1
        )
        if self.batch_output_folder:
            # Batch endpoint
            return self.predict_batch(text_prompts, **params)
        output = self._pipe(text_prompts, **params)
        generated_images = []
        text_prompts_extended = []
        for idx, img in enumerate(output.images):
            generated_images.append(image_to_base64(img, format=DatatypeLiterals.IMAGE_FORMAT))
            text_prompts_extended.append(text_prompts[idx // num_images_per_prompt])

        nsfw_content = None
        if hasattr(output, MLFlowSchemaLiterals.OUTPUT_COLUMN_NSFW_FLAG):
            nsfw_content = output.nsfw_content_detected

        df = pd.DataFrame(
            {
                MLFlowSchemaLiterals.INPUT_COLUMN_PROMPT: text_prompts_extended,
                MLFlowSchemaLiterals.OUTPUT_COLUMN_IMAGE: generated_images,
                MLFlowSchemaLiterals.OUTPUT_COLUMN_NSFW_FLAG: nsfw_content,
            }
        )

        return df

    def predict_batch(self, text_prompts: List[str], params: Optional[Dict[str, Any]]) -> pd.DataFrame:
        """
        Perform batch inference on the input data.

        :param text_prompts: A list of text prompts for which we need to generate images.
        :type text_prompts: list
        :param params: Additional parameters for inference.
        :type params: Optional[Dict[str, Any]]
        :return: Pandas dataframe having generated images and NSFW flag. Images in form of base64 string.
        :rtype: pandas.DataFrame
        """
        generated_images = []
        nsfw_content_detected = []
        text_prompts_extended = []
        for text_prompt in text_prompts:
            output = self._pipe(text_prompt, **params)
            for idx, img in enumerate(output.images):
                generated_images.append(save_image(self.batch_output_folder, img, DatatypeLiterals.IMAGE_FORMAT))
                text_prompts_extended.append(text_prompt)
                nsfw_content = output.nsfw_content_detected[idx] if output.nsfw_content_detected else None
                nsfw_content_detected.append(nsfw_content)

        df = pd.DataFrame(
            {
                MLFlowSchemaLiterals.INPUT_COLUMN_PROMPT: text_prompts_extended,
                MLFlowSchemaLiterals.OUTPUT_COLUMN_IMAGE: generated_images,
                MLFlowSchemaLiterals.OUTPUT_COLUMN_NSFW_FLAG: nsfw_content_detected,
            }
        )

        return df
