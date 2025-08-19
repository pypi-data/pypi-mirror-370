# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Finetuning component task-level defaults."""

from dataclasses import dataclass
from azureml.acft.image.components.finetune.defaults.hf_trainer_defaults import (
    HFTrainerDefaults,
)


@dataclass
class MultiClassClassificationDefaults(HFTrainerDefaults):
    """
    This class contain trainer defaults specific to multiclass classification models.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    _num_train_epochs: int = 15
    _lr_scheduler_type: str = "cosine"
    _metric_for_best_model: str = "accuracy"


@dataclass
class MultiLabelClassificationDefaults(HFTrainerDefaults):
    """
    This class contain trainer defaults specific to multilabel classification models.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    _num_train_epochs: int = 15
    _lr_scheduler_type: str = "cosine"
    _metric_for_best_model: str = "iou"
    _label_smoothing_factor: float = 0.0
    # Setting it to 0.0 as label_smoothing_factor is not supported for multi-label classification.


@dataclass
class ObjectDetectionDefaults(HFTrainerDefaults):
    """
    This class contain trainer defaults specific to object detection models.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    _image_max_size: int = -1
    _image_min_size: int = -1
    _num_train_epochs: int = 10
    _per_device_train_batch_size: int = 2
    _per_device_eval_batch_size: int = 2
    _optim: str = "adamw_torch"
    _learning_rate: float = 1e-5
    _warmup_steps: int = 1
    _weight_decay: float = 1.4679630586541725e-05
    _lr_scheduler_type: str = "cosine"
    _metric_for_best_model: str = "mean_average_precision"
    _iou_threshold: float = 0.5
    _box_score_threshold: float = 0.3


@dataclass
class InstanceSegmentationDefaults(HFTrainerDefaults):
    """
    This class contain trainer defaults specific to instance segmentation models.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    _image_max_size: int = -1
    _image_min_size: int = -1
    _num_train_epochs: int = 10
    _per_device_train_batch_size: int = 1
    _per_device_eval_batch_size: int = 1
    _optim: str = "adamw_torch"
    _learning_rate: float = 9.674567440430093e-05
    _warmup_steps: int = 1
    _weight_decay: float = 6.335073210739572e-06
    _lr_scheduler_type: str = "cosine"
    _metric_for_best_model: str = "mean_average_precision"
    _iou_threshold: float = 0.5
    _box_score_threshold: float = 0.3


@dataclass
class MultiObjectTrackingDefaults(HFTrainerDefaults):
    """
    This class contain trainer defaults specific to multi-object tracking models.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    # todo: updated defaults for object tracking after benchmarking
    _per_device_train_batch_size: int = 1
    _per_device_eval_batch_size: int = 1
    _learning_rate: float = 1e-4
    _optim: str = "sgd"
    _num_train_epochs: int = 10
    _warmup_steps: int = 1
    _weight_decay: float = 1.4679630586541725e-05
    _lr_scheduler_type: str = "cosine"
    _metric_for_best_model: str = "MOTA"
    _iou_threshold: float = 0.5
    _box_score_threshold: float = 0.3
    _image_width: int = -1
    _image_height: int = -1
