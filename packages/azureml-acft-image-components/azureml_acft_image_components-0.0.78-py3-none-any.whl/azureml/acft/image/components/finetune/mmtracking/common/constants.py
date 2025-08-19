# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File for adding all the constants required for MMTracking."""


class MmTrackingDatasetLiterals:
    """Constants for MMTracking dataset."""
    IMG = "img"
    IMG_METAS = "img_metas"
    GT_BBOXES = 'gt_bboxes'
    GT_LABELS = 'gt_labels'
    GT_CROWDS = 'gt_bboxes_ignore'
    GT_INSTANCE_IDS = 'gt_instance_ids'
    ORIGINAL_GT_BBOXES = 'original_gt_bboxes'
    DETECTION_BBOXES = "det_bboxes"
    DETECTION_LABELS = "det_labels"
    TRACKING_BBOXES = "track_bboxes"
    TRACKING_LABELS = "track_labels"
    IMAGE_ORIGINAL_SHAPE = "ori_shape"
    DUMMY_LABELS = "dummy_labels"

    VIDEO_DETAILS = "video_details"
    VIDEO_NAME = "video_name"
    FRAME_ID = "frame_id"
    IMAGE_DETAILS = "image_details"
    WIDTH = "width"
    HEIGHT = "height"
    LOCAL_IMAGE_URL = "local_image_url"

    IS_VIDEO_DATA = "is_video_data"
    IMAGE_INFO = "img_info"
    IMAGE_ID = "image_id"
    ANN_INFO = "ann_info"
    IMAGE_PREFIX = "img_prefix"
    BBOX_FIELDS = "bbox_fields"
    BBOX = "bbox"
    BBOXES = "bboxes"
    AREA = "area"
    CATEGORY_ID = "category_id"
    INSTANCE_ID = "instance_ids"
    IS_CROWD = "iscrowd"


class MmTrackingConfigLiterals:
    """Constants for MMTracking config."""
    NUM_CLASSES = "num_classes"
    BOX_SCORE_THRESHOLD = "score_thr"
    IMAGE_SCALE = "img_scale"
    INPUT_SIZE = "input_size"
