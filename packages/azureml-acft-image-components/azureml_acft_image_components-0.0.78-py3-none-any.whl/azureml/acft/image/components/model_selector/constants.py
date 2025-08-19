# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Constants used for image model selector component."""


class ImageModelSelectorConstants:
    """String constants for model selector component."""

    ARTIFACTS_DIR = "artifacts"
    MODEL_FAMILY = "model_family"
    MODEL_METAFILE_NAME = "model_metadata.json"

    MMLAB_MODEL_WEIGHTS_PATH_OR_URL = "model_weights_path_or_url"
    MMLAB_MODEL_METAFILE_PATH = "model_metafile_path"
    MMD_MODEL_CHECKPOINT_FILE_NAME = "mmd_pytorch_model.pth"
    MODEL_DEFAULTS_PATH = "model_defaults_path"


class MMDetectionModelZooConfigConstants:
    """
    Constants for MMDetection model zoo config.
    """

    MODEL_ZOO_MODELS = "Models"
    MODEL_ZOO_MODEL_NAME = "Name"
    MODEL_ZOO_CONFIG = "Config"
    MODEL_ZOO_WEIGHTS = "Weights"
    RESULTS = "Results"
    TASK = "Task"


class MMDSupportedTasks:
    """Supported tasks for MMDetection."""

    OBJECT_DETECTION = "object detection"
    INSTANCE_SEGMENTATION = "instance segmentation"


class MMTSupportedTasks:
    """Supported tasks for MMTracking"""

    MULTI_OBJECT_TRACKING = "multiple object tracking"
