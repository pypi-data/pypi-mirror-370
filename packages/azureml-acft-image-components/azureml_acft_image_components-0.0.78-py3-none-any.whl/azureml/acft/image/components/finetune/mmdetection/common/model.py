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

"""MMDetection model related classes."""

from __future__ import annotations

import torch

from typing import Dict, Any, List

try:
    # mmcv-full under 2.0
    from mmcv import Config
except ImportError:
    # mmcv version >= 2.0
    from mmengine.config import Config
from mmengine.runner import load_checkpoint
from mmdet.apis import init_detector
from torch import nn

from azureml._common._error_definition.azureml_error import AzureMLError

from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTSystemError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTSystemException
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals,
    InferenceParameters,
)
from azureml.acft.image.components.finetune.common.mlflow.common_utils import (
    get_current_device
)
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.mmdetection.common.constants import (
    MmDetectionConfigLiterals,
)
from azureml.acft.image.components.finetune.mmdetection.instance_segmentation.model_wrapper import (
    InstanceSegmentationModelWrapper,
)
from azureml.acft.image.components.finetune.mmdetection.object_detection.model_wrapper import (
    ObjectDetectionModelWrapper,
)
from azureml.acft.image.components.finetune.interfaces.azml_interface import (
    AzmlModelInterface,
)
from azureml.acft.image.components.model_selector.constants import ImageModelSelectorConstants
from azureml.metrics.constants import Tasks as MetricsTasks


logger = get_logger_app(__name__)


class DetectionConfigBuilder:
    """ Builder class to build the MM Detection config."""
    def __init__(self, config_file_path):
        """ Builder class to build the MM Detection config.
        :param config_file_path: parameters used for inference
        :type config_file_path: str
        """
        self.config: Config = Config.fromfile(config_file_path)
        self._flag = False  # Internal flag to track if model config is updated with key-val or not

    def _find_key_and_set_value(
            self, config: Dict, search_field: str, value: Any, stack: List
    ) -> None:
        """
        Recursively find the search field and update it with value in given config dictionary
        :param config: mm detection model configuration
        :type config: Dict
        :param search_field: field to update
        :type search_field: str
        :param value: value to update
        :type value: Any
        :param stack: The stack to maintain the path of the search field
        :type stack: List
        """
        if not isinstance(config, Dict):
            return
        for key in config:
            stack.append(key)
            if isinstance(config[key], dict):
                self._find_key_and_set_value(
                    config[key], search_field, value, stack
                )
            elif isinstance(key, str) and key == search_field:
                config[key] = value
                self._flag = True
                logger.info(f"Setting {value} at {'.'.join(stack)} in config.")
            elif isinstance(config[key], list) or isinstance(config[key], tuple):
                for item in config[key]:
                    self._find_key_and_set_value(
                        item, search_field, value, stack
                    )
            stack.pop()

    def set_num_labels(self, num_labels: int) -> DetectionConfigBuilder:
        """
        Set number of labels/ classes in the model config
        :param num_labels: number of labels
        :type num_labels: int
        :return: config builder
        :rtype: DetectionConfigBuilder
        """
        if num_labels > 0:
            self._flag = False
            self._find_key_and_set_value(
                self.config.model,
                MmDetectionConfigLiterals.NUM_CLASSES,
                num_labels,
                stack=["model"],
            )
            if not self._flag:
                raise ACFTSystemException._with_error(
                    AzureMLError.create(ACFTSystemError, pii_safe_message="Number of labels are not updated in model"
                                                                          "config")
                )
        return self

    def set_box_scoring_or_iou_threshold(
            self, threshold: float, is_iou_threshold: bool = False
    ) -> DetectionConfigBuilder:
        """
        Set threshold in the model config
        :param threshold: threshold for bounding box score or iou_threshols
        :type threshold: float
        :param is_iou_threshold: flag to indicate if threshold is iou threshold or not
        :type is_iou_threshold: bool
        :return: config builder
        :rtype: DetectionConfigBuilder
        """
        threshold_name = MmDetectionConfigLiterals.IOU_THRESHOLD if is_iou_threshold else \
            MmDetectionConfigLiterals.BOX_SCORE_THRESHOLD
        try:
            self._flag = False
            # find and replace threshold in model.test_cfg.rcnn for two stage models
            if "rcnn" in self.config.model.test_cfg:
                self._find_key_and_set_value(
                    self.config.model.test_cfg.rcnn,
                    threshold_name,
                    threshold,
                    stack=["model", "test_cfg", "rcnn"],
                )
            else:
                if "rpn" in self.config.model.test_cfg:
                    error_str = "rpn should not be present, if rcnn is not present in config"
                    logger.error(error_str)
                    raise ACFTSystemException._with_error(
                        AzureMLError.create(ACFTSystemError, pii_safe_message=error_str)
                    )

                # find and replace threshold in model.test_cfg for ssd models
                self._find_key_and_set_value(
                    self.config.model.test_cfg,
                    threshold_name,
                    threshold,
                    stack=["model", "test_cfg"],
                )
            if not self._flag:
                logger.warning("Box scoring threshold is not updated in model config.")
        except Exception as ex:
            logger.warning(
                f"Exception {ex} when calling set_box_scoring_threshold. "
            )
            # If test_cfg or score_threshold or iou_threshold is not present in config, then this thresholding
            # is handled while calculating the metrics.
        return self

    def build(self) -> Config:
        """ Return the built MM Detection config.
        :return: MM Detection config
        :rtype: MMCV Config
        """
        return self.config


class DetectionModel(AzmlModelInterface):
    """MM Detection models."""

    def from_pretrained(self, model_name_or_path: str, **kwargs) -> nn.Module:
        """ Load the model config and weights if weight path specified.
        :param model_name_or_path: parameters used for inference
        :type model_name_or_path: str
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        :return: MM Detection model
        :rtype: nn.Module
        """
        model_weights_path = kwargs.get(ImageModelSelectorConstants.MMLAB_MODEL_WEIGHTS_PATH_OR_URL, None)
        task_name = kwargs.get(SettingLiterals.TASK_NAME, Tasks.MM_OBJECT_DETECTION)
        num_labels = kwargs.get(SettingLiterals.NUM_LABELS, 0)
        box_score_threshold = kwargs.get(
            SettingLiterals.BOX_SCORE_THRESHOLD,
            InferenceParameters.DEFAULT_BOX_SCORE_THRESHOLD,
        )

        iou_threshold = kwargs.get(SettingLiterals.IOU_THRESHOLD,
                                   InferenceParameters.DEFAULT_IOU_THRESHOLD)

        config = (
            DetectionConfigBuilder(model_name_or_path)
            .set_num_labels(num_labels)
            .set_box_scoring_or_iou_threshold(box_score_threshold, is_iou_threshold=False)
            .set_box_scoring_or_iou_threshold(iou_threshold, is_iou_threshold=True)
            .build()
        )

        # copy the label2id mapping from kwargs to config. To be used in mlflow export
        config.id2label = kwargs.get(SettingLiterals.ID2LABEL, None)
        model_meta_file_path = kwargs.get(ImageModelSelectorConstants.MMLAB_MODEL_METAFILE_PATH)
        model = init_detector(config, model_weights_path, device=get_current_device())
        logger.info(f"Successfully loaded model config and with {num_labels} labels.")
        model_state_dict = torch.load(model_weights_path, map_location="cpu")
        if 'state_dict' in model_state_dict:
            model_state_dict = model_state_dict['state_dict']
        # state_dict starts with model.* for the case of aml models.
        # need to load the checkpint to wrapped model for the case of aml models.
        load_after_wrapping = list(model_state_dict.keys())[0].startswith('model.')

        if model_weights_path and not load_after_wrapping:
            load_checkpoint(model, model_weights_path)
            logger.info(f"Successfully loaded model weight from {model_weights_path}.")

        model_wrapper = None
        if task_name == Tasks.MM_OBJECT_DETECTION:
            model_wrapper = ObjectDetectionModelWrapper(
                model, config, model_name_or_path,
                task_type=MetricsTasks.IMAGE_OBJECT_DETECTION,
                num_labels=num_labels, box_score_threshold=box_score_threshold,
                iou_threshold=iou_threshold,
                meta_file_path=model_meta_file_path
            )
        elif task_name == Tasks.MM_INSTANCE_SEGMENTATION:
            model_wrapper = InstanceSegmentationModelWrapper(
                model, config, model_name_or_path,
                task_type=MetricsTasks.IMAGE_INSTANCE_SEGMENTATION,
                num_labels=num_labels, box_score_threshold=box_score_threshold,
                iou_threshold=iou_threshold,
                meta_file_path=model_meta_file_path
            )
        if model_weights_path and load_after_wrapping:
            load_checkpoint(model_wrapper, model_weights_path)
            logger.info(f"Successfully loaded model weight from {model_weights_path}.")
        return model_wrapper
