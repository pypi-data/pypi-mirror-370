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

"""MMtracking multi-object tracking model wrapper class."""


import numpy as np
import torch

from mmcv import Config
from torch import nn, Tensor
from typing import Dict, List, Union, Any, Tuple

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.common.mlflow.common_utils import get_current_device
from azureml.acft.image.components.finetune.mmtracking.common.constants import (
    MmTrackingDatasetLiterals,
)
from azureml.acft.image.components.finetune.mmdetection.object_detection.model_wrapper import (
    ObjectDetectionModelWrapper,
)
from azureml.acft.image.components.finetune.common.constants.constants import (
    DetectionDatasetLiterals,
)
from azureml.acft.image.components.finetune.common.mlflow.common_constants import MetricsLiterals

from azureml.metrics.vision.track_eval.azureml_mot_metrics import AzureMlMOTODMetrics
from azureml.metrics import list_metrics

logger = get_logger_app(__name__)


class MultiObjectTrackingModelWrapper(ObjectDetectionModelWrapper):
    """Wrapper class over multi-object tracking model of MMTracking framework."""

    def __init__(
        self,
        mm_multi_object_tracking_model: nn.Module,
        config: Config,
        model_name_or_path: str,
        task_type: str,
        num_labels: int,
        box_score_threshold: int,
        iou_threshold: int,
        meta_file_path: str,
    ):
        """Wrapper class over multi_object_tracking model of MMTracking.
        :param mm_multi_object_tracking_model: MM multi_object_tracking model
        :type mm_multi_object_tracking_model: nn.Module
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
        super().__init__(
            mm_multi_object_tracking_model,
            config,
            model_name_or_path,
            task_type,
            num_labels,
            box_score_threshold,
            iou_threshold,
            meta_file_path
        )
        metrics_list = list_metrics(task_type)
        self.metrics_computer = AzureMlMOTODMetrics(
            num_classes=num_labels,
            iou_threshold=iou_threshold,
            metrics=metrics_list,
        )

    def _rescale_prediction_bboxes(self, img_metas, predictions):
        """
        Rescale predictions bounding boxes according to image meta info.
         In the forward call, we have rescaled the predictions to the original size of the image,
         this is to enable tracking results in different frames could be connected and evaluated.
         The groundtruths, however, are changed due to data augmentation.
         To have an evaluation on the same scale for OD, we need to manually rescale the predictions back,
         so it will be on the same scale as the groundtruths.

        :param img_metas: image meta info
        :type img_metas: list of dict
        :param predictions: prediction bboxes
        :type predictions: list of numpy arrays
        :return: prediction bboxes rescaled back to the size as in the data aug pipeline
        :rtype: list of numpy arrays
        """
        scale_factor = np.array(img_metas[0]['scale_factor'])
        scaled_predictions = []
        for prediction in predictions:
            prediction[:, :4] *= scale_factor
            scaled_predictions.append(prediction)
        return scaled_predictions

    def _organize_track_ground_truths_for_evaluation(self, gt_bboxes: List[Tensor],
                                                     gt_labels: List[Tensor],
                                                     gt_crowds: List[Tensor],
                                                     gt_instance_ids: List[Tensor]) -> Tuple[List[Dict], List[Dict]]:
        """
        Organize the batch of ground truth as required by the azureml-metrics package for MOTA calculations.
        :param gt_bboxes: batch of ground truth bounding boxes (N, 4)
        :type gt_bboxes: list of tensor
        :param gt_labels: batch of ground truth class labels (N,)
        :type gt_labels: list of tensor
        :param gt_crowds: batch of ground truth crowds boolean flag (N,)
        :type gt_crowds: list of tensor
        :param gt_instance_ids: batch of ground truth instance ids (N,)
        :type gt_instance_ids: list of tensor
        :return: Dict of ground truth labels in Tensor type
        :rtype: Dict[str, Tensor]
        """
        gt_bboxes = gt_bboxes[0]
        gt_labels = gt_labels[0].cpu().numpy()
        gt_crowds = gt_crowds[0].cpu().numpy()
        gt_instance_ids = gt_instance_ids[0].cpu().numpy()
        # In the evaluation of multi-object tracking, where we employ eval_mot function from mmtracking repo,
        # the gt_crowds is used to filter out the crowd boxes in the evaluation.
        # Say if we have N bboxes in a frame, and M of them are crowd boxes,
        # bboxes_ignore will be of shape (M, 4) and bboxes will be of shape (N-M, 4).
        track_gts = dict(bboxes=gt_bboxes[~gt_crowds],
                         labels=gt_labels[~gt_crowds],
                         bboxes_ignore=gt_bboxes[gt_crowds],
                         instance_ids=gt_instance_ids[~gt_crowds])
        return track_gts

    @classmethod
    def _get_bboxes_and_labels(
        cls, predicted_bbox: List[List[np.ndarray]]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Map the MM detection model's predicted label to the bboxes and labels
        :param predicted_bbox: bbox of shape [Number of labels, Number of boxes, 5 [tl_x, tl_y, br_x, br_y,
        box_score]] format.
        :type predicted_bbox: List[List[np.ndarray]]
        :return: bounding boxes of shape [Number of boxes, 5 [tl_x, tl_y, br_x, br_y, box_score]] and labels of
        shape [Number of boxes, label id]
        :rtype: Tuple[np.ndarray, np.ndarray]

        Sample input: [[
            np.array([[11, 2, 24, 58, 0.03], [9, 4, 24, 55, 0.9]]),
            np.array([[8, 2, 23, 59, 0.5]]),
            np.empty(shape=(0, 5)),
            np.empty(shape=(0, 5)),
        ], [
            np.empty(shape=(0, 5)),
            np.empty(shape=(0, 5)),
            np.array([[13, 27, 276, 452, 0.75]]),
            np.empty(shape=(0, 5)),
        ]]

        Sample output: ([
            np.array([[11, 2, 24, 58, 0.03], [9, 4, 24, 55, 0.9], [8, 2, 23, 59, 0.5]]),
            np.array([[13, 27, 276, 452, 0.75]])
        ],
        # Labels(classes) for each bbox in the batch (0th image has 3 bboxes and 1st image has 1 bbox)
        [np.array([0, 0, 1]),np.array([2])]
        )
        """
        bboxes = np.vstack(predicted_bbox)
        labels = [
            np.full(bbox.shape[0], i, dtype=np.int32)
            for i, bbox in enumerate(predicted_bbox)
        ]
        labels = np.concatenate(labels)
        return bboxes, labels

    def get_valid_index(self, box_scores: np.ndarray) -> List[int]:
        """
        Get the index of valid bounding boxes i.e. box score above box score threshold
        :param box_scores: Optional, prediction score of bounding box
        :type box_scores: nd-array
        :return: index of valid labels
        :rtype: List

        Note: This helper function is used for preparing the model output before
        feeding to compute_metrics. (It returns the valid indices of predictions,
        we then filtered out the invalid bbox and masks).
        1. For prediction, It will only keep those indices for which
           the box scoring confidence >= box score threshold

        Sample Input: box_scores = np.array([0.03, 0.9, 0.5, 0.75])
        Sample Output: [1, 2, 3] // considering self.box_score_threshold = 0.5
        """

        if box_scores is not None:
            return [i for i, box_score in enumerate(box_scores)
                    if box_score >= self.box_score_threshold]
        return []

    def _organize_od_prediction_for_evaluation(self,
                                               predicted_bbox: List[np.ndarray]
                                               ) -> Tuple[Dict[str, np.ndarray], np.ndarray, List[int]]:
        """
        Organize predicted bounding box and labels in a format required by the compute method in azureml-metrics
        package.
        :param predicted_bbox: Predicted bounding box
        :type predicted_bbox: List[List[np.ndarray]]

        :return: Tuple of List of Transformed prediction as required by metrics compute function,
        List of labels and List of valid indices.
        :rtype: Tuple[Dict[str, np.ndarray], np.ndarray, List[int]]

        Sample input: [
                np.array([[11, 2, 24, 58, 0.03], [9, 4, 24, 55, 0.9]]),
                np.array([[8, 2, 23, 59, 0.5]]),
                np.empty(shape=(0, 5)),
                np.empty(shape=(0, 5),
        ],
        Sample output: ({
            DetectionDatasetLiterals.BOXES: np.array([[9, 4, 24, 55, 0.9], [8, 2, 23, 59, 0.5]]),
            MetricsLiterals.CLASSES: np.array([0, 1]),
            MetricsLiterals.SCORES: np.array([0.9, 0.5])
        },
            np.array([0, 1]),
            [1, 2]
        )
        """
        bboxes, labels = self._get_bboxes_and_labels(predicted_bbox)
        keep_index = self.get_valid_index(bboxes[:, 4])
        output = {
            DetectionDatasetLiterals.BOXES: bboxes[keep_index][:, :4],
            MetricsLiterals.CLASSES: labels[keep_index],
            MetricsLiterals.SCORES: bboxes[keep_index][:, 4]
        }
        return output, labels, keep_index

    def _organize_od_predictions_for_evaluation(
        self,
        batch_predictions: List
    ) -> List[Dict[str, np.ndarray]]:
        """
        This function transforms the predictions from HF trainer as required by the azureml-metrics function.
        It also filters out the predictions whose box score is under the box_score_threshold.
        :param predictions: model prediction containing bboxes, labels and masks
        :type predictions: Tuple
        :return: Transformed predictions as required by azureml-metrics compute method
        :rtype: List of prediction dictionary List[Dict[str, np.ndarray]]

        Sample input: [[
                np.array([[11, 2, 24, 58, 0.03], [9, 4, 24, 55, 0.9]]),
                np.array([[8, 2, 23, 59, 0.5]]),
                np.empty(shape=(0, 5), dtype=float32),
                np.empty(shape=(0, 5), dtype=float32)
            ], [
                np.empty(shape=(0, 5), dtype=float32),
                np.empty(shape=(0, 5), dtype=float32),
                np.array([[13, 27, 276, 452, 0.75]], dtype=float32),
                np.empty(shape=(0, 5), dtype=float32),
            ]
        ],
        Sample output: [{
            DetectionDatasetLiterals.BOXES: np.array([[9, 4, 24, 55, 0.9], [8, 2, 23, 59, 0.5]]),
            MetricsLiterals.CLASSES: np.array([0, 1]),
            MetricsLiterals.SCORES: np.array([0.9, 0.5])
        },{
            DetectionDatasetLiterals.BOXES: np.array([[13, 27, 276, 452, 0.75]]),
            DetectionDatasetLiterals.CLASSES: np.array([2]),
            DetectionDatasetLiterals.SCORES: np.array([0.75])
        }]
        """
        outputs = []
        for predicted_bbox in batch_predictions:
            output, _, _ = self._organize_od_prediction_for_evaluation(predicted_bbox)
            outputs.append(output)
        return outputs

    def forward(self, **data) -> Union[Dict[str, Any], Tuple[Tensor, Tuple]]:
        """
        Model forward pass for training and validation mode
        :param data: Input data to model
        :type data: Dict
        :return: A dictionary of loss components in training mode OR Tuple of dictionary of predicted and ground
        labels in validation mode
        :rtype: Dict[str, Any] in training mode; Tuple[Tensor, Dict[str, Tensor]] in validation mode;

        Note: Input data dictionary consist of
            img: Tensor of shape (N, C, H, W) encoding input images.
            img_metas: list of image info dict where each dict has: 'img_shape', 'scale_factor', 'flip',
             and may also contain 'filename', 'ori_shape', 'pad_shape', and 'img_norm_cfg'. For details on the values
             of these keys see `mmdet/datasets/pipelines/formatting.py:Collect`.
            gt_bboxes - list of tensor, ground truth bboxes for each image with shape (num_gts, 4)
                            in [tl_x, tl_y, br_x, br_y] format.
            gt_labels - List of tensor, class indices corresponding to each box
            gt_instance_ids - List of tensor, instance ids corresponding to each box (validation only)
            gt_bboxes_ignore - List of "is crowds" (boolean) to each box

        Example:
            data = {"img": np.random.randint(0, 255, size = (1, 3, 800, 1440)),
                    "gt_bboxes": [torch.tensor([[  0.,   0., 100., 100.], [135, 170, 220, 260]])],
                    "gt_labels": [torch.tensor([0, 0])],
                    "gt_bboxes_ignore": [torch.tensor([False, False])],
                    "gt_instance_ids": [torch.tensor([0, 1]))], # validation only
                    "img_metas": [{'img_shape': [800, 1440, 3], 'ori_shape': [1080, 1920, 3),
                                    scale_factor': [0.7, 0.6, 0.5, 0.3], 'flip': False,
                                    'filename': 'test.jpg', 'pad_shape': [800, 1440, 3],
                                    'img_norm_cfg': {'mean': [123.675, 116.28, 103.53],
                                                     'std': [58.395, 57.12, 57.375], 'to_rgb': True}},
                                    'frame_id': 0, "video_name": "test.mp4"}]
                    }

        """
        # removing dummy_labels for forward calls
        dummy_labels = data.pop(MmTrackingDatasetLiterals.DUMMY_LABELS, None)
        if self.model.training:
            # GT_CROWDS and ORIGINAL_GT_BBOXES are not required for training
            data.pop(MmTrackingDatasetLiterals.GT_CROWDS)
            data.pop(MmTrackingDatasetLiterals.ORIGINAL_GT_BBOXES)
            return self.model.detector.train_step(data, optimizer=None)
        else:
            img = data[MmTrackingDatasetLiterals.IMG]
            img = [i.unsqueeze(0).to(get_current_device()) for i in img]
            img_metas = data[MmTrackingDatasetLiterals.IMG_METAS]
            gt_bboxes = data[MmTrackingDatasetLiterals.GT_BBOXES]
            origin_gt_bboxes = data[MmTrackingDatasetLiterals.ORIGINAL_GT_BBOXES]
            gt_labels = data[MmTrackingDatasetLiterals.GT_LABELS]
            gt_crowds = data[MmTrackingDatasetLiterals.GT_CROWDS]
            gt_instance_ids = data[MmTrackingDatasetLiterals.GT_INSTANCE_IDS]

            # organize ground truth for evaluation
            # For OD evaluation, we use ground truths passed through data augmentation pipeline
            # (hence scaled according to data augmentations)
            # and predictions that are in the dimensions specified in data augmentation pipeline.
            # For track evaluation, we use original ground truths, that are in the dimensions of the input image
            # and predictions that are rescaled to original image dimensions
            od_gts, od_img_meta_infos = self._organize_ground_truths_for_evaluation(gt_bboxes, gt_labels, gt_crowds)
            track_gts = self._organize_track_ground_truths_for_evaluation(
                origin_gt_bboxes, gt_labels, gt_crowds, gt_instance_ids)

            # organize predictions for evaluation
            batch_predictions = self.model(
                img=img, img_metas=[img_metas], return_loss=False, rescale=True)
            track_predictions = batch_predictions[MmTrackingDatasetLiterals.TRACKING_BBOXES]
            # Since det_predictions are rescaled to in the original image dimensions,
            # they are rescaled back to the dimensions specified by data augmentation pipeline.
            det_predictions = batch_predictions[MmTrackingDatasetLiterals.DETECTION_BBOXES]
            det_predictions = self._rescale_prediction_bboxes(
                img_metas=img_metas, predictions=det_predictions)
            od_predictions: dict = self._organize_od_predictions_for_evaluation([det_predictions])

            self.metrics_computer.update_states(od_gts, od_predictions, od_img_meta_infos,
                                                track_gts, track_predictions, img_metas)

            dummy_loss = torch.asarray([]).to(get_current_device())
            dummy_labels = torch.asarray([]).to(get_current_device())
        return dummy_loss, dummy_labels  # output
