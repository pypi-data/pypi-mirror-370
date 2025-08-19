# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Finetuning component HuggingFace Trainer defaults."""

from dataclasses import dataclass


@dataclass
class HFTrainerDefaults:
    """
    This class contain Hugging Face trainer defaults

    Note: This class is not meant to be used directly.
    Provide the defaults name consistently with the Hugging Face Trainer class.
    """

    _num_train_epochs: int = 3
    _per_device_train_batch_size: int = 8
    _per_device_eval_batch_size: int = 8
    _learning_rate: float = 5e-5
    _optim: str = "adamw_hf"
    _gradient_accumulation_steps: int = 1
    _max_steps: int = -1
    _warmup_steps: int = 0
    _weight_decay: float = 0.0
    _adam_beta1: float = 0.9
    _adam_beta2: float = 0.999
    _adam_epsilon: float = 1e-8
    _lr_scheduler_type: str = "linear"
    _metric_for_best_model: str = "loss"
    _label_smoothing_factor: float = 0.0
    _max_grad_norm: float = 1.0
    _apply_deepspeed: bool = False
    _apply_ort: bool = False
