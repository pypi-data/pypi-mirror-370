# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Diffusion default settings."""

from dataclasses import dataclass


@dataclass
class DataDefaults:
    """Data defaults for diffusion."""

    CLASS_DATA_DIR = "class_data_dir"
    NUM_CLASS_IMAGES = 100
    DATALOADER_WORKERS = 0
    PRIOR_GENERATION_PRECISION = "fp32"
    SAMPLE_BATCH_SIZE = 1
