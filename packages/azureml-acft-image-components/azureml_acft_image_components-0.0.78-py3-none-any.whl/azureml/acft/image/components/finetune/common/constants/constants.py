# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File for adding all the constants"""

from dataclasses import dataclass


@dataclass
class HfConstants:
    """A class to represent constants for hugging face files."""

    HFModelType = "hugging_face"


@dataclass
class VisionDatasetConstants:
    """A class to represent constants for Vision dataset constants."""

    DEFAULT_VALIDATION_SIZE = 0.2


@dataclass
class ImageDataFrameConstants:
    """A class to represent constants for image dataframe."""

    LABEL_COLUMN_PROPERTY = "_Label_Column:Label_"
    DEFAULT_LABEL_COLUMN_NAME = "label"
    DEFAULT_IMAGE_DETAILS_COLUMN_NAME = "image_details"
    COLUMN_PROPERTY = "Column"
    IMAGE_COLUMN_PROPERTY = "_Image_Column:Image_"
    DEFAULT_IMAGE_COLUMN_NAME = "image_url"
    IMAGE_DETAILS_WIDTH = "width"
    IMAGE_DETAILS_HEIGHT = "height"


@dataclass
class ImageDataItemLiterals:
    """A class to represent literals for image data item."""
    DEFAULT_LABEL_KEY = "label"
    DEFAULT_IMAGE_KEY = "image"

    ALBUMENTATIONS_IMAGE_KEY = "image"
    ALBUMENTATIONS_BBOXES_KEY = "bboxes"

    HF_PIXEL_VALUES_KEY = "pixel_values"
    HF_LABELS_KEY = "labels"
    HF_PATH_KEY = "path"
    HF_BYTES_KEY = "bytes"


@dataclass
class InferenceParameters:
    """A class for inferece parameters."""

    DEFAULT_PROB_THRESHOLD = 0.5
    DEFAULT_IOU_THRESHOLD = 0.5
    DEFAULT_BOX_SCORE_THRESHOLD = 0.3


@dataclass
class SettingParameters:
    """A class for default settings."""

    REMOVE_UNUSED_COLUMNS = False
    DEFAULT_OUTPUT_DIR = "output"
    DEFAULT_MLFLOW_OUTPUT = "mlflow_output"
    DEFAULT_PYTORCH_OUTPUT = "pytorch_output"
    DEFAULT_PRECISION = 32


class SettingLiterals:
    """A class for settings literals."""

    SAVE_AS_MLFLOW_MODEL = "save_as_mlflow_model"
    PROBLEM_TYPE = "problem_type"
    TRAIN_MLTABLE_PATH = "train_mltable_path"
    TASK_NAME = "task_name"
    VALIDATION_MLTABLE_PATH = "valid_mltable_path"
    PROB_THRESHOLD = "prob_threshold"
    REMOVE_UNUSED_COLUMNS = "remove_unused_columns"
    LABEL_NAMES = "label_names"
    LABEL2ID = "label2id"
    ID2LABEL = "id2label"
    AUTO_HYPERPARAMETER_SELECTION = "auto_hyperparameter_selection"
    MODEL_NAME_OR_PATH = "model_name_or_path"
    APPLY_LORA = "apply_lora"

    # Model family
    MODEL_FAMILY = "model_family"
    MODEL_NAME = "model_name"

    # Augmentations
    APPLY_AUGMENTATIONS = "apply_augmentations"

    # Input image size
    IMAGE_HEIGHT = "image_height"
    IMAGE_WIDTH = "image_width"

    # Min and Max image size
    IMAGE_MIN_SIZE = "image_min_size"
    IMAGE_MAX_SIZE = "image_max_size"

    # Dataset
    USE_BG_LABEL = "use_bg_label"
    TRAIN_VAL_SPLIT_RATIO = "train_val_split_ratio"
    OUTPUT_DIR = "output_dir"
    IGNORE_DATA_ERRORS = "ignore_data_errors"
    IOU_THRESHOLD = "iou_threshold"
    NUM_LABELS = "num_labels"
    BOX_SCORE_THRESHOLD = "box_score_threshold"
    LABEL_COLUMN_NAME = "label_column_name"
    STREAM_IMAGE_FILES = "stream_image_files"

    # Optimizer
    WEIGHT_DECAY = "weight_decay"
    LR = "lr"
    OPTIMIZER = "optim"
    EXTRA_OPTIMIZER_ARGS = "extra_optim_args"
    PARAMS = "params"
    NESTEROV = "nesterov"
    MOMENTUM = "momentum"
    PRECISION = "precision"

    # trainer
    DDP_FIND_UNUSED_PARAMETERS = "ddp_find_unused_parameters"

    # sd
    TEXT_ENCODER = "text_encoder"
    AZML_SD_PIPELINE = "azml_sd_pipeline"


@dataclass
class HfProcessorParamNames:
    """Hugging face parameter names, primariy in preprocessing_config.json for models"""

    # Size related params from preprocess_config.json / FeatureExtractor
    DO_CENTER_CROP_KEY = "do_center_crop"
    CROP_SIZE_KEY = "crop_size"
    DO_RESIZE_KEY = "do_resize"
    SIZE_KEY = "size"
    HEIGHT_KEY = "height"
    WIDTH_KEY = "width"
    SHORTEST_EDGE_KEY = "shortest_edge"
    LONGEST_EDGE_KEY = "longest_edge"

    # Normalization related params from preprocess_config.json / FeatureExtractor
    MEAN_KEY = "image_mean"
    STD_KEY = "image_std"


@dataclass
class MmLabPreprocessorParamNames:
    """MMlab parameter names, primariy for model preprocessing config."""

    MEAN_KEY = "mean"
    STD_KEY = "std"


@dataclass
class MmDetectionPreprocessorParamNames:
    """MMDetection parameter names, primariy for model preprocessing config.
    """

    MEAN_KEY = "mean"
    STD_KEY = "std"
    TO_RGB_KEY = "to_rgb"
    PIPELINE = "pipeline"
    NORMALIZE = "Normalize"
    TRANSFORMS = "transforms"
    RESIZE = "Resize"
    PAD_SIZE_DIVISOR = "pad_size_divisor"
    MULTISCALE_FLIP_AUG = "MultiScaleFlipAug"
    DATA_PREPROCESSOR = "data_preprocessor"


class DetectionDatasetLiterals:
    """Literals for detection dataset"""

    HEIGHT = "height"
    WIDTH = "width"
    MASKS = "masks"
    BOXES = "boxes"
    LABELS = "labels"
    ISCROWD = "iscrowd"
    IMAGEFILENAME = "filename"
    TRANSFORM = "transform"
