# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import torch
import torch.nn as nn
import torch.distributed.distributed_c10d as dist_c10d

logger = logging.getLogger(__name__)


class BaseModel(nn.Module):
    """
    For classes extending this base class, only save_pretrained(), from_pretrained(), and get_training_parameters()
    interfaces are required to be same. Other interfaces are not restricted (the methods and their signatures don't
    have to be same as the base class). They should have minimum assumption or dependency on other components in the
    system. Task classes can use them accordingly.
    """

    def __init__(self):
        """
        Initialize model.
        """
        super(BaseModel, self).__init__()

        if torch.distributed.is_initialized():
            self.process_groups = {"world": dist_c10d._get_default_group(), "": None}
            # Process group being None means the group consists of only this one process,
            # so no real process group needs to be created (to save memory)
            # Always check if a process group is None when using it, because for PyTorch,
            # group=None means using the WORLD group, which is different from our assumption.
            self._dist_grids = None

    def forward(self, *inputs, **kwargs):
        """
        Forward function of the model
        """
        raise NotImplementedError

    def save_pretrained(self, save_dir):
        """
        Save config, model and tokenizer at save_dir

        Args:
            save_dir: path string of directory to save the model
        """
        raise NotImplementedError

    def from_pretrained(self, load_dir):
        """
        Load config, model and tokenizer at load_dir saved by save_pretrained() method

        Args:
            load_dir: path string of directory containing saved model
        """
        raise NotImplementedError

    def get_training_parameters(self):
        """
        Return model parameters or grouped parameters to be optimized
        """
        return self.parameters()

    def get_batch_size(self, batch):
        """
        Return batch size info as a dictionary

        Args:
            batch: a model input batch

        Returns:
            dict: a dictionary of named sizes
        """
        logger.warning("get_batch_size() not implemented, returning empty dictionary.")
        return {}

    def state_dict_to_dist_grid(self, state_dict_key):
        """
        Return a tuple of (dp_group_name, mp_group_name) for the given state_dict_key.
        dp_group_name is the data parallel group name in the self.process_groups the param belongs to.
        mp_group_name is the model parallel group name in the self.process_groups the param belongs to.

        Args:
            state_dict_key: a key in the self.state_dict()

        Returns:
            tuple: (dp_group_name, mp_group_name)
        """
        return ("world", "")  # (dp_group_name, mp_group_name)

    def named_param_to_dist_grid(self, param_name, param):
        """
        Return a tuple of (dp_group_name, mp_group_name) for the given param name and param.
        dp_group_name is the data parallel group name in the self.process_groups the param belongs to.
        mp_group_name is the model parallel group name in the self.process_groups the param belongs to.

        Args:
            param_name: the name of a param from self.named_parameters()
            param: a param from self.named_parameters()

        Returns:
            tuple: (dp_group_name, mp_group_name)
        """
        return ("world", "")  # (dp_group_name, mp_group_name)

    def get_world_size(self, group_name):
        if self.process_groups[group_name] is None:
            return 1
        return torch.distributed.get_world_size(group=self.process_groups[group_name])

    def get_rank(self, group_name):
        if self.process_groups[group_name] is None:
            return 0
        return torch.distributed.get_rank(group=self.process_groups[group_name])

    @property
    def dist_grids(self):
        assert torch.distributed.is_initialized()
        if self._dist_grids is None:
            self._dist_grids = []
            for name, param in self.named_parameters():
                dp_group_name, mp_group_name = self.named_param_to_dist_grid(
                    name, param
                )
                if (dp_group_name, mp_group_name) not in self._dist_grids:
                    dp_group_size = self.get_world_size(dp_group_name)
                    mp_group_size = self.get_world_size(mp_group_name)
                    assert (
                        dp_group_size * mp_group_size
                        == torch.distributed.get_world_size()
                    ), "The mp processes and dp processes must form a grid covering all processes."
                    self._dist_grids.append((dp_group_name, mp_group_name))
            logger.debug(f"initialized model dgrids: {self._dist_grids}")

        return self._dist_grids
