# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from torch.optim.lr_scheduler import LambdaLR


class CooldownScheduler(LambdaLR):
    """Linear cool down learning rate schedule"""

    def __init__(self, optimizer, num_steps):
        self.num_steps = num_steps
        self.start_step = 0
        super(CooldownScheduler, self).__init__(
            optimizer, self.lr_lambda, last_epoch=-1
        )

    def lr_lambda(self, step):
        return max(0.0, 1.0 - float(step - self.start_step) / self.num_steps)

    def load_state_dict(self, state_dict):
        if state_dict.get("is_cooldown_scheduler", False):
            super(CooldownScheduler, self).load_state_dict(state_dict)
        else:
            for key in ["_last_lr", "last_epoch", "_step_count"]:
                self.__dict__[key] = state_dict[key]
            self.base_lrs = state_dict["_last_lr"]
            self.start_step = state_dict["last_epoch"]

    def state_dict(self):
        state_dict = super(CooldownScheduler, self).state_dict()
        state_dict["is_cooldown_scheduler"] = True
        return state_dict
