# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Mlflow PythonModel wrapper class that loads the Mlflow model, preprocess inputs and performs inference."""

import logging
import subprocess
import sys
import tempfile
import math

import mlflow
import pandas as pd
import torch
from transformers import TrainingArguments
from common_constants import (HFMiscellaneousLiterals,
                              HFConstants, Tasks,
                              MMDetLiterals,
                              MLFlowSchemaLiterals)
from common_utils import process_video, create_temp_file, get_current_device

logger = logging.getLogger(__name__)


class ImagesMLFlowModelWrapper(mlflow.pyfunc.PythonModel):
    """MLFlow model wrapper for AutoML for Images models."""

    def __init__(
        self,
        task_type: str,
    ) -> None:
        """This method is called when the python model wrapper is initialized.

        :param task_type: Task type used in training.
        :type task_type: str
        """
        super().__init__()
        self.test_args = None
        self.test_transforms = None
        self.mmtrack_run_inference_batch = None
        self._config = None
        self._model = None
        self._task_type = task_type

    def load_context(self, context: mlflow.pyfunc.PythonModelContext) -> None:
        """This method is called when loading a Mlflow model with pyfunc.load_model().

        :param context: Mlflow context containing artifacts that the model can use for inference.
        :type context: mlflow.pyfunc.PythonModelContext
        """
        logger.info("Inside load_context()")

        if self._task_type in [Tasks.MM_MULTI_OBJECT_TRACKING]:
            """
            Install mmtrack, mmcv and mmdet using mim, with pip installation is not working
            1. for mmtrack, one of its dependency is mmcv 1.6.2, which will trigger cuda related issues.
                to mitigate, we use no dependency install for mmtrack, and put other dependencies in pip requirement
            2. for opencv, the default installed by mmcv is opencv-python. however, it's installing unwanted UI,
                which causes problems for stability. thus we force reinstall opencv-python-headless.
            3. for numpy, we are reinstalling numpy to older version to be compatible to opencv. more info:
                https://stackoverflow.com/questions/20518632/importerror-numpy-core-multiarray-failed-to-import
            """
            subprocess.check_call([sys.executable, "-m", "mim", "install", "mmcv-full==1.7.1"])
            subprocess.check_call([sys.executable, "-m", "mim", "install", "mmdet==2.28.2"])
            subprocess.check_call([sys.executable, "-m", "mim", "install", "--no-deps", "mmtrack==0.14.0"])
            subprocess.check_call([sys.executable, "-m", "pip", "install",
                                   "opencv-python-headless==4.7.0.72", "--force-reinstall"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.19.3", "--force-reinstall"])

            # importing mmdet/mmcv after installing using mim
            from mmtrack.apis import init_model
            from mmcv import Config
            from mmcv.runner import load_checkpoint
            from mmdet.datasets.pipelines import Compose
            from mmtrack_module import MultiObjectTrackingModelWrapper
            from mmtrack_utils import mmtrack_run_inference_batch
            self.mmtrack_run_inference_batch = mmtrack_run_inference_batch

            try:
                model_config_path = context.artifacts[MMDetLiterals.CONFIG_PATH]
                model_weights_path = context.artifacts[MMDetLiterals.WEIGHTS_PATH]
                self._config = Config.fromfile(model_config_path)
                self._model = init_model(self._config)
                if self._task_type == Tasks.MM_MULTI_OBJECT_TRACKING:
                    self._model = MultiObjectTrackingModelWrapper(self._model, self._config, model_weights_path)
                load_checkpoint(self._model, model_weights_path, map_location=get_current_device())
                logger.info("Model loaded successfully")
            except Exception:
                logger.warning("Failed to load the the model.")
                raise

            test_pipeline = self._config.data.test.pipeline
            test_pipeline[0].type = 'LoadImageFromWebcam'
            self.test_transforms = Compose(test_pipeline)
        else:
            raise ValueError(f"invalid task type {self._task_type}."
                             f"Supported tasks: {Tasks.MM_MULTI_OBJECT_TRACKING}")

    def predict(
        self, context: mlflow.pyfunc.PythonModelContext, input_data: pd.DataFrame
    ) -> pd.DataFrame:
        """This method performs inference on the input data.

        :param context: Mlflow context containing artifacts that the model can use for inference.
        :type context: mlflow.pyfunc.PythonModelContext
        :param input_data: Input images for prediction.
        :type input_data: Pandas DataFrame with a first column name ["image"] of images where each
        image is in base64 String format.
        :return: Output of inferencing
        :rtype: Pandas DataFrame with columns ["probs", "labels"] for classification and
        ["boxes"] for object detection, instance segmentation
        """
        task = self._task_type
        logger.info(f"evaluating with batch_size: {1}")

        # arguments for Trainer
        test_args = TrainingArguments(
            output_dir=".",
            do_train=False,
            do_predict=True,
            per_device_eval_batch_size=1,
            dataloader_num_workers=HFConstants.DEFAULT_DATALOADER_NUM_WORKERS,
            dataloader_drop_last=False,
            remove_unused_columns=False
        )

        # process the videos in video column
        processed_videos = input_data.loc[:, [MLFlowSchemaLiterals.INPUT_COLUMN_VIDEO]]\
            .apply(axis=1, func=process_video)

        result = self.mmtrack_run_inference_batch(
            test_args=test_args,
            model=self._model,
            id2label=self._config[HFMiscellaneousLiterals.ID2LABEL],
            processed_videos=processed_videos,
            task_type=task,
            test_transforms=self.test_transforms,
        )

        return pd.DataFrame(result)
