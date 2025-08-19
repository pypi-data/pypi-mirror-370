# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File for adding all the constants required for MMDetection."""


class MmDetectionConfigLiterals:
    """Constants for MMDetection config."""
    NUM_CLASSES = "num_classes"
    BOX_SCORE_THRESHOLD = "score_thr"
    IOU_THRESHOLD = "iou_threshold"
    TRAIN_PIPELINE = "train_pipeline"
    TEST_PIPELINE = "test_pipeline"
    COLLECT = "Collect"
    TYPE = "type"
    KEYS = "keys"
    CLASSES = "CLASSES"
    META = "meta"
    STATE_DICT = "state_dict"
    MODEL = "model"


class MmDetectionModelLiterals:
    """Constants for MMDetection model."""
    WITH_SEMANTIC = "with_semantic"
    WITH_RPN = "with_rpn"
    ROI_HEAD = "roi_head"
    PANOPTIC_HEAD = "panoptic_head"
    TEACHER_CONFIG = "teacher_config"
    LANG_MODEL_NAME = "lang_model_name"
    BBOX_HEAD = "bbox_head"
    LOSS_CLS = "loss_cls"
    CLASS_WEIGHT = "class_weight"
