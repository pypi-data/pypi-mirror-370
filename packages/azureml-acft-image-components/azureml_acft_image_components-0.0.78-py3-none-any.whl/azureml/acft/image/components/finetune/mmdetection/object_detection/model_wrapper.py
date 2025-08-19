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

"""MMdetection object detection model wrapper class."""


import numpy as np
import os
import shutil
import torch

from mmengine.config import Config, ConfigDict
from mmengine.structures import InstanceData
from mmdet.models.detectors.deformable_detr import DeformableDETR
try:
    from mmdet.structures import DetDataSample
except ImportError:
    DetDataSample = None
from pathlib import Path
from torch import nn, Tensor
from typing import Dict, List, Union, Any, Tuple, OrderedDict

from azureml.acft.common_components import get_logger_app, ModelSelectorDefaults
from azureml.acft.image.components.finetune.common.mlflow.common_utils import get_current_device
from azureml.acft.image.components.finetune.defaults.constants import TrainingDefaultsConstants
from azureml.acft.image.components.finetune.mmdetection.common.constants import (
    MmDetectionConfigLiterals,
    MmDetectionModelLiterals
)
from azureml.acft.image.components.finetune.common.mlflow.common_constants import (
    MmDetectionDatasetLiterals,
    MMdetModes
)
from azureml.acft.image.components.finetune.common.mlflow.mmdet_modules import (
    ObjectDetectionModelWrapper as mlflow_obj_det_wrapper
)

from azureml.acft.image.components.finetune.common.constants.constants import (
    DetectionDatasetLiterals,
)
from azureml.acft.image.components.finetune.mmdetection.common.model_config_rules import MODEL_RULES_MAP
from azureml.acft.image.components.finetune.common.mlflow.common_constants import MetricsLiterals
from azureml.acft.image.components.model_selector.constants import ImageModelSelectorConstants
from azureml.metrics.vision.od_is_eval.azureml_od_is_metrics import AzureMLODISMetrics
from azureml.metrics.constants import Tasks as MetricsTasks
from azureml.metrics import list_metrics


logger = get_logger_app(__name__)


class ObjectDetectionModelWrapper(nn.Module):
    """Wrapper class over object detection model of MMDetection framework."""

    def __init__(
        self,
        mm_object_detection_model: nn.Module,
        config: Config,
        model_name_or_path: str,
        task_type: str,
        num_labels: int,
        box_score_threshold: int,
        iou_threshold: int,
        meta_file_path: str = None,
    ):
        """Wrapper class over object detection model of MMDetection.
        :param mm_object_detection_model: MM object detection model
        :type mm_object_detection_model: nn.Module
        :param config: MM Detection model configuration
        :type config: MMCV Config
        :param model_name_or_path: model name or path
        :type model_name_or_path: str
        :param task_type: Task type either of Object Detection or Instance Segmentation
        :type task_type: str
        :param num_labels: Number of ground truth classes in the dataset
        :type num_labels: int
        :param box_score_threshold: Threshold for bounding box score
        :type box_score_threshold: float
        :param iou_threshold: Threshold for IoU(intersection over union)
        :type iou_threshold: float
        :param meta_file_path: path to meta file
        :type meta_file_path: str
        """
        super().__init__()
        self.model = mm_object_detection_model
        self.config = config
        self.model_name = Path(model_name_or_path).stem
        self.box_score_threshold = box_score_threshold
        self.classes = list(self.config.id2label.values())
        self.lang_model = hasattr(self.config, MmDetectionModelLiterals.LANG_MODEL_NAME)
        self.text = ". ".join(self.classes) if self.lang_model else None

        metrics_list = list_metrics(task_type)
        self.metrics_computer = AzureMLODISMetrics(
            task_is_detection=bool(task_type == MetricsTasks.IMAGE_OBJECT_DETECTION),
            num_classes=num_labels,
            iou_threshold=iou_threshold,
            metrics=metrics_list,
        )

    def _organize_predictions_for_evaluation(
        self,
        batch_predictions: List
    ) -> List[Dict[str, np.ndarray]]:
        """
        This function transforms the predictions from HF trainer as required by the metrics functions.
        It also filters out the predictions which are under the threshold.
        :param batch_predictions: list of model prediction with attributes bboxes, labels and masks
        :type batch_predictions: List[mmdet.structures.DetDataSample]
        :return: Transformed predictions as required by metrics compute function
        :rtype: List of prediction dictionary List[Dict[str, np.ndarray]]

        Sample output:
        [{
            # List of bounding boxes for first input image
            DetectionDatasetLiterals.BOXES: np.array([[0, 0, 1, 1], [2, 2, 3, 3]]),
            # List of predicetd classes for first input image
            MetricsLiterals.CLASSES: np.array([0, 1]),
            # List of predicetd rle masks for first input image
            MmDetectionDatasetLiterals.MASKS: [
                {"size": [5, 5], "counts": "0311090E"}, {"size": [5, 5], "counts": "0b01@01"}
            ]
        }, {
            # List of bounding boxes for second input image
            DetectionDatasetLiterals.BOXES: np.array([[0, 1, 3, 4]]),
            # List of predicetd classes for second input image
            MetricsLiterals.CLASSES: np.array([0]),
            # List of predicetd rle masks for second input image
            MmDetectionDatasetLiterals.MASKS: [
                [{"size": [5, 5], "counts": "0=1L0H"}]
            ]
        }]
        """
        outputs = []
        for prediction in batch_predictions:
            prediction = prediction.detach()
            pred_instances = prediction.pred_instances
            indices = pred_instances.scores >= self.box_score_threshold
            output = {
                DetectionDatasetLiterals.BOXES: pred_instances.bboxes[indices].cpu().numpy(),
                MetricsLiterals.CLASSES: pred_instances.labels[indices].cpu().numpy(),
                MetricsLiterals.SCORES: pred_instances.scores[indices].cpu().numpy(),
                DetectionDatasetLiterals.MASKS: [],
            }
            # Raw dimension is the original image size before resizing. img_shape is the resized image size.
            # The predicted bounding boxes are w.r.t. the resized image size.
            # Since the validation labels have bounding boxes w.r.t to the original image size, we are rescaling
            # the predicted bounding boxes w.r.t. the original image size as well.
            h_original, w_original, _ = prediction.raw_dimensions
            h_resized, w_resized = prediction.img_shape
            output[DetectionDatasetLiterals.BOXES] = [
                self.adjust_boundingbox_scale(bbox,
                                              h_resized,
                                              w_resized,
                                              h_original,
                                              w_original) for bbox in output[DetectionDatasetLiterals.BOXES]]
            outputs.append(output)
        return outputs

    def _organize_ground_truths_for_evaluation(
        self,
        gt_bboxes: List[Tensor],
        gt_labels: List[Tensor],
        gt_crowds: List[Tensor]
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Organize the batch of ground truth as required by the azureml-metrics package for mAP calculations.
        :param gt_bboxes: batch of ground truth bounding boxes
        :type gt_bboxes: list of tensor
        :param gt_labels: batch of ground truth class labels
        :type gt_labels: list of tensor
        :param gt_crowds: batch of ground truth crowds flag
        :type gt_crowds: list of tensor
        :return: Dict of ground truth labels in Tensor type
        :rtype: Dict[str, Tensor]

        Sample input:
            gt_bboxes: [
                torch.tensor([[0, 0, 1, 1], [2, 2, 3, 3]]),
                torch.tensor([[0, 1, 3, 4]])
            ]
            gt_labels: torch.tensor([[0, 1], [0]])
            gt_crowds: torch.tensor([[False, False], [True]])

        Sample output: ([
            {
                DetectionDatasetLiterals.BOXES: np.array([[0, 0, 1, 1], [2, 2, 3, 3]]),
                MetricsLiterals.CLASSES: np.array([0, 1]),
            }, {
                DetectionDatasetLiterals.BOXES: np.array([[0, 1, 3, 4]]),
                MetricsLiterals.CLASSES: np.array([0]),
            }
        ],
        [   # Image Metas
            {DetectionDatasetLiterals.ISCROWD: np.array([False, False])},
            {DetectionDatasetLiterals.ISCROWD: np.array([True])}
        ])
        """
        batch_gt_bboxes = [gt_bbox.cpu().numpy() for gt_bbox in gt_bboxes]
        batch_gt_labels = [gt_label.cpu().numpy() for gt_label in gt_labels]
        batch_gt_crowds = [gt_crowd.cpu().numpy() for gt_crowd in gt_crowds]

        gts: List[Dict] = list()
        meta_infos: List[Dict] = list()
        for gt_bboxes, gt_labels, gt_crowds in zip(
            batch_gt_bboxes, batch_gt_labels, batch_gt_crowds
        ):
            ground_truth = {
                DetectionDatasetLiterals.BOXES: gt_bboxes,
                MetricsLiterals.CLASSES: gt_labels,
            }
            image_metadata = {DetectionDatasetLiterals.ISCROWD: gt_crowds}

            gts.append(ground_truth)
            meta_infos.append(image_metadata)
        return gts, meta_infos

    def _handle_anchor_outside_image_boundary_in_rpn(
        self, inputs: torch.tensor, batch_data_samples: List["DetDataSample"], mode: MMdetModes  # type: ignore
    ) -> Union[Dict, List["DetDataSample"]]:  # type: ignore
        """
        Handles anchors that fall outside the image boundary during the Region Proposal Network (RPN) stage.

        This function temporarily allows anchors to be outside the image boundary by setting the 'allowed_border'
        parameter to -1. It then performs a forward pass through the model. After the forward pass, it restores
        the original value of 'allowed_border'.

        :param inputs: The input tensor for the forward pass.
        :type inputs: torch.tensor
        :param batch_data_samples: A list of data samples for the batch.
        :type batch_data_samples: List["DetDataSample"]
        :param mode: The mode for the forward pass.
        :type mode: MMdetModes
        :return: The output of the forward pass, which could be a dictionary or a list of data samples,
                depending on the mode.
        :rtype: Union[Dict, List["DetDataSample"]]
        """
        try:
            prev_val = self.model.train_cfg.rpn["allowed_border"]
            self.model.train_cfg.rpn["allowed_border"] = -1
        except Exception as ex:
            logger.warning(f'Error while setting model.train_cfg.rpn["allowed_border"]: {str(ex)}')

        output = self.model(inputs, batch_data_samples, mode=mode)
        self.model.train_cfg.rpn["allowed_border"] = prev_val
        return output

    def _robust_forward(
        self, inputs: torch.tensor, batch_data_samples: List["DetDataSample"], mode: MMdetModes  # type: ignore
    ) -> Union[Dict, List["DetDataSample"]]:  # type: ignore
        """This function performs a forward pass through the model, with additional error handling.

        :param inputs: The input data for the forward pass.
        :type inputs: torch.Tensor
        :batch_data_samples: The batch data samples.
        :type batch_data_samples: List[DetDataSample]
        :mode: The mode for the forward pass.
        :type mode: MMdetModes
        :return: The output of the forward pass, which could be a dictionary or a list of data samples,
                depending on the mode.
        :rtype: Union[Dict, List["DetDataSample"]]
        """
        try:
            return self.model(inputs, batch_data_samples, mode=mode)
        except ValueError as ex:
            error_message = (
                "There is no valid anchor inside the image boundary. "
                "Please check the image size and anchor sizes, or set "
                "``allowed_border`` to -1 to skip the condition."
            )
            if error_message.lower() in str(ex).lower():
                return self._handle_anchor_outside_image_boundary_in_rpn(inputs, batch_data_samples, mode)
            else:
                raise

    def forward(self, **data) -> Union[Dict[str, Any], Tuple[Tensor, Tensor]]:
        """
        Model forward pass for training and validation mode
        :param data: Input data to model
        :type data: Dict
        :return: A dictionary of loss components in training mode OR Tuple of dictionary of predicted and ground
        labels in validation mode
        :rtype: Dict[str, Any] in training mode; Tuple[Tensor, Tensor] in validation mode;

        Note: Input data dictionary consist of
            img: Tensor of shape (N, C, H, W) encoding input images.
            img_metas: list of image info dict where each dict has: 'img_shape', 'scale_factor', 'flip',
             and may also contain 'filename', 'ori_shape', 'pad_shape', and 'img_norm_cfg'. For details on the values
             of these keys see `mmdet/datasets/pipelines/formatting.py:Collect`.
            gt_bboxes - Ground truth bboxes for each image with shape (num_gts, 4) in [tl_x, tl_y, br_x, br_y] format.
            gt_labels - List of class indices corresponding to each box
            gt_crowds - List of "is crowds" (boolean) to each box
            gt_masks - List of masks (type BitmapMasks) for each image if task is instance_segmentation
        """
        # removing dummy_labels for forward calls
        dummy_labels = data.pop(MmDetectionDatasetLiterals.DUMMY_LABELS, None)
        is_train = self.model.training
        inputs, batch_data_samples = \
            mlflow_obj_det_wrapper.prepare_inputs_for_model_forward(data, is_train=is_train, text=self.text)
        if is_train:
            losses = self._robust_forward(inputs, batch_data_samples, mode=MMdetModes.LOSS)
            parsed_losses, log_vars = self.model.parse_losses(losses)
            op = {"loss" : parsed_losses}
            return op  # type: ignore
        else:
            data.pop(MmDetectionDatasetLiterals.IMG)
            data.pop(MmDetectionDatasetLiterals.IMG_METAS)
            batch_predictions = self._robust_forward(inputs, batch_data_samples, mode=MMdetModes.PREDICT)
            gt_bboxes = data.pop(MmDetectionDatasetLiterals.ORIGINAL_GT_BBOXES)
            gt_masks = data.pop(MmDetectionDatasetLiterals.ORIGINAL_GT_MASKS, None)
            data.pop(MmDetectionDatasetLiterals.GT_BBOXES)
            data.pop(MmDetectionDatasetLiterals.GT_MASKS, None)
            mask_args = {MmDetectionDatasetLiterals.GT_MASKS: gt_masks} if gt_masks is not None else {}

            predictions = self._organize_predictions_for_evaluation(batch_predictions)
            gts, img_meta_infos = self._organize_ground_truths_for_evaluation(gt_bboxes=gt_bboxes, **data, **mask_args)
            self.metrics_computer.update_states(y_test=gts, image_meta_info=img_meta_infos, y_pred=predictions)

            # Returning dummy_loss, dummy_labels since HF-trainer eval step expects two outputs.
            dummy_loss = torch.asarray([]).to(get_current_device())
            dummy_labels = torch.asarray([]).to(get_current_device())
            return dummy_loss, dummy_labels

    def save_pretrained(self, output_dir: os.PathLike, state_dict: OrderedDict) -> None:
        """
        Save finetuned weights and model configuration
        :param output_dir: Output directory to store the model
        :type output_dir: os.PathLike
        :param state_dict: Model state dictionary
        :type state_dict: Dict
        """
        # TODO: Revisit the logic for resuming training from checkpoint. Taking user input in python script
        #  may not be a good idea from security perspective. Or, it may not affect as user machine is individual.
        os.makedirs(output_dir, exist_ok=True)
        torch.save(state_dict, os.path.join(output_dir, ModelSelectorDefaults.MODEL_CHECKPOINT_FILE_NAME))
        # saving the unwrapped version that can be directly used with mmd repo
        MMD_PATH = os.path.join(output_dir, ImageModelSelectorConstants.MMD_MODEL_CHECKPOINT_FILE_NAME)
        torch.save(
            {
                MmDetectionConfigLiterals.STATE_DICT : self.model.state_dict(),
                MmDetectionConfigLiterals.META : {
                    MmDetectionConfigLiterals.CLASSES : self.classes}
            }, MMD_PATH)
        # dumping the class names in test_dataloader to be used with mmd repo
        # for mmtracking, config doens't have test_dataloader, thus we skip this step. id2label will be in config
        if hasattr(self.config, "test_dataloader") and hasattr(self.config.test_dataloader, "dataset"):
            self.config.test_dataloader.dataset.metainfo = {
                MmDetectionConfigLiterals.CLASSES : self.classes
            }
        model_type = self.config.model.type if hasattr(self.config, "model") \
            and hasattr(self.config.model, "type") else None
        if isinstance(self.model, DeformableDETR) and hasattr(self.config.model, "bbox_head"):
            # Removing the following keys due to a bug in mmdetection for DeformableDETR model.
            # https://github.com/open-mmlab/mmdetection/issues/10281. init_detector will fail if
            # these keys are present.
            # These keys are not present in the original config of the model, but init_detector adds
            # these keys to the config after first load and we need to remove it before saving.
            keys_to_remove = ["share_pred_layer", "num_pred_layer", "as_two_stage"]
            for key in keys_to_remove:
                if key in self.config.model.bbox_head:
                    print(f"Removing {key} from model's bbox_head since it is not supported for DeformableDETR model.")
                    del self.config.model.bbox_head[key]

            # delete num_classes in dn_cfg since re loading the config file is failing
            if hasattr(self.config.model, "dn_cfg"):
                self.config.model.dn_cfg.pop("num_classes")

        if model_type and model_type in MODEL_RULES_MAP:
            MODEL_RULES_MAP[model_type]().apply(self.config.model)

        self.config.dump(os.path.join(output_dir, self.model_name + ".py"))
        logger.info(f"Model saved at {output_dir}")
        Config.fromfile(os.path.join(output_dir, self.model_name + ".py"))
        logger.info("Validated the Saved Model configuration.")

    @staticmethod
    def adjust_boundingbox_scale(bbox: List, h_cur: int, w_cur: int, h_raw: int, w_raw: int) -> List:
        """ Adjusts the bounding box coordinates to the original image size.
        :bbox: list of bounding box coordinates
        :type bbox: list
        :h_cur: Height of the input image after transformation. This is
        the height of the image after constraint resize and not the final image height which
        has additional padding as well.
        :type h_cur: int
        :w_cur: Width of the input image after transformation. This is
        the width of the image after constraint resize and not the final image width which
        has additional padding as well.
        :type w_cur: int
        :h_raw: Original height of the image
        :type h_raw: int
        :w_raw: Original width of the image

        : return: list of bounding box coordinates adjusted to the original image size.
        : rtype: list
        """
        adjusted_bbox = (bbox / [w_cur, h_cur, w_cur, h_cur]) * [w_raw, h_raw, w_raw, h_raw]
        return adjusted_bbox
