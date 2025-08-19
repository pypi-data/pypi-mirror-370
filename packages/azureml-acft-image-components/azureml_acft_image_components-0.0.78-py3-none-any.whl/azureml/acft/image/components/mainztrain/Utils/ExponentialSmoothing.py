# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from collections import OrderedDict
import logging
import torch

logger = logging.getLogger(__name__)


class ExponentialSmoothingState(object):
    """Exponential moving average of model parameters.
    It maintains a smoothed copy of the model's parameter tensors.

    Args:
        model (torch.nn.Module): Model with parameters whose EMA will be kept.
        weight_smoothing_opt (dict): A dictionary with weight smoothing settings.
    """

    def __init__(self, model, weight_smoothing_opt):
        self.decay = weight_smoothing_opt["decay"]
        self.device = weight_smoothing_opt["device"]
        self.ref_batch_size_name, self.ref_batch_size_value = weight_smoothing_opt.get(
            "ref_batch_size", (None, 1)
        )

        # Register model parameters
        self.load_shadow_from_model(model, clone_params=True)

    @torch.no_grad()
    def load_shadow_from_model(self, model, clone_params=False):
        self.shadow = OrderedDict()
        for name, param in model.named_parameters():
            if param.requires_grad:
                if clone_params:
                    self.shadow[name] = param.data.clone().detach().to(self.device)
                else:
                    self.shadow[name] = param.data.to(self.device)

    @torch.no_grad()
    def step(self, model, batch_size, total_size):
        decay = self.decay ** (batch_size / self.ref_batch_size_value)
        steps = total_size / self.ref_batch_size_value
        # Decay parameters more quickly at the beginning to avoid retaining the random initialization
        decay = min(decay, (steps + 1.0) / (steps + 10))
        for name, param in model.named_parameters():
            if param.requires_grad:
                assert name in self.shadow
                self.shadow[name].copy_(
                    (1.0 - decay) * param.detach().to(self.device)
                    + decay * self.shadow[name]
                )


class AssignSmoothingState(object):
    """
    Context manager for applying smoothing state to a model
    """

    def __init__(self, smoothing_state, model):
        self.model = model
        self.smoothing_state = smoothing_state

    def __enter__(self):
        """Assign smoothed parameter values to the
        respective parameters.
        """
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                assert name in self.smoothing_state.shadow
                self.swap_tensors(self.smoothing_state.shadow[name], param.data)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Restore original parameter values to the model."""
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                self.swap_tensors(self.smoothing_state.shadow[name], param.data)

    @torch.no_grad()
    def swap_tensors(self, a, b):
        """Swap the values of two tensors in place."""
        tmp = a.clone().detach()
        a.copy_(b)
        b.copy_(tmp)
        del tmp
