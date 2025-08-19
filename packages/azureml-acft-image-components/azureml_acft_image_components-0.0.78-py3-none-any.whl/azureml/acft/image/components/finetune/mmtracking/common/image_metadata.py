# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Image metadata mapping to pass in MMTracking models """

import numpy as np
from dataclasses import dataclass
from typing import Tuple


@dataclass
class ImageMetadata:
    """ Dataclass for maintaining the metadata dictionary as required for MM detection models.
    The keys of metadata dictionary is same as the property name."""

    ori_shape: Tuple[int, int, int]
    img_shape: Tuple[int, int, int] = None
    pad_shape: Tuple[int, int, int] = None
    scale_factor: np.ndarray = np.array([1, 1, 1, 1])
    flip: bool = False
    flip_direction: str = None
    filename: str = None
    ori_filename: str = None

    def __post_init__(self):
        """If image shape after resizing and padding is not provided then assign it with original shape"""
        self.img_shape = self.ori_shape or self.img_shape
        self.pad_shape = self.ori_shape or self.pad_shape
