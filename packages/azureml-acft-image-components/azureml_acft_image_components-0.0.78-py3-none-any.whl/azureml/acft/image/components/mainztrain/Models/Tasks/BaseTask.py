# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Tuple, Dict, List, Union

from ...DataLoader import iterators
from ...Trainers.MainzTrainer import MainzTrainer

logger = logging.getLogger(__name__)


class BaseTask:
    """
    Base class for Task.
    User can extend this class for new tasks to interface with the MainzTrainer.

    Task class implements logic of setting up model, generating batches, training step, and evaluation.
    """

    def __init__(self, opt):
        self._opt = opt
        self.reset_eval_best_scores()

    def set_up_model(
        self,
    ) -> Tuple[List[str], Dict[str, nn.Module], Dict[str, nn.Module]]:
        """
        Set up raw_modules and criteria

        This method initializes raw_modules and criteria as dictionaries containing the
        instances of `BaseModel` and `BaseCriterion`. raw_modules are trainable models, while
        criteria are used for loss calculation and do not contain trainable parameters.

        Returns:
            Tuple: (module_names, raw_modules, criteria)
                module_names: a list of module names in the raw_modules
                raw_modules: a dictionary containing models of class `BaseModel`
                criteria: a dictionary containing criteria of class `BaseCriterion`
        """
        raise NotImplementedError

        return module_names, raw_modules, criteria  # noqa: F821

    def get_batch_generator(
        self, trainer: MainzTrainer, dataset_label: str, is_evaluation: bool
    ) -> Union[DataLoader, iterators.CheckpointableIterator]:
        """
        Get a batch generator from the task for "train", "dev", or "test" set.
        Make sure to use 'world_size' and 'rank' info in opt when preparing batch generator
        for distributed training.

        Args:
            trainer (MainzTrainer): trainer object
            dataset_label (str): "train", "dev", or "test"
            is_evaluation (bool): whether the batch generator is for evaluation or training

        Returns:
            Iterable: an iterable of class `DataLoader` or `iterators.CheckpointableIterator` that yields batches
        """
        raise NotImplementedError

        return batch_generator  # noqa: F821

    def train_step(
        self,
        trainer: MainzTrainer,
        batch,
        grad_acc_batches: List,
        grad_acc_index: int,
        is_distributed: bool,
        is_gradient_accumulation_boundary: bool,
    ) -> Tuple[Dict[str, float], Dict[str, int], Dict]:
        """
        train_step method defines the logics of one training step in the training loop.

        It calls the basic building blocks provided by MainzTrainer:​
        `trainer.forward_pass()​`
        `trainer.backward_pass()​`
        `trainer.step()​`
        Please see MainzTrainer for the definition of these methods.

        trainer.forward_pass() and trainer.backward_pass() can be called multiple times on one or more modules.​
        trainer.step() should be called on every module once and only once.

        Args:
            trainer (MainzTrainer): trainer object
            batch: one batch of training data from the batch generator, after being moved to device
            grad_acc_batches (list): a list of batches (on CPU) in the same gradient accumulation boundaries
            grad_acc_index (int): the index of the current batch in the grad_acc_batches
            is_distributed (bool): True if it is a distributed job, and modules are wrapped in DeepSpeed or DDP
            is_gradient_accumulation_boundary (bool):
            True if current iteration is at the boundary of gradient accumulation
            this and is_distributed can be used together to determine if gradient
            allreduce can be skiped or not.

        Returns:
            Tuple: (loss_info, sample_size_info, extra_info)
                loss_info (dict): a dictionary of loss values to be logged and plotted.
                It can be any losses user want to be aggregated and logged,
                    not limited to the losses used by the backward pass.
                    Losses in mini-batches of same effective batch are averaged.
                sample_size_info (dict): a dictionary of sample sizes to be logged and plotted.
                                        Sizes in mini-batches of same effective batch are summed.
                extra_info (dict): a dictionary of additional info to be logged.
        """
        raise NotImplementedError

        return loss_info, sample_size_info, extra_info  # noqa: F821

    def evaluate_model(
        self, trainer: MainzTrainer, dataset_label: str, save_folder, label=""
    ) -> Tuple[Dict, Dict, bool]:
        """
        Evaluate the module (usually the trainer.raw_modules) on the selected dataset.
        It is called on all ranks. The returned `got_better_score` must be consistant across all the ranks.
        It also maintains and updates self.eval_best_results and self.eval_best_scores.

        Args:
            trainer (MainzTrainer): trainer object
            dataset_label (str): "dev", or "test"
            save_folder: path to save the results
            label: prefix label for saving result files

        Returns:
            Tuple: (results, scores, got_better_score)
                results (dict): contains evaluation results
                scores (dict): contains evaluation scores
                got_better_score (bool): True if better evaluation score is achieved
                    It must be consistant across all the ranks.
        """
        raise NotImplementedError

        return results, scores, got_better_score  # noqa: F821

    def reset_eval_best_scores(self):
        """
        Resets the best evaluation results and scores.
        It clears the best evaluation results and scores stored in the task. As a result,
        next evaluation will always be considered best.
        """
        self.eval_best_results = {}
        self.eval_best_scores = {}

    @property
    def eval_best_scores(self) -> Dict:
        """
        Retrieve the best evaluation scores

        Returns:
            Dict: best evaluation scores dictionary
        """
        return self._eval_best_scores

    @eval_best_scores.setter
    def eval_best_scores(self, value: Dict):
        """
        Set the best evaluation scores
        """
        self._eval_best_scores = value

    @property
    def eval_best_results(self) -> Dict:
        """
        Retrieve the best evaluation results

        Returns:
            Dict: best evaluation results dictionary
        """
        return self._eval_best_results

    @eval_best_results.setter
    def eval_best_results(self, value: Dict):
        """
        Set the best evaluation results
        """
        self._eval_best_results = value
