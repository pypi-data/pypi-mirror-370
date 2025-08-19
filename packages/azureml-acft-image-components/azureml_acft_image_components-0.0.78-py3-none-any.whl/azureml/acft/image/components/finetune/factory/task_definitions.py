# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Task definitions for all Image tasks"""


class Tasks:
    "Tasks supported for All Frameworks"

    HF_MULTI_CLASS_IMAGE_CLASSIFICATION = "image-classification"
    HF_MULTI_LABEL_IMAGE_CLASSIFICATION = "image-classification-multilabel"
    MM_OBJECT_DETECTION = "image-object-detection"
    MM_INSTANCE_SEGMENTATION = "image-instance-segmentation"
    MM_MULTI_OBJECT_TRACKING = "video-multi-object-tracking"
    HF_SD_TEXT_TO_IMAGE = "stable-diffusion-text-to-image"
