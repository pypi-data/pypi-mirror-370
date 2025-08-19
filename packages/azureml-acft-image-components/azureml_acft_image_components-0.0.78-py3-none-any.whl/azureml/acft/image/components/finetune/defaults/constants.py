# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Finetuning component default contants."""


from dataclasses import dataclass
from azureml.acft.image.components.finetune.defaults.task_defaults import (
    MultiClassClassificationDefaults,
    MultiLabelClassificationDefaults,
    InstanceSegmentationDefaults,
    ObjectDetectionDefaults,
    MultiObjectTrackingDefaults,
)
from azureml.acft.image.components.finetune.defaults.multiclass_classification_models_defaults import (
    MultiClassBEITDefaults,
    MultiClassDEITDefaults,
    MultiClassVITDefaults,
    MultiClassSWINV2Defaults,
    MultiClassMobileVITDefaults,
)
from azureml.acft.image.components.finetune.defaults.multilabel_classification_models_defaults import (
    MultiLabelBEITDefaults,
    MultiLabelDEITDefaults,
    MultiLabelMobileVITDefaults,
    MultiLabelSWINV2Defaults,
    MultiLabelVITDefaults,
)
from azureml.acft.image.components.model_selector.constants import ImageModelSelectorConstants
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.defaults.multi_object_tracking_models_defaults import (
    ByteTrackDefaults,
)


@dataclass
class TrainingDefaultsConstants:
    """
    This class contains constants for the TrainingDefaults class.
    Note: Provide mapping of model name to dataclass and task to dataclass.
    """

    # model name to model family mapping
    # if a model name matches to multiple model families, then provide a dict of task to model family
    # mapping for that model name else provide a single model family directly
    MODEL_NAME_TO_DATACLASS_MAPPING = {
        "google/vit-base-patch16-224": {
            Tasks.HF_MULTI_CLASS_IMAGE_CLASSIFICATION: MultiClassVITDefaults,
            Tasks.HF_MULTI_LABEL_IMAGE_CLASSIFICATION: MultiLabelVITDefaults,
        },
        "microsoft/beit-base-patch16-224-pt22k-ft22k": {
            Tasks.HF_MULTI_CLASS_IMAGE_CLASSIFICATION: MultiClassBEITDefaults,
            Tasks.HF_MULTI_LABEL_IMAGE_CLASSIFICATION: MultiLabelBEITDefaults,
        },
        "microsoft/swinv2-base-patch4-window12-192-22k": {
            Tasks.HF_MULTI_CLASS_IMAGE_CLASSIFICATION: MultiClassSWINV2Defaults,
            Tasks.HF_MULTI_LABEL_IMAGE_CLASSIFICATION: MultiLabelSWINV2Defaults,
        },
        "facebook/deit-base-patch16-224": {
            Tasks.HF_MULTI_CLASS_IMAGE_CLASSIFICATION: MultiClassDEITDefaults,
            Tasks.HF_MULTI_LABEL_IMAGE_CLASSIFICATION: MultiLabelDEITDefaults,
        },
        "apple/mobilevit-small": {
            Tasks.HF_MULTI_CLASS_IMAGE_CLASSIFICATION: MultiClassMobileVITDefaults,
            Tasks.HF_MULTI_LABEL_IMAGE_CLASSIFICATION: MultiLabelMobileVITDefaults,
        },
        "bytetrack_yolox_x_crowdhuman_mot17-private-half": ByteTrackDefaults,
    }

    TASK_TO_DATACLASS_MAPPING = {
        Tasks.HF_MULTI_CLASS_IMAGE_CLASSIFICATION: MultiClassClassificationDefaults,
        Tasks.HF_MULTI_LABEL_IMAGE_CLASSIFICATION: MultiLabelClassificationDefaults,
        Tasks.MM_INSTANCE_SEGMENTATION: InstanceSegmentationDefaults,
        Tasks.MM_OBJECT_DETECTION: ObjectDetectionDefaults,
        Tasks.MM_MULTI_OBJECT_TRACKING: MultiObjectTrackingDefaults,
    }

    MODEL_DEFAULTS_FILE = "model_defaults.json"
    MODEL_METADATA_FILE = ImageModelSelectorConstants.MODEL_METAFILE_NAME
    MODEL_NAME_KEY = "model_name"


@dataclass
class HFTrainerDefaultsKeys:
    """
    This class contains the keys for the Hugging Face trainer defaults.
    Note: Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    NUM_TRAIN_EPOCHS = "num_train_epochs"
    PER_DEVICE_TRAIN_BATCH_SIZE = "per_device_train_batch_size"
    PER_DEVICE_EVAL_BATCH_SIZE = "per_device_eval_batch_size"
    LEARNING_RATE = "learning_rate"
    OPTIM = "optim"
    GRADIENT_ACCUMULATION_STEPS = "gradient_accumulation_steps"
    MAX_STEPS = "max_steps"
    WARMUP_STEPS = "warmup_steps"
    WEIGHT_DECAY = "weight_decay"
    ADAM_BETA1 = "adam_beta1"
    ADAM_BETA2 = "adam_beta2"
    ADAM_EPSILON = "adam_epsilon"
    LR_SCHEDULING_TYPE = "lr_scheduler_type"
    METRIC_FOR_BEST_MODEL = "metric_for_best_model"
    LABEL_SMOOTHING_FACTOR = "label_smoothing_factor"
    MAX_GRAD_NORM = "max_grad_norm"
    SAVE_SAFETENSORS = "save_safetensors"


@dataclass
class NonHfTrainerDefaultsKeys:
    """
    This class contains the keys for the non Hugging Face trainer defaults.

    """

    IMAGE_WIDTH = "image_width"
    IMAGE_HEIGHT = "image_height"
    IMAGE_MIN_SIZE = "image_min_size"
    IMAGE_MAX_SIZE = "image_max_size"
    # adamw hyperparameters are not part of HF Training Arguments but part of Namespace
    ADAM_BETA1 = "adam_beta1"
    ADAM_BETA2 = "adam_beta2"
    ADAM_EPSILON = "adam_epsilon"
    IOU_THRESHOLD = "iou_threshold"
    BOX_SCORE_THRESHOLD = "box_score_threshold"
    APPLY_ORT = "apply_ort"
    APPLY_DEEPSPEED = "apply_deepspeed"
