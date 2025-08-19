# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Finetuning component multiclass classification model family defaults."""

from dataclasses import dataclass
from azureml.acft.image.components.finetune.defaults.task_defaults import (
    MultiClassClassificationDefaults,
)


@dataclass
class MultiClassVITDefaults(MultiClassClassificationDefaults):
    """
    This class contain trainer defaults specific to VIT model family for multiclass classification.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    _per_device_train_batch_size: int = 72
    _per_device_eval_batch_size: int = 72
    _learning_rate: float = 5.0249077359786836e-05
    _optim: str = "adamw_torch"
    _weight_decay: float = 6.933735771405163e-07
    _metric_for_best_model: str = "loss"


@dataclass
class MultiClassBEITDefaults(MultiClassClassificationDefaults):
    """
    This class contain trainer defaults specific to BEIT model family for multiclass classification.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    _per_device_train_batch_size: int = 72
    _per_device_eval_batch_size: int = 72
    _learning_rate: float = 9.973114624235077e-05
    _weight_decay: float = 1.1847040694703787e-07
    _metric_for_best_model: str = "loss"


@dataclass
class MultiClassSWINV2Defaults(MultiClassClassificationDefaults):
    """
    This class contain trainer defaults specific to SwinV2 model family for multiclass classification.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    _num_train_epochs: int = 5
    _per_device_train_batch_size: int = 12
    _per_device_eval_batch_size: int = 12
    _learning_rate: float = 3.388822145881516e-05
    _optim: str = "adafactor"
    _weight_decay: float = 1.6496304960471456e-08
    _metric_for_best_model: str = "loss"


@dataclass
class MultiClassDEITDefaults(MultiClassClassificationDefaults):
    """
    This class contain trainer defaults specific to Deit model family for multiclass classification.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    _per_device_train_batch_size: int = 60
    _per_device_eval_batch_size: int = 60
    _learning_rate: float = 5e-5
    _metric_for_best_model: str = "accuracy"


@dataclass
class MultiClassMobileVITDefaults(MultiClassClassificationDefaults):
    """
    This class contain trainer defaults specific to mobile vit model family for multiclass classification.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    _per_device_train_batch_size: int = 16
    _per_device_eval_batch_size: int = 16
    _learning_rate: float = 6.605687285815252e-05
    _weight_decay: float = 1.3211374571630504e-05
    _lr_scheduler_type: str = "constant"
    _label_smoothing_factor: float = 0.1
    _metric_for_best_model: str = "loss"
