# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging

from ..Schedulers import CosineLRScheduler
from ..Schedulers import StepLRScheduler
from ..Schedulers import MultiStepLRScheduler
from ..Schedulers import OneCycleLRScheduler

logger = logging.getLogger(__name__)


class TimmScheduler:
    def __init__(self, optimizer, **args):
        self.steps_update = 0

        lr_scheduler = self._create_scheduler(optimizer, **args)
        self._lr_scheduler = lr_scheduler

    def _create_scheduler(self, optimizer, **args):
        num_epochs = args["epochs"]
        steps_update_per_epoch = args["steps_update_per_epoch"]
        t_initial = num_epochs * steps_update_per_epoch

        if "warmup_epochs" in args:
            warmup_t = steps_update_per_epoch * args["warmup_epochs"]
        elif "warmup_steps" in args:
            warmup_t = args["warmup_steps"]

        if args.get("lr_noise", None) is not None:
            lr_noise = args["lr_noise"]
            if isinstance(lr_noise, (list, tuple)):
                noise_range = [n * num_epochs for n in lr_noise]
                if len(noise_range) == 1:
                    noise_range = noise_range[0]
            else:
                noise_range = lr_noise * num_epochs
        else:
            noise_range = None

        lr_scheduler = None
        if args["sched"] == "cosine":
            lr_scheduler = CosineLRScheduler(
                optimizer,
                t_initial=t_initial,
                cycle_mul=args.get("lr_cycle_mul", 1.0),
                cycle_decay=args.get(
                    "decay_rate", 1.0
                ),  # Note: cycle_decay is named as decay_rate in Timm 0.3.2.
                cycle_limit=args.get("lr_cycle_limit", 1),
                lr_min=args["min_lr"],
                warmup_lr_init=args["warmup_lr"],
                warmup_t=warmup_t,
                t_in_epochs=False,
                noise_range_t=noise_range,
                noise_pct=args.get("lr_noise_pct", 0.67),
                noise_std=args.get("lr_noise_std", 1.0),
                noise_seed=args.get("seed", 42),
            )
        elif args["sched"] == "step":
            if "decay_epochs" in args:
                decay_t = steps_update_per_epoch * args["decay_epochs"]
            else:
                decay_t = args["decay_steps"]
            lr_scheduler = StepLRScheduler(
                optimizer,
                decay_t=decay_t,
                decay_rate=args["decay_rate"],
                warmup_lr_init=args["warmup_lr"],
                warmup_t=warmup_t,
                t_in_epochs=False,
                noise_range_t=noise_range,
                noise_pct=args.get("lr_noise_pct", 0.67),
                noise_std=args.get("lr_noise_std", 1.0),
                noise_seed=args.get("seed", 42),
            )
        elif args["sched"] == "onecycle":
            lr_scheduler = OneCycleLRScheduler(
                optimizer,
                t_initial=t_initial,
                noise_range_t=noise_range,
                noise_pct=args.get("lr_noise_pct", 0.67),
                noise_std=args.get("lr_noise_std", 1.0),
                noise_seed=args.get("seed", 42),
            )
        elif args["sched"] == "multistep":
            if "decay_epochs" in args:
                decay_t = [steps_update_per_epoch * t for t in args["decay_epochs"]]
            else:
                decay_t = args["decay_steps"]
            lr_scheduler = MultiStepLRScheduler(
                optimizer,
                decay_t=decay_t,
                decay_rate=args["decay_rate"],
                warmup_lr_init=args["warmup_lr"],
                warmup_t=warmup_t,
                t_in_epochs=False,
                noise_range_t=noise_range,
                noise_pct=args.get("lr_noise_pct", 0.67),
                noise_std=args.get("lr_noise_std", 1.0),
                noise_seed=args.get("seed", 42),
            )
        else:
            logger.error(f"Unsupported scheduler: {args}")
            raise NotImplementedError
        return lr_scheduler

    def load_state_dict(self, state_dict):
        self.steps_update = state_dict["steps_update"]

    def get_last_lr(self):
        lr = self._lr_scheduler.get_update_values(self.steps_update)
        return lr

    def step(self):
        self._lr_scheduler.step_update(self.steps_update)
        self.steps_update += 1

    def state_dict(self):
        state_dict = {}
        state_dict["steps_update"] = self.steps_update

        return state_dict
