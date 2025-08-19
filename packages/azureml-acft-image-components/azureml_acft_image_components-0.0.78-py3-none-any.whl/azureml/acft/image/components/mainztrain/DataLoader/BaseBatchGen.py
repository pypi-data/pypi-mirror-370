# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Dict, Optional

from . import iterators

logger = logging.getLogger(__name__)


class BaseBatchGen(iterators.CheckpointableIterator):
    """
    This is a base class for batch generators that use infinibatch.

    See `MultiTaskBatchGen` for an example usage.

    The interfaces for classes extending this base class are not restricted (the methods and their
    signatures don't have to be same as the base class). They should have minimum assumption or
    dependency on other components in the system. Task classes can use them accordingly.
    """

    def __init__(
        self,
        opt,
        dataset_label,
        is_evaluation,
        model_config=None,
        tokenizer=None,
        world_size=1,
        rank=0,
        seed=None,
    ):
        """
        Args:
            opt (dict): setting options
            dataset_label (str): 'train', 'dev' or 'test'
            is_evaluation (bool): is the data loader used for evaluation or not
            model_config: config of the model
            tokenizer: tokenizer used to process text
            world_size (int): total number of GPUs
            rank (int): order of current GPU
            seed (int): random seed
        """
        self.opt = opt
        self.dataset_label = dataset_label
        self.model_config = model_config
        self.tokenizer = tokenizer
        self.world_size = world_size
        self.rank = rank
        self.seed = seed
        self.evaluation = is_evaluation

        self._iter: Optional[iterators.CheckpointableIterator] = None

    def _build_iter(self):
        """
        Build infinibatch iterator and assign to self._iter
        """
        raise NotImplementedError()

    @property
    def iterator(self) -> iterators.CheckpointableIterator:
        if self._iter is None:
            # build iterators lazily when it is needed.
            self._build_iter()
        return self._iter

    def __iter__(self):
        if self._iter is None:
            # build iterators lazily when it is needed.
            self._build_iter()
        return self

    def __next__(self):
        assert (
            self._iter is not None
        ), "next() is called before self._build_iter() is called."
        return next(self._iter)

    def getstate(self) -> Dict:
        assert (
            self._iter is not None
        ), "self.getstate() is called before self._build_iter() is called."
        return self._iter.getstate()

    def setstate(self, checkpoint: Optional[Dict]):
        if self._iter is None:
            # build iterators lazily when it is needed.
            self._build_iter()
        self._iter.setstate(checkpoint)

    def close(self):
        if self._iter is not None:
            self._iter.close()
