# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Finetuning component instance segmentation model family defaults."""

from dataclasses import dataclass
from azureml.acft.image.components.finetune.defaults.task_defaults import (
    InstanceSegmentationDefaults,
)


@dataclass
class RCNNDefaults(InstanceSegmentationDefaults):

    """
    This class contain trainer defaults specific to RCNN models.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    # todo: add the defaults for RCNN model family
