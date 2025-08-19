# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File for adding all the hugging face related constants"""

from dataclasses import dataclass


@dataclass
class HfImageModelConstants:
    """Hf Image Model Constants"""

    HF_IMAGE_AUTO_MODEL_CLS = "AutoModelForImageClassification"
    HF_MODEL_CONFIG_IMAGE_SIZE_KEY = "image_size"


@dataclass
class HfImageInterfaceConstants:
    """Hf Image Interface Constants"""

    HF_IMAGE_MODEL_CLS = "hf_image_model_cls"


@dataclass
class HfProblemType:
    """problem types used by hugging face models internally"""

    SINGLE_LABEL_CLASSIFICATION = "single_label_classification"
    MULTI_LABEL_CLASSIFICATION = "multi_label_classification"
    OBJECT_DETECTION = "object_detection"
    INSTANCE_SEGMENTATION = "instance_segmentation"
    MULTI_OBJECT_TRACKING = "multi_object_tracking"
