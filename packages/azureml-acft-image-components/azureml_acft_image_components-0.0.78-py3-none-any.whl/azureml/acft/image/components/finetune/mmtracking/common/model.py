# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2018-2023 OpenMMLab. All rights reserved.
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

"""MMTrackingn model related classes."""

from __future__ import annotations
from typing import Dict, Any, List

from mmcv import Config
from mmcv.runner import load_checkpoint
from mmtrack.apis import init_model
from torch import nn

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals,
    InferenceParameters,
)
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.mmtracking.common.constants import (
    MmTrackingConfigLiterals,
)

from azureml.acft.image.components.finetune.mmtracking.mot.model_wrapper import (
    MultiObjectTrackingModelWrapper,
)
from azureml.acft.image.components.finetune.interfaces.azml_interface import (
    AzmlModelInterface,
)
from azureml.acft.image.components.finetune.mmdetection.common.model import (
    DetectionConfigBuilder, DetectionModel,
)
from azureml.metrics.constants import Tasks as MetricsTasks
from azureml.acft.image.components.model_selector.constants import ImageModelSelectorConstants

logger = get_logger_app(__name__)


class TrackingConfigBuilder(DetectionConfigBuilder):
    """ Builder class to build the MM Tracking config."""
    def __init__(self, config_file_path):
        """ Builder class to build the MM Tracking config.
        :param config_file_path: parameters used for inference
        :type config_file_path: str
        """
        super().__init__(config_file_path)

    def set_num_labels(self, num_labels: int) -> TrackingConfigBuilder:
        """
        Set number of labels/ classes in the model config
        :param num_labels: number of labels
        :type num_labels: int
        :return: config builder
        :rtype: TrackingConfigBuilder
        """
        if num_labels > 0:
            self._find_key_and_set_value(
                self.config.model,
                MmTrackingConfigLiterals.NUM_CLASSES,
                num_labels,
                stack=["model"],
            )
        return self

    def set_box_scoring_threshold(
        self, box_score_threshold: float
    ) -> TrackingConfigBuilder:
        """
        Set box scoring threshold in the model config
        :param box_score_threshold: threshold for bounding box score
        :type box_score_threshold: float
        :return: config builder
        :rtype: TrackingConfigBuilder
        """
        try:
            self._find_key_and_set_value(
                self.config.model.detector.test_cfg,
                MmTrackingConfigLiterals.BOX_SCORE_THRESHOLD,
                box_score_threshold,
                stack=["model", "test_cfg"],
            )
        except Exception as ex:
            logger.warning(
                f"Exception {ex} when calling set_box_scoring_threshold. "
            )
            # If test_cfg or score_threshold is not present in config, then this thresholding
            # is handled while calculating the metrics.
        return self

    def set_image_scale(
        self, img_scale: tuple
    ) -> TrackingConfigBuilder:
        """
        Set img_scale threshold in the model config
        :param img_scale: image scale
        :type img_scale: tuple of int
        :return: config builder
        :rtype: TrackingConfigBuilder
        """
        if img_scale == (-1, -1):
            return self
        self._find_key_and_set_value(
            self.config.model,
            MmTrackingConfigLiterals.INPUT_SIZE,
            img_scale,
            stack=["model"],
        )
        self._find_key_and_set_value(
            self.config.data,
            MmTrackingConfigLiterals.IMAGE_SCALE,
            img_scale,
            stack=["data"],
        )
        return self


class TrackingModel(AzmlModelInterface):
    """MM Tracking models."""
    def from_pretrained(self, model_name_or_path: str, **kwargs) -> nn.Module:
        """ Load the model config and weights if weight path specified.
        :param model_name_or_path: parameters used for inference
        :type model_name_or_path: str
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        :return: MM Tracking model
        :rtype: nn.Module
        """
        model_weights_path = kwargs.get(ImageModelSelectorConstants.MMLAB_MODEL_WEIGHTS_PATH_OR_URL, None)
        task_name = kwargs.get(SettingLiterals.TASK_NAME, Tasks.MM_MULTI_OBJECT_TRACKING)
        num_labels = kwargs.get(SettingLiterals.NUM_LABELS, 0)
        box_score_threshold = kwargs.get(
            SettingLiterals.BOX_SCORE_THRESHOLD,
            InferenceParameters.DEFAULT_BOX_SCORE_THRESHOLD,
        )
        image_width = kwargs.get(SettingLiterals.IMAGE_WIDTH)
        image_height = kwargs.get(SettingLiterals.IMAGE_HEIGHT)
        iou_threshold = kwargs.get(SettingLiterals.IOU_THRESHOLD,
                                   InferenceParameters.DEFAULT_IOU_THRESHOLD)
        config = (
            TrackingConfigBuilder(model_name_or_path)
            .set_num_labels(num_labels)
            .set_box_scoring_threshold(box_score_threshold)
            .set_image_scale((image_width, image_height))
            .build()
        )

        # copy the label2id mapping from kwargs to config. To be used in mlflow export
        config.id2label = kwargs.get(SettingLiterals.ID2LABEL, None)
        model_meta_file_path = kwargs.get(ImageModelSelectorConstants.MMLAB_MODEL_METAFILE_PATH)
        model = init_model(config)
        logger.info(f"Successfully loaded model config and with {num_labels} labels.")
        if model_weights_path:
            load_checkpoint(model, model_weights_path)
            logger.info(f"Successfully loaded model weight from {model_weights_path}.")

        model_wrapper = None
        if task_name == Tasks.MM_MULTI_OBJECT_TRACKING:
            model_wrapper = MultiObjectTrackingModelWrapper(
                model, config, model_name_or_path,
                task_type=MetricsTasks.VIDEO_MULTI_OBJECT_TRACKING,
                num_labels=num_labels, box_score_threshold=box_score_threshold,
                iou_threshold=iou_threshold,
                meta_file_path=model_meta_file_path
            )
        return model_wrapper
