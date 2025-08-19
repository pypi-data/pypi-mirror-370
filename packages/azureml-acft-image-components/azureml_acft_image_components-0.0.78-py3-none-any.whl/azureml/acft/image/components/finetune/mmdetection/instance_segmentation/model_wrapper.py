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

"""MMdetection instance segmentation model wrapper class."""

import mmcv
import numpy as np
import torch

from mmengine.config import Config
try:
    # mmdet version 3.x
    from mmdet.structures import DetDataSample
    from mmdet.structures.mask import BitmapMasks
except ImportError:
    # mmdet version 2.x
    from mmdet.core.mask import BitmapMasks
    DetDataSample = None
from torch import nn, Tensor
from typing import List, Dict, Tuple, Union

from azureml.acft.image.components.finetune.common import masktools
from azureml.acft.image.components.finetune.common.constants.constants import DetectionDatasetLiterals
from azureml.acft.image.components.finetune.common.mlflow.common_constants import (
    MetricsLiterals,
    MmDetectionDatasetLiterals
)
from azureml.acft.image.components.finetune.common.mlflow.mmdet_utils import resize_masks
from azureml.acft.image.components.finetune.mmdetection.object_detection.model_wrapper import (
    ObjectDetectionModelWrapper,
)


class InstanceSegmentationModelWrapper(ObjectDetectionModelWrapper):
    """Wrapper class over mm instance segmentation model of MMDetection framework."""

    def __init__(
        self,
        mm_instance_segmentation_model: nn.Module,
        config: Config,
        model_name_or_path: str,
        task_type: str,
        num_labels: int,
        box_score_threshold: int,
        iou_threshold: int,
        meta_file_path: str = None,
    ):
        """Wrapper class over mm instance segmentation model of MMDetection framework.
        :param mm_instance_segmentation_model: MM instance segmentation model
        :type mm_instance_segmentation_model: nn.Module
        :param config: MM Instance segmentation model configuration
        :type config: MMCV Config
        :param model_name_or_path: model name or path
        :type model_name_or_path: str
        :param task_type: Name of the Task(Instance Segmentation)
        :type task_type: str
        :param num_labels: Number of ground truth classes in the dataset
        :type num_labels: int
        :param box_score_threshold: Threshold for bounding box score
        :type box_score_threshold: float
        :param iou_threshold: Threshold for IoU(inetersection over union)
        :type iou_threshold: float
        :param meta_file_path: path to meta file
        :type meta_file_path: str
        """
        super(InstanceSegmentationModelWrapper, self).__init__(
            mm_instance_segmentation_model,
            config,
            model_name_or_path,
            task_type,
            num_labels,
            box_score_threshold,
            iou_threshold,
            meta_file_path
        )

    @classmethod
    def _convert_masks_to_rle(cls, masks: Union[List[torch.Tensor], torch.Tensor]) -> List[Dict]:
        """
        Convert masks to rle as required by metrics functions
        :param masks: Binary masks
        :type masks: np.ndarray
        :return: List of masks in rle format
        :rtype: List of rle dict
        sample input: [[0, 0, 1, 1], [2, 2, 3, 3]]
        sample output: [{"size": [5, 5], "counts": "0311090E"}, {"size": [5, 5], "counts": "0b01@01"}]
        """
        rle_mask = list()
        for mask in masks:
            rle_mask.append(masktools.encode_mask_as_rle(mask))
        return rle_mask

    def _organize_predictions_for_evaluation(
        self,
        batch_predictions: List[DetDataSample]
    ) -> List[Dict[str, np.ndarray]]:
        """
        This function transforms the predictions from HF trainer as required by the metrics functions.
        It also filters out the predictions which are under the threshold.
        :param predictions: list of model prediction with attributes bboxes, labels and masks
        :type predictions: List[mmdet.structures.DetDataSample]
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
            h_original, w_original, _ = prediction.raw_dimensions
            h_resized, w_resized = prediction.img_shape
            output[DetectionDatasetLiterals.BOXES] = [
                self.adjust_boundingbox_scale(bbox,
                                              h_resized,
                                              w_resized,
                                              h_original,
                                              w_original) for bbox in output[DetectionDatasetLiterals.BOXES]]

            for idx in range(len(indices)):
                if not indices[idx]:
                    continue
                pred_mask = pred_instances.masks[idx].cpu().numpy()
                pred_masks = np.array([pred_mask[:h_resized, :w_resized]])
                resized_masks = resize_masks(pred_masks, [h_original, w_original])
                resized_masks[0].dtype = np.bool8
                output[DetectionDatasetLiterals.MASKS].append(
                    self._convert_masks_to_rle(torch.from_numpy(np.array(resized_masks)))[0])
            outputs.append(output)
        return outputs

    def _organize_ground_truths_for_evaluation(
        self,
        gt_bboxes: List[Tensor],
        gt_labels: List[Tensor],
        gt_crowds: List[Tensor],
        gt_masks: List[BitmapMasks] = None,
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Organize the batch of ground truth as required by the azureml-metrics package for mAP calculations.
        :param gt_bboxes: batch of ground truth bounding boxes
        :type gt_bboxes: list of tensor
        :param gt_labels: batch of ground truth class labels
        :type gt_labels: list of tensor
        :param gt_crowds: batch of ground truth crowds flag
        :type gt_crowds: list of tensor
        :param gt_masks: batch of ground truth masks(bitmask type)
        :type gt_masks: list of BitmapMasks
        :return: Tuple of Dict of ground truth labels and Dict of image metadata information
        :rtype: Tuple[List[Dict], List[Dict]]

        sample output: (
        [{
            DetectionDatasetLiterals.BOXES: np.array([[0, 0, 1, 1], [2, 2, 3, 3]]),
            MetricsLiterals.CLASSES: np.array([0, 1]),
            DetectionDatasetLiterals.MASKS:
                [{"size": [5, 5], "counts": "0311090E"}, {"size": [5, 5], "counts": "0b01@01"}]
        }, {
            DetectionDatasetLiterals.BOXES: np.array([[0, 1, 3, 4]]),
            MetricsLiterals.CLASSES: np.array([0]),
            DetectionDatasetLiterals.MASKS: [{"size": [5, 5], "counts": "0=1L0H"}]
        }],
        "image_metas": [
            { DetectionDatasetLiterals.ISCROWD: np.array([False, False]) },
            { DetectionDatasetLiterals.ISCROWD: np.array([True]) }
        ])
        """

        gts, meta_infos = super()._organize_ground_truths_for_evaluation(gt_bboxes=gt_bboxes,
                                                                         gt_labels=gt_labels,
                                                                         gt_crowds=gt_crowds)
        if gt_masks:
            for i, gt_mask in enumerate(gt_masks):
                gt_image_mask = gt_mask.to_tensor(dtype=torch.bool, device="cpu")
                gt_rle_masks = self._convert_masks_to_rle(gt_image_mask)
                gts[i].update({MmDetectionDatasetLiterals.MASKS: gt_rle_masks})
        return gts, meta_infos
