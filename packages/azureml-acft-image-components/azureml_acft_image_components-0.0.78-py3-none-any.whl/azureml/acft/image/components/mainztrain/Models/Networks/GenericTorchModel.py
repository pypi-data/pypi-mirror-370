# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import logging
import torch
import torch.nn as nn

from .BaseModel import BaseModel

logger = logging.getLogger(__name__)


class GenericTorchModel(BaseModel):
    """
    A wrapper model for interfacing any generic pytorch models with MainzTrainer
    """

    def __init__(self, opt, module: nn.Module):
        """
        Args:
            opt (dict): configuration dict provided by MainzTrainer
            module (nn.Module): pytorch model to be wrapped
        """
        super(GenericTorchModel, self).__init__()
        self.opt = opt
        self.model = module

    def forward(self, *inputs, **kwargs):
        outputs = self.model(*inputs, **kwargs)
        return outputs

    def save_pretrained(self, save_dir):
        """
        Save the model

        Args:
            save_dir: path string of directory to save the model
        """
        save_path = os.path.join(save_dir, "model_state_dict.pt")
        torch.save(self.model.state_dict(), save_path)

    def from_pretrained(self, load_dir):
        """
        Load model at load_dir saved by save_pretrained() method

        Args:
            load_dir: path string of directory containing saved model
        """
        load_path = os.path.join(load_dir, "model_state_dict.pt")
        state_dict = torch.load(load_path, map_location=self.opt["device"])
        self.model.load_state_dict(state_dict)
        return self

    def get_training_parameters(self):
        """
        Return model parameters or grouped parameters to be optimized
        """
        return [p for p in self.parameters() if p.requires_grad]
