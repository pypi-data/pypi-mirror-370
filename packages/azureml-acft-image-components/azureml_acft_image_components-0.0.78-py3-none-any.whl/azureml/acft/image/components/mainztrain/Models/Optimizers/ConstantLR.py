# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from torch.optim.lr_scheduler import LambdaLR

logger = logging.getLogger(__name__)


def ConstantLR(optimizer, last_epoch=-1):
    """
    Create a schedule with a constant learning rate.
    """
    return LambdaLR(optimizer, lambda _: 1, last_epoch=last_epoch)
