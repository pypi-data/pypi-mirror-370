# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Image metadata mapping to pass in MMDetection models """

import numpy as np
from dataclasses import dataclass
from typing import Tuple


@dataclass
class ImageMetadata:
    """ Dataclass for maintaining the metadata dictionary as required for MM detection models.
    The keys of metadata dictionary is same as the property name."""

    ori_shape: Tuple[int, int, int]         # Dimension of the transformed image H x W x C. This is the shape of the
    # image after resizing and padding. If we set it to the original image shape i.e. shape before transformation
    # then the MMD model is not able to learn and the eval_mAP is always 0.0.
    img_shape: Tuple[int, int, int] = None  # Dimension of the image after ConstraintResize transformation.
    pad_shape: Tuple[int, int, int] = None  # Dimension of the tranformed image after padding. Please note that padding
    # is applied after ConstraintResize transformation, so pad_shape is always greater than or equal to img_shape.
    raw_dimensions: Tuple[int, int] = None   # Dimension of the raw image H x W. This is used to resize the predicted
    # mask to the original image size.
    scale_factor: np.ndarray = np.array([1, 1])
    flip: bool = False
    flip_direction: str = None
    filename: str = None
    ori_filename: str = None
    border: Tuple[int, int, int, int] = (0, 0, 0, 0)

    def __post_init__(self):
        """If image shape after resizing and padding is not provided then assign it with original shape"""
        self.img_shape = self.img_shape or self.ori_shape
        self.pad_shape = self.pad_shape or self.ori_shape
