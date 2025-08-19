# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""MMTracking dataset class"""

import copy
import random
import collections

import torch
import mmcv
import json
import numpy as np
import pandas as pd
import os.path as osp
from mmcv.parallel import DataContainer as DC
from collections import defaultdict
from terminaltables import AsciiTable
from typing import Any, Callable, Dict, Optional, Tuple

from torch.utils.data import Dataset
from azureml.acft.common_components import get_logger_app

from azureml.acft.common_components.image.runtime_common.object_detection.data.object_annotation import (
    VideoObjectAnnotation)
from azureml.acft.image.components.finetune.common.constants.constants import (
    DetectionDatasetLiterals,
    ImageDataItemLiterals
)
from azureml._common._error_definition import AzureMLError
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError, ACFTSystemError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException, ACFTSystemException
from azureml.acft.image.components.finetune.mmtracking.common.constants import (
    MmTrackingDatasetLiterals,
)

logger = get_logger_app(__name__)


class MmTrackingDataset:
    """Base coco video dataset for VID, MOT and SOT tasks.
    Note:
        1. frame_id, category_id starts from 0
        2. video_id, image_id starts from 1
        3. bounding box (after parsing): x0, y0, w, h
    """

    def __init__(self, images_df: pd.DataFrame,
                 is_train: bool=False,
                 mask_required=False,
                 load_as_video: Optional[bool]=True,
                 key_img_sampler: Optional[dict]=dict(interval=1),
                 ref_img_sampler: Optional[dict]=None,
                 pipeline: Optional[list]=None
                 ):
        """
        :param images_df: dataframe to initialize the class
        :type images_df: pd.DataFrame
        :param is_train: which mode (training, inference) is the network in?
        :type is_train: bool
        :param mask_required: whether mask is required
        :type mask_required: bool
        :param load_as_video: Default: True. If True, load video dataset,
            otherwise, load image dataset, treat each image as an video.
        :type load_as_video: bool
        :param key_img_sampler: Configuration of sampling key images.
        :type key_img_sampler: dict
        :param ref_img_sampler: Configuration of sampling ref images.
        :type ref_img_sampler: dict
        :param pipeline: list of pipeline dict
        :type pipeline: list
        """
        self._is_train = is_train
        self.mask_required = mask_required
        self.images_df = images_df

        self.max_refetch = 15
        self.load_as_video = load_as_video
        self.key_img_sampler = key_img_sampler
        self.ref_img_sampler = ref_img_sampler
        self.pipeline = pipeline
        self._init_dataset()

    #############################################################################
    # Dataset Loading
    #############################################################################
    def _init_dataset(self):
        """Load annotations from COCO/COCOVID style annotation file.
        """
        # image_id, video_id are both 1 indexed.
        # frame_id is 0 indexed
        videos_set = set()
        self.videos = []  # [video_dict]

        self.vidToImgs = collections.defaultdict(list)  # video_id -> [image_id]
        self.imgs = dict()  # image_id -> image_dict

        self.imgToAnns = collections.defaultdict(list)  # image_id -> [VideoObjectAnnotation]
        classes = set()

        for index, row in self.images_df.iterrows():
            video_name = row[MmTrackingDatasetLiterals.VIDEO_DETAILS][MmTrackingDatasetLiterals.VIDEO_NAME]
            if video_name not in videos_set:
                videos_set.add(video_name)
                video_dict = {"name": video_name,
                              "id": len(videos_set)}
                self.videos.append(video_dict)

            video_id = len(videos_set)
            image_id = index + 1
            image_dict = dict(
                image_id=image_id,
                video_name=video_name,
                frame_id=row[MmTrackingDatasetLiterals.VIDEO_DETAILS][MmTrackingDatasetLiterals.FRAME_ID],
                height=row[MmTrackingDatasetLiterals.IMAGE_DETAILS][MmTrackingDatasetLiterals.HEIGHT],
                width=row[MmTrackingDatasetLiterals.IMAGE_DETAILS][MmTrackingDatasetLiterals.WIDTH],
                filename=row[MmTrackingDatasetLiterals.LOCAL_IMAGE_URL]
            )
            if self._filter_imgs(image_dict):
                continue
            self.vidToImgs[video_id].append(image_id)
            self.imgs[image_id] = image_dict

            labels_dict = row.get("label", [])
            for j, label_dict in enumerate(labels_dict):
                object_info = VideoObjectAnnotation(_masks_required=self.mask_required)
                object_info.init(label_dict)
                self.imgToAnns[image_id].append(object_info)

                classes.add(label_dict["label"])

        self.has_annotations = (len(self.imgToAnns) != 0)
        if self._is_train and not self.has_annotations:
            raise ACFTDataException._with_error(
                AzureMLError.create(ACFTUserError,
                                    pii_safe_message="no valid records available for training. "
                                    "Please review the input data format requirements"))

        self.prepare_data_infos()
        self.set_classes(list(classes))
        self._set_group_flag()

    def prepare_data_infos(self):
        """prepare self.data_infos, which will be accessed for inference/ evaluation
        """
        if self.load_as_video:
            vid_ids = list(range(1, len(self.videos) + 1))
        else:
            # consider each image a video, for training object detection
            vid_ids = list(range(1, len(self.imgs) + 1))
            self.vidToImgs = {i: [i] for i in vid_ids}

        self.data_infos = []
        self.img_ids = []  # list of list, per video has a list of img_ids
        for vid_id in vid_ids:
            img_ids = self.vidToImgs[vid_id]
            if self.key_img_sampler is not None:
                img_ids = self.key_img_sampling(img_ids,
                                                **self.key_img_sampler)
            self.img_ids.extend(img_ids)
            for img_id in img_ids:
                info = self.imgs[img_id]
                self.data_infos.append(info)

    def set_classes(self, classes):
        """ setting class names for the dataset
        """
        if not classes:
            return
        self.classes = sorted(classes)
        self.cat_ids = range(len(classes))
        self.class_name_to_id = {cls: id_ for cls, id_ in zip(classes, self.cat_ids)}

    def _filter_imgs(self, img_info, min_size=32):
        """Filter images too small.
        :param img_info: image information containing width and height info
        :type img_info: dict
        :param min_size: minimum size of the images to filter
        :param min_size: int
        :return: if the image needed to be filtered out
        :rtype: bool
        """
        return min(img_info[MmTrackingDatasetLiterals.WIDTH],
                   img_info[MmTrackingDatasetLiterals.HEIGHT]) < min_size

    def _set_group_flag(self):
        """Set flag according to image aspect ratio.

        Images with aspect ratio greater than 1 will be set as group 1,
        otherwise group 0.
        """
        self.flag = np.zeros(len(self), dtype=np.uint8)
        for i in range(len(self)):
            img_info = self.data_infos[i]
            if img_info[MmTrackingDatasetLiterals.WIDTH] / img_info[MmTrackingDatasetLiterals.HEIGHT] > 1:
                self.flag[i] = 1

    #############################################################################
    # get item
    #############################################################################
    def __getitem__(self, idx, samples_for_augmentation=False):
        """Get training/test data after pipeline.
        :param idx: Index of data.
        :type idx: int
        :param samples_for_augmentation: if this is just to get samples for mosaic like augmentation
        :type samples_for_augmentation: bool
        :return dict containing training/test data
        :rtype dict
        """
        results = self.get_item_info(idx)
        if self.pipeline is not None:
            results = self.apply_mm_transform(results, samples_for_augmentation)
            if not samples_for_augmentation:
                results = self.apply_postprocessing(results)
                results[MmTrackingDatasetLiterals.ORIGINAL_GT_BBOXES] = \
                    self.get_ann_info(idx)[MmTrackingDatasetLiterals.BBOXES]
        return results

    def get_item_info(self, img_idx: int):
        """Get COCO annotations by image idx.
        :param img_idx: idx of image.
        :type img_idx: int
        :return: annotation information of `img_info`.
        :rtype: dict
        """
        results = dict()
        results[MmTrackingDatasetLiterals.IS_VIDEO_DATA] = self.load_as_video
        image_info = self.data_infos[img_idx]
        results[MmTrackingDatasetLiterals.IMAGE_INFO] = image_info
        # note: image_id might not equal to img_idx, as some of the images might be filtered out due to size/ sampling
        image_id = image_info[MmTrackingDatasetLiterals.IMAGE_ID]
        anno_info = self.imgToAnns[image_id]
        results[MmTrackingDatasetLiterals.ANN_INFO] = self._parse_ann_info(image_info, anno_info)
        results[MmTrackingDatasetLiterals.IMAGE_PREFIX] = None
        results[MmTrackingDatasetLiterals.BBOX_FIELDS] = []
        return results

    def convert_ann_to_dict(self, object_annotation, image_height, image_width):
        """ convert VideoObjectAnnotation information to dict, and un-normalize input
        :param object_annotation: object annnotation
        :type object_annotation: VideoObjectAnnotation
        :param image_height: image height
        :type image_height: int
        :param image_width: image width
        :type image_width: int
        :return: annotation information of bbox info.
        :rtype: dict
        """
        ann_dict = {}
        label, topX, topY, bottomX, bottomY = object_annotation.bounding_box
        x0, y0 = topX * image_width, topY * image_height
        x1, y1 = bottomX * image_width, bottomY * image_height
        h, w = y1 - y0, x1 - x0
        ann_dict[MmTrackingDatasetLiterals.BBOX] = [x0, y0, w, h]
        ann_dict[MmTrackingDatasetLiterals.AREA] = w * h
        ann_dict[MmTrackingDatasetLiterals.CATEGORY_ID] = self.class_name_to_id[label]
        ann_dict[MmTrackingDatasetLiterals.INSTANCE_ID] = object_annotation.instance_id
        ann_dict[MmTrackingDatasetLiterals.IS_CROWD] = bool(object_annotation.iscrowd)
        return ann_dict

    def _parse_ann_info(self, img_info, ann_info):
        """Parse bbox and mask annotations.
        :param img_anfo: Information of image.
        :type img_anfo: dict
        :param ann_info: Annotation information of image.
        :type: ann_info: list[VideoObjectAnnotation])
        :return: A dict containing the following keys: bboxes, bboxes_ignore,
            labels, instance_ids, masks, seg_map. "masks" are raw
            annotations and not decoded into binary masks.
        :rtype: dict
        """
        gt_bboxes = []
        gt_labels = []
        gt_bboxes_ignore = []
        gt_instance_ids = []

        image_height = img_info[MmTrackingDatasetLiterals.HEIGHT]
        image_width = img_info[MmTrackingDatasetLiterals.WIDTH]
        for i, object_annotation in enumerate(ann_info):
            ann = self.convert_ann_to_dict(object_annotation, image_height, image_width)
            x1, y1, w, h = ann[MmTrackingDatasetLiterals.BBOX]
            inter_w = max(0, min(x1 + w, image_width) - max(x1, 0))
            inter_h = max(0, min(y1 + h, image_height) - max(y1, 0))
            if inter_w * inter_h == 0:
                continue
            if ann[MmTrackingDatasetLiterals.AREA] <= 0 or w < 1 or h < 1:
                continue
            if ann[MmTrackingDatasetLiterals.CATEGORY_ID] not in self.cat_ids:
                continue
            bbox = [x1, y1, x1 + w, y1 + h]
            if ann.get(MmTrackingDatasetLiterals.IS_CROWD, False):
                gt_bboxes_ignore.append(bbox)
            else:
                gt_bboxes.append(bbox)
                gt_labels.append(ann[MmTrackingDatasetLiterals.CATEGORY_ID])
                if MmTrackingDatasetLiterals.INSTANCE_ID in ann:
                    gt_instance_ids.append(ann[MmTrackingDatasetLiterals.INSTANCE_ID])

        if gt_bboxes:
            gt_bboxes = np.array(gt_bboxes, dtype=np.float32)
            gt_labels = np.array(gt_labels, dtype=np.int64)
        else:
            gt_bboxes = np.zeros((0, 4), dtype=np.float32)
            gt_labels = np.array([], dtype=np.int64)

        if gt_bboxes_ignore:
            gt_bboxes_ignore = np.array(gt_bboxes_ignore, dtype=np.float32)
        else:
            gt_bboxes_ignore = np.zeros((0, 4), dtype=np.float32)

        results = dict(
            bboxes=gt_bboxes,
            labels=gt_labels,
            bboxes_ignore=gt_bboxes_ignore)

        if self.load_as_video:
            results[MmTrackingDatasetLiterals.INSTANCE_ID] = np.array(gt_instance_ids).astype(np.int)
        else:
            results[MmTrackingDatasetLiterals.INSTANCE_ID] = np.arange(len(gt_labels))  # each gt as a new instance

        return results

    def get_ann_info(self, img_idx: int):
        """ get annotation information given img_idx
        :param img_idx: image idx
        :type img_idx: int
        """
        return self.get_item_info(img_idx)[MmTrackingDatasetLiterals.ANN_INFO]

    #############################################################################
    # dataset pipelines
    #############################################################################
    def set_transform(self, transform: list):
        """ set pipelines for the dataset class
        :param transform: list of composed openmmlab transforms
        :type transform: list
        """
        self.pipeline = transform

    def apply_mm_transform(self, results, samples_for_augmentation=False):
        """ apply transformations & postprocessings
        param: results: dict of image & bbox annotation info
        type: results: dict
        param: samples_for_augmentation: if this is just to get samples for mosaic like augmentation
        :type samples_for_augmentation: bool
        return: image & bbox annotation info after data augmentation
        rtype:  dict
        """
        for pipeline in self.pipeline:
            results = self.transform_via_pipeline(results, pipeline)
            if samples_for_augmentation:
                return results
        results = self.remove_data_container(results)
        return results

    def transform_via_pipeline(self, results, pipeline):
        """ apply openmm pipeline transformation to results
        param: results: dict of image & bbox annotation info
        type: results: dict
        param: pipeline: composed openmmlab pipeline
        return: image & bbox annotation info after data augmentation
        rtype:  dict
        """
        for transform in pipeline.transforms:
            if hasattr(transform, 'get_indexes'):
                for i in range(self.max_refetch):
                    # Make sure the results passed the loading pipeline
                    # of the original dataset is not None.
                    indexes = transform.get_indexes(self)
                    if not isinstance(indexes, collections.abc.Sequence):
                        indexes = [indexes]
                    mix_results = [
                        copy.deepcopy(self.__getitem__(index, samples_for_augmentation=True)) for index in indexes
                    ]
                    if None not in mix_results:
                        results['mix_results'] = mix_results
                        break
                else:
                    raise ACFTSystemException._with_error(
                        AzureMLError.create(ACFTSystemError,
                                            pii_safe_message=f"The augmentation {transform.__name__} failed. "
                                            "please check the correctness of the dataset."))
            for i in range(self.max_refetch):
                # To confirm the results passed the training pipeline
                # of the wrapper is not None.
                updated_results = transform(copy.deepcopy(results))
                if updated_results is not None:
                    results = updated_results
                    break
            else:
                raise ACFTSystemException._with_error(
                      AzureMLError.create(ACFTSystemError,
                                          pii_safe_message=f"The augmentation {transform.__name__} failed. "
                                          "please check the correctness of the dataset."))

            if 'mix_results' in results:
                results.pop('mix_results')
        return results

    def _rand_another(self, idx: int) -> int:
        """Get another random index from the same group as the given index.
        param: idx: image index of the original image
        type: idx: int
        return: image index of a different image
        rtype: int
        """
        pool = np.where(self.flag == self.flag[idx])[0]
        return np.random.choice(pool)

    def remove_data_container(self, data):
        """remove data container which is introduced by openmm pipelines
        param: results obtained after transformation
        type: dict or DataContainer or list
        return: results that doesn't contain any data container
        rtype: dict
        """
        if isinstance(data, DC):
            return data.data
        if isinstance(data, list):
            return [self.remove_data_container(d) for d in data]
        if isinstance(data, dict):
            for key, item in data.items():
                data[key] = self.remove_data_container(item)
            return data
        return data

    def remove_nested_list(self, results):
        """ remove nested list which is introduced by openmm pipelines
        param: results obtained after transformation
        type: dict
        return: results obtained after transformation
        rtype: dict
        """
        for key in results.keys():
            if isinstance(results[key], list):
                results[key] = results[key][0]
        return results

    def apply_postprocessing(self, results):
        """
        Before applying postprocessing:
        train dataset:
            img_metas: list[dict]
            img: list[tensor] (3*W*H)
            gt_bboxes: list[tensor] (N*4)
            gt_labels: list[tensor] (N)
            gt_bboxes_ignore: list[tensor] (0*4)

        val dataset:
            img_metas: list[dict]
            img: list[tensor] [(3*W*H)]
            gt_bboxes: [ndarray] [(N*4)]
            gt_labels: [ndarray] (N)
            gt_bboxes_ignore: tensor (0*4)
        param: results obtained after transformation
        type: dict
        return: results obtained after transformation
        type: dict
        """
        results = self.remove_nested_list(results)
        results[MmTrackingDatasetLiterals.GT_CROWDS] = torch.zeros_like(
            results[MmTrackingDatasetLiterals.GT_LABELS], dtype=torch.bool)
        return results

    def __len__(self):
        """Total number of samples of data.
        return: length of dataset
        rtype: int
        """
        return len(self.data_infos)

    #############################################################################
    # Samplings
    #############################################################################
    def key_img_sampling(self, img_ids, interval=1):
        """Sampling key images.
        param: img_ids: list of all image ids
        type: img_ids: list of int
        param: interval: skip interval
        type: interval: int
        return: list of image ids
        rtype: list
        """
        return img_ids[::interval]

    def ref_img_sampling(self,
                         img_info,
                         frame_range,
                         stride=1,
                         num_ref_imgs=1,
                         filter_key_img=True,
                         method='uniform',
                         return_key_img=True):
        """Sampling reference frames in the same video for key frame.
        function will be used in future iterations.

        param: img_info: The information of key frame.
        type: img_info: dict
        param: frame_range: The sampling range of reference
                frames in the same video for key frame.
        type: frame_range: List(int) | int
        param: stride: The sampling frame stride when sampling reference
                images. Default: 1.
        type: stride: int
        param: num_ref_imgs: The number of sampled reference images.
                Default: 1.
        type: num_ref_imgs: int
        param: filter_key_img: If False, the key image will be in the
                sampling reference candidates, otherwise, it is exclude.
                Default: True.
        type: filter_key_img: bool
        param: method: The sampling method. Options are 'uniform',
                'bilateral_uniform', 'test_with_adaptive_stride',
                'test_with_fix_stride'. 'uniform' denotes reference images are
                randomly sampled from the nearby frames of key frame.
                'bilateral_uniform' denotes reference images are randomly
                sampled from the two sides of the nearby frames of key frame.
                'test_with_adaptive_stride' is only used in testing, and
                denotes the sampling frame stride is equal to (video length /
                the number of reference images). test_with_fix_stride is only
                used in testing with sampling frame stride equalling to
                `stride`. Default: 'uniform'.
        type: method: str
        param: return_key_img: If True, the information of key frame is
                returned, otherwise, not returned. Default: True.
        type: return_key_img: bool
        return: `img_info` and the reference images information or
            only the reference images information.
        rtype: list(dict)
        """
        assert isinstance(img_info, dict)
        if isinstance(frame_range, int):
            assert frame_range >= 0, 'frame_range can not be a negative value.'
            frame_range = [-frame_range, frame_range]
        elif isinstance(frame_range, list):
            assert len(frame_range) == 2, 'The length must be 2.'
            assert frame_range[0] <= 0 and frame_range[1] >= 0
            for i in frame_range:
                assert isinstance(i, int), 'Each element must be int.'
        else:
            raise TypeError('The type of frame_range must be int or list.')

        if 'test' in method and \
                (frame_range[1] - frame_range[0]) != num_ref_imgs:
            logger.info(
                'Warning:'
                "frame_range[1] - frame_range[0] isn't equal to num_ref_imgs."
                'Set num_ref_imgs to frame_range[1] - frame_range[0].')
            self.ref_img_sampler[
                'num_ref_imgs'] = frame_range[1] - frame_range[0]

        if (not self.load_as_video) or img_info.get('frame_id', -1) < 0 \
                or (frame_range[0] == 0 and frame_range[1] == 0):
            ref_img_infos = []
            for i in range(num_ref_imgs):
                ref_img_infos.append(img_info.copy())
        else:
            vid_id, img_id, frame_id = img_info['video_id'], img_info[
                'id'], img_info['frame_id']
            img_ids = self.coco.get_img_ids_from_vid(vid_id)
            left = max(0, frame_id + frame_range[0])
            right = min(frame_id + frame_range[1], len(img_ids) - 1)

            ref_img_ids = []
            if method == 'uniform':
                valid_ids = img_ids[left:right + 1]
                if filter_key_img and img_id in valid_ids:
                    valid_ids.remove(img_id)
                num_samples = min(num_ref_imgs, len(valid_ids))
                ref_img_ids.extend(random.sample(valid_ids, num_samples))
            elif method == 'bilateral_uniform':
                assert num_ref_imgs % 2 == 0, \
                    'only support load even number of ref_imgs.'
                for mode in ['left', 'right']:
                    if mode == 'left':
                        valid_ids = img_ids[left:frame_id + 1]
                    else:
                        valid_ids = img_ids[frame_id:right + 1]
                    if filter_key_img and img_id in valid_ids:
                        valid_ids.remove(img_id)
                    num_samples = min(num_ref_imgs // 2, len(valid_ids))
                    sampled_inds = random.sample(valid_ids, num_samples)
                    ref_img_ids.extend(sampled_inds)
            elif method == 'test_with_adaptive_stride':
                if frame_id == 0:
                    stride = float(len(img_ids) - 1) / (num_ref_imgs - 1)
                    for i in range(num_ref_imgs):
                        ref_id = round(i * stride)
                        ref_img_ids.append(img_ids[ref_id])
            elif method == 'test_with_fix_stride':
                if frame_id == 0:
                    for i in range(frame_range[0], 1):
                        ref_img_ids.append(img_ids[0])
                    for i in range(1, frame_range[1] + 1):
                        ref_id = min(round(i * stride), len(img_ids) - 1)
                        ref_img_ids.append(img_ids[ref_id])
                elif frame_id % stride == 0:
                    ref_id = min(
                        round(frame_id + frame_range[1] * stride),
                        len(img_ids) - 1)
                    ref_img_ids.append(img_ids[ref_id])
                img_info['num_left_ref_imgs'] = abs(frame_range[0]) \
                    if isinstance(frame_range, list) else frame_range
                img_info['frame_stride'] = stride
            else:
                raise NotImplementedError

            ref_img_infos = []
            for ref_img_id in ref_img_ids:
                ref_img_info = self.coco.load_imgs([ref_img_id])[0]
                ref_img_info['filename'] = ref_img_info['file_name']
                ref_img_infos.append(ref_img_info)
            ref_img_infos = sorted(ref_img_infos, key=lambda i: i['frame_id'])

        if return_key_img:
            return [img_info, *ref_img_infos]
        else:
            return ref_img_infos
