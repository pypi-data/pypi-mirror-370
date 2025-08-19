# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import torch
from typing import Callable

from .BaseCriterion import BaseCriterion


class GenericTorchCriterion(BaseCriterion):
    """
    A wrapper model for interfacing any generic pytorch criteria with MainzTrainer
    """

    def __init__(self, opt, criterion: Callable[..., torch.Tensor]):
        """
        Args:
            opt (dict): configuration dict provided by MainzTrainer
            criterion (Callable): pytorch criterion to be wrapped, usually a torch.nn.Module or \
                from torch.nn.functional
        """
        super(GenericTorchCriterion, self).__init__()
        self.opt = opt
        self.criterion = criterion

    def forward(self, *inputs, **kwargs):
        loss = self.criterion(*inputs, **kwargs)
        return loss
