# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""MMTracking modules."""

import torch
import numpy as np

from mmcv import Config
from pathlib import Path
from torch import nn, Tensor
from torch.nn.utils.rnn import pad_sequence
from typing import Dict, List, Union, Any, Tuple
from common_constants import MmTrackingDatasetLiterals
from common_utils import get_current_device


class MultiObjectTrackingModelWrapper(nn.Module):
    """Wrapper class over multi-object-tracking model of MMTracking."""
    def __init__(
        self,
        mm_multi_object_tracking_model: nn.Module,
        config: Config,
        model_name_or_path: str = None,
    ):
        """Wrapper class over multi-object-tracking model of MMTracking.
        :param mm_object_detection_model: MM multi-object-tracking
        :type mm_object_detection_model: nn.Module
        :param config: MM Tracking model configuration
        :type config: MMCV Config
        :param model_name_or_path: model name or path
        :type model_name_or_path: str
        """

        super().__init__()
        self.model = mm_multi_object_tracking_model
        self.config = config
        self.model_name = Path(model_name_or_path).stem

    @classmethod
    def _pad_sequence(cls, sequences: Tensor, padding_value: float = -1, batch_first: bool = True) -> Tensor:
        """
        It stacks a list of Tensors sequences, and pads them to equal length.
        :param sequences: list of variable length sequences.
        :type sequences: Tensor
        :param padding_value: value for padded elements
        :type padding_value: float
        :param batch_first: output will be in B x T x * if True, or in T x B x * otherwise
        :type batch_first: bool
        :return: Tensor of size ``B x T x *`` if batch_first is True
        :rtype: Tensor
        """
        rt_tensor = pad_sequence(sequences, padding_value=padding_value, batch_first=batch_first)
        rt_tensor = rt_tensor.to(device=get_current_device())
        return rt_tensor

    def _organize_track_predictions_for_trainer(self, predicted_bbox: dict) -> dict:
        """
        Organize track predictions
        :param predicted_bbox: predictions
        :type data: Dict, contains keys: det_bboxes, track_bboxes
            det_bboxes: List[array] of shape (N, 5) encoding bounding boxes (x1, y1, x2, y2, score)
            det_labels: List[array] of shape (N, 6) encoding bounding boxes (instance_id, x1, y1, x2, y2, score)
              both lists denotes categories, meaning List[0] means the bounding boxes predicted for category 0
        :return: A dictionary of loss components in training mode OR Tuple of dictionary of predicted and ground
        labels in validation mode
        :rtype: Dict[str, Any] in training mode; Tuple[Tensor, Dict[str, Tensor]] in validation mode;
        """
        det_bboxes = torch.as_tensor(np.vstack(predicted_bbox[MmTrackingDatasetLiterals.DET_BBOXES]))
        track_bboxes = torch.as_tensor(np.vstack(predicted_bbox[MmTrackingDatasetLiterals.TRACK_BBOXES]))

        det_labels = [np.full(det.shape[0], i, dtype=np.int32)
                      for i, det in enumerate(predicted_bbox[MmTrackingDatasetLiterals.DET_BBOXES])]
        det_labels = torch.as_tensor(np.concatenate(det_labels))

        track_labels = [np.full(track.shape[0], i, dtype=np.int32)
                        for i, track in enumerate(predicted_bbox[MmTrackingDatasetLiterals.TRACK_BBOXES])]
        track_labels = torch.as_tensor(np.concatenate(track_labels))

        output = dict()
        output[MmTrackingDatasetLiterals.DET_BBOXES] = self._pad_sequence(det_bboxes.unsqueeze(0))
        output[MmTrackingDatasetLiterals.DET_LABELS] = self._pad_sequence(det_labels.unsqueeze(0))
        output[MmTrackingDatasetLiterals.TRACK_BBOXES] = self._pad_sequence(track_bboxes.unsqueeze(0))
        output[MmTrackingDatasetLiterals.TRACK_LABELS] = self._pad_sequence(track_labels.unsqueeze(0))
        return output

    def forward(
        self, **data
    ) -> Union[Dict[str, Any], Tuple[Tensor, Dict[str, Tensor]]]:
        """
        Model forward pass for validation mode
        :param data: Input data to model
        :type data: Dict
        :return: Tuple of dictionary of empty loss and predicted labels
        :rtype: Tuple[Tensor, Dict[str, Tensor]] in validation mode;

        Note: Input data dictionary consist of
            img: List of Tensor of shape (N, C, H, W) encoding input images.
            img_metas: list of image info dict where each dict has: "frame_id", "img_prefix"
        """
        # test mode
        img = data[MmTrackingDatasetLiterals.IMG]
        img_metas = data[MmTrackingDatasetLiterals.IMG_METAS]
        batch_predictions = self.model(
            img=img, img_metas=[img_metas], return_loss=False, rescale=True
        )
        output: dict = self._organize_track_predictions_for_trainer(
            batch_predictions)

        return torch.asarray([], device=get_current_device()), output
