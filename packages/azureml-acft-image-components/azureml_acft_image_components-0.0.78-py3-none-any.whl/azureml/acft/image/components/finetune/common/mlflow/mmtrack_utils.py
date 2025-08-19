# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Mlflow PythonModel wrapper helper scripts."""

import logging
import numpy as np
import torch

import mmcv
from torch.utils.data import Dataset
from dataclasses import asdict
from transformers import Trainer, TrainingArguments
from typing import Dict, List, Callable, Tuple

from common_constants import (HFMiscellaneousLiterals,
                              Tasks,
                              MmTrackingDatasetLiterals,
                              ODLiterals)

logger = logging.getLogger(__name__)


def _parse_mot_output(output: Dict[str, np.ndarray], id2label: Dict[int, str], data_infos) -> List[Dict]:
    proc_op = []
    for (data_info, det_labels, det_bboxes, track_bboxes, track_labels) in \
        zip(data_infos, output[MmTrackingDatasetLiterals.DET_LABELS], output[MmTrackingDatasetLiterals.DET_BBOXES],
            output[MmTrackingDatasetLiterals.TRACK_BBOXES], output[MmTrackingDatasetLiterals.TRACK_LABELS]):
        img_info = data_info[MmTrackingDatasetLiterals.IMG_INFO]
        curimage_preds = {MmTrackingDatasetLiterals.DET_BBOXES: [], MmTrackingDatasetLiterals.TRACK_BBOXES: [],
                          "frame_id": img_info[MmTrackingDatasetLiterals.FRAME_ID],
                          "video_url": img_info[MmTrackingDatasetLiterals.VIDEO_URL]}
        for label, bbox in zip(det_labels, det_bboxes):
            if label >= 0:
                curimage_preds[MmTrackingDatasetLiterals.DET_BBOXES].append({
                    ODLiterals.BOX: {
                        ODLiterals.TOP_X: float(bbox[0]),
                        ODLiterals.TOP_Y: float(bbox[1]),
                        ODLiterals.BOTTOM_X: float(bbox[2]),
                        ODLiterals.BOTTOM_Y: float(bbox[3]),
                    },
                    ODLiterals.LABEL: id2label[label],
                    ODLiterals.SCORE: float(bbox[4]),
                })
        for tlabel, tbbox in zip(track_labels, track_bboxes):
            if tlabel >= 0:
                curimage_preds[MmTrackingDatasetLiterals.TRACK_BBOXES].append({
                    ODLiterals.BOX: {
                        MmTrackingDatasetLiterals.INSTANCE_ID: int(tbbox[0]),
                        ODLiterals.TOP_X: float(tbbox[1]),
                        ODLiterals.TOP_Y: float(tbbox[2]),
                        ODLiterals.BOTTOM_X: float(tbbox[3]),
                        ODLiterals.BOTTOM_Y: float(tbbox[4]),
                    },
                    ODLiterals.LABEL: id2label[tlabel],
                    ODLiterals.SCORE: float(tbbox[5]),
                })
        proc_op.append(curimage_preds)
    return proc_op


def mmtrack_run_inference_batch(
    test_args: TrainingArguments,
    model: torch.nn.Module,
    id2label: Dict[int, str],
    processed_videos: str,
    task_type: Tasks,
    test_transforms: Callable,
) -> List:
    """This method performs inference on batch of input images.

    :param test_args: Training arguments path.
    :type test_args: transformers.TrainingArguments
    :param model: Pytorch model weights.
    :type model: mmtrack model with model wraper
    :param id2label: id to label mapping
    :type id2label: dict
    :param image_path_list: list of image paths for inferencing.
    :type image_path_list: List
    :param: processed_videos: validated video urls
    :type: processed_videos: str
    :param task_type: Task type of the model.
    :type task_type: constants.Tasks
    :param test_transforms: Transformations to apply to the test dataset before
                            sending it to the model.
    :param test_transforms: Callable
    :return: list of dict.
    :rtype: list
    """

    def collate_fn(examples: List[Dict[str, Dict]]) -> Dict[str, Dict]:
        # Filter out invalid examples
        valid_examples = [example for example in examples if example["img"] is not None]
        if len(valid_examples) != len(examples):
            if len(valid_examples) == 0:
                raise Exception("video frame invalid, please check the video source")

        batched_images = [torch.stack(example[MmTrackingDatasetLiterals.IMG]) for example in valid_examples]
        img_metas = [example[MmTrackingDatasetLiterals.IMG_METAS][0].data for example in valid_examples]
        output = {
            MmTrackingDatasetLiterals.IMG: batched_images,
            MmTrackingDatasetLiterals.IMG_METAS: img_metas
        }

        return output

    data_infos = []
    for _, video_url in processed_videos.iteritems():
        video_frames = mmcv.VideoReader(video_url)
        for j, img in enumerate(video_frames):
            data = dict(img=img, img_info=dict(frame_id=j, video_url=video_url), img_prefix=None)
            data_infos.append(data)
    inference_dataset = TrackingDataset(data_infos=data_infos, transforms=test_transforms)
    # Initialize the trainer
    trainer = Trainer(
        model=model,
        args=test_args,
        data_collator=collate_fn,
    )
    results = trainer.predict(inference_dataset)
    output = results.predictions[1]
    return _parse_mot_output(output, id2label, data_infos)


class TrackingDataset(Dataset):
    """Dummy dataset for tracking"""
    def __init__(self, data_infos, transforms=None):
        """init dummy dataset with or without test transform
        """
        self.data_infos = data_infos
        self.transforms = transforms

    def __getitem__(self, index):
        """get item by index
        """
        data = self.data_infos[index]
        if self.transforms is not None:
            data = self.transforms(data)
        return data

    def __len__(self):
        """length of dataset
        """
        return len(self.data_infos)
