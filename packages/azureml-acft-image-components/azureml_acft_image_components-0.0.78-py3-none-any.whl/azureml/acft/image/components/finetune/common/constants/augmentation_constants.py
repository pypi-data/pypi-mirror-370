# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image finetune component - augmentation related constants."""

from dataclasses import dataclass


@dataclass
class AugmentationConfigKeys:
    """Keys in augmentation configs"""

    TRAINING_PHASE_KEY = "train"
    VALIDATION_PHASE_KEY = "validation"
    VALID_PHASE_KEY = "val"
    MODEL_KEY = "model"
    AUGMENTATION_LIBRARY_NAME = "augmentation_library_name"
    FUNC_NAME = "augmentation_function_name"
    FUNC_PARAMS_DICT = "augmentation_function_params_dict"
    PHASE_NAME = "phase_name"
    TASK_PARAM_DICT = "task_input_params_dict"


@dataclass
class AugmentationConfigFileNames:
    """Augmentation configs inside config folder at
    src/azureml-acpt-image-components/azureml/train/vision/components/finetune/common/augmentation/
    """

    CLASSIFICATION_ALBUMENTATIONS_CONFIG = "configs/albumentations_classification.yaml"
    OD_IS_ALBUMENTATIONS_CONFIG = "configs/albumentations_od_is.yaml"


@dataclass
class AlbumentationParamNames:
    """Albumentations parameter and function names"""

    LIB_NAME = "albumentations"

    HEIGHT_KEY = "height"
    WIDTH_KEY = "width"

    NORMALIZE_FUNC_NAME = "Normalize"
    MEAN_KEY = "mean"
    STD_KEY = "std"
    PAD_HEIGHT_DIVISOR_KEY = "pad_height_divisor"
    PAD_WIDTH_DIVISOR_KEY = "pad_width_divisor"
    CONSTRAINT_RESIZE_KEY = "img_scale"
    KEEP_RATIO = "keep_ratio"
    PAD_IF_NEEDED_FUNC_NAME = "PadIfNeeded"


@dataclass
class TorchvisionParamNames:
    """Torchvision parameter and function names"""

    LIB_NAME = "torchvision"


@dataclass
class OpenmmlabAugmentationNames:
    """Openmmlab data augmentation names"""
    LOAD_ANNOTATIONS = "LoadAnnotations"
    LOAD_TRACK = "LoadTrack"
    VIDEO_COLLECT_FOR_MODELS = "VideoCollectForModel"
