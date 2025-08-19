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

"""Dataset for MMDetection"""

import torch
import numpy as np
import albumentations

from PIL.Image import Image
from dataclasses import asdict
try:
    # mmdet version 3.x
    from mmdet.structures.mask import BitmapMasks
except ImportError:
    # mmdet version 2.x
    # temp hack to solve version discrepency in mmdet package
    from mmdet.core.mask import BitmapMasks
from typing import Union, Dict, Any, Callable, Tuple, Optional, List
from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.common.constants.augmentation_constants import (
    AlbumentationParamNames,
)
from azureml.acft.image.components.finetune.common.mlflow.common_constants import (
    AlbumentationParameterNames
)
from azureml.acft.image.components.finetune.common.constants.constants import (
    DetectionDatasetLiterals,
    ImageDataItemLiterals
)
from azureml.acft.image.components.finetune.common.data.runtime_detection_dataset_adapter import (
    RuntimeDetectionDatasetAdapter,
)
from azureml.acft.image.components.finetune.common.mlflow.common_constants import MmDetectionDatasetLiterals

from azureml.acft.image.components.finetune.mmdetection.common.image_metadata import (
    ImageMetadata,
)

logger = get_logger_app(__name__)


class MmObjectDetectionDataset(RuntimeDetectionDatasetAdapter):
    """ Dataset for Object Detection Models from MMDetection """

    SUPPORTED_TRANSFORM_LIB_NAME_MAPPING = {
        albumentations.core.composition.Compose: AlbumentationParamNames.LIB_NAME
    }

    def __getitem__(self, index: int) -> Union[Dict[str, Any], None]:
        """Get item by index

        :param index: Index of object
        :type index: int
        :return: Item at Index
        :rtype: dict, None
        """
        image, training_labels, image_info = super(
            MmObjectDetectionDataset, self
        ).__getitem__(index)

        if image is None:
            logger.info("Image was not found for a data point in the batch, the data point is marked as invalid.")
            return None

        if training_labels[DetectionDatasetLiterals.BOXES].shape[0] == 0:
            # empty training labels tensor
            logger.info(
                "Bounding boxes were not found for a data point in the batch, the data point is marked as invalid."
            )
            return None

        gtbboxes = training_labels[DetectionDatasetLiterals.BOXES]
        original_gtbboxes = gtbboxes.clone()
        gtlabels = training_labels[DetectionDatasetLiterals.LABELS]
        gtmasks = [mask for mask in training_labels[DetectionDatasetLiterals.MASKS].numpy()] \
            if DetectionDatasetLiterals.MASKS in training_labels else None
        original_gtmasks = gtmasks or None
        c, h, w = image.shape
        ori_shape = (h, w, c)
        resized_image_height, resized_image_width = ori_shape[0], ori_shape[1]
        # Convert np.ndarray to List[np.ndarray] since albumentation expects list[np.ndarray]
        if hasattr(self, DetectionDatasetLiterals.TRANSFORM) and self.transform is not None:
            transformed = self._apply_transform(
                # Move channel to last dimension. i.e. (C,H,W) to (H,W,C)
                image=image.numpy().transpose(1, 2, 0),
                bboxes=gtbboxes,
                labels=gtlabels,
                masks=gtmasks
            )
            image = transformed[ImageDataItemLiterals.ALBUMENTATIONS_IMAGE_KEY]
            # The transformed image is first resized(using constraint resize) and then padded to make divisible by
            # stride(32 by default).
            # The resized_width and resized_height is the image size after resizing(before padding).
            resized_image_width = transformed[AlbumentationParameterNames.IMAGE_METADATA][
                AlbumentationParameterNames.RESIZED_WIDTH
            ]
            resized_image_height = transformed[AlbumentationParameterNames.IMAGE_METADATA][
                AlbumentationParameterNames.RESIZED_HEIGHT
            ]
            if isinstance(image, np.ndarray):
                # Move channel to first dimension. i.e. (H,W,C) to (C,H,W)
                image = torch.from_numpy(image.transpose(2, 0, 1))

            gtbboxes = transformed[ImageDataItemLiterals.ALBUMENTATIONS_BBOXES_KEY]
            if not torch.is_tensor(gtbboxes):
                gtbboxes = torch.as_tensor(gtbboxes, dtype=torch.float32)
            gtlabels = transformed[AlbumentationParameterNames.CLASS_LABELS]
            if not torch.is_tensor(gtlabels):
                gtlabels = torch.as_tensor(gtlabels, dtype=torch.long)
            gtmasks = transformed[DetectionDatasetLiterals.MASKS]

        channels, height, width = image.shape

        img_metas = ImageMetadata(ori_shape=(height, width, channels),
                                  img_shape=(resized_image_height, resized_image_width),
                                  filename=image_info[DetectionDatasetLiterals.IMAGEFILENAME],
                                  ori_filename=image_info[DetectionDatasetLiterals.IMAGEFILENAME],
                                  raw_dimensions=ori_shape)

        example = {
            MmDetectionDatasetLiterals.IMG: image,
            MmDetectionDatasetLiterals.IMG_METAS: asdict(img_metas),
            MmDetectionDatasetLiterals.GT_BBOXES: gtbboxes,
            MmDetectionDatasetLiterals.GT_LABELS: gtlabels,
            MmDetectionDatasetLiterals.GT_CROWDS: torch.tensor(
                [bool(is_crowd) for is_crowd in image_info[DetectionDatasetLiterals.ISCROWD]]
            ),
            # Untransformed ground truth bounding boxes. Used for validation metrics calculation.
            MmDetectionDatasetLiterals.ORIGINAL_GT_BBOXES: original_gtbboxes
        }

        if DetectionDatasetLiterals.MASKS in training_labels:
            masks = BitmapMasks(
                gtmasks,
                height=height,
                width=width,
            )
            example[MmDetectionDatasetLiterals.GT_MASKS] = masks
            example[MmDetectionDatasetLiterals.ORIGINAL_GT_MASKS] = BitmapMasks(
                original_gtmasks,
                height=ori_shape[0],
                width=ori_shape[1],
            )

        return example

    def _apply_transform(self,
                         image: np.ndarray,
                         bboxes: torch.Tensor,
                         labels, masks: torch.Tensor = None) -> \
            Tuple[Image, torch.Tensor, Optional[torch.Tensor]]:
        """Apply transform

        :param image: Input image
        :type image: np.ndarray

        :return: An image with transform applied, if transform type is supported. Otherwise, raise error.
        :rtype: np.ndarray
        """
        return self.apply_transform_factory[self.augmentation_lib_name](
            image=image, bboxes=bboxes, labels=labels, masks=masks
        )

    def set_transform(self, transform: Callable) -> None:
        """Set transform to the specified transform"""
        self.transform = transform

        # check supported augmentation transforms
        self._check_supported_transform_type()

        # Get augmentation library name
        self._set_augmentation_library_name_from_transform()

        # Prepare an apply transform factory
        self._set_apply_transform_factory()

    def _check_supported_transform_type(self) -> None:
        """Check supported transform type

        :return: None
        :rtype: None
        """
        # Check for supported augmentation transform
        if self.transform and not any(
            [
                isinstance(self.transform, supported_transform)
                for supported_transform in self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys()
            ]
        ):
            raise NotImplementedError(
                f"{type(self.transform)} is not supported. "
                f"Only {list( self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys())} are supported for now."
            )

    def _set_augmentation_library_name_from_transform(self):
        """Extract augmentation library name based on the transform and set it."""
        # Get augmentation library name
        for supported_transform in self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING.keys():
            if isinstance(self.transform, supported_transform):
                self.augmentation_lib_name = self.SUPPORTED_TRANSFORM_LIB_NAME_MAPPING[
                    supported_transform
                ]
                break

    def _set_apply_transform_factory(self):
        """Prepare apply_transform factory."""
        # Prepare an apply transform factory
        self.apply_transform_factory = {
            AlbumentationParamNames.LIB_NAME: self._albumentations_apply_transform
        }

    def _albumentations_apply_transform(self,
                                        image: np.ndarray,
                                        bboxes: torch.Tensor,
                                        labels: List[torch.Tensor],
                                        masks: Optional[List[torch.Tensor]] = None) -> Dict[str, Any]:
        """Apply albumentations transform

        :param image: Input image
        :type image: np.ndarray
        :param bboxes
        :type bboxes: torch.Tensor
        :param labels: List of labels
        :type labels: List[torch.Tensor]
        :param masks: List of mask if present
        :type labels: Optional[List[torch.Tensor]]

        :return: A dictonary containing the transformed image, transformed bbox, transformed mask and
        transformed labels.
        :rtype: Dict[str, Any]
        """
        return self.transform(image=image, bboxes=bboxes, class_labels=labels, masks=masks, image_metadata=dict())
