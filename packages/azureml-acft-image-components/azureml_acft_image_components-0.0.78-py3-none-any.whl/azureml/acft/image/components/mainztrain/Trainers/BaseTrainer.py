# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os

from ..Utils.Arguments import save_opt_to_yaml


class BaseTrainer:
    def __init__(self, opt):
        self.opt = opt

    def get_save_folder(self):
        runid = 1
        while True:
            save_folder = os.path.join(
                self.opt["SAVE_DIR"], f"{self.opt['BASENAME']}_conf~", f"run_{runid}"
            )
            if not os.path.exists(save_folder):
                self.save_folder = save_folder
                self.best_model_path = os.path.join(self.save_folder, "best_model")
                os.makedirs(self.save_folder)
                os.makedirs(self.best_model_path)
                print(f"Saving logs, model and evaluation in {self.save_folder}")
                return
            runid = runid + 1

    # save copy of conf file
    def save_config(self):
        save_opt_to_yaml(self.opt, os.path.join(self.save_folder, "conf_copy.yaml"))
        save_opt_to_yaml(self.opt, os.path.join(self.best_model_path, "conf_copy.yaml"))

    def train(self):
        pass

    def eval(self):
        pass
