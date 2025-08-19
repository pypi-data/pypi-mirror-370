# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from enum import IntEnum

logger = logging.getLogger(__name__)


class EVAL_STRATEGY(IntEnum):
    PER_OPTIM_STEPS = 1
    SAVED_CHECKPOINT_AND_MODEL = 0
    SAVED_CHECKPOINT = -1
    SAVED_MODEL = -2
    NO_EVAL = -3
