# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Finetuning component multilabel classification model family defaults."""

from dataclasses import dataclass
from azureml.acft.image.components.finetune.defaults.task_defaults import (
    MultiLabelClassificationDefaults,
)


@dataclass
class MultiLabelVITDefaults(MultiLabelClassificationDefaults):
    """
    This class contain trainer defaults specific to VIT model family for multilabel classification.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    Currently, multilabel classification defaults are same as multiclass classification defaults.
    """

    _per_device_train_batch_size: int = 72
    _per_device_eval_batch_size: int = 72
    _learning_rate: float = 5.0249077359786836e-05
    _optim: str = "adamw_torch"
    _weight_decay: float = 6.933735771405163e-07
    _metric_for_best_model: str = "loss"


@dataclass
class MultiLabelBEITDefaults(MultiLabelClassificationDefaults):
    """
    This class contain trainer defaults specific to BEIT model family for multilabel classification.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    Currently, multilabel classification defaults are same as multiclass classification defaults.
    """

    _per_device_train_batch_size: int = 72
    _per_device_eval_batch_size: int = 72
    _learning_rate: float = 9.973114624235077e-05
    _weight_decay: float = 1.1847040694703787e-07
    _metric_for_best_model: str = "loss"


@dataclass
class MultiLabelSWINV2Defaults(MultiLabelClassificationDefaults):
    """
    This class contain trainer defaults specific to SwinV2 model family for multilabel classification.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    Currently, multilabel classification defaults are same as multiclass classification defaults.
    """

    _num_train_epochs: int = 5
    _per_device_train_batch_size: int = 12
    _per_device_eval_batch_size: int = 12
    _learning_rate: float = 3.388822145881516e-05
    _optim: str = "adafactor"
    _weight_decay: float = 1.6496304960471456e-08
    _metric_for_best_model: str = "loss"


@dataclass
class MultiLabelDEITDefaults(MultiLabelClassificationDefaults):
    """
    This class contain trainer defaults specific to Deit model family for multilabel classification.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    Currrently, multilabel classification defaults are same as multiclass classification defaults.
    """

    _per_device_train_batch_size: int = 60
    _per_device_eval_batch_size: int = 60
    _learning_rate: float = 5e-5
    _metric_for_best_model: str = "accuracy"


@dataclass
class MultiLabelMobileVITDefaults(MultiLabelClassificationDefaults):
    """
    This class contain trainer defaults specific to mobile vit model family for multilabel classification.

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    Currrently, multilabel classification defaults are same as multiclass classification defaults.
    """

    _per_device_train_batch_size: int = 16
    _per_device_eval_batch_size: int = 16
    _learning_rate: float = 6.605687285815252e-05
    _weight_decay: float = 1.3211374571630504e-05
    _lr_scheduler_type: str = "constant"
    # Setting to 0.0 as label_smoothing_factor is not supported for multi-label classification.
    _label_smoothing_factor: float = 0.0
    _metric_for_best_model: str = "loss"
