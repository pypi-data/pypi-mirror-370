# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import faulthandler
import os
import sys
import torch
import logging

from .Trainers.MainzTrainer import MainzTrainer
from .Utils.Arguments import load_opt_command
from .Utils.Timing import Timer

logger = logging.getLogger(__name__)


def main(args=None):
    """
    Main execution point for PyLearn.
    """

    print("MainzTrain started", file=sys.stderr)

    opt, cmdline_args = load_opt_command(args)
    command = cmdline_args.command
    if cmdline_args.user_dir:
        absolute_user_dir = os.path.abspath(cmdline_args.user_dir)
        opt["user_dir"] = absolute_user_dir

    if opt.get("SAVE_TIMER_LOG", False):
        Timer.setEnabled(True)

    # enable attaching from PDB; use 'kill -10 PID' to enter the debugger
    def handle_pdb(sig, frame):
        import pdb

        pdb.Pdb().set_trace(frame)

    # import signal
    # signal.signal(signal.SIGUSR1, handle_pdb)

    trainer = MainzTrainer(opt)

    if opt.get("DEBUG_DUMP_TRACEBACKS_INTERVAL", 0) > 0:
        timeout = opt["DEBUG_DUMP_TRACEBACKS_INTERVAL"]
        traceback_dir = (
            trainer.log_folder
            if trainer.log_folder is not None
            else trainer.save_folder
        )
        traceback_file = os.path.join(traceback_dir, f"tracebacks_{opt['rank']}.txt")
        faulthandler.dump_traceback_later(
            timeout, repeat=True, file=open(traceback_file, "w")
        )

    splits = opt.get("EVALUATION_SPLITS", ["dev", "test"])

    print(f"Running command: {command}")
    with torch.autograd.profiler.profile(
        use_cuda=True, enabled=opt.get("AUTOGRAD_PROFILER", False) and opt["rank"] == 0
    ) as prof:
        if command == "train":
            trainer.train()
        elif command == "evaluate":
            trainer.eval(splits=splits)
        elif command == "train-and-evaluate":
            best_checkpoint_path = trainer.train()
            opt["PYLEARN_MODEL"] = best_checkpoint_path
            trainer.eval(splits=splits)
        else:
            raise ValueError(f"Unknown command: {command}")

    if opt.get("AUTOGRAD_PROFILER", False):
        logger.info(prof.key_averages().table(sort_by="cuda_time_total"))
        logger.info(prof.total_average())

    if opt.get("SAVE_TIMER_LOG", False):
        timer_log_dir = (
            trainer.log_folder
            if trainer.log_folder is not None
            else trainer.save_folder
        )
        timer_log_file = os.path.join(timer_log_dir, f"timer_log_{opt['rank']}.txt")
        Timer.timer_report(timer_log_file)


if __name__ == "__main__":
    main()
