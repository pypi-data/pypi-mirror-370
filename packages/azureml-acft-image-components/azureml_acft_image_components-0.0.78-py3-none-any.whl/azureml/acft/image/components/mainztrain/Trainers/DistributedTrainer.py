# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import random
import logging
from mpi4py import MPI
import numpy as np
from pprint import pformat
import torch
from torch.utils.tensorboard import SummaryWriter

from ..Utils.Arguments import save_opt_to_yaml, load_config_dict_to_opt
from ..Utils.MPIAdapter import MPIAdapter
from ..Utils import GlobalExceptHook
from ..Utils.CheckpointUtils import init_Nebula_service, SAVE_STRATEGY
from ..Utils.EvalUtils import EVAL_STRATEGY

logger = logging.getLogger(__name__)


class DistributedTrainer(object):
    """
    DistributedTrainer handles distributed training environment set up.

    It also sets up save_folder, logging, and learning rate auto-scaling under the distributed environment.

    Currently it supports tensorboard log for local, Philly, and PhillyTools.
    """

    def __init__(self, opt):
        self.opt = opt
        self.print_tmp_buffer = (
            []
        )  # temp buffer to hold print strings before logging is set up

        self.tb_writers = []

        # parse environment information for distributed training
        adapter = MPIAdapter(
            master_address=self.opt.get("MASTER_IP", None),
            port=self.opt.get("PORT", "55551"),
        )
        self.opt["world_size"] = adapter.world_size
        self.opt["local_size"] = adapter.local_size
        self.opt["rank"] = adapter.rank
        self.opt["local_rank"] = adapter.local_rank

        self._opt_sanity_check()

        # set up device
        if not self.opt["CUDA"]:
            assert (
                self.opt["world_size"] == 1
            ), "multi-GPU training without CUDA is not supported since we use NCCL as communication backend"
            self.opt["device"] = torch.device("cpu")
        else:
            torch.cuda.set_device(self.opt["local_rank"])
            self.opt["device"] = torch.device("cuda", self.opt["local_rank"])

        # for AML: create run object that, among other things, allows us to pretty-print information to AML's web UI
        # outside of AML, any information logged using this mechanism will be printed to stdout
        try:
            from azureml.core.run import Run

            self.aml_run_context = Run.get_context(allow_offline=False)
        except Exception:
            self.aml_run_context = None

        try:
            import mlflow

            self.mlflow = mlflow
        except Exception:
            self.mlflow = None

        self.get_save_folder()
        self.set_up_logging()
        self.log_print_tmp_buffer()

        # Launch Nebula backend service.
        if self.opt.get("NEBULA_CHECKPOINTING", False):
            # the NEBULA_PERSISTENT_TIME_INTERVAL unit is second.
            persistent_interval = self.opt.get("NEBULA_PERSISTENT_TIME_INTERVAL", 60)
            init_Nebula_service(self.save_folder, persistent_interval)

        # if there is SEED in opt, set seeds to make training deterministic
        self.seed = self.opt.get("SEED", None)
        if self.seed:
            self.seed = int(self.seed)
            random.seed(self.seed)
            np.random.seed(self.seed)
            torch.manual_seed(self.seed)
            # ddp: only set seed on GPU associated with this process
            torch.cuda.manual_seed(self.seed)
            if not self.opt.get("DISABLE_DETERMINISTIC", False):
                logger.info(
                    "To increase the reproducibility of the training process, set: 1. deterministic as true, \
                        2. benchmark as false. You can skip them by setting DISABLE_DETERMINISTIC \
                            to True in the training config."
                )
                torch.backends.cudnn.deterministic = True
                torch.backends.cudnn.benchmark = False

        logger.info(f"MainzTrain config options: \n{pformat(self.opt)}")
        self.save_config()

        # log information for distributed training and initialize process group
        adapter.log_info()
        if torch.distributed.is_available() and self.opt["CUDA"]:
            adapter.init_process_group(backend="nccl")
            if (
                not self.opt["DEEPSPEED"]
                and self.opt["DDP"] == "FSDP"
                and "FSDP_EXPERT_PARALLEL_SIZE" in self.opt
            ):
                from ..Models.Networks.moe_module.ort_moe.grids import (
                    DistributionGrid,
                )  # using tools from ort_moe currently

                expert_parallel_size = self.opt.get(
                    "FSDP_EXPERT_PARALLEL_SIZE", self.opt["world_size"]
                )
                assert (
                    self.opt["world_size"] % expert_parallel_size == 0
                ), "world_size % FSDP_EXPERT_PARALLEL_SIZE needs to be zero"
                self.opt["fsdp_expert_grid"] = DistributionGrid(
                    expert_parallel_group_size=expert_parallel_size,
                    expert_parallel_replica_group_size=self.opt["world_size"]
                    // expert_parallel_size,
                )

        if self.opt["CUDA"]:
            logger.info("Using CUDA")
        else:
            logger.info("Using CPU")

        logger.info(f"PyTorch version: {torch.__version__}")

        # ddp: log stats and update learning rate
        logger.info(f"Start learning rate is {self.opt['START_LEARNING_RATE']}")
        logger.info(f"Number of GPUs is {self.opt['world_size']}")
        logger.info(
            f"Gradient accumulation steps = {self.opt['GRADIENT_ACCUMULATE_STEP']}"
        )
        if self.opt.get("NO_AUTO_LR_SCALING", False):
            self.opt["learning_rate"] = self.opt["START_LEARNING_RATE"]
        else:
            logger.info(
                f"Boosting start learning rate from {self.opt['START_LEARNING_RATE']} to "
                f"{self.opt['START_LEARNING_RATE'] * self.opt['world_size'] * self.opt['GRADIENT_ACCUMULATE_STEP']}"
            )
            self.opt["learning_rate"] = (
                self.opt["START_LEARNING_RATE"]
                * self.opt["world_size"]
                * self.opt["GRADIENT_ACCUMULATE_STEP"]
            )

        if self.opt["world_size"] > 1 and not self.opt.get("NO_MPI_ABORT", False):
            GlobalExceptHook.add_hook()

    def print_tmp(self, s):
        """
        Only used before logging is set up.
        Print the string and temporarily save it to a buffer. After logging is set up,
        the strings in the buffer are logged with logger.
        """
        print(s)
        self.print_tmp_buffer.append(s)

    def log_print_tmp_buffer(self):
        """
        Log all the strings in self.print_tmp_buffer, and delete self.print_tmp_buffer.
        """
        for s in self.print_tmp_buffer:
            logger.warning(s)
        del self.print_tmp_buffer

    def set_up_logging(self):
        """
        Set up logging config to log to stream and log files in the save folder.
        """
        # if azureml.core.run.Run import successfully, a stream handler is added to the root logger,
        # making the following call to basicConfig() a noop
        # so we need to remove all existing handlers on the root logger first.
        # in python >= 3.8, `force=True` argument can be added to `logging.basicConfig()` call to achieve same thing
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
            handler.close()
        self.opt["log_file"] = f"log_{self.opt['rank']}.txt"
        if self.opt.get("OFFICIAL", False):
            logging_level = logging.ERROR
        elif self.opt.get("DEBUG", False):
            logging_level = logging.DEBUG
        else:
            logging_level = logging.INFO if self.opt["rank"] == 0 else logging.WARNING

        if self.opt.get("LOGLEVEL_OVERRIDE", None):
            mapping = {
                "CRITICAL": logging.CRITICAL,
                "ERROR": logging.ERROR,
                "WARNING": logging.WARNING,
                "INFO": logging.INFO,
                "DEBUG": logging.DEBUG,
                "NOTSET": logging.NOTSET,
                50: logging.CRITICAL,
                40: logging.ERROR,
                30: logging.WARNING,
                20: logging.INFO,
                10: logging.DEBUG,
                0: logging.NOTSET,
            }
            if self.opt["LOGLEVEL_OVERRIDE"] not in mapping:
                raise ValueError("LogLevel does not matching logging API")

            logging_level = mapping[self.opt["LOGLEVEL_OVERRIDE"]]

        handlers = []
        if self.log_folder is not None:
            handlers.append(
                logging.FileHandler(
                    os.path.join(self.log_folder, self.opt["log_file"]),
                    encoding="utf-8",
                )
            )
        handlers.append(logging.StreamHandler())

        logging.basicConfig(
            handlers=handlers,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%m/%d/%Y %H:%M:%S",
            level=logging_level,
        )

        # Hook-up deepspeed logger with Mainz logger
        if self.opt["DEEPSPEED"]:
            from deepspeed.utils import logger as _ds_logger

            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] "
                "[DeepSpeed:%(filename)s:%(lineno)d:%(funcName)s] %(message)s"
            )
            if self.log_folder is not None:
                ch = logging.FileHandler(
                    os.path.join(self.log_folder, self.opt["log_file"]),
                    encoding="utf-8",
                )
                ch.setLevel(logging_level)
                ch.setFormatter(formatter)
                _ds_logger.addHandler(ch)
            _ds_logger.handlers[0].formatter = formatter
            del _ds_logger

    def get_save_folder(self):
        """
        Acquire a new save folder for this run for all processes.
        The rank-0 process figures out the correct new "runid" that is not used before under same 'SAVE_DIR' and
        'BASENAME', and share it to all processes.
        """
        runid = 1
        if self.opt.get("IS_TEST_PROCESS", False):
            save_folder = log_folder = os.path.normpath(self.opt["TEST_OUTPUT_FOLDER"])
        else:
            if self.opt["rank"] == 0:
                while True:
                    save_folder = os.path.join(
                        self.opt["SAVE_DIR"],
                        f"{self.opt['BASENAME']}_conf~",
                        f"run_{runid}",
                    )
                    try:
                        os.makedirs(save_folder, exist_ok=False)
                        break
                    except FileExistsError:
                        runid = runid + 1
            if self.opt["world_size"] > 1:
                runid = MPI.COMM_WORLD.bcast(runid, root=0)
            save_folder = os.path.join(
                self.opt["SAVE_DIR"], f"{self.opt['BASENAME']}_conf~", f"run_{runid}"
            )
            log_folder = (
                os.path.join(
                    self.opt["LOG_DIR"], f"{self.opt['BASENAME']}_conf~", f"run_{runid}"
                )
                if self.opt["LOG_DIR"] is not None
                else None
            )

        self.save_folder = save_folder
        os.makedirs(self.save_folder, exist_ok=True)
        self.print_tmp(
            f"Saving model, checkpoint, and evaluation in {self.save_folder}"
        )

        self.best_model_path = os.path.join(save_folder, "best_model")
        os.makedirs(self.best_model_path, exist_ok=True)

        self.log_folder = log_folder
        if self.log_folder is not None:
            os.makedirs(self.log_folder, exist_ok=True)
            self.print_tmp(f"Saving logs in {self.log_folder}")
        else:
            self.print_tmp("Not saving logs.")
        self.runid = runid
        return

    def init_tb_writers(self):
        """
        Initialize tensorboard writers for logging and plotting
        """
        if self.opt["rank"] == 0:
            base_and_run = f"{self.opt['BASENAME']}_run_{self.runid}"
            if self.log_folder is not None:
                log_dir = os.path.join(self.log_folder, "tensorboard", "log")
                log_dir = os.path.join(log_dir, base_and_run)
                self.tb_writers.append(SummaryWriter(log_dir=log_dir))
                logger.info(f"Saving tensorboard log to {log_dir}")

            if os.getenv("PHILLY_JOB_DIRECTORY"):
                log_dir = os.path.join(
                    os.environ["PHILLY_JOB_DIRECTORY"], "tensorboard", "log"
                )
                log_dir = os.path.join(log_dir, base_and_run)
                self.tb_writers.append(SummaryWriter(log_dir=log_dir))
                logger.info(f"Saving Philly tensorboard log to {log_dir}")

            if os.getenv("PT_OUTPUT_DIR"):
                log_dir = os.path.join(
                    os.environ["PT_OUTPUT_DIR"], "tensorboard", "log"
                )
                log_dir = os.path.join(log_dir, base_and_run)
                self.tb_writers.append(SummaryWriter(log_dir=log_dir))
                logger.info(f"Saving PhillyTools tensorboard log to {log_dir}")

            # AML
            if os.getenv("AZUREML_TB_PATH"):
                log_dir = os.environ["AZUREML_TB_PATH"]
                log_dir = os.path.join(log_dir, base_and_run)
                self.tb_writers.append(SummaryWriter(log_dir=log_dir))
                logger.info(f"Saving AML tensorboard log to {log_dir}")

            if os.getenv("SINGULARITY_JOB"):
                log_dir = os.environ["TENSORBOARD_LOG_DIR"]
                log_dir = os.path.join(log_dir, base_and_run)
                self.tb_writers.append(SummaryWriter(log_dir=log_dir))
                logger.info(f"Saving SINGULARITY tensorboard log to {log_dir}")

    def update_tb_writers(self, metric_name, value, global_step=None, **kwargs):
        """
        Log new value to the tensorboard writers. If an AML run context is available, also log value to it.
        'value' can be a scalar value, or a tuple of (<type>, <value>). \
            <type> should be one of the types supported by TensorBoard.
        Only scalar value is supported to log to AML now.
        """

        def update_tb_writer(tb_writer, metric_name, value, global_step=None, **kwargs):
            if tb_writer:
                if value[0] == "scalar":
                    tb_writer.add_scalar(
                        metric_name, value[1], global_step=global_step, **kwargs
                    )
                elif value[0] == "scalars":
                    tb_writer.add_scalars(
                        metric_name, value[1], global_step=global_step, **kwargs
                    )
                elif value[0] == "histogram":
                    tb_writer.add_histogram(
                        metric_name, value[1], global_step=global_step, **kwargs
                    )
                elif value[0] == "image":
                    tb_writer.add_image(
                        metric_name, value[1], global_step=global_step, **kwargs
                    )
                elif value[0] == "images":
                    tb_writer.add_images(
                        metric_name, value[1], global_step=global_step, **kwargs
                    )
                elif value[0] == "figure":
                    tb_writer.add_figure(
                        metric_name, value[1], global_step=global_step, **kwargs
                    )
                elif value[0] == "video":
                    tb_writer.add_video(
                        metric_name, value[1], global_step=global_step, **kwargs
                    )
                elif value[0] == "audio":
                    tb_writer.add_audio(
                        metric_name, value[1], global_step=global_step, **kwargs
                    )
                elif value[0] == "text":
                    tb_writer.add_text(
                        metric_name, value[1], global_step=global_step, **kwargs
                    )
                else:
                    logger.warning(
                        f"{value[0]} is not a supported type to be written to TensorBoard. Value skipped."
                    )
                tb_writer.flush()

        if self.opt["rank"] == 0:
            if not isinstance(value, tuple):
                value = ("scalar", value)
            assert (
                len(value) == 2
            ), "The 'value' argument should be a tuple of 2 elements, e.g. ('scalar', 1.0)"

            for tb_writer in self.tb_writers:
                update_tb_writer(
                    tb_writer, metric_name, value, global_step=global_step, **kwargs
                )

            aml_do_not_log = self.opt.get("AML_DO_NOT_LOG", [])
            if isinstance(aml_do_not_log, str):
                import re

                ignore = re.match(aml_do_not_log, metric_name)
            else:
                ignore = metric_name in aml_do_not_log
            if self.aml_run_context is not None and not ignore:
                if value[0] == "scalar":
                    if global_step is None:
                        self.aml_run_context.log(metric_name, value[1])
                    else:
                        self.aml_run_context.log_row(
                            metric_name, step=global_step, value=value[1]
                        )
                else:
                    logger.warning(
                        f"{value[0]} is not a supported type to be written to AML. Value skipped."
                    )

            if self.mlflow is not None and not ignore:
                if value[0] == "scalar":
                    try:
                        if global_step is None:
                            self.mlflow.log_metric(metric_name, value[1])
                        else:
                            self.mlflow.log_metric(
                                metric_name, value[1], step=global_step
                            )
                    except Exception:
                        logger.warning("MLFlow error encountered")
                else:
                    logger.warning(
                        f"{value[0]} is not a supported type to be written to AML. Value skipped."
                    )

    def close_tb_writers(self):
        """
        Shut down tensorboard writers
        """
        if self.opt["rank"] == 0:
            for tb_writer in self.tb_writers:
                tb_writer.close()

    def save_config(self):
        """
        Save a copy of the configs (self.opt) to the run save folder
        """
        if self.opt["rank"] == 0:
            save_opt_to_yaml(self.opt, os.path.join(self.save_folder, "conf_copy.yaml"))
            save_opt_to_yaml(
                self.opt, os.path.join(self.best_model_path, "conf_copy.yaml")
            )
            if self.log_folder is not None:
                save_opt_to_yaml(
                    self.opt, os.path.join(self.log_folder, "conf_copy.yaml")
                )

    def _opt_backward_compatible(self):
        """
        Patch old configs for backward compatibility
        If some of the configs are in older formats, fix them to the new formats
        """
        if "SAVE_PER_OPTIM_STEPS" not in self.opt and "SAVE_PER_UPDATE_NUM" in self.opt:
            self.print_tmp(
                "Please use 'SAVE_PER_OPTIM_STEPS' instead of 'SAVE_PER_UPDATE_NUM' to set the saving frequency."
            )
            if int(self.opt["SAVE_PER_UPDATE_NUM"]) > 0:
                assert (
                    int(self.opt["SAVE_PER_UPDATE_NUM"])
                    % int(self.opt.get("GRADIENT_ACCUMULATE_STEP", 1))
                    == 0
                )
                self.opt["SAVE_PER_OPTIM_STEPS"] = int(
                    self.opt["SAVE_PER_UPDATE_NUM"]
                ) // int(self.opt.get("GRADIENT_ACCUMULATE_STEP", 1))
            else:
                self.opt["SAVE_PER_OPTIM_STEPS"] = int(self.opt["SAVE_PER_UPDATE_NUM"])

        if self.opt.get("SAVE_PER_OPTIM_STEPS", None) is not None:
            for file_type in ["CHECKPOINT", "MODEL"]:
                if (
                    self.opt.get("SAVE_STRATEGY", {})
                    .get(file_type, {})
                    .get("SAVE_PER_OPTIM_STEPS", None)
                    is None
                ):
                    self.print_tmp(
                        f"Please use 'SAVE_STRATEGY.{file_type}.SAVE_PER_OPTIM_STEPS' instead of "
                        f"'SAVE_PER_OPTIM_STEPS' to set the {file_type} saving frequency."
                    )
                    load_config_dict_to_opt(
                        self.opt,
                        {
                            f"SAVE_STRATEGY.{file_type}.SAVE_PER_OPTIM_STEPS": int(
                                self.opt["SAVE_PER_OPTIM_STEPS"]
                            )
                        },
                    )

        if "EVAL_PER_OPTIM_STEPS" not in self.opt and "EVAL_PER_UPDATE_NUM" in self.opt:
            self.print_tmp(
                "Please use 'EVAL_PER_OPTIM_STEPS' instead of 'EVAL_PER_UPDATE_NUM' to set the evaluation frequency."
            )
            if int(self.opt["EVAL_PER_UPDATE_NUM"]) > 0:
                assert (
                    int(self.opt["EVAL_PER_UPDATE_NUM"])
                    % int(self.opt.get("GRADIENT_ACCUMULATE_STEP", 1))
                    == 0
                )
                self.opt["EVAL_PER_OPTIM_STEPS"] = int(
                    self.opt["EVAL_PER_UPDATE_NUM"]
                ) // int(self.opt.get("GRADIENT_ACCUMULATE_STEP", 1))
            else:
                self.opt["EVAL_PER_OPTIM_STEPS"] = int(self.opt["EVAL_PER_UPDATE_NUM"])

        if self.opt.get("EVAL_PER_OPTIM_STEPS", None) is not None:
            if (
                self.opt.get("EVAL_STRATEGY", {}).get("EVAL_PER_OPTIM_STEPS", None)
                is None
            ):
                self.print_tmp(
                    "Please use 'EVAL_STRATEGY.EVAL_PER_OPTIM_STEPS' instead of 'EVAL_PER_OPTIM_STEPS' \
                        to set the evaluation frequency."
                )
                load_config_dict_to_opt(
                    self.opt,
                    {
                        "EVAL_STRATEGY.EVAL_PER_OPTIM_STEPS": int(
                            self.opt["EVAL_PER_OPTIM_STEPS"]
                        )
                    },
                )

        if "OPTIM_STEPS_PER_EPOCH" not in self.opt and "UPDATES_PER_EPOCH" in self.opt:
            self.print_tmp(
                "Please use 'OPTIM_STEPS_PER_EPOCH' instead of 'UPDATES_PER_EPOCH' to set the length of an epoch."
            )
            assert (
                int(self.opt["UPDATES_PER_EPOCH"])
                % int(self.opt.get("GRADIENT_ACCUMULATE_STEP", 1))
                == 0
            )
            self.opt["OPTIM_STEPS_PER_EPOCH"] = int(
                self.opt["UPDATES_PER_EPOCH"]
            ) // int(self.opt.get("GRADIENT_ACCUMULATE_STEP", 1))

        if "AMP" not in self.opt and "USE_APEX_AMP" in self.opt:
            self.print_tmp("Please use 'AMP' to choose the AMP package to use.")
            if self.opt["USE_APEX_AMP"]:
                self.opt["AMP"] = "APEX"
            else:
                self.opt["AMP"] = "PYTORCH"

        if "DDP" not in self.opt and any(key in self.opt for key in ["USE_APEX_DDP"]):
            self.print_tmp("Please use 'DDP' to choose the DDP package to use.")
            if self.opt.get("USE_APEX_DDP", False):
                self.opt["DDP"] = "APEX"
            else:
                self.opt["DDP"] = "PYTORCH"

    def _opt_save_strategy_sanity_check(self, key):
        assert key in [
            "CHECKPOINT",
            "MODEL",
        ], f"Unknown file type for saving strategy: {key}."

        if (
            self.opt.get("SAVE_STRATEGY", {})
            .get(key, {})
            .get("SAVE_PER_OPTIM_STEPS", None)
            is None
        ):
            load_config_dict_to_opt(
                self.opt, {f"SAVE_STRATEGY.{key}.SAVE_PER_OPTIM_STEPS": 0}
            )  # backward compatible

        strategy = self.opt["SAVE_STRATEGY"][key]

        # if NAME is not specified, infer it from SAVE_PER_OPTIM_STEPS
        if strategy.get("NAME", None) is None:
            if strategy["SAVE_PER_OPTIM_STEPS"] >= SAVE_STRATEGY.PER_OPTIM_STEPS:
                strategy["NAME"] = "PER_OPTIM_STEPS"
            else:
                for e, v in SAVE_STRATEGY.__members__.items():
                    if strategy["SAVE_PER_OPTIM_STEPS"] == v.value:
                        strategy["NAME"] = e
                        break
                else:
                    raise ValueError(
                        f"Invalid SAVE_PER_OPTIM_STEPS {strategy['SAVE_PER_OPTIM_STEPS']}. "
                        f"Expected range: [{min(list(SAVE_STRATEGY.__members__.values()))}:]."
                    )

        strategy_name = strategy["NAME"]
        assert (
            strategy_name in SAVE_STRATEGY.__members__
        ), f"Unknown saving strategy '{strategy_name}'. Choose from {list(SAVE_STRATEGY.__members__.keys())}."

        # override SAVE_PER_OPTIM_STEPS if NAME is known
        if strategy_name == "PER_OPTIM_STEPS":
            assert strategy["SAVE_PER_OPTIM_STEPS"] >= SAVE_STRATEGY.PER_OPTIM_STEPS, (
                f"Saving strategy '{strategy_name}' requires positive SAVE_PER_OPTIM_STEPS. "
                f"Got {strategy['SAVE_PER_OPTIM_STEPS']}."
            )

            strategy["KEEP_LAST_N"] = int(
                strategy.get("KEEP_LAST_N", -1)
            )  # -1 means all
        else:
            for e, v in SAVE_STRATEGY.__members__.items():
                if strategy_name == e:
                    strategy["SAVE_PER_OPTIM_STEPS"] = v.value
                    break

    def _opt_eval_strategy_sanity_check(self):
        if self.opt.get("EVAL_STRATEGY", {}).get("EVAL_PER_OPTIM_STEPS", None) is None:
            load_config_dict_to_opt(
                self.opt, {"EVAL_STRATEGY.EVAL_PER_OPTIM_STEPS": 0}
            )  # backward compatible

        strategy = self.opt["EVAL_STRATEGY"]

        # if NAME is not specified, infer it from EVAL_PER_OPTIM_STEPS
        if strategy.get("NAME", None) is None:
            if strategy["EVAL_PER_OPTIM_STEPS"] >= EVAL_STRATEGY.PER_OPTIM_STEPS:
                strategy["NAME"] = "PER_OPTIM_STEPS"
            else:
                for e, v in EVAL_STRATEGY.__members__.items():
                    if strategy["EVAL_PER_OPTIM_STEPS"] == v.value:
                        strategy["NAME"] = e
                        break
                else:
                    raise ValueError(
                        f"Invalid EVAL_PER_OPTIM_STEPS {strategy['EVAL_PER_OPTIM_STEPS']}. "
                        f"Expected range: [{min(list(EVAL_STRATEGY.__members__.values()))}:]."
                    )

        strategy_name = strategy["NAME"]
        assert (
            strategy_name in EVAL_STRATEGY.__members__
        ), f"Unknown evaluation strategy '{strategy_name}'. Choose from {list(EVAL_STRATEGY.__members__.keys())}."

        # override EVAL_PER_OPTIM_STEPS if NAME is known
        if strategy_name == "PER_OPTIM_STEPS":
            assert strategy["EVAL_PER_OPTIM_STEPS"] >= EVAL_STRATEGY.PER_OPTIM_STEPS, (
                f"Evaluation strategy '{strategy_name}' requires positive EVAL_PER_OPTIM_STEPS. "
                f"Got {strategy['EVAL_PER_OPTIM_STEPS']}."
            )
        else:
            for e, v in EVAL_STRATEGY.__members__.items():
                if strategy_name == e:
                    strategy["EVAL_PER_OPTIM_STEPS"] = v.value
                    break

    def _opt_sanity_check(self):
        """
        Sanity check for the configs (self.opt)
        """
        self._opt_backward_compatible()
        # Fill in the default values for required keywords
        self.opt["CUDA"] = self.opt.get("CUDA", True) and torch.cuda.is_available()
        self.opt["USE_HIT"] = self.opt.get("USE_HIT", False)
        self.opt["DEEPSPEED"] = self.opt.get("DEEPSPEED", True)
        self.opt["FP16"] = self.opt.get("FP16", False) and self.opt["CUDA"]
        self.opt["BF16"] = self.opt.get("BF16", False) and self.opt["CUDA"]
        self.opt["FP16_OPT_LEVEL"] = self.opt.get("FP16_OPT_LEVEL", "O1")
        self.opt["GRADIENT_ACCUMULATE_STEP"] = int(
            self.opt.get("GRADIENT_ACCUMULATE_STEP", 1)
        )

        self._opt_save_strategy_sanity_check("CHECKPOINT")
        self._opt_save_strategy_sanity_check("MODEL")
        self._opt_eval_strategy_sanity_check()

        assert not (
            (
                self.opt.get("NEBULA_CHECKPOINTING", False)
                and (
                    self.opt.get("COPY_BEST_CHECKPOINT", True)
                    or self.opt["SAVE_STRATEGY"]["CHECKPOINT"]["SAVE_PER_OPTIM_STEPS"]
                    < EVAL_STRATEGY.PER_OPTIM_STEPS
                    or self.opt["SAVE_STRATEGY"]["CHECKPOINT"]["KEEP_LAST_N"] > 0
                )
            )
        ), (
            "Due to synchronously persisting checkpoint, NEBULA_CHECKPOINTING can only be enabled when: "
            " 1. COPY_BEST_CHECKPOINT(default true) is false"
            " 2. SAVE_PER_OPTIM_STEPS > 0. or "
            " 3. SAVE_STRATEGY.CHECKPOINT.NAME is 'PER_OPTIM_STEPS'"
            " and SAVE_STRATEGY.CHECKPOINT.SAVE_PER_OPTIM_STEPS > 0,"
            " and SAVE_STRATEGY.CHECKPOINT.KEEP_LAST_N was not set "
        )

        if self.opt.get("NEBULA_CHECKPOINTING", False):
            try:
                import torch_nebula  # noqa: F401
            except ImportError:
                self.print_tmp("Nebula checkpointing is disabled.")
                self.print_tmp(
                    "Please install torch_nebula to use Nebula checkpointing."
                )
                self.opt["NEBULA_CHECKPOINTING"] = False

        if self.opt["USE_HIT"]:
            try:
                import hit  # noqa: F401
            except ImportError:
                self.print_tmp("HiT is disabled.")
                self.print_tmp(
                    "Please install HiT from https://speedme.visualstudio.com/SpeeDME/_git/HiT to use HiT training."
                )
                self.opt["USE_HIT"] = False
        if self.opt["DEEPSPEED"]:
            try:
                import deepspeed  # noqa: F401
            except ImportError:
                self.print_tmp("DeepSpeed is disabled.")
                self.print_tmp(
                    "Please install DeepSpeed from https://github.com/microsoft/DeepSpeed to use DeepSpeed training."
                )
                self.opt["DEEPSPEED"] = False
        if self.opt["DEEPSPEED"] and not self.opt["CUDA"]:
            self.opt["DEEPSPEED"] = False
            self.print_tmp("DeepSpeed is turned OFF because CUDA is not found.")
        if not self.opt["DEEPSPEED"]:
            self.opt["AMP"] = self.opt.get("AMP", "APEX")  # default to use APEX AMP.
            self.opt["DDP"] = self.opt.get(
                "DDP", "PYTORCH"
            )  # default to use PYTORCH DDP.
            if self.opt["FP16"]:
                assert self.opt["AMP"] in ["APEX", "PYTORCH"]
                if self.opt["AMP"] == "PYTORCH":
                    try:
                        from torch.cuda.amp import autocast  # noqa: F401
                        from torch.cuda.amp import GradScaler  # noqa: F401

                        self.print_tmp("Using torch.cuda.amp for FP16.")
                    except ImportError:
                        self.print_tmp(
                            "PyTorch version 1.6.0+ is needed to use torch.cuda.amp. Fallback to use apex.amp."
                        )
                        self.opt["AMP"] = "APEX"
                if self.opt["AMP"] == "APEX":
                    try:
                        from apex import amp  # noqa: F401

                        self.print_tmp("Using apex.amp for FP16.")
                    except ImportError:
                        self.print_tmp(
                            "Please install apex from https://www.github.com/nvidia/apex to use fp16 training."
                        )
                        self.print_tmp("fp16 is disabled.")
                        self.opt["FP16"] = False
            assert self.opt["DDP"] in ["APEX", "PYTORCH", "MAINZ", "FSDP"]
            if self.opt["DDP"] == "APEX":
                try:
                    # from apex.parallel import (
                    #     DistributedDataParallel as DDP,
                    # )  # noqa: F401

                    self.print_tmp("Using APEX DDP.")
                except ImportError:
                    self.print_tmp("Cannot use apex DDP, using Pytorch DDP instead.")
                    self.print_tmp(
                        "Please install apex from https://www.github.com/nvidia/apex to use apex DDP."
                    )
                    self.opt["DDP"] = "PYTORCH"
            if self.opt["DDP"] == "FSDP":
                try:
                    if "FSDP_EXPERT_PARALLEL_SIZE" in self.opt:
                        # from ..Models.Networks.moe_module import (
                        #     ort_moe,
                        # )  # noqa: F401,F811

                        """
                        ORT MoE is currently used by FSDP
                        """
                    self.print_tmp("Using FSDP DDP.")
                except ImportError:
                    self.print_tmp("Cannot use FSDP, ORT moe_module is not available.")
                    raise
                assert not self.opt["USE_HIT"], "FSDP DDP is not compatible with HiT."
            if self.opt["DDP"] == "PYTORCH":
                self.print_tmp("Using Pytorch DDP.")
            if self.opt["DDP"] == "MAINZ":
                self.print_tmp("Using MAINZ DDP.")
                assert not self.opt["USE_HIT"], "MAINZ DDP is not compatible with HiT."
        else:
            if "AMP" in self.opt or "DDP" in self.opt:
                self.print_tmp(
                    "***************************WARNING***************************"
                )
                self.print_tmp(
                    "'AMP' and 'DDP' settings are ignored when DEEPSPEED is True."
                )
                self.print_tmp(
                    "*************************************************************"
                )

        # Fill the DATA_DIR and BASENAME if not provided by user
        # DATA_DIR is the directory containing the config file
        # BASENAME is the basename of the config file
        if not ("DATA_DIR" in self.opt and "BASENAME" in self.opt):
            assert (
                len(self.opt["conf_files"]) == 1
            ), "DATA_DIR and BASENAME can only be automatically filled if there is only one config file."
            conf_file = self.opt["conf_files"][0]
            if "DATA_DIR" not in self.opt:
                self.opt["DATA_DIR"] = os.path.dirname(conf_file)
                self.print_tmp(
                    f"Using config file to locate the DATA_DIR as {self.opt['DATA_DIR']}"
                )
            if "BASENAME" not in self.opt:
                self.opt["BASENAME"] = os.path.basename(conf_file)
                self.print_tmp(
                    f"Using config file to name the BASENAME as {self.opt['BASENAME']}"
                )

        if "SAVE_DIR" not in self.opt:
            self.opt["SAVE_DIR"] = self.opt["DATA_DIR"]
        if "LOG_DIR" not in self.opt:
            self.opt["LOG_DIR"] = self.opt["SAVE_DIR"]
        self.opt["DATA_DIR"] = os.path.normpath(self.opt["DATA_DIR"])
        self.opt["SAVE_DIR"] = os.path.normpath(self.opt["SAVE_DIR"])
        if self.opt["LOG_DIR"] is not None:
            self.opt["LOG_DIR"] = os.path.normpath(self.opt["LOG_DIR"])
        self.print_tmp(f"Setting DATA_DIR as {self.opt['DATA_DIR']}")
        self.print_tmp(f"Setting SAVE_DIR as {self.opt['SAVE_DIR']}")
        self.print_tmp(
            "When using premium blob, SAVE_DIR must point to a folder that is being periodically cleaned up."
        )
        self.print_tmp(f"Setting LOG_DIR as {self.opt['LOG_DIR']}")
        self.print_tmp("Please do NOT use a blobfuse mounted folder for LOG_DIR.")
