# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import torch.nn as nn


class BaseCriterion(nn.Module):
    """
    The interfaces for classes extending this base class are not restricted (the methods and their
    signatures don't have to be same as the base class). They should have minimum assumption or dependency
    on other components in the system. Task classes can use them accordingly.
    """

    def __init__(self):
        """
        Initialize criterion model.
        Criterion model should have no trainable parameters.
        """
        super(BaseCriterion, self).__init__()

    def forward(self, *inputs, **kwargs):
        """
        Forward function of the criterion to calculate loss
        """
        raise NotImplementedError
