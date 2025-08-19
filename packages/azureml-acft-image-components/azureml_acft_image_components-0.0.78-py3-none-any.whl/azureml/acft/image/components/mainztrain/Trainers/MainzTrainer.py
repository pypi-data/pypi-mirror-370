# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from collections import OrderedDict
import copy
import contextlib
from datetime import datetime
import importlib
import json
import logging
import math
from mpi4py import MPI
import numpy as np
import os
import random
import shutil
import stat
import sys
import time
import torch
import torch.nn as nn
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler
from torch.utils.data import DataLoader
from torch.utils.data import IterableDataset
from torch.utils.data.distributed import DistributedSampler
from typing import Any, Callable, Union

from .DistributedTrainer import DistributedTrainer
from ..DataLoader import iterators
from ..Utils.Arguments import load_config_dict_to_opt
from ..Utils.CheckpointUtils import (
    get_nebula_checkpoint_tag_name,
    init_Nebula_service,
    save_to_checkpoint,
    load_from_checkpoint,
    SAVE_STRATEGY,
)
from ..Utils.EvalUtils import EVAL_STRATEGY
from ..Utils.ExponentialSmoothing import ExponentialSmoothingState, AssignSmoothingState
from ..Utils.FSDPUtils import clip_grad_norm_fsdp
from ..Utils.GeneralUtils import (
    AverageMeter,
    ObjectView,
    move_batch_to_device,
    cast_batch_to_half,
    retry_on_failure,
    cast_batch_to_bf16,
)
from ..Utils.Serialization import MainzJSONEncoder, filter_jsonable
from ..Utils.Timing import Timer

logger = logging.getLogger(__name__)


class MainzTrainer(DistributedTrainer):
    """
    MainzTrainer is the core of MainzTrain training pipeline

    The trainer class for MainzTrain model training (pre-train and fine-tune).
    Its train() and eval() methods are intended to directly called to
    start training and evaluation respectively.
    """

    def __init__(self, opt):
        """
        Set up the task the model is being trained for.
        """
        super().__init__(opt)
        if self.opt.get("user_dir", None):
            try:
                user_dir_module_name = "user_dir_module"
                user_dir_module_path = os.path.join(self.opt["user_dir"], "__init__.py")
                spec = importlib.util.spec_from_file_location(
                    user_dir_module_name, user_dir_module_path
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[user_dir_module_name] = module
                spec.loader.exec_module(module)
                logger.info(
                    f"Imported user_dir_module at user_dir {self.opt['user_dir']}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to import user_dir_module at user_dir {self.opt['user_dir']}. Error: {e}"
                )
        else:
            logger.info(
                "user_dir is not provided, user_dir_module will not be imported."
            )

        try:
            task_module = importlib.import_module(
                f"user_dir_module.Tasks.{self.opt['TASK']}"
            )
            task_class = getattr(task_module, self.opt["TASK"])
            logger.info(f"Using custom task: {self.opt['TASK']}")
        except Exception:
            logger.info(
                f"user_dir_module is not imported or Task {self.opt['TASK']} is not found in it. \
                    Trying to load from MainzTrain."
            )
            try:
                task_module = importlib.import_module(
                    f"...Models.Tasks.{self.opt['TASK']}", package=__name__
                )
                task_class = getattr(task_module, self.opt["TASK"])
                logger.info(f"Using MainzTrain task: {self.opt['TASK']}")
            except Exception as e:
                logger.error(f"Failed to load Task {self.opt['TASK']}. Error: {e}")
                raise e
        self.task = task_class(self.opt)
        self.setup_sift()

    @staticmethod
    def _log_oom(exc):
        msg = f"OOM: Ran out of memory with exception: {exc}"
        logger.warning(msg)
        if torch.cuda.is_available() and hasattr(torch.cuda, "memory_summary"):
            for device_idx in range(torch.cuda.device_count()):
                logger.warning(torch.cuda.memory_summary(device=device_idx))
        sys.stderr.flush()

    def _dist_barrier(self, **kwargs):
        if self.opt["world_size"] > 1:
            torch.distributed.barrier(**kwargs)

    def is_gradient_accumulation_boundary(self):
        """
        Check whether the current mini-batch update is at the gradient accumulation boundary
        """
        return (self.num_updates + 1) % self.opt["GRADIENT_ACCUMULATE_STEP"] == 0

    def get_training_losses(self):
        """
        If available, return a list of all training training losses in the form of (val, avg).
        """
        if hasattr(self, "train_loss"):
            return {
                key: (self.train_loss[key].val, self.train_loss[key].avg)
                for key in sorted(self.train_loss.keys())
            }
        return None

    def get_batch_size(self, batch, module_name="default"):
        """
        Return batch size info as a dictionary

        Args:
            batch: a model input batch

        Returns:
            dict: a dictionary of named sizes
        """
        if hasattr(self.raw_modules[module_name], "get_batch_size"):
            if callable(self.raw_modules[module_name].get_batch_size):
                return self.raw_modules[module_name].get_batch_size(batch)
        return {}

    def is_infinite_batch_generator(self):
        if isinstance(self.train_batch_generator, iterators.CheckpointableIterator):
            return True
        return getattr(self.train_batch_generator, "is_infinite", False)

    def is_checkpointable_batch_generator(self):
        if isinstance(self.train_batch_generator, iterators.CheckpointableIterator):
            return True
        return getattr(self.train_batch_generator, "is_checkpointable", False)

    def _get_optimizer_params_config(self):
        """
        Acquire optimizer parameters from settings in config file
        The settings in config file should have the parameter names in uppercase.
        """
        optimizer_parameters = self.opt["OPTIMIZER_PARAMS"]
        optimizer_parameters["lr"] = self.opt["learning_rate"]
        logger.info(f"Optimizer lr set to {self.opt['learning_rate']}")
        return optimizer_parameters

    def _get_lr_scheduler_params_config(self):
        """
        Acquire lr scheduler parameters from settings in config file
        The settings in config file should have the parameter names in uppercase.
        """
        lr_scheduler_parameters = self.opt["LR_SCHEDULER_PARAMS"]
        num_steps_param = self.opt.get("LR_TRAINING_STEPS_NAME", None)
        if num_steps_param is not None:
            if self.opt.get("MAX_OPTIM_STEPS", -1) > -1:
                num_training_steps = self.opt["MAX_OPTIM_STEPS"]
            else:
                num_training_steps = (
                    self.opt["MAX_NUM_EPOCHS"]
                    * self.updates_per_epoch
                    // self.opt["GRADIENT_ACCUMULATE_STEP"]
                )
            lr_scheduler_parameters[num_steps_param] = num_training_steps
            logger.info(f"LR scheduler {num_steps_param} set to {num_training_steps}")
        return lr_scheduler_parameters

    def _get_deepspeed_optimizer_class(self, optimizer_name):
        """
        Get optimizer_class if optimizer_name is supported by deepspeed. If not, return None.
        Adapted from deepspeed.runtime.engine._configure_basic_optimizer()
        """
        try:
            import deepspeed  # noqa: F401
        except Exception:
            return None

        try:
            # Attempt getting optimizer_class from deepspeed v0.3.0
            from deepspeed.runtime.config import (
                ADAM_OPTIMIZER,
                ADAMW_OPTIMIZER,
                LAMB_OPTIMIZER,
                ONEBIT_ADAM_OPTIMIZER,
                ONEBIT_LAMB_OPTIMIZER,
                DEEPSPEED_OPTIMIZERS,
            )

            assert optimizer_name.lower() in DEEPSPEED_OPTIMIZERS
            ds_optimizer_name = optimizer_name.lower()
            if ds_optimizer_name in [ADAM_OPTIMIZER, ADAMW_OPTIMIZER]:
                from deepspeed.ops.adam import FusedAdam

                optimizer_class = FusedAdam
            elif ds_optimizer_name == LAMB_OPTIMIZER:
                from deepspeed.ops.lamb import FusedLamb

                optimizer_class = FusedLamb
            elif ds_optimizer_name == ONEBIT_ADAM_OPTIMIZER:
                assert self.opt[
                    "init_lr_scheduler_in_deepspeed"
                ], f"{ONEBIT_ADAM_OPTIMIZER} can only be initialized within DeepSpeed."
                from deepspeed.runtime.fp16.onebit.adam import OnebitAdam

                optimizer_class = OnebitAdam
            else:
                assert ds_optimizer_name == ONEBIT_LAMB_OPTIMIZER
                assert self.opt[
                    "init_lr_scheduler_in_deepspeed"
                ], f"{ONEBIT_LAMB_OPTIMIZER} can only be initialized within DeepSpeed."
                from deepspeed.runtime.fp16.onebit.lamb import OnebitLamb

                optimizer_class = OnebitLamb
        except Exception:
            try:
                # Attempt getting pytorch native optimizer_class, which is also supported by deepspeed
                optimizer_class = getattr(optim, optimizer_name)
            except Exception:
                optimizer_class = None

        return optimizer_class

    def _get_deepspeed_lr_scheduler_class(self, lr_scheduler_name):
        """
        Get lr_scheduler_class if lr_scheduler_name is supported by deepspeed. If not, return None.
        Adapted from deepspeed.runtime.engine._scheduler_from_config()
        """
        try:
            import deepspeed
        except Exception:
            return None

        try:
            # Attempt getting lr_scheduler_class from deepspeed v0.3.0
            lr_scheduler_class = getattr(
                deepspeed.runtime.lr_schedules, lr_scheduler_name
            )
        except Exception:
            try:
                # Attempt getting pytorch native lr_scheduler_class, which is also supported by deepspeed
                lr_scheduler_class = getattr(lr_scheduler, lr_scheduler_name)
            except Exception:
                lr_scheduler_class = None

        return lr_scheduler_class

    def _set_up_optimizers_and_lr_schedulers(self):
        """
        Set up self.optimizers and self.lr_schedulers

        This method initializes self.optimizers and self.lr_schedulers as dictionaries of
        instances of the classes that OPTIMIZER and LR_SCHEDULER in the config file points to.
        One optimizer and lr scheduler for each model in self.raw_modules. They have the same keys
        as self.raw_modules.
        """
        self.optimizers = {module_name: None for module_name in self.module_names}
        self.lr_schedulers = {module_name: None for module_name in self.module_names}
        self.opt["init_optimizer_in_deepspeed"] = False
        self.opt["init_lr_scheduler_in_deepspeed"] = False

        if self.opt["DEEPSPEED"]:
            # Figure out if the optimizer or lr scheduler chosen in the MainzTrain config file can be
            # initialized in DeepSpeed. If it can, leave self.optimizers or self.lr_schedulers as None in Mainz.
            # Otherwise, continue to initialize self.optimizers or self.lr_schedulers in MainzTrain and pass them
            # to deepspeed.initialize() later.

            lr_scheduler_class = self._get_deepspeed_lr_scheduler_class(
                self.opt["LR_SCHEDULER"]
            )
            if lr_scheduler_class is not None:
                self.opt["init_lr_scheduler_in_deepspeed"] = True
            else:
                logger.warning(
                    f"LR scheduler {self.opt['LR_SCHEDULER']} can NOT be recognized by DeepSpeed."
                )
                logger.warning(
                    "Initializing optimizer and LR scheduler in MainzTrainer."
                )

            if self.opt["init_lr_scheduler_in_deepspeed"]:
                optimizer_class = self._get_deepspeed_optimizer_class(
                    self.opt["OPTIMIZER"]
                )
                if optimizer_class is not None:
                    self.opt["init_optimizer_in_deepspeed"] = True
                else:
                    logger.warning(
                        f"Optimizer {self.opt['OPTIMIZER']} can NOT be recognized by DeepSpeed."
                    )
                    logger.warning("Initializing optimizer in MainzTrainer.")

        if not self.opt["init_optimizer_in_deepspeed"]:
            # instantiate optimizer for each module
            try:  # first look for custom optimizer inside user_dir_module.Optimizers
                optimizer_module = importlib.import_module(
                    f"user_dir_module.Optimizers.{self.opt['OPTIMIZER']}"
                )
                optimizer_class = getattr(optimizer_module, self.opt["OPTIMIZER"])
                logger.info(f"Using custom optimizer: {self.opt['OPTIMIZER']}")
            except Exception:
                try:  # then look for MainzTrain optimizer inside Models.Optimizers
                    optimizer_module = importlib.import_module(
                        f"...Models.Optimizers.{self.opt['OPTIMIZER']}",
                        package=__name__,
                    )
                    optimizer_class = getattr(optimizer_module, self.opt["OPTIMIZER"])
                    logger.info(f"Using MainzTrain optimizer: {self.opt['OPTIMIZER']}")
                except Exception:
                    try:  # then look for pytorch native optimizer
                        optimizer_class = None
                        if self.opt["OPTIMIZER"] == "Adam" and self.opt["CUDA"]:
                            try:
                                from apex.optimizers.fused_adam import FusedAdam

                                optimizer_class = FusedAdam
                            except Exception:
                                pass
                        if self.opt["OPTIMIZER"] == "ORT_ADAM":
                            from onnxruntime.training.optim.fused_adam import FusedAdam

                            optimizer_class = FusedAdam
                            logger.info(
                                f"Using onnxruntime.training.optim.fused_adam: {self.opt['OPTIMIZER']}"
                            )
                        elif self.opt["OPTIMIZER"].startswith("Mu"):
                            import mup.optim

                            optimizer_class = getattr(mup.optim, self.opt["OPTIMIZER"])
                            logger.info(
                                f"Using muP wrapped pytorch native optimizer: {self.opt['OPTIMIZER']}"
                            )
                        elif optimizer_class is None:
                            optimizer_class = getattr(optim, self.opt["OPTIMIZER"])
                            logger.info(
                                f"Using pytorch native optimizer: {self.opt['OPTIMIZER']}"
                            )
                    except Exception as e:  # then look for DeepSpeed optimizer
                        optimizer_class = self._get_deepspeed_optimizer_class(
                            self.opt["OPTIMIZER"]
                        )
                        if optimizer_class is not None:
                            logger.info(
                                f"Using DeepSpeed optimizer: {self.opt['OPTIMIZER']}"
                            )
                        else:
                            logger.error(str(e))
                            logger.error(
                                f"ERROR: Optimizer {self.opt['OPTIMIZER']} is unknown"
                            )
                            raise e

            optimizer_parameters = self._get_optimizer_params_config()
            logger.info(f"Optimizer parameters: {optimizer_parameters}")
            for module_name in self.module_names:
                if (
                    not self.opt["DEEPSPEED"]
                    and self.opt["world_size"] > 1
                    and self.opt["DDP"] == "MAINZ"
                ):
                    from ..Utils.Distributed import ModelParallelOptimizer

                    if (
                        self.opt.get("ORT", None)
                        and self.opt.get("ORT_CONFIG", None) == "HIERARCHICAL"
                    ):
                        self.optimizers[module_name] = ModelParallelOptimizer(
                            self.raw_modules[module_name]._original_module,
                            optimizer_class,
                            optimizer_parameters,
                        )
                    else:
                        self.optimizers[module_name] = ModelParallelOptimizer(
                            self.raw_modules[module_name],
                            optimizer_class,
                            optimizer_parameters,
                        )
                else:
                    parameters = self.raw_modules[module_name].get_training_parameters()
                    self.optimizers[module_name] = optimizer_class(
                        parameters, **optimizer_parameters
                    )
                self.optimizers[module_name].zero_grad()

        if not self.opt["init_lr_scheduler_in_deepspeed"]:
            # instantiate lr scheduler for each optimizer
            try:  # first look for custom lr scheduler inside user_dir_module.Optimizers
                lr_scheduler_module = importlib.import_module(
                    f"user_dir_module.Optimizers.{self.opt['LR_SCHEDULER']}"
                )
                lr_scheduler_class = getattr(
                    lr_scheduler_module, self.opt["LR_SCHEDULER"]
                )
                logger.info(f"Using custom lr scheduler: {self.opt['LR_SCHEDULER']}")
            except Exception:
                try:  # then look for MainzTrain lr scheduler inside Models.Optimizers
                    lr_scheduler_module = importlib.import_module(
                        f"...Models.Optimizers.{self.opt['LR_SCHEDULER']}",
                        package=__name__,
                    )
                    lr_scheduler_class = getattr(
                        lr_scheduler_module, self.opt["LR_SCHEDULER"]
                    )
                    logger.info(
                        f"Using MainzTrain lr scheduler: {self.opt['LR_SCHEDULER']}"
                    )
                except Exception:
                    try:  # then look for pytorch native lr scheduler
                        lr_scheduler_class = getattr(
                            lr_scheduler, self.opt["LR_SCHEDULER"]
                        )
                        logger.info(
                            f"Using pytorch native lr scheduler: {self.opt['LR_SCHEDULER']}"
                        )
                    except Exception as e:  # then look for DeepSpeed lr scheduler
                        lr_scheduler_class = self._get_deepspeed_lr_scheduler_class(
                            self.opt["LR_SCHEDULER"]
                        )
                        if lr_scheduler_class is not None:
                            logger.info(
                                f"Using DeepSpeed lr scheduler: {self.opt['LR_SCHEDULER']}"
                            )
                        else:
                            logger.error(str(e))
                            logger.error(
                                f"ERROR: LR Scheduler {self.opt['LR_SCHEDULER']} is unknown"
                            )
                            raise e

            lr_scheduler_parameters = self._get_lr_scheduler_params_config()
            logger.info(f"Lr scheduler parameters: {lr_scheduler_parameters}")
            for module_name in self.module_names:
                if (
                    not self.opt["DEEPSPEED"]
                    and self.opt["world_size"] > 1
                    and self.opt["DDP"] == "MAINZ"
                ):
                    from ..Utils.Distributed import ModelParallelLRScheduler

                    self.lr_schedulers[module_name] = ModelParallelLRScheduler(
                        self.optimizers[module_name],
                        lr_scheduler_class,
                        lr_scheduler_parameters,
                    )
                else:
                    self.lr_schedulers[module_name] = lr_scheduler_class(
                        self.optimizers[module_name], **lr_scheduler_parameters
                    )

    def _print_number_of_params(self):
        for module_name in self.module_names:
            num_params = 0
            num_trainable_params = 0
            for name, param in self.raw_modules[module_name].named_parameters():
                num_params += param.numel()
                if param.requires_grad:
                    num_trainable_params += param.numel()
            logger.info(
                f"Total number of parameters in {module_name} module (on each GPU): {num_params}"
            )
            logger.info(
                f"Number of trainable parameters in {module_name} module (on each GPU): {num_trainable_params}"
            )

    def _initialize_fp16_DDP(self):
        """
        Depending on the settings, wrap self.modules with apex amp module for fp16 training,
        and wrap the network with pytorch/apex DDP module for distributed data parallel training.
        The wrapped module is in self.modules
        """
        assert (
            self.opt.get("BF16", False) is False
        ), "BF16 only supported with DeepSpeed currently"
        if self.opt["FP16"]:
            if self.opt["AMP"] == "APEX":
                from apex import amp

                module_list = [
                    self.modules[module_name] for module_name in self.module_names
                ]
                criterion_names = [criterion_name for criterion_name in self.criteria]
                criterion_list = [
                    self.criteria[criterion_name] for criterion_name in criterion_names
                ]
                if self.opt["world_size"] > 1 and self.opt["DDP"] == "MAINZ":
                    optimizer_list = []
                    optimizer_pos = []
                    for module_name in self.module_names:
                        optimizer_pos.append(len(optimizer_list))
                        optimizer_list.extend(
                            self.optimizers[module_name].inner_optimizer_list
                        )
                    optimizer_pos.append(len(optimizer_list))
                else:
                    optimizer_list = [
                        self.optimizers[module_name]
                        for module_name in self.module_names
                    ]
                module_criterion_list, optimizer_list = amp.initialize(
                    module_list + criterion_list,
                    optimizer_list,
                    opt_level=self.opt["FP16_OPT_LEVEL"],
                )
                for i, module_criterion_name in enumerate(
                    self.module_names + criterion_names
                ):
                    if i < len(self.module_names):
                        self.modules[module_criterion_name] = module_criterion_list[i]
                    else:
                        self.criteria[module_criterion_name] = module_criterion_list[i]
                if self.opt["world_size"] > 1 and self.opt["DDP"] == "MAINZ":
                    for i, module_name in enumerate(self.module_names):
                        self.optimizers[module_name].inner_optimizer_list = (
                            optimizer_list[optimizer_pos[i]: optimizer_pos[i + 1]]
                        )
                else:
                    for i, module_name in enumerate(self.module_names):
                        self.optimizers[module_name] = optimizer_list[i]
                logger.warning(
                    "APEX AMP initialized for all modules, criteria, and optimizers."
                )
            else:  # self.opt['AMP'] == 'PYTORCH'
                from torch.cuda.amp import GradScaler

                self.grad_scaler = GradScaler()
                logger.warning("PyTorch AMP GradScaler initialized.")

        for module_name in self.module_names:
            if self.opt["world_size"] > 1:
                # ddp: wrap model in DDP
                if self.opt["USE_HIT"]:
                    description = "HiT"
                    args = ObjectView({})
                    self._prepare_hit_config(args)

                    import hit

                    self.modules[module_name], self.optimizers[module_name] = (
                        hit.initialize_hit_optimizer(
                            self.modules[module_name],
                            self.optimizers[module_name],
                            args,
                        )
                    )
                    assert (
                        self.raw_modules[module_name]
                        is self.modules[module_name].module
                    )
                else:
                    if self.opt["DDP"] == "MAINZ":
                        description = "MAINZ_DDP"
                        from ..Utils.Distributed import (
                            DistributedModelDataParallel as DMDP,
                        )

                        if (
                            self.opt.get("ORT", None)
                            and self.opt.get("ORT_CONFIG", None) == "HIERARCHICAL"
                        ):
                            self.modules[module_name] = DMDP(
                                self.modules[module_name]._original_module
                            )
                        else:
                            self.modules[module_name] = DMDP(self.modules[module_name])
                        if self.opt["FP16"] and self.opt["AMP"] == "APEX":
                            from ..Utils.Distributed import monkey_patch_apex_amp_scaler

                            monkey_patch_apex_amp_scaler()
                        if (
                            self.opt.get("ORT", None)
                            and self.opt.get("ORT_CONFIG", None) == "HIERARCHICAL"
                        ):
                            assert (
                                self.raw_modules[module_name]._original_module
                                is self.modules[module_name].module
                            )
                        else:
                            assert (
                                self.raw_modules[module_name]
                                is self.modules[module_name].module
                            )
                    elif self.opt["DDP"] == "APEX":
                        description = "APEX_DDP"
                        # using apex DDP with delay_allreduce=True to solve the issue
                        # in torch DDP when there is unused parameters in forward
                        from apex.parallel import DistributedDataParallel as DDP

                        self.modules[module_name] = DDP(
                            self.modules[module_name], delay_allreduce=True
                        )
                        assert (
                            self.raw_modules[module_name]
                            is self.modules[module_name].module
                        )
                    else:  # self.opt['DDP'] == 'PYTORCH'
                        description = "PYTORCH_DDP"
                        self.modules[module_name] = nn.parallel.DistributedDataParallel(
                            self.modules[module_name],
                            device_ids=[self.opt["local_rank"]],
                            output_device=self.opt["local_rank"],
                            find_unused_parameters=self.opt["FIND_UNUSED_PARAMETERS"],
                        )
                        assert (
                            self.raw_modules[module_name]
                            is self.modules[module_name].module
                        )
                logger.warning(
                    f"Wrapped module {module_name} with {description} on rank {self.opt['rank']}."
                )
            else:
                assert self.raw_modules[module_name] is self.modules[module_name]

    def _prepare_hit_config(self, args):
        """
        Convert relevant settings in MainzTrain config to DeepSpeed config dictionary
        """
        import yaml

        with open(os.path.join(self.opt["DATA_DIR"], self.opt["HIT_CONFIG"])) as f:
            config_dict = yaml.safe_load(f)

            if "layers" in config_dict["hit"]:
                # new config
                layer0_config = config_dict["hit"]["layers"][0]
            else:
                # old config
                layer0_config = config_dict["hit"]["distributed_optimizers"][0]

            if self.opt["DEEPSPEED"]:
                layer0_config["type"] = "deepspeed"
            else:
                if self.opt["DDP"] == "APEX":
                    layer0_config["type"] = "apex_ddp"
                    layer0_config["delay_allreduce"] = True
                elif self.opt["DDP"] == "PYTORCH":
                    layer0_config["type"] = "ddp"
                    layer0_config["find_unused_parameters"] = True
                else:
                    logger.error("HiT do not work with other DDP types.")
                    raise ValueError

            args.hit = True
            args.hit_config_file = None
            args.hit_config_params = config_dict

    def _prepare_deepspeed_config_dict(self):
        """
        Convert relevant settings in MainzTrain config to DeepSpeed config dictionary
        """
        deepspeed_config_dict = {}
        deepspeed_config_dict["gradient_accumulation_steps"] = self.opt[
            "GRADIENT_ACCUMULATE_STEP"
        ]
        deepspeed_config_dict["steps_per_print"] = self.updates_per_epoch
        deepspeed_config_dict["wall_clock_breakdown"] = self.opt.get("DEBUG", False)
        assert (
            int(self.opt["FP16"]) + int(self.opt["BF16"]) <= 1
        ), "FP16 and BF16 cannot be enabled at the same time"
        if self.opt.get("ZERO_STAGE", 0) > 0:
            logger.info(
                "DeepSpeed ZeRO is turned on. Using fp16 mode. fp16_opt_level is ignored."
            )
            if self.opt["FP16"]:
                deepspeed_config_dict["fp16"] = {
                    "enabled": True,
                    "initial_scale_power": 16,
                }
            else:
                deepspeed_config_dict["bf16"] = {"enabled": self.opt["BF16"]}
        else:
            # Deepspeed amp integration has unresolved bugs right now, so we stick to the fp16 mode
            # This PR resolves part of the bugs: https://github.com/microsoft/DeepSpeed/pull/290
            # deepspeed_config_dict['amp'] = {'enabled': self.opt['FP16'], 'opt_level': self.opt['FP16_OPT_LEVEL']}
            if self.opt["FP16"]:
                deepspeed_config_dict["fp16"] = {
                    "enabled": True,
                    "initial_scale_power": 16,
                }
            else:
                deepspeed_config_dict["bf16"] = {"enabled": self.opt["BF16"]}

        # For more info on deepspeed zero configs check:
        # https://www.deepspeed.ai/docs/config-json/#zero-optimizations-for-fp16-training
        if self.opt.get("ZERO_STAGE", 0) == 2:
            deepspeed_config_dict["zero_optimization"] = {
                "stage": 2,
                "allgather_partitions": True,
                "reduce_scatter": True,
                "allgather_bucket_size": 50000000,
                "reduce_bucket_size": 50000000,
                "overlap_comm": True,
                "contiguous_gradients": True,
                "cpu_offload": False,
            }
        else:
            deepspeed_config_dict["zero_optimization"] = {
                "stage": self.opt.get("ZERO_STAGE", 0)
            }

        deepspeed_config_dict["gradient_clipping"] = self.opt.get("GRAD_CLIPPING", 0)
        # 'train_batch_size' is a dummy value here. It is required by DeepSpeed, but We use
        # our own batch generator in Mainz, so it doesn't affect the actual training process.
        # It is only used in DeepSpeed for throughput calculation, which we don't look at.
        # The only requirement is that it is divisible by
        # self.opt['world_size'] * self.opt['GRADIENT_ACCUMULATE_STEP'].
        deepspeed_config_dict["train_batch_size"] = (
            1 * self.opt["world_size"] * self.opt["GRADIENT_ACCUMULATE_STEP"]
        )

        # Get the optimizer and lr_scheduler settings from self.opt if they are going to be initializezd in DeepSpeed
        if self.opt["init_optimizer_in_deepspeed"]:
            optimizer_parameters = self._get_optimizer_params_config()
            deepspeed_config_dict["optimizer"] = {
                "type": self.opt["OPTIMIZER"],
                "params": optimizer_parameters,
            }
        if self.opt["init_lr_scheduler_in_deepspeed"]:
            lr_scheduler_parameters = self._get_lr_scheduler_params_config()
            deepspeed_config_dict["scheduler"] = {
                "type": self.opt["LR_SCHEDULER"],
                "params": lr_scheduler_parameters,
            }

        # If there are advanced overriding deepspeed settings, apply them to the deepspeed config dictionary
        if "DEEPSPEED_CONFIG_OVERRIDES" in self.opt:
            load_config_dict_to_opt(
                deepspeed_config_dict,
                self.opt["DEEPSPEED_CONFIG_OVERRIDES"],
                splitter="::",
            )

        self.opt["deepspeed_config_dict"] = deepspeed_config_dict

    def _initialize_deepspeed(self):
        """
        Wrap self.modules with deepspeed module.
        If using the optimizer and lr_scheduler defined in the deepspeed
        config file, pass the model parameters to the deepspeed initialization function.
        Otherwise, pass the optimizer and lr_scheduler we already initialized to the function.
        The wrapped module is in self.modules
        """
        self._prepare_deepspeed_config_dict()
        logger.debug(f"DeepSpeed config dict: {self.opt['deepspeed_config_dict']}")
        for module_name in self.module_names:
            model_parameters = (
                self.modules[module_name].get_training_parameters()
                if self.opt["init_optimizer_in_deepspeed"]
                else None
            )
            args = ObjectView(
                copy.deepcopy(self.opt)
            )  # convert opt dict to an args object, with keys as attributes
            args.deepspeed = True
            args.deepspeed_config = None

            if self.opt["USE_HIT"]:
                self._prepare_hit_config(args)

                import hit

                init_fn = hit.initialize
                description = "DeepSpeed + HiT"
            else:
                import deepspeed

                init_fn = deepspeed.initialize
                description = "DeepSpeed"

            (
                self.modules[module_name],
                self.optimizers[module_name],
                _,
                self.lr_schedulers[module_name],
            ) = init_fn(
                args=args,
                model=self.modules[module_name],
                model_parameters=model_parameters,
                optimizer=self.optimizers[module_name],
                lr_scheduler=self.lr_schedulers[module_name],
                dist_init_required=False,
                config_params=args.deepspeed_config_dict,
            )
            logger.warning(
                f"Wrapped module {module_name} with {description} on rank {self.opt['rank']}."
            )
            assert self.raw_modules[module_name] is self.modules[module_name].module

        for criterion_name in self.criteria:
            if (
                "fp16" in self.opt["deepspeed_config_dict"]
                and self.opt["deepspeed_config_dict"]["fp16"]["enabled"]
            ):
                self.criteria[criterion_name].half()

    def _initialize_fsdp(self, modules_full):
        """
        Wrap modules_full with FSDP module.
        Parameters can only be in the leaf modules of modules_full
        """
        from fairscale.nn.data_parallel import FullyShardedDataParallel as FSDP
        from fairscale.nn.wrap import auto_wrap, enable_wrap, default_auto_wrap_policy
        import functools

        """
        [Todo] Add code for check if there is any non-leaf module containing parameter, \
            if there is, send assertion error
        """
        if "fsdp_expert_grid" in self.opt:
            expert_replica_group = self.opt[
                "fsdp_expert_grid"
            ].get_expert_replica_group()
            assert (
                expert_replica_group is not None and expert_replica_group.size() > 1
            ), "FSDP does not support sharding with process group size = 1 or process group = None"

        """
        fsdp_config_non_moe: FSDP config for general modules
        fsdp_config_non_moe_fp32: FSDP config for modules which parameters should be kept in FP32
        (not apply mixed-precision)
        fsdp_config_moe: FSDP config for moe modules (parameters need to be sharded within expert_replica_groups)

        flatten_parameters is set to False to ensure that the optimizer is setup correctly
        The details of config's args can be found in
        https://github.com/facebookresearch/fairscale/blob/main/fairscale/nn/data_parallel/fully_sharded_data_parallel.py
        """
        fsdp_config_non_moe = {
            "mixed_precision": self.opt["FSDP_SETTING"]["MIXED_PRECISION"],
            "flatten_parameters": False,
            "process_group": None,
        }
        fsdp_config_non_moe_fp32 = {
            "mixed_precision": False,
            "flatten_parameters": False,
            "process_group": None,
        }
        if "fsdp_expert_grid" in self.opt:
            fsdp_config_moe = {
                "mixed_precision": self.opt["FSDP_SETTING"]["MIXED_PRECISION"],
                "flatten_parameters": False,
                "process_group": expert_replica_group,
            }

        for name, submodule in modules_full.named_modules():
            if "fsdp_expert_grid" in self.opt:
                from ..Models.Networks.moe_module.ort_moe.utils import (
                    contain_only_moe_parameters,
                    contain_only_gate_parameters,
                )

                if contain_only_moe_parameters(submodule):
                    submodule.wrapper_config = fsdp_config_moe
                elif contain_only_gate_parameters(submodule) or isinstance(
                    submodule, torch.nn.modules.batchnorm._BatchNorm
                ):
                    """
                    parameters in gate should to be FP32 for better evaluation quality
                    parameters in batchnorm should to be FP32 (in accordance with APEX O1, O2)
                    """
                    submodule.wrapper_config = fsdp_config_non_moe_fp32
                else:
                    submodule.wrapper_config = fsdp_config_non_moe
            else:
                if isinstance(submodule, torch.nn.modules.batchnorm._BatchNorm):
                    """
                    parameters in batchnorm should to be FP32 (in accordance with APEX O1, O2)
                    """
                    submodule.wrapper_config = fsdp_config_non_moe_fp32
                else:
                    submodule.wrapper_config = fsdp_config_non_moe

        # min_num_params=1 implies no threshold (number of parameters) for wrapping
        wrap_policy = functools.partial(default_auto_wrap_policy, min_num_params=1)

        with enable_wrap(wrapper_cls=FSDP):
            modules_fsdp = auto_wrap(modules_full, auto_wrap_policy=wrap_policy)
        assert modules_fsdp is modules_full
        # Verify that no module is wrap more than once
        for name, submodule in modules_fsdp.named_modules():
            if isinstance(submodule, FSDP):
                for name_descendant, descendant in submodule.named_modules():
                    assert name_descendant == "" or not isinstance(
                        descendant, FSDP
                    ), f"The module, {name}.{name_descendant}, is wrapped by FSDP more than once"
        if self.opt["rank"] == 0:
            logger.info("****************FSDP Model****************")
            for name, submodule in modules_fsdp.named_modules():
                logger.info(name)
            logger.info("******************************************")

        if self.opt["FSDP_SETTING"]["MIXED_PRECISION"]:
            from fairscale.optim.grad_scaler import ShardedGradScaler

            self.sharded_grad_scaler = ShardedGradScaler()
            logger.warning("FairScale-PyTorch AMP GradScaler initialized.")

        return modules_fsdp

    def _validate_num_updates(self):
        # validate that the num_updates is in sync on all ranks.
        if self.opt["world_size"] > 1:
            sum_num_updates = torch.tensor(self.num_updates).to(self.opt["device"])
            torch.distributed.all_reduce(
                sum_num_updates, torch.distributed.ReduceOp.SUM
            )
            sum_num_updates = sum_num_updates.item()
            assert (
                sum_num_updates == self.num_updates * self.opt["world_size"]
            ), f"All ranks should be at the same num_updates: \
                {self.num_updates} * {self.opt['world_size']}, {sum_num_updates}"

    def _get_and_validate_current_optim_steps(self):
        current_optim_steps = set(
            [self.optim_steps[module_name] for module_name in self.module_names]
        )
        assert (
            len(current_optim_steps) == 1
        ), f"All modules should be at the same optim step: {self.optim_steps}"
        return next(iter(current_optim_steps))

    @Timer("MainzTrainer: evaluate")
    def eval(self, splits=["dev", "test"]):
        """
        Perform evaluation
        Evaluate saved model(s) in self.opt['PYLEARN_MODEL'] with the datasets in 'splits'.
        """
        logger.info("-----------------------------------------------")
        logger.info("Evaluating model ... ")
        self.mode = self.opt["trainer_mode"] = "eval"
        self.init_tb_writers()

        self.module_names, self.raw_modules, self.criteria = self.task.set_up_model()
        # move models to the device
        for module_name in self.module_names:
            self.raw_modules[module_name].to(self.opt["device"])
        for criterion_name in self.criteria:
            self.criteria[criterion_name].to(self.opt["device"])

        self.modules = {
            module_name: self.raw_modules[module_name]
            for module_name in self.module_names
        }

        try:
            # This means the model will be evaluated without loading the pretrained weights,
            # perhaps for profiling reasons.
            eval_without_loading = self.opt.get("DONT_LOAD_MODEL", False)

            if not eval_without_loading:
                if os.path.isdir(self.opt["PYLEARN_MODEL"]):
                    model_path = self.opt[
                        "PYLEARN_MODEL"
                    ]  # this is a directory, not a file
                else:
                    model_path = os.path.join(
                        self.opt["DATA_DIR"], self.opt["PYLEARN_MODEL"]
                    )  # this is a directory, not a file

            # If 'MIN_CHECKPOINT' or 'MAX_CHECKPOINT' is provided,
            # we scan all the number-named folders between them in model_path,
            # and evaluate all saved models in these folders
            if not eval_without_loading and (
                self.opt.get("MIN_CHECKPOINT", None) is not None
                or self.opt.get("MAX_CHECKPOINT", None) is not None
            ):

                def score_file_name(ckpt):
                    ckpt_run_dir = os.path.basename(os.path.dirname(ckpt))[4:]
                    ckpt_stp_dir = os.path.basename(ckpt)
                    return f"score_{ckpt_run_dir}_{ckpt_stp_dir}.json"

                if not os.path.isdir(model_path):
                    raise ValueError(f"Model directory not found: {model_path}")

                # enumerate all run_ folders in the model path
                run_folders = [
                    os.path.join(model_path, x.name)
                    for x in os.scandir(model_path)
                    if x.is_dir() and x.name.startswith("run_")
                ]

                # enumerate all ckpt folders
                ckpt_folders = [
                    os.path.join(x, y.name)
                    for x in run_folders
                    for y in os.scandir(x)
                    if y.is_dir() and y.name.isdecimal()
                ]
                if ckpt_folders == []:
                    ckpt_folders = [
                        os.path.join(model_path, x.name)
                        for x in os.scandir(model_path)
                        if x.is_dir() and x.name.isdecimal()
                    ]
                if ckpt_folders == []:
                    logger.info(f"No checkpoint in {model_path}.")
                    return

                # enumerate all ckpt folders in [min_checkpoint, max_checkpoint]
                min_checkpoint = int(self.opt.get("MIN_CHECKPOINT", 0))
                max_checkpoint = int(self.opt.get("MAX_CHECKPOINT", 10**6))
                inc_checkpoint = int(
                    self.opt.get("EVAL_STRATEGY", {}).get("EVAL_PER_OPTIM_STEPS", 1)
                )
                ckpt_folders = [
                    x
                    for x in ckpt_folders
                    if min_checkpoint <= int(os.path.basename(x)) <= max_checkpoint
                    and int(os.path.basename(x)) % inc_checkpoint == 0
                ]
                if ckpt_folders == []:
                    logger.info(
                        f"No checkpoints in range [{min_checkpoint}, {max_checkpoint}]."
                    )
                    return

                # enumerate ckpt folders with saved module folders
                ckpt_folders = [
                    x
                    for x in ckpt_folders
                    if os.path.isdir(os.path.join(x, self.module_names[0]))
                ]
                if ckpt_folders == []:
                    logger.info("No saved module folders in checkpoint folders.")
                    return

                # enumerate all unfinished ckpt folders
                root_save_folder = os.path.dirname(self.save_folder)
                ckpt_folders = [
                    x
                    for x in ckpt_folders
                    if not os.path.isfile(
                        os.path.join(root_save_folder, score_file_name(x))
                    )
                ]
                if ckpt_folders == []:
                    logger.info("All checkpoints are evaluated.")
                    return

                ckpt_folders.sort(key=lambda x: int(os.path.basename(x)))

                for ckpt in ckpt_folders:
                    ckpt_run_dir = os.path.basename(os.path.dirname(ckpt))[4:]
                    ckpt_stp_dir = os.path.basename(ckpt)
                    save_folder = os.path.join(
                        self.save_folder, f"res_{ckpt_run_dir}_{ckpt_stp_dir}"
                    )

                    self.load_model(ckpt)

                    all_results = {}
                    for eval_dataset in splits:
                        self.task.reset_eval_best_scores()
                        plot_label = f"run_{ckpt_run_dir}"
                        results, scores, _ = self._eval_on_set(
                            eval_dataset,
                            save_folder,
                            current_optim_steps=int(ckpt_stp_dir),
                            plot_label=plot_label,
                        )
                        all_results[eval_dataset] = {
                            "results": filter_jsonable(
                                results, json_encoder=MainzJSONEncoder
                            ),
                            "scores": filter_jsonable(
                                scores, json_encoder=MainzJSONEncoder
                            ),
                        }
                    if self.opt["rank"] == 0:
                        all_results_path = os.path.join(
                            root_save_folder, score_file_name(ckpt)
                        )
                        with open(all_results_path, "w", encoding="utf-8") as f:
                            logger.info(f"Storing all results to: {all_results_path}")
                            json.dump(all_results, f, indent=4, cls=MainzJSONEncoder)

            else:
                if not eval_without_loading:
                    if not os.path.isdir(model_path):
                        raise ValueError(f"Model directory not found: {model_path}")
                    else:
                        self.load_model(model_path)

                all_results = {}
                for eval_dataset in splits:
                    self.task.reset_eval_best_scores()
                    results, scores, _ = self._eval_on_set(
                        eval_dataset, self.save_folder
                    )
                    all_results[eval_dataset] = {
                        "results": filter_jsonable(
                            results, json_encoder=MainzJSONEncoder
                        ),
                        "scores": filter_jsonable(
                            scores, json_encoder=MainzJSONEncoder
                        ),
                    }
                if self.opt["rank"] == 0:
                    all_results_path = os.path.join(self.save_folder, "scores.json")
                    with open(all_results_path, "w", encoding="utf-8") as f:
                        logger.info(f"Storing all results to: {all_results_path}")
                        json.dump(all_results, f, indent=4, cls=MainzJSONEncoder)
        except Exception as e:
            logger.warning(f"Caught exception {e}")
            raise e
        finally:
            self.close_tb_writers()

        return all_results

    @Timer("MainzTrainer: train")
    def train(self):
        """
        Perform model training
        """
        logger.warning(f"train on rank {self.opt['rank']}")
        logger.info("-----------------------------------------------")
        logger.info("Initializing model...")
        self.mode = self.opt["trainer_mode"] = "train"
        self.init_tb_writers()

        self.module_names, self.raw_modules, self.criteria = (
            self.task.set_up_model()
        )  # setup self.raw_modules as original model
        # move models to the device
        for module_name in self.module_names:
            self.raw_modules[module_name].to(self.opt["device"])
            if self.opt.get("ORT", None):
                from onnxruntime.training.ortmodule._custom_autograd_function import (
                    enable_custom_autograd_support,
                )

                enable_custom_autograd_support()
            if (
                self.opt.get("ORT", None)
                and self.opt.get("ORT_CONFIG", None) == "HIERARCHICAL"
            ):
                from onnxruntime.training.ortmodule.experimental.hierarchical_ortmodule import (
                    HierarchicalORTModule,
                )

                self.raw_modules[module_name] = HierarchicalORTModule(
                    self.raw_modules[module_name]
                )
                self.raw_modules[module_name].get_training_parameters = (
                    self.raw_modules[
                        module_name
                    ]._original_module.get_training_parameters
                )
            else:
                if self.opt.get("ORT", None):
                    from onnxruntime.training.ortmodule import ORTModule

                    self.raw_modules[module_name] = ORTModule(
                        self.raw_modules[module_name]
                    )
                self.raw_modules[module_name].get_training_parameters = (
                    self.raw_modules[module_name].get_training_parameters
                )
        for criterion_name in self.criteria:
            self.criteria[criterion_name].to(self.opt["device"])

        self.current_best_model_path = None
        self.train_batch_generator: Union[
            DataLoader, iterators.CheckpointableIterator
        ] = self.task.get_batch_generator(self, "train", is_evaluation=False)
        if self.is_infinite_batch_generator():
            # training batch generator is infinite
            self.updates_per_epoch = (
                self.opt["OPTIM_STEPS_PER_EPOCH"] * self.opt["GRADIENT_ACCUMULATE_STEP"]
            )
        elif isinstance(self.train_batch_generator.dataset, IterableDataset):
            self.updates_per_epoch = (
                len(self.train_batch_generator.dataset)
                // self.opt["TRAIN"]["BATCH_SIZE_TOTAL"]
                * self.opt["GRADIENT_ACCUMULATE_STEP"]
            )
        else:
            self.updates_per_epoch = len(self.train_batch_generator)
        self.num_updates = 0
        self.optim_steps = {module_name: 0 for module_name in self.module_names}
        self.start_epoch_idx = 0
        self.start_batch_idx = 0
        self.train_loss = {}  # track the average training losses
        self.train_items_per_batch = {}  # track the average item counts per batch
        self.has_cleared_cuda_cache = False

        if self.opt["DEEPSPEED"] or (not self.opt["DDP"] == "FSDP"):
            # optimizers of FSDP model should be set up after the model is wrapped (sharded)
            self._set_up_optimizers_and_lr_schedulers()
            self._print_number_of_params()
        # self.modules is self.raw_modules wrapped by distributed packages if necessary
        self.modules = {
            module_name: self.raw_modules[module_name]
            for module_name in self.module_names
        }
        if self.opt["DEEPSPEED"]:
            self._initialize_deepspeed()
        elif self.opt["DDP"] == "FSDP":
            """
            If RESUME == True, full model should be loaded before it is sharded,
            so FSDP is initialized in load_checkpoint()
            """
            if not self.opt.get("RESUME", False):
                for module_name in self.module_names:
                    self.modules[module_name] = self._initialize_fsdp(
                        self.modules[module_name]
                    )
                self._set_up_optimizers_and_lr_schedulers()
                self._print_number_of_params()
        else:
            self._initialize_fp16_DDP()

        # initialize weight smoothing states
        if self.opt.get("WEIGHT_SMOOTHING", None):
            # validate weight smoothing opt
            assert (
                "decay" in self.opt["WEIGHT_SMOOTHING"]
                and 1 > self.opt["WEIGHT_SMOOTHING"]["decay"] > 0
            )
            if self.opt["WEIGHT_SMOOTHING"].get("use_cpu", False):
                self.opt["WEIGHT_SMOOTHING"]["device"] = "cpu"
            else:
                self.opt["WEIGHT_SMOOTHING"]["device"] = self.opt["device"]

            self.weight_smoothing_states = {}
            for module_name in self.module_names:
                self.weight_smoothing_states[module_name] = ExponentialSmoothingState(
                    self.raw_modules[module_name], self.opt["WEIGHT_SMOOTHING"]
                )

        checkpoint_loaded = False
        is_nebula_checkpointing = self.opt.get("NEBULA_CHECKPOINTING", False)
        if self.opt.get("RESUME", False):
            # Resume complete training states, including optimizers, lr_schedulers,
            # train batch generator, and updates count
            # from the checkpoint location indicated in a .json file
            checkpoint_loaded = self.load_checkpoint()
        if not checkpoint_loaded and self.opt.get("RESUME_FROM", None):
            self.load_checkpoint(self.opt["RESUME_FROM"], must_exist=True)

        self._validate_num_updates()
        current_optim_steps = self._get_and_validate_current_optim_steps()
        ######################
        # Start the main loop
        ######################
        if self.opt.get("MAX_OPTIM_STEPS", -1) > -1:
            num_epochs = math.ceil(
                self.opt["MAX_OPTIM_STEPS"]
                * self.opt["GRADIENT_ACCUMULATE_STEP"]
                / self.updates_per_epoch
            )
            total_optim_steps = self.opt["MAX_OPTIM_STEPS"]
        else:
            num_epochs = self.opt["MAX_NUM_EPOCHS"]
            total_optim_steps = math.ceil(
                self.opt["MAX_NUM_EPOCHS"]
                * self.updates_per_epoch
                / self.opt["GRADIENT_ACCUMULATE_STEP"]
            )

        if self.opt["rank"] == 0:
            logger.info(f"********** Start training loop **********")  # noqa: F541
            logger.info(f"    Num of GPUs = {self.opt['world_size']}")
            logger.info(
                f"    Grad Accumulation Steps = {self.opt['GRADIENT_ACCUMULATE_STEP']}"
            )
            logger.info(f"    Num of Epochs = {num_epochs}")
            logger.info(f"    Num of Mini Batches per Epoch = {self.updates_per_epoch}")
            logger.info(
                f"    Total Num of Mini Batches = {total_optim_steps * self.opt['GRADIENT_ACCUMULATE_STEP']}"
            )
            logger.info(f"    Total Optimization Steps = {total_optim_steps}")
            logger.info(f"*****************************************")  # noqa: F541

        if self.opt.get("EVAL_AT_START", False):
            with Timer("MainzTrainer: initial evaluation"):
                self._eval_during_training(current_optim_steps)

        if self.opt["CUDA"] and self.opt.get("LOG_GPU_MEM", False):
            max_mem_alloc = torch.cuda.max_memory_allocated() / (1024 * 1024 * 1024)
            self.update_tb_writers(
                f"max_mem_alloc_in_GB_{self.opt['rank']}",
                max_mem_alloc,
                current_optim_steps,
            )
            torch.cuda.reset_peak_memory_stats()

        self.grad_acc_batches = []
        self.current_epoch_idx = None
        training_time_last_logged = datetime.now()
        train_items_last_logged = {
            key: obj.sum for key, obj in self.train_items_per_batch.items()
        }
        try:
            for epoch in range(self.start_epoch_idx, num_epochs):
                self.current_epoch_idx = epoch
                logger.warning(f"Epoch {epoch}")

                if self.opt.get("SET_SAMPLER_EPOCH", False) or (
                    isinstance(self.train_batch_generator, DataLoader)
                    and isinstance(
                        self.train_batch_generator.sampler, DistributedSampler
                    )
                ):
                    # if the sampler needs to set_sample_idx before set_epoch to prepare
                    # for checkpoint resumption, call this function here.
                    # currently only some vision samplers have this requirement.
                    if hasattr(self.train_batch_generator.sampler, "set_sample_idx"):
                        if self.current_epoch_idx == self.start_epoch_idx:
                            self.train_batch_generator.sampler.set_sample_idx(
                                self.train_batch_generator.batch_size
                                * self.start_batch_idx
                            )
                        else:
                            self.train_batch_generator.sampler.set_sample_idx(0)

                    # if hasattr(self.train_batch_generator.dataset, 'resume_from_checkpoint') \
                    # and self.start_batch_idx > 0 and self.current_epoch_idx == self.start_epoch_idx:
                    if hasattr(
                        self.train_batch_generator.dataset, "resume_from_checkpoint"
                    ):
                        if hasattr(
                            self.train_batch_generator.dataset, "resume_from_checkpoint"
                        ):
                            step_in_epoch = (
                                self.start_batch_idx
                                * self.opt["TRAIN"]["BATCH_SIZE_PER_GPU"]
                                if self.current_epoch_idx == self.start_epoch_idx
                                else 0
                            )
                            logger.info(
                                f"Resume data loader from checkpoint: epoch({epoch}), step_in_epoch({step_in_epoch})"
                            )
                            self.train_batch_generator.dataset.resume_from_checkpoint(
                                epoch, step_in_epoch
                            )
                    else:
                        self.train_batch_generator.sampler.set_epoch(
                            epoch
                        )  # otherwise each epoch will use the same random seed
                    logger.info(
                        f"Setting epoch {epoch} for {self.train_batch_generator.sampler}"
                    )

                epoch_start_time = datetime.now()

                epoch_timer = Timer(f"MainzTrainer: Epoch {epoch}")
                epoch_timer.start()

                batch_load_timer = Timer("MainzTrainer: load batch 0")
                batch_load_timer.start()

                batch_load_start_time = datetime.now()
                for batch_idx, batch in enumerate(self.train_batch_generator):
                    if self.current_epoch_idx == self.start_epoch_idx:
                        if self.is_checkpointable_batch_generator() or isinstance(
                            self.train_batch_generator.dataset, IterableDataset
                        ):
                            batch_idx += self.start_batch_idx
                        elif batch_idx < self.start_batch_idx:
                            continue
                    self.current_batch_idx = batch_idx

                    batch_load_timer.stop()

                    logger.debug(
                        f"batch loading on rank {self.opt['rank']} took \
                            {datetime.now() - batch_load_start_time} seconds."
                    )

                    # update
                    prev_optim_steps = current_optim_steps
                    if self.opt.get("FAKE_UPDATE", False) or (
                        self.opt.get("SKIP_STEPS", False)
                        and self.opt["SKIP_STEPS"][0]
                        < current_optim_steps
                        < self.opt["SKIP_STEPS"][1]
                    ):
                        # enable FAKE_UPDATE for testing batch loader
                        extra_info = self.fake_update(batch)
                    else:
                        extra_info = self.update(batch)
                    current_optim_steps = self._get_and_validate_current_optim_steps()

                    if (
                        prev_optim_steps != current_optim_steps
                    ):  # an optimizer update was made
                        # after every 'SAVE_STRATEGY.CHECKPOINT.SAVE_PER_OPTIM_STEPS' optimizations, save a checkpoint
                        save_a_checkpoint = False
                        save_a_model = False
                        if self.opt["SAVE_STRATEGY"]["CHECKPOINT"][
                            "SAVE_PER_OPTIM_STEPS"
                        ] >= SAVE_STRATEGY.PER_OPTIM_STEPS and (
                            current_optim_steps
                            % self.opt["SAVE_STRATEGY"]["CHECKPOINT"][
                                "SAVE_PER_OPTIM_STEPS"
                            ]
                            == 0
                        ):
                            save_a_checkpoint = True
                        if self.opt["SAVE_STRATEGY"]["MODEL"][
                            "SAVE_PER_OPTIM_STEPS"
                        ] >= SAVE_STRATEGY.PER_OPTIM_STEPS and (
                            current_optim_steps
                            % self.opt["SAVE_STRATEGY"]["MODEL"]["SAVE_PER_OPTIM_STEPS"]
                            == 0
                        ):
                            save_a_model = True

                        # after every 'SAVE_STRATEGY.CHECKPOINT.SAVE_PER_OPTIM_STEPS'
                        # optimizations, evaluate a checkpoint
                        eval_a_checkpoint = False
                        if self.opt["EVAL_STRATEGY"][
                            "EVAL_PER_OPTIM_STEPS"
                        ] >= EVAL_STRATEGY.PER_OPTIM_STEPS and (
                            current_optim_steps
                            % self.opt["EVAL_STRATEGY"]["EVAL_PER_OPTIM_STEPS"]
                            == 0
                        ):
                            eval_a_checkpoint = True
                        elif (
                            self.opt["EVAL_STRATEGY"]["EVAL_PER_OPTIM_STEPS"]
                            == EVAL_STRATEGY.SAVED_CHECKPOINT
                        ):  # fall back to SAVE CHECKPOINT
                            eval_a_checkpoint = save_a_checkpoint
                        elif (
                            self.opt["EVAL_STRATEGY"]["EVAL_PER_OPTIM_STEPS"]
                            == EVAL_STRATEGY.SAVED_MODEL
                        ):  # fall back to SAVE MODEL
                            eval_a_checkpoint = save_a_model
                        elif (
                            self.opt["EVAL_STRATEGY"]["EVAL_PER_OPTIM_STEPS"]
                            == EVAL_STRATEGY.SAVED_CHECKPOINT_AND_MODEL
                        ):  # fall back to SAVE_MODEL or SAVE CHECKPOINT
                            eval_a_checkpoint = save_a_checkpoint or save_a_model
                        elif (
                            self.opt["EVAL_STRATEGY"]["EVAL_PER_OPTIM_STEPS"]
                            == EVAL_STRATEGY.NO_EVAL
                        ):  # don't do any evaluation.
                            eval_a_checkpoint = False

                        # evaluate at the checkpointed moment, and log the results
                        got_better_score = False
                        if eval_a_checkpoint:
                            with Timer("MainzTrainer: evaluate checkpoint"):
                                got_better_score = self._eval_during_training(
                                    current_optim_steps
                                )
                                if got_better_score:
                                    logger.warning(
                                        f"Got new better scores on rank-{self.opt['rank']} \
                                            evaluator, at optim step {current_optim_steps}"
                                    )
                                if self.opt["world_size"] > 1:
                                    # `got_better_score` returned from `self.task.evaluate_model` is
                                    # supporsed to be consistant across all the ranks,
                                    # but in case it failed to do so, we always trust the conclustion on rank 0.
                                    # Broadcast the `got_better_score` result from rank 0, so all ranks have
                                    # consistant conclusion
                                    got_better_score = MPI.COMM_WORLD.bcast(
                                        got_better_score, root=0
                                    )

                        if got_better_score:
                            # Update self.current_best_model_path and save a checkpoint
                            self.update_best_checkpoint_or_model()
                            save_a_checkpoint = False  # self.update_best_checkpoint_or_model() saves a checkpoint
                            save_a_model = False  # self.update_best_checkpoint_or_model() already saves a model

                        if save_a_checkpoint:
                            # save complete training states, including model weights, optimizers, lr_schedulers,
                            # batch generator, and updates count
                            # number of last_n indicate that only keep the last_n saved folder, -1 means save all
                            last_n = self.opt["SAVE_STRATEGY"]["CHECKPOINT"].get(
                                "KEEP_LAST_N", -1
                            )
                            self.save_checkpoint(
                                current_optim_steps,
                                last_n=last_n,
                                is_nebula_checkpointing=is_nebula_checkpointing,
                            )
                        if save_a_model:
                            # save the pretrained model
                            # number of last_n indicate that only keep the last_n saved folder, -1 means save all
                            last_n = self.opt["SAVE_STRATEGY"]["MODEL"].get(
                                "KEEP_LAST_N", -1
                            )
                            self.save_pretrained_model(
                                current_optim_steps, last_n=last_n
                            )

                        # logging
                        log_first = self.opt.get("LOG_FIRST", 10)
                        log_every = self.opt.get("LOG_EVERY", 100)
                        if (
                            (current_optim_steps % log_every == 0)
                            or (epoch == 0 and current_optim_steps <= log_first)
                            or self.opt.get("DEBUG", False)
                        ):
                            # Call get_last_lr() if available. Otherwise, call get_lr().
                            # get_lr() has been deprecated in PyTorch 1.5, but DeepSpeed's
                            # LR schedulers do not have a function get_last_lr().
                            last_lr = {}
                            for module_name in self.module_names:
                                if (
                                    getattr(
                                        self.lr_schedulers[module_name],
                                        "get_last_lr",
                                        None,
                                    )
                                    is not None
                                ):
                                    last_lr[module_name] = self.lr_schedulers[
                                        module_name
                                    ].get_last_lr()[0]
                                else:
                                    last_lr[module_name] = self.lr_schedulers[
                                        module_name
                                    ].get_lr()[0]
                            # calculate new train items from the last logging, and the time used
                            train_items_delta = {}
                            for key, obj in self.train_items_per_batch.items():
                                train_items_delta[key] = (
                                    obj.sum
                                    if key not in train_items_last_logged
                                    else (obj.sum - train_items_last_logged[key])
                                )
                            train_time_delta = (
                                datetime.now() - training_time_last_logged
                            ).total_seconds()
                            # update training_time_last_logged and train_items_last_logged
                            training_time_last_logged = datetime.now()
                            train_items_last_logged = {
                                key: obj.sum
                                for key, obj in self.train_items_per_batch.items()
                            }

                            logger.info(
                                f"epochs[{epoch:6}] optim steps[{current_optim_steps:.0f}] "
                                f"learning rate[{', '.join([f'{key}: {val:.5e}' for key, val in last_lr.items()])}] "
                                f"""train loss[{', '.join(
                                    [f'{key}: {obj.val:.5f}/{obj.avg:.5f}' for key, obj in self.train_loss.items()]
                                    )}]"""
                                f"""items per batch[
                                {', '.join([f'''
                                        {key}: {int(obj.avg)}
                                        ''' for key, obj in self.train_items_per_batch.items()])}
                                    ]"""
                                f"""items per second
                                [{', '.join([
                                    f'{key}: {int(train_items_delta[key] / train_time_delta)}'
                                    for key in self.train_items_per_batch])}] """
                                f"""total items[{', '.join(
                                    [f'{key}: {obj.sum}' for key, obj in self.train_items_per_batch.items()]
                                    )}] """
                                f"mini batches[{self.num_updates:6}] "
                                f"extra_info[{extra_info}] "
                                f"""epoch remaining[
                                    {str((datetime.now() - epoch_start_time) / (batch_idx + 1) *
                                    (self.updates_per_epoch - batch_idx - 1)).split('.')[0]}]"""
                            )

                            for key, obj in self.train_loss.items():
                                self.update_tb_writers(
                                    f"train_loss_{key}", obj.val, current_optim_steps
                                )
                            for key, obj in self.train_items_per_batch.items():
                                self.update_tb_writers(
                                    f"items_per_batch_{key}",
                                    obj.avg,
                                    current_optim_steps,
                                )
                                self.update_tb_writers(
                                    f"items_per_second_{key}",
                                    train_items_delta[key] / train_time_delta,
                                    current_optim_steps,
                                )
                                self.update_tb_writers(
                                    f"total_items_{key}", obj.sum, current_optim_steps
                                )
                            for key, val in last_lr.items():
                                self.update_tb_writers(
                                    f"learning_rate_{key}", val, current_optim_steps
                                )

                            if self.opt["CUDA"] and self.opt.get("LOG_GPU_MEM", False):
                                max_mem_alloc = torch.cuda.max_memory_allocated() / (
                                    1024 * 1024 * 1024
                                )
                                self.update_tb_writers(
                                    f"max_mem_alloc_in_GB_{self.opt['rank']}",
                                    max_mem_alloc,
                                    current_optim_steps,
                                )
                                torch.cuda.reset_peak_memory_stats()

                    if (
                        self.opt.get("DEBUG", False) and batch_idx > 200
                    ):  # exit early for DEBUG mode
                        break

                    if (
                        self.is_infinite_batch_generator()
                        and batch_idx + 1 == self.updates_per_epoch
                    ):
                        break

                    if current_optim_steps >= total_optim_steps:
                        break

                    batch_load_timer = Timer(
                        f"MainzTrainer: load batch {batch_idx + 1}"
                    )
                    batch_load_timer.start()

                    batch_load_start_time = datetime.now()

                batch_load_timer.abort()
                epoch_timer.stop()

                logger.info(f"This epoch takes {datetime.now() - epoch_start_time}")
                logger.info(f"PROGRESS: {100.0 * (epoch + 1) / num_epochs:.2f}%")
                logger.info(f"Config files are at {self.opt['conf_files']}")

                if self.opt.get("DEBUG", False):  # exist early for DEBUG mode
                    break

                if current_optim_steps >= total_optim_steps:
                    break

            last_model_folder = None
            save_last_checkpoint = False
            save_last_model = False
            if (
                self.current_epoch_idx is not None
                and self.opt["SAVE_STRATEGY"]["CHECKPOINT"]["SAVE_PER_OPTIM_STEPS"]
                >= SAVE_STRATEGY.LAST
            ):
                save_last_checkpoint = True
            if (
                self.current_epoch_idx is not None
                and self.opt["SAVE_STRATEGY"]["MODEL"]["SAVE_PER_OPTIM_STEPS"]
                >= SAVE_STRATEGY.LAST
            ):
                save_last_model = True

            # evaluate at the end
            eval_last_checkpoint = False
            if self.opt["EVAL_STRATEGY"].get("EVAL_LAST_MODEL", False):
                eval_last_checkpoint = save_last_checkpoint
            if eval_last_checkpoint:
                got_better_score = False
                with Timer("MainzTrainer: evaluate final checkpoint"):
                    got_better_score = self._eval_during_training(current_optim_steps)
                    if got_better_score:
                        logger.warning(
                            f"""Got new better scores on rank-{self.opt['rank']}
                            evaluator, at optim step {current_optim_steps}"""
                        )
                    if self.opt["world_size"] > 1:
                        # `got_better_score` returned from `self.task.evaluate_model`
                        # is supporsed to be consistant across all the ranks,
                        # but in case it failed to do so, we always trust the conclustion on rank 0.
                        # Broadcast the `got_better_score` result from rank 0, so all ranks have consistant conclusion
                        got_better_score = MPI.COMM_WORLD.bcast(
                            got_better_score, root=0
                        )
                if got_better_score:
                    # Update self.current_best_model_path and save a checkpoint
                    self.update_best_checkpoint_or_model()

            if save_last_checkpoint:
                # number of last_n indicate that only keep the last_n saved checkpoint folder, -1 means save all
                last_n = self.opt["SAVE_STRATEGY"]["CHECKPOINT"].get("KEEP_LAST_N", -1)
                self.save_checkpoint(
                    current_optim_steps,
                    last_n=last_n,
                    is_nebula_checkpointing=is_nebula_checkpointing,
                )

            if save_last_model:
                # number of last_n indicate that only keep the last_n saved model folder, -1 means save all
                last_n = self.opt["SAVE_STRATEGY"]["MODEL"].get("KEEP_LAST_N", -1)
                last_model_folder = self.save_pretrained_model(
                    current_optim_steps, last_n=last_n
                )

        except Exception as e:
            logger.warning(f"Caught exception {e}")
            self.write_to_test_file(f"Exception {e} on rank {self.opt['rank']}")
            raise e
        finally:
            self.close_tb_writers()
            if isinstance(self.train_batch_generator, iterators.CheckpointableIterator):
                self.train_batch_generator.close()

        self.write_to_test_file("Done")

        return (
            self.current_best_model_path
            if self.current_best_model_path
            else last_model_folder
        )

    def write_to_test_file(self, content):
        if self.opt.get("IS_TEST_PROCESS", False):
            done_file_path = self.opt["TEST_DONE_FILE_PATH"]
            f = open(done_file_path, "w")
            f.write(content)
            f.close()

    def _eval_on_set(
        self, eval_dataset, save_folder, current_optim_steps=None, plot_label=""
    ):
        saving_label = eval_dataset
        if current_optim_steps:
            saving_label += f"_optim_step_{current_optim_steps}"
        if plot_label:
            plot_label = f"_{plot_label}"
            saving_label += plot_label

        logger.info(f"Evaluating on {saving_label}...")
        results, scores, got_better_score = self.task.evaluate_model(
            self, eval_dataset, save_folder, saving_label
        )
        for key in scores:
            self.update_tb_writers(
                f"{eval_dataset}_score_{key}{plot_label}",
                scores[key],
                current_optim_steps,
            )
        logger.warning(f"{saving_label}: Current scores: {scores}")
        if results:
            logger.warning(f"Current results breakdown:\n{results}")
        if self.mode == "train":
            logger.warning(f"Best scores: {self.task.eval_best_scores}")
            if self.task.eval_best_results:
                logger.warning(
                    f"Best results breakdown:\n{self.task.eval_best_results}"
                )

        return results, scores, got_better_score

    def _eval_during_training(self, current_optim_steps):
        _, _, got_better_score = self._eval_on_set(
            "dev", self.save_folder, current_optim_steps=current_optim_steps
        )
        if self.opt.get("WEIGHT_SMOOTHING", None) and self.opt["WEIGHT_SMOOTHING"].get(
            "eval_smoothed_weight", False
        ):
            with contextlib.ExitStack() as stack:
                for module_name in self.module_names:
                    stack.enter_context(
                        AssignSmoothingState(
                            self.weight_smoothing_states[module_name],
                            self.raw_modules[module_name],
                        )
                    )
                _, _, got_better_smoothed_score = self._eval_on_set(
                    "dev",
                    self.save_folder,
                    current_optim_steps=current_optim_steps,
                    plot_label="smoothed_weight",
                )
            got_better_score = got_better_score or got_better_smoothed_score
        return got_better_score

    def update_best_checkpoint_or_model(self):
        """
        This function saves the current checkpoint or model, and if 'COPY_BEST_CHECKPOINT' is `True`, copy the
        saved checkpoint/model to the best_model folder replacing their contents if any.
        """
        is_nebula_enabled = self.opt.get("NEBULA_CHECKPOINTING", False)
        is_copy_best_checkpoint = self.opt.get("COPY_BEST_CHECKPOINT", True)
        current_optim_steps = self._get_and_validate_current_optim_steps()
        logger.info(f"Updating best model with score {self.task.eval_best_scores}")
        # save the best scores in the self.best_model_path
        if self.opt["rank"] == 0:
            with open(
                os.path.join(self.best_model_path, "best_model_score.json"),
                "w",
                encoding="utf-8",
            ) as f:
                data = {
                    "validation_scores": filter_jsonable(
                        self.task.eval_best_scores, json_encoder=MainzJSONEncoder
                    ),
                    "tag": current_optim_steps,
                }
                json.dump(data, f, cls=MainzJSONEncoder)

        save_a_checkpoint = False
        save_a_model = False
        if (
            self.opt["SAVE_STRATEGY"]["CHECKPOINT"]["SAVE_PER_OPTIM_STEPS"]
            != SAVE_STRATEGY.NO_SAVE
        ):
            # save checkpoint
            save_a_checkpoint = True
        if (
            self.opt["SAVE_STRATEGY"]["MODEL"]["SAVE_PER_OPTIM_STEPS"]
            != SAVE_STRATEGY.NO_SAVE
        ):
            # save pretrained model
            save_a_model = True
        if not save_a_checkpoint and not save_a_model:
            return

        # need to update self.current_best_model_path ahead of self.save_checkpoint() call
        # because it is saved in the checkpoint as well
        if is_copy_best_checkpoint:
            # best model path points to the folder we will copy the best checkpoint to
            self.current_best_model_path = os.path.join(self.best_model_path, "model")
        else:
            # best model path points to the checkpoint folder
            self.current_best_model_path = os.path.join(
                self.save_folder, str(current_optim_steps)
            )

        if save_a_checkpoint:
            # save current checkpoint
            # if the save strategy of checkpoint is SAVE_STRATEGY.BEST, then only keep the last saved checkpoint folder
            # number of last_n indicate that only keep the last_n checkpoint model folder, -1 means save all
            last_n = (
                1
                if self.opt["SAVE_STRATEGY"]["CHECKPOINT"]["SAVE_PER_OPTIM_STEPS"]
                == SAVE_STRATEGY.BEST
                else self.opt["SAVE_STRATEGY"]["CHECKPOINT"].get("KEEP_LAST_N", -1)
            )
            saved_checkpoint_folder = self.save_checkpoint(
                current_optim_steps,
                last_n=last_n,
                is_nebula_checkpointing=is_nebula_enabled,
            )

        if save_a_model:
            # save current pretrained model
            # if the save strategy of model is SAVE_STRATEGY.BEST, then only keep the last saved model folder
            # number of last_n indicate that only keep the last_n saved model folder, -1 means save all
            last_n = (
                1
                if self.opt["SAVE_STRATEGY"]["MODEL"]["SAVE_PER_OPTIM_STEPS"]
                == SAVE_STRATEGY.BEST
                else self.opt["SAVE_STRATEGY"]["MODEL"].get("KEEP_LAST_N", -1)
            )
            saved_pretrained_model_folder = self.save_pretrained_model(
                current_optim_steps, last_n=last_n
            )

        # make sure checkpoint saving is finished on all ranks
        self._dist_barrier()

        # Note: When enable 'NEBULA_CHECKPOINTING' as true for checkpoint saving,
        # the saving process was asynchronous. so not allow copying
        # Copying behavior will happen only for None-Nebula
        if is_copy_best_checkpoint:
            # copy checkpoint contents to best model folder
            # for later supporting the Nebula async persisting checkpoint,
            # the Nebula is disabled when 'COPY_BEST_CHECKPOINT' is true
            if self.opt["rank"] == 0:

                @retry_on_failure(
                    max_retries=3,
                    on_retry_func=lambda idx: logger.info(
                        f"Retry #{idx} copy on best checkpoint of {saved_pretrained_model_folder}"
                    ),
                )
                def copy_best_checkpoint():

                    def copytree(src, dst, symlinks=False, ignore=None):
                        if not os.path.exists(dst):
                            os.makedirs(dst)
                            shutil.copystat(src, dst)
                        lst = os.listdir(src)
                        if ignore:
                            excl = ignore(src, lst)
                            lst = [x for x in lst if x not in excl]
                        for item in lst:
                            s = os.path.join(src, item)
                            d = os.path.join(dst, item)
                            if symlinks and os.path.islink(s):
                                if os.path.lexists(d):
                                    os.remove(d)
                                os.symlink(os.readlink(s), d)
                                try:
                                    st = os.lstat(s)
                                    mode = stat.S_IMODE(st.st_mode)
                                    os.lchmod(d, mode)
                                except Exception as e:
                                    # lchmod not available
                                    logger.info(
                                        f"Ignore copytree() exception: {str(e)}"
                                    )
                                    pass
                            elif os.path.isdir(s):
                                copytree(s, d, symlinks, ignore)
                            else:
                                shutil.copy2(s, d)

                    if os.path.isdir(self.current_best_model_path):
                        shutil.rmtree(self.current_best_model_path, ignore_errors=True)
                    if save_a_model:
                        copytree(
                            saved_pretrained_model_folder, self.current_best_model_path
                        )
                    if save_a_checkpoint:
                        copytree(saved_checkpoint_folder, self.current_best_model_path)

                copy_best_checkpoint()

            self._dist_barrier()
        else:
            assert self.current_best_model_path == saved_pretrained_model_folder

        if self.opt["rank"] == 0:
            # save the best checkpoint location to json file
            checkpoint_location = {
                "NEBULA_CHECKPOINTING": is_nebula_enabled,
                "is_checkpoint_and_model_folder_separated": True,
                "checkpoint_tag": str(current_optim_steps),
                "best_scores": filter_jsonable(
                    self.task.eval_best_scores, json_encoder=MainzJSONEncoder
                ),
                "current_best_model_path": (
                    os.path.relpath(
                        self.current_best_model_path, start=self.opt["SAVE_DIR"]
                    )
                    if self.current_best_model_path
                    else None
                ),
                "checkpoint_path": os.path.relpath(
                    self.save_folder, start=self.opt["SAVE_DIR"]
                ),
            }
            with open(
                os.path.join(
                    self.opt["SAVE_DIR"], f"{self.opt['BASENAME']}_best_checkpoint.json"
                ),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(checkpoint_location, f, cls=MainzJSONEncoder)

    def fake_update(self, batch):
        """
        Helper for debugging data-loading issues. To use this, change the call to update() above to fake_update().
        """
        if self.is_gradient_accumulation_boundary():
            for module_name in self.module_names:
                self.optim_steps[module_name] += 1
                self.modules[module_name].global_steps += 1
        self.num_updates += 1
        logger.info(f"Mini-batch {self.num_updates}")

    @Timer("MainzTrainer: forward pass")
    def forward_pass(
        self,
        forward_func: Callable[["MainzTrainer", Any], torch.Tensor],
        batch,
        skip_gradient_sync: bool = False,
    ):  # noqa: E252
        """
        Apply forward pass of the batch through the module according to the provided forward function
        Task.train_step() calls this function to let it handle DeepSpeed, DDP behind the scenes.

        Args:
            forward_func (Callable[[MainzTrainer, Any], torch.Tensor]): forward function provided by user
                to define forward computation of batch through MainzTrainer.modules and MainzTrainer.criteria.
            batch: input batch for the forward pass.
            skip_gradient_sync (bool): True if the gradient allreduce can be skipped.

        Returns:
            torch.Tensor: loss tensor
        """
        # forward
        forward_start_time = datetime.now()
        if self.opt["DEEPSPEED"]:
            if self.opt["FP16"]:
                # in FP16 mode, DeepSpeed casts the model to FP16, so the input needs to be manually casted to FP16
                batch = cast_batch_to_half(batch)
            elif self.opt["BF16"]:
                batch = cast_batch_to_bf16(batch)
            loss = forward_func(self, batch)
        elif self.opt["DDP"] == "FSDP":
            if skip_gradient_sync:
                from fairscale.nn.data_parallel import FullyShardedDataParallel as FSDP

                with contextlib.ExitStack() as stack:
                    for tmp_module_name, tmp_module in self.modules.items():
                        for module in tmp_module.modules():
                            if isinstance(module, FSDP):
                                stack.enter_context(module.no_sync())
                    loss = forward_func(self, batch)
            else:
                if self.opt["rank"] == 0:
                    logger.debug("Performing synchronized forward.")
                loss = forward_func(self, batch)
        else:

            def forward(func, trainer, batch, skip_gradient_sync):
                if skip_gradient_sync:
                    if self.opt["DDP"] == "MAINZ":
                        loss = func(trainer, batch)
                    elif self.opt["DDP"] == "APEX":
                        for tmp_module_name, tmp_module in self.modules.items():
                            tmp_module.disable_allreduce()
                        loss = func(trainer, batch)
                        for tmp_module_name, tmp_module in self.modules.items():
                            tmp_module.enable_allreduce()
                    else:  # self.opt['DDP'] == 'PYTORCH'
                        with contextlib.ExitStack() as stack:
                            for tmp_module_name, tmp_module in self.modules.items():
                                stack.enter_context(tmp_module.no_sync())
                            loss = func(trainer, batch)
                else:
                    if self.opt["rank"] == 0:
                        logger.debug("Performing synchronized forward.")
                    loss = func(trainer, batch)
                return loss

            if self.opt["FP16"] and self.opt["AMP"] == "PYTORCH":
                from torch.cuda.amp import autocast

                with autocast():
                    loss = forward(forward_func, self, batch, skip_gradient_sync)
            else:
                loss = forward(forward_func, self, batch, skip_gradient_sync)
        logger.debug(
            f"forward on rank {self.opt['rank']} took {datetime.now() - forward_start_time} seconds."
        )

        return loss

    @Timer("MainzTrainer: backward pass")
    def backward_pass(
        self,
        loss: torch.Tensor,
        skip_gradient_sync: bool = False,
        module_names=["default"],
    ):  # noqa: E252
        """
        Apply backward pass on the loss tensor.
        Task.train_step() calls this function to let it handle DeepSpeed, FP16, and DDP behind the scenes.

        Args:
            loss (torch.Tensor): loss tensor used for backward
            skip_gradient_sync (bool): True if the gradient allreduce can be skipped.
            module_names (list): list of module names that will receive gradients in this backward pass.
                When using DeepSpeed, there can only be one module receiving gradients.

        Returns:
            torch.Tensor: loss tensor after scaled to the gradient accumulation steps.
        """
        # backward
        backward_start_time = datetime.now()
        if self.opt["DEEPSPEED"]:
            if len(module_names) > 1:
                raise ValueError(
                    "Only one module can receive the gradients in one backward pass."
                )
            # DeepSpeed scale the loss to the gradient accumulation steps during backward
            loss = self.modules[module_names[0]].backward(loss)
        elif self.opt["DDP"] == "FSDP":
            # scale the loss to the gradient accumulation steps
            if self.opt["GRADIENT_ACCUMULATE_STEP"] > 1:
                loss = loss / self.opt["GRADIENT_ACCUMULATE_STEP"]
            if self.opt["FSDP_SETTING"]["MIXED_PRECISION"]:
                loss = self.sharded_grad_scaler.scale(loss)
            if skip_gradient_sync:
                from fairscale.nn.data_parallel import FullyShardedDataParallel as FSDP

                with contextlib.ExitStack() as stack:
                    for tmp_module_name, tmp_module in self.modules.items():
                        for module in tmp_module.modules():
                            if isinstance(module, FSDP):
                                stack.enter_context(module.no_sync())
                    loss.backward()
            else:
                if self.opt["rank"] == 0:
                    logger.debug(
                        f"Performing synchronized backward at step {self.optim_steps[module_names[0]]}."
                    )
                loss.backward()
        else:

            def backward(loss_tensor, skip_gradient_sync):
                if skip_gradient_sync:
                    if self.opt["DDP"] == "MAINZ":
                        loss_tensor.backward()
                    elif self.opt["DDP"] == "APEX":
                        for tmp_module_name, tmp_module in self.modules.items():
                            tmp_module.disable_allreduce()
                        loss_tensor.backward()
                        for tmp_module_name, tmp_module in self.modules.items():
                            tmp_module.enable_allreduce()
                    else:  # self.opt['DDP'] == 'PYTORCH'
                        with contextlib.ExitStack() as stack:
                            for tmp_module_name, tmp_module in self.modules.items():
                                stack.enter_context(tmp_module.no_sync())
                            loss_tensor.backward()
                else:
                    if self.opt["rank"] == 0:
                        logger.debug(
                            f"Performing synchronized backward at step {self.optim_steps[module_names[0]]}."
                        )
                    loss_tensor.backward()
                    if self.opt["world_size"] > 1:
                        if self.opt["DDP"] == "MAINZ":
                            for module_name in module_names:
                                self.modules[module_name].all_reduce_grads()

            # scale the loss to the gradient accumulation steps
            if self.opt["GRADIENT_ACCUMULATE_STEP"] > 1:
                loss = loss / self.opt["GRADIENT_ACCUMULATE_STEP"]
            if self.opt["FP16"]:
                if self.opt["AMP"] == "APEX":
                    # By delaying amp gradient unscaling during gradient accumulation, and only allowing unscaling
                    # at gradient accumulation boundary,
                    # we avoid partially syncing the gradients at accumulation boundary.
                    # It allows us to skip gradient allreduce during gradient accumulation,
                    # without letting the model going out of sync.
                    from apex import amp

                    if self.opt["world_size"] > 1 and self.opt["DDP"] == "MAINZ":
                        optimizer_list = []
                        for module_name in module_names:
                            optimizer_list.extend(
                                self.optimizers[module_name].inner_optimizer_list
                            )
                    else:
                        optimizer_list = [
                            self.optimizers[module_name] for module_name in module_names
                        ]
                    with amp.scale_loss(
                        loss, optimizer_list, delay_unscale=skip_gradient_sync
                    ) as scaled_loss:
                        backward(scaled_loss, skip_gradient_sync)
                else:  # self.opt['AMP'] == 'PYTORCH'
                    backward(self.grad_scaler.scale(loss), skip_gradient_sync)
            else:
                backward(loss, skip_gradient_sync)
        logger.debug(
            f"backward on rank {self.opt['rank']} took {datetime.now() - backward_start_time} seconds."
        )

        return loss

    def _get_grad_clipping_params(self, module_name):
        if self.opt["DDP"] == "FSDP":
            if "fsdp_expert_grid" in self.opt:
                from ..Models.Networks.moe_module.ort_moe.utils import (
                    get_non_expert_parameters_list,
                )

                grad_clipping_params = get_non_expert_parameters_list(
                    self.modules[module_name]
                )
            else:
                grad_clipping_params = self.modules[module_name].parameters()
        elif self.opt["FP16"] and self.opt["AMP"] == "APEX":
            from apex import amp

            grad_clipping_params = amp.master_params(self.optimizers[module_name])
        else:
            grad_clipping_params = self.modules[module_name].parameters()
        return grad_clipping_params

    def _get_grad_clipping_dgrid_params(self, module_name):
        dgrid_params = OrderedDict()
        for dgrid, named_params in self.modules[module_name].dgrid_named_params.items():
            if self.opt["FP16"] and self.opt["AMP"] == "APEX":
                from apex import amp

                dgrid_params[dgrid] = list(
                    amp.master_params(
                        self.optimizers[module_name].dgrid_optimizer[dgrid]
                    )
                )
            else:
                dgrid_params[dgrid] = [p for (_, p) in named_params]
        return dgrid_params

    @Timer("MainzTrainer: model update step")
    def step(self, is_gradient_accumulation_boundary, module_name="default"):
        """
        Apply update step to the trainable module parameters if at gradient accumulation boundary.
        It should be called on each module once and only once in each train_step.
        Task.train_step() calls this function to let it handle DeepSpeed, DDP
        and gradient accumulation behind the scenes.

        Args:
            module_name (str): the name of the module to be updated
            batch_size (Optional[int]): the number of target labels in the effective batch.
        """
        # step
        step_start_time = datetime.now()
        if self.opt["DEEPSPEED"]:
            assert (
                self.modules[module_name].is_gradient_accumulation_boundary()
                == is_gradient_accumulation_boundary
            )
            self.modules[module_name].step()
            self.optim_steps[module_name] = self.modules[module_name].global_steps
        elif self.opt["DDP"] == "FSDP":
            if is_gradient_accumulation_boundary:
                if self.opt["FSDP_SETTING"]["MIXED_PRECISION"]:
                    self.sharded_grad_scaler.unscale_(self.optimizers[module_name])
                max_norm = self.opt.get("GRAD_CLIPPING", 0)
                if max_norm > 0:
                    norm = clip_grad_norm_fsdp(
                        self._get_grad_clipping_params(module_name), None, max_norm
                    )
                    num_elem = sum(
                        sum(param.shape)
                        for param in self._get_grad_clipping_params(module_name)
                    )
                    if norm > max_norm:
                        logger.info(
                            f"""Gradient was clipped: norm = {norm}, per param = {norm / np.sqrt(num_elem)};
                            max_norm = {max_norm}, per param = {max_norm / np.sqrt(num_elem)}"""
                        )
                if self.opt["FSDP_SETTING"]["MIXED_PRECISION"]:
                    self.sharded_grad_scaler.step(self.optimizers[module_name])
                else:
                    self.optimizers[module_name].step()

                if "OPTIM_SET_TO_NONE" in self.opt:
                    self.optimizers[module_name].zero_grad(
                        set_to_none=self.opt["OPTIM_SET_TO_NONE"]
                    )
                else:
                    self.optimizers[module_name].zero_grad()
                self.lr_schedulers[module_name].step()
                self.optim_steps[module_name] += 1
        else:
            if is_gradient_accumulation_boundary:
                if self.opt["FP16"]:
                    if self.opt["AMP"] == "PYTORCH":
                        if self.opt["world_size"] > 1 and self.opt["DDP"] == "MAINZ":
                            found_infs = []
                            for optimizer in self.optimizers[
                                module_name
                            ].inner_optimizer_list:
                                self.grad_scaler.unscale_(optimizer)
                                found_inf_per_device = (
                                    self.grad_scaler._found_inf_per_device(optimizer)
                                )
                                assert (
                                    len(found_inf_per_device) == 1
                                    and self.opt["device"] in found_inf_per_device
                                )
                                found_infs.append(
                                    found_inf_per_device[self.opt["device"]]
                                )
                            found_inf_combined = found_infs[0]
                            if len(found_infs) > 1:
                                for i in range(1, len(found_infs)):
                                    found_inf_combined += found_infs[i]
                            torch.distributed.all_reduce(
                                found_inf_combined, op=torch.distributed.ReduceOp.MAX
                            )
                            for found_inf in found_infs:
                                found_inf.copy_(found_inf_combined)
                        else:
                            self.grad_scaler.unscale_(self.optimizers[module_name])

                max_norm = self.opt.get("GRAD_CLIPPING", 0)
                if max_norm > 0:
                    if self.opt["world_size"] > 1 and self.opt["DDP"] == "MAINZ":
                        norm = self.modules[module_name].clip_grad_norm_(
                            self._get_grad_clipping_dgrid_params(module_name),
                            self.modules[module_name].process_groups,
                            max_norm,
                        )
                    else:
                        norm = torch.nn.utils.clip_grad_norm_(
                            self._get_grad_clipping_params(module_name), max_norm
                        )
                    if norm > max_norm:
                        logger.warning(
                            f"Gradient was clipped: norm = {norm}; max_norm = {max_norm}"
                        )

                # stupid hack needed to correctly resume APEX AMP O2 checkpoint
                # the optimizer states need to be loaded again right before the first `step()` after resumption.
                if (
                    self.opt["FP16"]
                    and self.opt["AMP"] == "APEX"
                    and self.opt["FP16_OPT_LEVEL"] == "O2"
                    and hasattr(self, f"apex_amp_o2_optim_state_dict_{module_name}")
                ):
                    if self.opt["world_size"] > 1 and self.opt["DDP"] == "MAINZ":
                        self.optimizers[module_name].load_dgrid_state_dict(
                            getattr(self, f"apex_amp_o2_optim_state_dict_{module_name}")
                        )
                    else:
                        self.optimizers[module_name].load_state_dict(
                            getattr(self, f"apex_amp_o2_optim_state_dict_{module_name}")
                        )
                    delattr(self, f"apex_amp_o2_optim_state_dict_{module_name}")

                def optim_step(optimizer):
                    if self.opt["FP16"] and self.opt["AMP"] == "PYTORCH":
                        if self.opt["world_size"] > 1 and self.opt["DDP"] == "MAINZ":
                            for inner_optimizer in optimizer.inner_optimizer_list:
                                self.grad_scaler.step(inner_optimizer)
                        else:
                            self.grad_scaler.step(optimizer)
                    else:
                        optimizer.step()

                if self.opt["USE_HIT"]:
                    import hit

                    with hit.ensure_hit_syncs(self.optimizers[module_name]) as optim:
                        optim_step(optim)
                else:
                    optim_step(self.optimizers[module_name])
                self.optimizers[module_name].zero_grad()
                self.lr_schedulers[module_name].step()
                self.optim_steps[module_name] += 1

        self.stepped_modules.append(module_name)
        logger.debug(
            f"step on rank {self.opt['rank']} took {datetime.now() - step_start_time} seconds."
        )

    @Timer("MainzTrainer: mini batch update")
    def update(self, batch):
        """
        One mini-batch update
        This method is called in each iteration in the main training loop in train() method.
        Within the gradient accumulation boundaries, it simply aggregate a mini-batch to self.grad_acc_batches list.
        On the gradient accumulation boundary, it calls task.train_step() to execute the training step logic on each
        aggregated mini-batch, and collects and aggregates returned mini-batch losses and sample sizes to be logged
        and plotted.
        'extra_info' returned from task.train_step() will be aggregated and directly added to the logs.
        """
        self.grad_acc_batches.append(batch)
        aggregated_extra_info = {}
        if self.is_gradient_accumulation_boundary():
            # set all modules and criteria into training mode
            for module_name in self.module_names:
                self.modules[module_name].train()
            for criterion_name in self.criteria:
                self.criteria[criterion_name].train()

            assert len(self.grad_acc_batches) == self.opt["GRADIENT_ACCUMULATE_STEP"]
            acc_loss = {}
            acc_items_per_batch = {}
            for batch_index, batch in enumerate(self.grad_acc_batches):
                # put the batch to the device
                batch = move_batch_to_device(batch, self.opt["device"])

                self.stepped_modules = []
                try:
                    loss_info, sample_size_info, extra_info = self.task.train_step(
                        self,
                        batch,
                        self.grad_acc_batches,
                        batch_index,
                        is_distributed=(self.opt["world_size"] > 1),
                        is_gradient_accumulation_boundary=(
                            batch_index + 1 == self.opt["GRADIENT_ACCUMULATE_STEP"]
                        ),
                    )
                    if len(self.stepped_modules) != len(self.module_names) or set(
                        self.stepped_modules
                    ) != set(self.module_names):
                        raise ValueError(
                            """In one task.train_step() call, step()
                            should be called on every module once and only once."""
                        )

                    # collect and accumulate the losses and sample sizes from this mini-batch
                    for key in loss_info:
                        if key not in acc_loss:
                            acc_loss[key] = 0
                        sample_size_info[f"{key}_count"] = sample_size_info.get(
                            f"{key}_count", 1
                        )
                        acc_loss[key] += (
                            loss_info[key]
                            * sample_size_info[f"{key}_count"]
                            / self.opt["GRADIENT_ACCUMULATE_STEP"]
                        )

                    for key in sample_size_info:
                        if key not in acc_items_per_batch:
                            acc_items_per_batch[key] = 0
                        acc_items_per_batch[key] += sample_size_info[key]

                    for key in extra_info:
                        if key not in aggregated_extra_info:
                            aggregated_extra_info[key] = []
                        aggregated_extra_info[key].append(extra_info[key])

                    if not self.opt["DEEPSPEED"]:
                        # Emptying the CUDA cache after the first step can reduce the chance of OOM.
                        # Idea from fairseq trainer:
                        # https://github.com/pytorch/fairseq/blob/1164a7fc432a188d401895018eaa85175fb06f9d/fairseq/trainer.py#L903
                        if self.opt["CUDA"] and not self.has_cleared_cuda_cache:
                            torch.cuda.empty_cache()
                            self.has_cleared_cuda_cache = True
                except RuntimeError as e:
                    if not self.opt["DEEPSPEED"] and "out of memory" in str(e):
                        self._log_oom(e)

                        logger.warning(
                            "attempting to recover from OOM in forward/backward pass"
                        )
                        for module_name in self.module_names:
                            self.optimizers[module_name].zero_grad()
                        if self.opt["CUDA"]:
                            torch.cuda.empty_cache()
                    else:
                        if "out of memory" in str(e):
                            self._log_oom(e)
                        raise e

            if self.opt["DEEPSPEED"]:
                pass
            elif self.opt["DDP"] == "FSDP":
                if self.opt["FSDP_SETTING"]["MIXED_PRECISION"]:
                    # Update GradScaler after an effective batch
                    self.sharded_grad_scaler.update()
            else:
                if self.opt["FP16"] and self.opt["AMP"] == "PYTORCH":
                    # Update GradScaler after an effective batch
                    self.grad_scaler.update()

            # update losses and item counts of an effective batch to the AverageMeters
            if self.opt["world_size"] > 1:
                # Averaging the losses across the processes
                # The resulting loss values will be the averaged losses of all mini batches within one batch
                keys = [key for key in acc_loss]
                keys.sort()  # sort the keys to make sure the orders are same on different ranks
                vals = torch.tensor([acc_loss[key] for key in keys]).to(
                    self.opt["device"]
                )
                torch.distributed.all_reduce(vals, torch.distributed.ReduceOp.SUM)
                vals = vals.tolist()
                for key, val in zip(keys, vals):
                    acc_loss[key] = val / self.opt["world_size"]

                # Accumulating the item counts across the processes
                # The resulting item count values will be the sum of item counts in all mini batches within one batch
                keys = [key for key in acc_items_per_batch]
                keys.sort()  # sort the keys to make sure the orders are same on different ranks
                vals = torch.tensor([acc_items_per_batch[key] for key in keys]).to(
                    self.opt["device"]
                )
                torch.distributed.all_reduce(vals, torch.distributed.ReduceOp.SUM)
                vals = vals.tolist()
                for key, val in zip(keys, vals):
                    acc_items_per_batch[key] = val

                for key in aggregated_extra_info:
                    aggregated_extra_info[key] = MPI.COMM_WORLD.allgather(
                        aggregated_extra_info[key]
                    )

            log_every = self.opt.get("LOG_EVERY", 100)
            for key in acc_loss:
                loss_count = acc_items_per_batch.pop(f"{key}_count") / (
                    self.opt["GRADIENT_ACCUMULATE_STEP"] * self.opt["world_size"]
                )
                loss_val = acc_loss[key] / loss_count
                if key not in self.train_loss:
                    self.train_loss[key] = AverageMeter()
                self.train_loss[key].update(loss_val, loss_count, log_every)
            for key in acc_items_per_batch:
                if key not in self.train_items_per_batch:
                    self.train_items_per_batch[key] = AverageMeter()
                self.train_items_per_batch[key].update(acc_items_per_batch[key], 1)

            self.grad_acc_batches = []

            # update weight smoothing states with updated models
            if self.opt.get("WEIGHT_SMOOTHING", None):
                for module_name in self.module_names:
                    smoothing_batch_size_name = self.weight_smoothing_states[
                        module_name
                    ].ref_batch_size_name
                    if smoothing_batch_size_name is not None:
                        smoothing_batch_size = self.train_items_per_batch[
                            smoothing_batch_size_name
                        ].val
                        smoothing_total_size = self.train_items_per_batch[
                            smoothing_batch_size_name
                        ].sum
                    else:
                        smoothing_batch_size = 1
                        smoothing_total_size = self.optim_steps[module_name]

                    self.weight_smoothing_states[module_name].step(
                        self.raw_modules[module_name],
                        smoothing_batch_size,
                        smoothing_total_size,
                    )

        self.num_updates += 1

        return aggregated_extra_info

    @Timer("MainzTrainer: save model")
    def save_pretrained_model(self, tag, last_n=-1):
        """
        Save
        1. model with save_pretrained API for model transfer.
        2. smoothed parameters

        Args:
            tag (int): the tag of the checkpoint, usually be the optim_step number
            last_n(int): the number of saved folders, default is -1 which means keeping all saved folders
        Returns:
            save_dir (str): the folder path of the saved model and the smoothed parameters
        """
        # save models
        save_dir = os.path.join(self.save_folder, str(tag))
        if os.path.isdir(save_dir):
            logger.warning(f"Already saved a model at {save_dir}. Skip this saving.")
            return save_dir

        self.creat_dir(save_dir)

        logger.warning("Saving model...")

        if (
            self.opt["rank"] == 0
            or (
                not self.opt["DEEPSPEED"]
                and self.opt["world_size"] > 1
                and self.opt["DDP"] == "MAINZ"
            )
            or (
                not self.opt["DEEPSPEED"]
                and self.opt["world_size"] > 1
                and self.opt["DDP"] == "FSDP"
            )
        ):

            num_retries = 0
            while num_retries < 3:
                try:
                    for module_name in self.module_names:
                        module_save_dir = os.path.join(save_dir, module_name)
                        os.makedirs(module_save_dir, exist_ok=True)
                        self.raw_modules[module_name].save_pretrained(module_save_dir)

                        # save a smoothed model
                        if self.opt.get("WEIGHT_SMOOTHING", None):
                            smoothed_module_save_dir = os.path.join(
                                module_save_dir, "smoothed_model"
                            )
                            os.makedirs(smoothed_module_save_dir, exist_ok=True)
                            with AssignSmoothingState(
                                self.weight_smoothing_states[module_name],
                                self.raw_modules[module_name],
                            ):
                                self.raw_modules[module_name].save_pretrained(
                                    smoothed_module_save_dir
                                )

                    logger.warning(f"Finished saving model to {save_dir}.")
                    break

                except OSError as err:
                    logger.warning(err)
                    logger.warning(
                        "Failed to save model, waiting for 2 minutes to retry."
                    )
                    time.sleep(120)
                num_retries += 1

            if num_retries >= 3:
                logger.warning(
                    f"Failed to save model for {num_retries} times, continue training."
                )
            else:
                # Apply the logic (may delete folders) of keeping the last N folders when the saving is successful.
                if last_n > 0:
                    if self.opt["rank"] == 0:
                        pretrained_model_folders = [
                            os.path.join(self.save_folder, x.name)
                            for x in os.scandir(self.save_folder)
                            if x.is_dir() and x.name.isdecimal()
                        ]
                        self.keep_last_N_folders(pretrained_model_folders, last_n)
        self._dist_barrier()
        return save_dir

    def creat_dir(self, path):
        """
        Create the foler with the path.

        Args:
            path (str): the folder path of the dir
        """
        self._dist_barrier()
        if self.opt["rank"] == 0:
            os.makedirs(path, exist_ok=False)
        self._dist_barrier()
        if self.opt["world_size"] > 1:
            # this second os.makedirs() call on all ranks is to force sync
            # the save_dir creation between blobFuse and local fs
            os.makedirs(path, exist_ok=True)

    def delete_folders(self, folders):
        if self.opt["rank"] == 0:
            for folder_to_be_cleaned in folders:
                shutil.rmtree(folder_to_be_cleaned, ignore_errors=True)

    def keep_last_N_folders(self, original_folders, n, folder_prefix=None):
        if n >= 0 and len(original_folders) > 0:
            if folder_prefix:
                original_folders.sort(
                    key=lambda x: int(os.path.basename(x).split(folder_prefix)[1]),
                    reverse=True,
                )
            else:
                original_folders.sort(
                    key=lambda x: int(os.path.basename(x)), reverse=True
                )
            folders_to_be_deleted = original_folders[n:]
            if len(folders_to_be_deleted) > 0:
                logger.info(
                    f"Only keep at most {n} latest saved folders, folders to be deleted: {folders_to_be_deleted}"
                )
                self.delete_folders(folders_to_be_deleted)

    @Timer("MainzTrainer: save checkpoint")
    def save_checkpoint(self, tag, last_n=-1, is_nebula_checkpointing=False):
        """
        Save complete training states, including model weights, optimizers, lr_schedulers,
        fp16 loss scaler, random state, batch generator, and updates count
        Args:
            tag (int): the tag of the checkpoint, usually be the optim_step number
            last_n(int): the number of saved folders, default is -1 which means keeping all saved folders
            is_nebula_checkpointing (bool): true if Nebula is enabled for checkpointing
        Returns:
            str: the real checkpoint' state file path for non-Nebula loading or partition for Nebula loading
        """
        save_dir = os.path.join(self.save_folder, "checkpoint_step" + str(tag))
        nebula_snapshot = None
        if is_nebula_checkpointing:
            nebula_tag_name = get_nebula_checkpoint_tag_name(str(tag))
            logger.warning(f"Creating Nabula checkpoint with tag: {nebula_tag_name}")
            if self.opt["world_size"] > 1:
                torch.distributed.barrier()
            import torch_nebula

            nebula_snapshot = torch_nebula.get_checkpoint(tag=nebula_tag_name)
            if nebula_snapshot is not None:
                logger.warning(
                    f"Already saved a Nebula checkpoint {nebula_tag_name}. Skip this saving."
                )
                return nebula_tag_name
            nebula_snapshot = torch_nebula.Checkpoint(nebula_tag_name)
        else:
            save_dir = os.path.join(self.save_folder, "checkpoint_step" + str(tag))
            if os.path.isdir(save_dir):
                logger.warning(
                    f"Already saved a checkpoint or pretrained model at {save_dir}. Skip this saving."
                )
                return save_dir
            self.creat_dir(save_dir)

        logger.warning("Saving checkpoint...")
        resume_epoch_idx = self.current_epoch_idx
        resume_batch_idx = self.current_batch_idx + 1
        if resume_batch_idx == self.updates_per_epoch:
            resume_batch_idx = 0
            resume_epoch_idx += 1

        num_retries = 0
        while num_retries < 3:
            try:
                for module_name in self.module_names:
                    # save each model's training states
                    if self.opt["DEEPSPEED"]:
                        self.modules[module_name].save_checkpoint(save_dir, module_name)
                    elif self.opt["DDP"] == "FSDP":
                        """
                        We will save the full modules and sharded optimizers for FSDP.
                        To rebuild the full model, the state_dict() needs to be called for all ranks.
                        """
                        if self.opt["FSDP_SETTING"]["MIXED_PRECISION"]:
                            amp_state = self.sharded_grad_scaler.state_dict()
                        else:
                            amp_state = None

                        if (
                            self.opt["world_size"] > 1
                            and "fsdp_expert_grid" in self.opt
                        ):
                            from ..Models.Networks.moe_module.ort_moe.utils import (
                                get_non_expert_parameters_state_dict,
                            )

                            state = {
                                "module": get_non_expert_parameters_state_dict(
                                    self.modules[module_name]
                                ),
                                "lr_scheduler": self.lr_schedulers[
                                    module_name
                                ].state_dict(),
                                "amp_state": amp_state,
                                "optim_steps": self.optim_steps[module_name],
                            }
                        else:
                            state = {
                                "module": self.modules[module_name].state_dict(),
                                "lr_scheduler": self.lr_schedulers[
                                    module_name
                                ].state_dict(),
                                "amp_state": amp_state,
                                "optim_steps": self.optim_steps[module_name],
                            }
                        if self.opt["rank"] == 0:
                            save_to_checkpoint(
                                state,
                                "module_training_states",
                                save_dir,
                                nebula_snapshot,
                                module_name=module_name,
                                is_nebula_enabled=is_nebula_checkpointing,
                            )
                        if (
                            self.opt["world_size"] > 1
                            and "fsdp_expert_grid" in self.opt
                        ):
                            from ..Models.Networks.moe_module.ort_moe.utils import (
                                get_expert_parameters_state_dict,
                            )

                            state = {
                                "module": get_expert_parameters_state_dict(
                                    self.modules[module_name]
                                )
                            }
                            if (
                                self.opt[
                                    "fsdp_expert_grid"
                                ].get_expert_parallel_replica_rank()
                                == 0
                            ):
                                save_to_checkpoint(
                                    state,
                                    f"""
                                    module_training_states_rank_
                                    {self.opt['fsdp_expert_grid'].get_expert_parallel_rank():04d}""",
                                    save_dir,
                                    nebula_snapshot,
                                    module_name=module_name,
                                    is_nebula_enabled=is_nebula_checkpointing,
                                )
                        state = {
                            "optimizer": self.optimizers[module_name].state_dict()
                        }  # in DDP FSDP,  optimizers of all ranks need to be save
                        save_to_checkpoint(
                            state,
                            f"module_fsdp_optimizer_states_rank_{self.opt['rank']}",
                            save_dir,
                            nebula_snapshot,
                            module_name=module_name,
                            is_nebula_enabled=is_nebula_checkpointing,
                        )
                    else:
                        if self.opt["world_size"] > 1 and self.opt["DDP"] == "MAINZ":
                            if self.opt["rank"] == 0:
                                if self.opt["FP16"]:
                                    if self.opt["AMP"] == "APEX":
                                        from apex import amp

                                        amp_state = amp.state_dict()
                                    else:  # self.opt['AMP'] == 'PYTORCH'
                                        amp_state = self.grad_scaler.state_dict()
                                else:
                                    amp_state = None
                                state = {
                                    "amp_state": amp_state,
                                    "optim_steps": self.optim_steps[module_name],
                                }
                                save_to_checkpoint(
                                    state,
                                    "module_training_states",
                                    save_dir,
                                    nebula_snapshot,
                                    module_name=module_name,
                                    is_nebula_enabled=is_nebula_checkpointing,
                                )

                            module_dgrid_state_dict = self.modules[
                                module_name
                            ].group_state_dict_by_dgrid(
                                self.modules[module_name].state_dict()
                            )
                            optimizer_dgrid_state_dict = self.optimizers[
                                module_name
                            ].get_dgrid_state_dict()
                            lr_scheduler_dgrid_state_dict = self.lr_schedulers[
                                module_name
                            ].get_dgrid_state_dict()
                            for (
                                dp_group_name,
                                mp_group_name,
                            ) in module_dgrid_state_dict.keys():
                                if (
                                    self.modules[module_name].get_rank(dp_group_name)
                                    == 0
                                ):
                                    mp_rank = self.modules[module_name].get_rank(
                                        mp_group_name
                                    )
                                    state = {
                                        "module": module_dgrid_state_dict[
                                            (dp_group_name, mp_group_name)
                                        ],
                                        "optimizer": optimizer_dgrid_state_dict[
                                            (dp_group_name, mp_group_name)
                                        ],
                                        "lr_scheduler": lr_scheduler_dgrid_state_dict[
                                            (dp_group_name, mp_group_name)
                                        ],
                                    }
                                    save_to_checkpoint(
                                        state,
                                        f"module_training_states_{mp_group_name}_rank_{mp_rank}",
                                        save_dir,
                                        nebula_snapshot,
                                        module_name=module_name,
                                        is_nebula_enabled=is_nebula_checkpointing,
                                    )
                        else:
                            if self.opt["rank"] == 0:
                                if self.opt["FP16"]:
                                    if self.opt["AMP"] == "APEX":
                                        from apex import amp

                                        amp_state = amp.state_dict()
                                    else:  # self.opt['AMP'] == 'PYTORCH'
                                        amp_state = self.grad_scaler.state_dict()
                                else:
                                    amp_state = None
                                state = {
                                    "module": self.modules[module_name].state_dict(),
                                    "optimizer": self.optimizers[
                                        module_name
                                    ].state_dict(),
                                    "lr_scheduler": self.lr_schedulers[
                                        module_name
                                    ].state_dict(),
                                    "amp_state": amp_state,
                                    "optim_steps": self.optim_steps[module_name],
                                }
                                save_to_checkpoint(
                                    state,
                                    "module_training_states",
                                    save_dir,
                                    nebula_snapshot,
                                    module_name=module_name,
                                    is_nebula_enabled=is_nebula_checkpointing,
                                )

                # save trainer's states
                if self.opt["rank"] == 0:
                    trainer_state = {
                        "num_updates": self.num_updates,
                        "train_loss": {
                            key: obj.getstate() for key, obj in self.train_loss.items()
                        },
                        "train_items_per_batch": {
                            key: obj.getstate()
                            for key, obj in self.train_items_per_batch.items()
                        },
                        "updates_per_epoch": self.updates_per_epoch,
                        "start_epoch_idx": resume_epoch_idx,
                        "start_batch_idx": resume_batch_idx,
                        "eval_best_scores": self.task.eval_best_scores,
                    }
                    save_to_checkpoint(
                        trainer_state,
                        "trainer_states",
                        save_dir,
                        nebula_snapshot,
                        is_nebula_enabled=is_nebula_checkpointing,
                    )

                # save random states on each rank
                random_state = {
                    "random": random.getstate(),
                    "numpy_random": np.random.get_state(),
                    "torch_random": torch.get_rng_state(),
                    "torch_cuda_random": (
                        torch.cuda.get_rng_state(device=self.opt["device"])
                        if self.opt["CUDA"]
                        else None
                    ),
                }
                save_to_checkpoint(
                    random_state,
                    f"random_state_rank_{self.opt['rank']:04d}",
                    save_dir,
                    nebula_snapshot,
                    is_nebula_enabled=is_nebula_checkpointing,
                )

                # save data loader on each rank
                if isinstance(
                    self.train_batch_generator, iterators.CheckpointableIterator
                ) or hasattr(self.train_batch_generator, "getstate"):
                    # save batch generators for all ranks
                    batch_generator_state = self.train_batch_generator.getstate()
                    save_to_checkpoint(
                        batch_generator_state,
                        f"batch_generator_checkpoint_rank_{self.opt['rank']:04d}",
                        save_dir,
                        nebula_snapshot,
                        is_nebula_enabled=is_nebula_checkpointing,
                    )
                else:
                    logger.warning(
                        "Batch generator is not checkpointable. Cannot save to checkpoint."
                    )

                if self.opt["rank"] == 0:
                    # save the latest checkpoint location to json file
                    # add this flag -- 'NEBULA_CHECKPOINTING' for supporting Nebula service loading checkpoint
                    checkpoint_location = {
                        "NEBULA_CHECKPOINTING": is_nebula_checkpointing,
                        "is_checkpoint_and_model_folder_separated": True,
                        "checkpoint_tag": str(tag),
                        "best_scores": filter_jsonable(
                            self.task.eval_best_scores, json_encoder=MainzJSONEncoder
                        ),
                        "current_best_model_path": (
                            os.path.relpath(
                                self.current_best_model_path, start=self.opt["SAVE_DIR"]
                            )
                            if self.current_best_model_path
                            else None
                        ),
                        "checkpoint_path": os.path.relpath(
                            self.save_folder, start=self.opt["SAVE_DIR"]
                        ),
                    }
                    with open(
                        os.path.join(
                            self.opt["SAVE_DIR"],
                            f"{self.opt['BASENAME']}_resume_checkpoint.json",
                        ),
                        "w",
                        encoding="utf-8",
                    ) as f:
                        json.dump(checkpoint_location, f, cls=MainzJSONEncoder)
                logger.warning(f"Finished saving checkpoint to {save_dir}.")
                break
            except OSError as err:
                logger.warning(err)
                logger.warning(
                    "Failed to save checkpoint, waiting for 2 minutes to retry."
                )
                # time.sleep(120)
                # num_retries += 1
                num_retries = 3
                break

        if num_retries >= 3:
            logger.warning(
                f"Failed to save checkpoint for {num_retries} times, continue training."
            )
        else:
            # Apply the logic (may delete folders) of keeping the last N folders when the saving is successful.
            if last_n > 0:
                if self.opt["rank"] == 0:
                    folder_prefix = "checkpoint_step"
                    folders = [
                        os.path.join(self.save_folder, x.name)
                        for x in os.scandir(self.save_folder)
                        if x.is_dir() and x.name.startswith(folder_prefix)
                    ]
                    self.keep_last_N_folders(
                        folders, last_n, folder_prefix=folder_prefix
                    )
                self._dist_barrier()

        return save_dir

    def load_model(self, load_dir):
        """
        Load the model only, without any training states, using the from_pretrained API
        'load_dir' is checkpoint folder path that MainzTrainer.save_pretrained_model() returns
        """
        for module_name in self.module_names:
            module_load_dir = os.path.join(load_dir, module_name)
            if self.opt.get("WEIGHT_SMOOTHING", None) and self.opt[
                "WEIGHT_SMOOTHING"
            ].get("eval_smoothed_weight", False):
                logger.info("=> loading smoothed module")
                smoothed_module_load_dir = os.path.join(
                    module_load_dir, "smoothed_model"
                )
                if os.path.isdir(smoothed_module_load_dir):
                    module_load_dir = smoothed_module_load_dir
                else:
                    logger.warning(
                        f"Could not find smoothed weight for module {module_name} in the checkpoint."
                    )
                    logger.warning("Loading the original weight instead.")
            self.raw_modules[module_name] = self.raw_modules[
                module_name
            ].from_pretrained(module_load_dir)

            self.raw_modules[module_name].to(self.opt["device"])

    def load_checkpoint(self, checkpoint_json_path=None, must_exist=False):
        """
        Load complete training states, including model weights, optimizers, lr_schedulers,
        fp16 loss scaler, random state, batch generator, and updates count

        If 'checkpoint_json_path' is not given, this uses the default path.
        You can pass this path explicitly to allow cross-resuming into a new training folder.

        If 'must_exist' is False, then this will just return if the file does not exist,
        meaning to start over from start.

        Note: if the 'NEBULA_CHECKPOINTING' flag in the *_checkpoint.json is set as true,
        Nebula will be leveraged to load the checkpoint,
        Otherwise still use originally torch.load for loading checkpoint.
        """
        try:
            if checkpoint_json_path is None:
                checkpoint_json_path = os.path.join(
                    self.opt["SAVE_DIR"],
                    f"{self.opt['BASENAME']}_resume_checkpoint.json",
                )
            # find the checkpoint location and the tag from json file
            with open(checkpoint_json_path, encoding="utf-8") as f:
                checkpoint_location = json.load(
                    f
                )  # @TODO: can we not pass the pathname directly?

            is_checkpoint_and_model_folder_separated = checkpoint_location.get(
                "is_checkpoint_and_model_folder_separated", False
            )

            is_nebula_saved_checkpoint = checkpoint_location.get(
                "NEBULA_CHECKPOINTING", False
            )
            is_nebula_sevice_initialized = self.opt.get("NEBULA_CHECKPOINTING", False)
            if is_nebula_saved_checkpoint and not is_nebula_sevice_initialized:
                init_Nebula_service()

            if is_checkpoint_and_model_folder_separated:
                # use new checkpoint folder name which is the same folder as pretrained mode folder.
                checkpoint_path = os.path.join(
                    os.path.dirname(checkpoint_json_path),
                    checkpoint_location["checkpoint_path"],
                    "checkpoint_step" + str(checkpoint_location["checkpoint_tag"]),
                )
                smoothed_checkpoint_path = os.path.join(
                    os.path.dirname(checkpoint_json_path),
                    checkpoint_location["checkpoint_path"],
                    str(checkpoint_location["checkpoint_tag"]),
                )
            else:
                # use old checkpoint folder name which is the same folder as pretrained mode folder.
                checkpoint_path = os.path.join(
                    os.path.dirname(checkpoint_json_path),
                    checkpoint_location["checkpoint_path"],
                    str(checkpoint_location["checkpoint_tag"]),
                )
                smoothed_checkpoint_path = os.path.join(
                    os.path.dirname(checkpoint_json_path),
                    checkpoint_location["checkpoint_path"],
                    str(checkpoint_location["checkpoint_tag"]),
                )

            nebula_snapshot = None
            if is_nebula_saved_checkpoint:
                # Note: Nebula recommend to use the absolute path instead of the relative path
                # for the torch_nebula list_checkpoints(), get_checkpoint(), get_latest_checkpoint()
                absolute_persist_path = os.path.abspath(
                    os.path.dirname(checkpoint_path)
                )
                nebula_tag_name = get_nebula_checkpoint_tag_name(
                    checkpoint_location["checkpoint_tag"]
                )
                logger.warning(
                    f"Nebula loading checkpoint from persist_path: {absolute_persist_path}, with tag:{nebula_tag_name}"
                )

                import torch_nebula

                # Firstly, try to load checkpoint from provided persistent path recorded in the cross-run meta json.
                # Get checkpoint with persist_path and specific tag.
                # Secondly, try to load latest persisted checkpoint maintained by Nebula from provided persistent path
                # Thirdly, if got nothing, try to load checkpoint from cache tier.
                nebula_snapshot = torch_nebula.get_checkpoint(
                    persist_path=absolute_persist_path, tag=nebula_tag_name
                )
                if nebula_snapshot is None:
                    logger.warning(
                        f"""Nebula snapshot is None from persist_path: {absolute_persist_path},
                        with tag:{nebula_tag_name}, try to load latest persisted checkpoint from the run_id folder"""
                    )
                    nebula_snapshot = torch_nebula.get_latest_checkpoint(
                        persist_path=absolute_persist_path
                    )
                if nebula_snapshot is None:
                    logger.warning(
                        f"""Nebula snapshot of the latest checkpoint is None from persist_path:
                        {absolute_persist_path},
                        try to load checkpoint from cache tier ...."""
                    )
                    nebula_snapshot = torch_nebula.get_latest_checkpoint()
                if nebula_snapshot is None or nebula_snapshot.tag is None:
                    raise Exception("No valid Nebula checkpoint was found!")
                logger.warning(
                    f"""Got valid Nebula snapshot.
                    Loading Nebula checkpoint from checkpoint tag {nebula_snapshot.tag}..."""
                )

                # update the 'checkpoint_tag' for the resumed_checkpoint.json
                try:
                    real_checkpoint_tag = str(nebula_snapshot.tag).split(
                        "global_step", 1
                    )[1]
                    if real_checkpoint_tag != checkpoint_location["checkpoint_tag"]:
                        logger.warning(
                            f"""Updated the 'checkpoint_tag' for the resumed_checkpoint.json
                            from {checkpoint_location['checkpoint_tag']} to {real_checkpoint_tag}"""
                        )
                        checkpoint_location["checkpoint_tag"] = real_checkpoint_tag
                except Exception as e:
                    logger.warning(
                        f"""Failed to update the 'checkpoint_tag'
                        for the resumed_checkpoint.json. Error message: {str(e)}."""
                    )
            else:
                if not os.path.isdir(checkpoint_path):
                    raise Exception(
                        f"Checkpoint path does not exist: {checkpoint_path}"
                    )

            # current_best_model_path in the JSON is relative to the JSON file
            self.current_best_model_path = (
                os.path.join(
                    os.path.dirname(checkpoint_json_path),
                    checkpoint_location["current_best_model_path"],
                )
                if checkpoint_location["current_best_model_path"]
                else None
            )
        except Exception as e:
            logger.warning(
                f"Failed to load checkpoint JSON file: {checkpoint_json_path}, Error message: {str(e)}."
            )
            if must_exist:
                raise e
            else:
                logger.warning("Continuing without loading checkpoint")
                return False

        # save a copy of the resumed checkpoint location in the save folder of current run
        if self.opt["rank"] == 0:
            with open(
                os.path.join(self.save_folder, "resumed_checkpoint.json"),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(checkpoint_location, f, cls=MainzJSONEncoder)

        logger.warning(f"Loading checkpoint from {checkpoint_path}...")
        for module_name in self.module_names:
            # load each model's training states
            if self.opt["DEEPSPEED"]:
                self.modules[module_name].load_checkpoint(checkpoint_path, module_name)
                self.optim_steps[module_name] = self.modules[module_name].global_steps
            elif self.opt["DDP"] == "FSDP":
                state = load_from_checkpoint(
                    self.opt["device"],
                    "module_training_states",
                    checkpoint_path,
                    nebula_snapshot,
                    module_name=module_name,
                    is_nebula_enabled=is_nebula_saved_checkpoint,
                )
                if self.opt["world_size"] > 1 and "fsdp_expert_grid" in self.opt:
                    moe_state = load_from_checkpoint(
                        self.opt["device"],
                        f"module_training_states_rank_{self.opt['fsdp_expert_grid'].get_expert_parallel_rank():04d}",
                        checkpoint_path,
                        nebula_snapshot,
                        module_name=module_name,
                        is_nebula_enabled=is_nebula_saved_checkpoint,
                    )
                    state["module"].update(moe_state["module"])
                optimizer_state = load_from_checkpoint(
                    self.opt["device"],
                    f"""module_fsdp_optimizer_states_rank_{self.opt['rank']}""",
                    # optimizer state of each rank is saved respectively
                    checkpoint_path,
                    nebula_snapshot,
                    module_name=module_name,
                    is_nebula_enabled=is_nebula_saved_checkpoint,
                )
                state["optimizer"] = optimizer_state["optimizer"]
                self.modules[module_name].load_state_dict(state["module"])
                # FSDP initialization
                self.modules[module_name] = self._initialize_fsdp(
                    self.modules[module_name]
                )
                self._set_up_optimizers_and_lr_schedulers()
                self._print_number_of_params()
                # Load optimizers, lr_schedulers, sharded_grad_scaler (mixed precision), and optim_steps
                self.optimizers[module_name].load_state_dict(state["optimizer"])
                self.lr_schedulers[module_name].load_state_dict(state["lr_scheduler"])
                if self.opt["FSDP_SETTING"]["MIXED_PRECISION"]:
                    self.sharded_grad_scaler.load_state_dict(state["amp_state"])
                self.optim_steps[module_name] = state["optim_steps"]
            else:
                if self.opt["world_size"] > 1 and self.opt["DDP"] == "MAINZ":
                    state = load_from_checkpoint(
                        self.opt["device"],
                        "module_training_states",
                        checkpoint_path,
                        nebula_snapshot,
                        module_name=module_name,
                        is_nebula_enabled=is_nebula_saved_checkpoint,
                    )
                    module_state_dict = OrderedDict()
                    optimizer_dgrid_state_dict = OrderedDict()
                    lr_scheduler_dgrid_state_dict = OrderedDict()
                    for dp_group_name, mp_group_name in self.modules[
                        module_name
                    ].dgrid_state_dict_keys.keys():
                        mp_rank = self.modules[module_name].get_rank(mp_group_name)
                        mp_group_state = load_from_checkpoint(
                            self.opt["device"],
                            f"module_training_states_{mp_group_name}_rank_{mp_rank}",
                            checkpoint_path,
                            nebula_snapshot,
                            module_name=module_name,
                            is_nebula_enabled=is_nebula_saved_checkpoint,
                        )
                        module_state_dict.update(mp_group_state["module"])
                        optimizer_dgrid_state_dict[(dp_group_name, mp_group_name)] = (
                            mp_group_state["optimizer"]
                        )
                        lr_scheduler_dgrid_state_dict[
                            (dp_group_name, mp_group_name)
                        ] = mp_group_state["lr_scheduler"]
                    self.modules[module_name].load_state_dict(module_state_dict)
                    self.optimizers[module_name].load_dgrid_state_dict(
                        optimizer_dgrid_state_dict
                    )
                    self.lr_schedulers[module_name].load_dgrid_state_dict(
                        lr_scheduler_dgrid_state_dict
                    )
                    if self.opt["FP16"]:
                        if self.opt["AMP"] == "APEX":
                            from apex import amp

                            amp.load_state_dict(state["amp_state"])
                        else:  # self.opt['AMP'] == 'PYTORCH'
                            self.grad_scaler.load_state_dict(state["amp_state"])
                    self.optim_steps[module_name] = state["optim_steps"]

                    # stupid hack needed to correctly resume APEX AMP O2 checkpoint
                    # the optimizer states need to be loaded again right before the first `step()` after resumption.
                    if (
                        self.opt["FP16"]
                        and self.opt["AMP"] == "APEX"
                        and self.opt["FP16_OPT_LEVEL"] == "O2"
                    ):
                        setattr(
                            self,
                            f"apex_amp_o2_optim_state_dict_{module_name}",
                            optimizer_dgrid_state_dict,
                        )
                else:
                    state = load_from_checkpoint(
                        self.opt["device"],
                        "module_training_states",
                        checkpoint_path,
                        nebula_snapshot,
                        module_name=module_name,
                        is_nebula_enabled=is_nebula_saved_checkpoint,
                    )
                    self.modules[module_name].load_state_dict(state["module"])
                    self.optimizers[module_name].load_state_dict(state["optimizer"])
                    self.lr_schedulers[module_name].load_state_dict(
                        state["lr_scheduler"]
                    )
                    if self.opt["FP16"]:
                        if self.opt["AMP"] == "APEX":
                            from apex import amp

                            amp.load_state_dict(state["amp_state"])
                        else:  # self.opt['AMP'] == 'PYTORCH'
                            self.grad_scaler.load_state_dict(state["amp_state"])
                    self.optim_steps[module_name] = state["optim_steps"]

                    # stupid hack needed to correctly resume APEX AMP O2 checkpoint
                    # the optimizer states need to be loaded again right before the first `step()` after resumption.
                    if (
                        self.opt["FP16"]
                        and self.opt["AMP"] == "APEX"
                        and self.opt["FP16_OPT_LEVEL"] == "O2"
                    ):
                        setattr(
                            self,
                            f"apex_amp_o2_optim_state_dict_{module_name}",
                            state["optimizer"],
                        )

        # load trainer's states
        trainer_state = load_from_checkpoint(
            "cpu",
            "trainer_states",
            checkpoint_path,
            nebula_snapshot,
            is_nebula_enabled=is_nebula_saved_checkpoint,
        )
        self.num_updates = trainer_state["num_updates"]
        for key, tmp_state in trainer_state["train_loss"].items():
            self.train_loss[key] = AverageMeter()
            if isinstance(tmp_state, dict):
                self.train_loss[key].setstate(tmp_state)
            else:
                # Older checkpoint with AverageMeter objects directly saved
                self.train_loss[key].setstate(tmp_state.getstate())
        for key, tmp_state in trainer_state["train_items_per_batch"].items():
            self.train_items_per_batch[key] = AverageMeter()
            if isinstance(tmp_state, dict):
                self.train_items_per_batch[key].setstate(tmp_state)
            else:
                # Older checkpoint with AverageMeter objects directly saved
                self.train_items_per_batch[key].setstate(tmp_state.getstate())
        self.start_epoch_idx = trainer_state["start_epoch_idx"]
        self.start_batch_idx = trainer_state["start_batch_idx"]
        if "eval_best_scores" in trainer_state:
            self.task.eval_best_scores = trainer_state["eval_best_scores"]
        else:
            # Older checkpoint with eval_best_scores only saved in checkpoint_location
            self.task.eval_best_scores = checkpoint_location["best_scores"]
        assert self.updates_per_epoch == trainer_state["updates_per_epoch"]
        # assert self.start_batch_idx < self.updates_per_epoch
        if self.start_batch_idx >= self.updates_per_epoch:
            self.start_batch_idx = 0
            self.start_epoch_idx += 1

        # load random states on each rank
        random_state = load_from_checkpoint(
            "cpu",
            f"random_state_rank_{self.opt['rank']:04d}",
            checkpoint_path,
            nebula_snapshot,
            is_nebula_enabled=is_nebula_saved_checkpoint,
        )
        random.setstate(random_state["random"])
        np.random.set_state(random_state["numpy_random"])
        torch.set_rng_state(random_state["torch_random"])
        if self.opt["CUDA"]:
            torch.cuda.set_rng_state(
                random_state["torch_cuda_random"], device=self.opt["device"]
            )

        # load data loader on each rank
        if (not self.opt.get("RESET_DATA_LOADER", False)) and (
            isinstance(self.train_batch_generator, iterators.CheckpointableIterator)
            or (hasattr(self.train_batch_generator, "setstate"))
        ):
            batch_generator_state = load_from_checkpoint(
                "cpu",
                f"batch_generator_checkpoint_rank_{self.opt['rank']:04d}",
                checkpoint_path,
                nebula_snapshot,
                is_nebula_enabled=is_nebula_saved_checkpoint,
            )
            self.train_batch_generator.setstate(batch_generator_state)
        else:
            logger.warning(
                """No need to resume batch generator or
                batch generator is not checkpointable. Didn't load from checkpoint."""
            )

        # load weight smoothing states from saved smoothed models
        # TODO: Need to test this logic to double confirm whether it can work correctly with Nebula,
        # weight smoothing states are saved by save_pretrained_model without Nebula,
        # but they may be loaded with Nebula.
        if self.opt.get("WEIGHT_SMOOTHING", None):
            logger.info(f"=> loading weight smoothing states from {checkpoint_path}")
            _, tmp_raw_modules, _ = (
                self.task.set_up_model()
            )  # set up a temporary model to load smoothed weights
            for module_name in self.module_names:
                smoothed_module_load_dir = os.path.join(
                    smoothed_checkpoint_path, module_name, "smoothed_model"
                )
                if os.path.isdir(smoothed_module_load_dir):
                    tmp_raw_modules[module_name] = tmp_raw_modules[
                        module_name
                    ].from_pretrained(smoothed_module_load_dir)
                    if (
                        self.opt["DDP"] == "FSDP"
                    ):  # weight smoothing params need to be sharded
                        tmp_raw_modules[module_name] = self._initialize_fsdp(
                            tmp_raw_modules[module_name]
                        )
                    self.weight_smoothing_states[module_name].load_shadow_from_model(
                        tmp_raw_modules[module_name], clone_params=False
                    )
                else:
                    del tmp_raw_modules[module_name]
                    logger.warning(
                        f"Could not find smoothed weight for module {module_name} in the checkpoint."
                    )
                    logger.warning(
                        "Reinitialize its weight smoothing state with resumed module weights..."
                    )
                    self.weight_smoothing_states[module_name].load_shadow_from_model(
                        self.raw_modules[module_name], clone_params=True
                    )
            del tmp_raw_modules

        logger.warning(f"Finished loading checkpoint from {checkpoint_path}.")
        self._dist_barrier()
        return True

    def setup_sift(self):
        if self.opt.get("ADD_SIFT", False):
            from ..Models.SIFT.SiftTask import SiftTask

            self.task = SiftTask(self.opt, self.task)
