# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Default model settings."""

from dataclasses import dataclass

from diffusers.schedulers import KarrasDiffusionSchedulers

from .constant import Literals


@dataclass
class DefaultSettings:
    """Default model settings."""

    text_encoder_type: str = Literals.CLIP_TEXT_MODEL
    scheduler_type: str = KarrasDiffusionSchedulers.DDPMScheduler.name
    scheduler_folder = "scheduler"
