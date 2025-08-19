# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
import logging
from random import Random
from typing import Dict, Optional
from collections import OrderedDict

from infinibatch.iterators import NativeCheckpointableIterator  # noqa: F401

from azureml.acft.image.components.mainztrain.DataLoader.BaseBatchGen import BaseBatchGen

logger = logging.getLogger(__name__)


class MultiTaskSampler(BaseBatchGen):
    """
    An Infinibatch iterator that combines multiple Pytorch dataloaders with given smoothing factor.

    Each dataloader is treated as a task.
    """

    def __init__(self, opt, dataloaders, tau=1.0):
        """
        Args:
            opt: MainzTrainerCore config dict
            dataloaders: dict of dataloaders each for a task
            tau: smoothing factor for combining tasks
        """

        super().__init__(
            opt,
            "train",
            False,
            world_size=opt["world_size"],
            rank=opt["rank"],
            seed=opt["SEED"],
        )

        self.dataloaders = OrderedDict(
            sorted(dataloaders.items())
        )  # ensure the task order consistent with task id
        self.tau = tau
        self._build_indices()

        self.seed_rng = Random(self.seed)
        self.setstate()

    @property
    def task_sizes(self):
        """Original sizes (before smoothing) of the dataloaders."""
        if not hasattr(self, "_task_sizes"):
            # ensure the task order consistent with task id
            self._task_sizes = OrderedDict(
                sorted({k: len(v) for k, v in self.dataloaders.items()}.items())
            )
        return self._task_sizes

    def _build_indices(self):
        """Generate smoothed sampling indices of the tasks."""
        total_items = sum(self.task_sizes.values())
        if self.tau == 1:
            task_items = list(self.task_sizes.values())
        else:
            Z = sum(pow(v, self.tau) for v in self.task_sizes.values())
            task_items = [
                round(pow(v, self.tau) / Z * total_items)
                for v in self.task_sizes.values()
            ]
        indices = sum(
            [[i] * max(1, n) for i, n in enumerate(task_items)], []
        )  # repeat items proportionally to their weight
        self.indices = indices[:total_items] + indices[: total_items - len(indices)]

    def _build_iter(self):
        """Build task sampling iterator."""
        self.shuffled_indices = self._reshuffle()
        self._iter = NativeCheckpointableIterator(self.shuffled_indices)

    def set_epoch(self, epoch):
        """Set resumption state, shuffle data, and build task sampling iterator at the beginning of each epoch."""

        # resume checkpoint
        self.set_task_states(self.task_states)
        self.task_states = None  # for later epochs, no need to resume

        # shuffle data in dataloaders based on epoch
        for dataloader in self.dataloaders.values():
            dataloader.sampler.set_epoch(epoch)

        # build task sampling iterator
        self._build_iter()
        logger.debug(f"Sampler state after setting epoch: {self.getstate()}")

    def get_task_states(self):
        return {
            taskname: dataloader.sampler.get_sample_idx()
            for taskname, dataloader in self.dataloaders.items()
        }

    def set_task_states(self, checkpoint):
        for taskname, dataloader in self.dataloaders.items():
            dataloader.sampler.set_sample_idx(
                checkpoint[taskname] if checkpoint is not None else 0
            )

    def getstate(self) -> Dict:
        return {
            "random_state": self._random_state,
            "task_states": self.get_task_states(),
        }

    def setstate(self, checkpoint: Optional[Dict] = None):
        self._random_state = (
            checkpoint["random_state"] if checkpoint is not None else None
        )
        self.task_states = checkpoint["task_states"] if checkpoint is not None else None
        self._random = (
            None  # this will trigger the lazy initialization in self._reshuffle
        )

    def __next__(self):
        self.reshuffled = False
        return next(self._iter)

    def _reshuffle(self):
        if self._random is None:
            # lazy initialization
            self._random = Random(self.seed_rng.randrange(2**32))
            if self._random_state is not None:
                self._random.setstate(self._random_state)

        shuffled_indices = copy.deepcopy(self.indices)

        self._random_state = self._random.getstate()  # save state before shuffle
        self._random.shuffle(shuffled_indices)

        logger.debug(f"Shuffled indices: {shuffled_indices}")
        self.reshuffled = True

        return shuffled_indices


class MultiTaskDataloader(BaseBatchGen):
    def __init__(self, opt, sampler, dataloaders):
        """
        Args:
            opt: MainzTrainerCore config dict
            sampler: a MultiTaskSampler instance
            dataloaders: dict of dataloaders each for a task
        """

        super().__init__(
            opt,
            "train",
            False,
            world_size=opt["world_size"],
            rank=opt["rank"],
            seed=opt["SEED"],
        )

        self.sampler = sampler
        self.dataloaders = OrderedDict(
            sorted(dataloaders.items())
        )  # ensure the task order consistent with task id
        self.setstate()

    def _build_iter(self):
        self.dataiters = None
        self._iter = self.sampler

    @property
    def task_sizes(self):
        # original sizes (before smoothing) of the dataloaders
        if not hasattr(self, "_task_sizes"):
            # ensure the task order consistent with task id
            self._task_sizes = OrderedDict(
                sorted({k: len(v) for k, v in self.dataloaders.items()}.items())
            )
        return self._task_sizes

    def getstate(self) -> Dict:
        return {"sampler_state": self._iter.getstate()}

    def setstate(self, checkpoint: Optional[Dict] = None):
        if self._iter is None:
            # build iterators lazily when it is needed.
            self._build_iter()
        self._iter.setstate(
            checkpoint["sampler_state"] if checkpoint is not None else None
        )

    def _reset_iterators(self, task_idx=None):
        if task_idx is None:
            self.dataiters = [
                iter(dataloader) for dataloader in self.dataloaders.values()
            ]
        else:
            self.dataiters[task_idx] = iter(list(self.dataloaders.values())[task_idx])

    def _advance_iterators(self):
        """Helper to advance all iterators to the checkpoints."""
        task_states = self.sampler.getstate()["task_states"]
        for taskid, (taskname, sample_ckpt) in enumerate(task_states.items()):
            batch_ckpt = sample_ckpt // self.dataloaders[taskname].batch_size
            for _ in range(batch_ckpt):
                next(self._iter)
                self._next_data(taskid)
                logger.debug(
                    f"""Skip task: {taskid},
                    items: {self.sampler._iter.getstate()},
                    task_items: {list(self.sampler.getstate()['task_states'].values())}"""
                )

    def _next_data(self, task_idx):
        """Get next data of a given task. If StopIteration is triggered, reset the dataloader iterator of the task."""
        try:
            return next(self.dataiters[task_idx])
        except StopIteration:
            self._reset_iterators(task_idx)
            return next(self.dataiters[task_idx])

    def __len__(self):
        return sum(v for v in self.task_sizes.values())

    def __next__(self):
        if self.dataiters is None or self.sampler.reshuffled:
            # re-build task data iterators whenever the multitask sampler is reshuffled
            self._reset_iterators()
            logger.debug(f"Dataloader state after reshuffle: {self.getstate()}")

            # move to the checkpoint
            self._advance_iterators()

        task_idx = next(self._iter)
        result = self._next_data(task_idx)

        logger.debug(
            f"""Task: {task_idx}, items: {self.sampler._iter.getstate()},
            task_items: {list(self.sampler.getstate()['task_states'].values())}"""
        )
        return result

    def close(self):
        self._iter.close()
