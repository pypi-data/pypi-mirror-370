# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import math
import copy
import gzip
import json
import logging
import numpy as np
from numpy.random import RandomState
import os
from random import Random
import time
from typing import Any, Callable

from .Utils.MaskingUtils import RandomWordMasking, RandomTokenMasking
from .Utils.NoisingUtils import DaeNoising
from . import iterators
from .BaseBatchGen import BaseBatchGen

from .NoisingScheduler import NoisingScheduler

logger = logging.getLogger(__name__)


def SamplingNumpyRandomMapIterator(
    source_iterator: iterators.CheckpointableIterator,
    transform: Callable[[Random, RandomState, Any], Any],
    seed: int = 0,
    scheduling_settings={},
):
    """
    An iterator that calls a transform function on each item,
    while also passing a checkpointed
    random generator.

    Args:
        source_iterator: checkpointable iterator to recur over
        transform: user-supplied function with signature
        transform(random, np_random, item) -> result_item
        seed: random seed
    """
    _random = Random(seed)
    _np_random = RandomState(seed)
    _scheduler = NoisingScheduler(scheduling_settings)
    logger.info(f"noising_scheduler initial state: " f"{_scheduler.getstate()}")

    def _step_function(state, item):
        _random.setstate(state["_random"])
        _np_random.set_state(state["_np_random"])
        _scheduler.setstate(state["scheduler_state"])
        _scheduler.step()
        if state["idx"] % 10000 == 0:
            logger.info(
                f"Scheduler state ({state['idx']}): " f"{_scheduler.getstate()}"
            )
        output = transform(_random, _np_random, _scheduler, item)
        new_state = {
            "_random": _random.getstate(),
            "_np_random": _np_random.get_state(),
            "scheduler_state": _scheduler.getstate(),
            "idx": state["idx"] + 1,
        }
        return new_state, output

    initial_state = {
        "_random": _random.getstate(),
        "_np_random": _np_random.get_state(),
        "scheduler_state": _scheduler.getstate(),
        "idx": 0,
    }

    return iterators.RecurrentIterator(
        source_iterator, _step_function, initial_state=initial_state
    )


class MultiTaskBatchGen(BaseBatchGen):
    """
    This batch generator implements model-agnostic processing steps of multi-task corpora.
    It requires a .json file at `TRAIN_FILE`, `DEV_FILE`, or `TEST_FILE` that contains description of all corpora.

    Implemented tasks are:
    mlm, dae, mt, noised_mt, mt_dae, xmlm, contrastive

    Config settings in `opt` used by this class are:

    - TRAINING_TASKS: optional, a list of tasks used in training, e.g. ["mlm", "dae", "mt"]. If provided, all tasks \
        in this list must exist in the corpora for training.
    - TRAINING_LANGS: optional, a list of languages used in training, e.g. ["en", "es"]. If provided, all languages \
        in this list must exist in the corpora for training.
    - TRAINING_LANG_PAIRS: optional, a list of language pairs for parallel corpora used in training, e.g. ["en-es", \
        "es-en"]. If provided, all language pairs in this list must exist in the corpora for training.
    - EVAL_TASKS: optional, a list of tasks used in evaluation, e.g. ["mlm", "dae", "mt"]. If not provided, \
        fall back to use TRAINING_TASKS.
    - EVAL_LANGS: optional, a list of languages used in evaluation, e.g. ["en", "es"]. If not provided, \
        fall back to use TRAINING_LANGS.
    - EVAL_LANG_PAIRS: optional, a list of language pairs for parallel corpora used in evaluation, \
        e.g. ["en-es", "es-en"]. If not provided, fall back to use EVAL_LANG_PAIRS.
    - MAX_TOKENS_BATCH: required, max tokens in a batch for training. It is used to calculate training batch size.
    - EVAL_MAX_TOKENS_BATCH: required, max tokens in a batch for evaluation. \
        It is used to calculate evaluation batch size.
    - IGNORE_GROUP_WEIGHT: default False, if True, each group always contains one batch.
    - PREFETCH_BUFFER: default 100, if > 0, add a prefetch iterator with the buffer size for each group.
    - EVAL_PREFETCH_BUFFER: default 100, if > 0, add a prefetch iterator with the buffer size \
        for the evaluation batch iterator.
    - MAX_LEN: max sequence length.
    - MAX_GEN_LENGTH: max length for generation in evaluation.
    - BEAM_WIDTH: beam width for generation in evaluation.
    - CONCAT_SENTENCE: default 0.0, the probablity of concatenating to MAX_LEN in training.
    - DOC_SHUFFLE_BUF_SIZE: block size for shuffling docs in a corpus.
    - SAMPLE_SHUFFLE_BUFFER_SIZE: block size for shuffling samples in a corpus.
    - BATCH_READ_AHEAD: read ahead size for batch iterator of a corpus.
    - WHOLE_WORD_MASKING: default True, enable whole word masking for MLM tasks.
    - MLM_MASK_RATIO: percentage of tokens being masked in MLM tasks.
    - MLM_MASK_PROB: probability of using the mask token to mask tokens.
    - MLM_RAND_TOKEN_PROB: probability of using a random token to mask tokens.
    - DAE_DROPOUT_PROB: probability of token dropout for DAE tasks.
    - DAE_BLANK_PROB: probability of token blanking for DAE tasks.
    - DAE_MAX_SHUFFLE_DISTANCE: token shuffling mas distance.
    - DAE_TEXT_INFILL_RATIO, DAE_TEXT_INFILL_LAMBDA: span masking ratio and length lambda for DAE tasks.
    - FS_RETRIES: default 3, max number of retries for file io failures. Wait time between retries is 30 seconds.
    - NOISE_SCHEDULING_SETTINGS: is a dict with options to schedule over time values used by \
        other tasks (mlm, dae, etc). On this dictionary, each key corresponds to the parameter \
            to schedule (DAE_DROPOUT_PROB, MLM_MASK_RATIO, etc), and the value must be a dictionary \
                with an entry "SCHEDULING_TYPE" which specifies the type of scheduling, only "linear" \
                    supported as of now, which requires "MIN", "MAX" and "WARMUP_EXAMPLES", \
                        see the `NoisingScheduler` documentation for more details.
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
        **kwargs,
    ):
        super().__init__(
            opt,
            dataset_label,
            is_evaluation,
            model_config,
            tokenizer,
            world_size,
            rank,
            seed,
        )
        self.seed_rng = Random(self.seed)

    def _build_iter(self):
        # set self.corpus_root_dir as the dir containing the .json dataset file
        # open .json dataset file
        # filter the corpus list
        # create a single-task corpus iterator for each corpus in the list
        # MultiplexIterator and ZipIterator to combine all corpus iterators
        dataset_file = os.path.join(
            self.opt["DATA_DIR"], self.opt[f"{self.dataset_label.upper()}_FILE"]
        )
        max_retries = self.opt.get("FS_RETRIES", 3)
        num_retries = 0
        while True:
            try:
                with open(dataset_file, encoding="utf-8") as f:
                    corpora = json.load(f)
                break
            except Exception as err:
                logger.warning(err)
                logger.warning(
                    f"Failed to load dataset JSON file {dataset_file}, waiting for 30 seconds to retry."
                )
                num_retries += 1
                if num_retries > max_retries:
                    error_message = f"Failed to load dataset JSON file {dataset_file} after {max_retries} retries."
                    logger.error(error_message)
                    raise Exception(error_message)
                time.sleep(30)

        self.corpus_root_dir = os.path.dirname(dataset_file)
        self.chunk_cache = {}  # Cache the list of chunk files under a scanned dir

        if not self.evaluation:
            self.selected_tasks = self.opt.get("TRAINING_TASKS", None)
            self.selected_languages = self.opt.get("TRAINING_LANGS", None)
            self.selected_language_pairs = self.opt.get("TRAINING_LANG_PAIRS", None)
        else:
            self.selected_tasks = self.opt.get(
                "EVAL_TASKS", self.opt.get("TRAINING_TASKS", None)
            )
            self.selected_languages = self.opt.get(
                "EVAL_LANGS", self.opt.get("TRAINING_LANGS", None)
            )
            self.selected_language_pairs = self.opt.get(
                "EVAL_LANG_PAIRS", self.opt.get("TRAINING_LANG_PAIRS", None)
            )

        cids = []
        corpus_dict = {}
        corpus_itrs = {}
        # used_XXX are the ones in the corpora and are selected
        used_tasks = set()
        used_languages = set()
        used_language_pairs = set()
        # unused_XXX are the ones in the corpora but are not selected
        # only used for logging
        unused_tasks = set()
        unused_languages = set()
        unused_language_pairs = set()
        for i, corpus_list in enumerate(corpora):
            # A corpus is a dictionary object in form of:
            # {source: ...,
            #  target: ...,
            #  task: ...,
            #  weight: ...,}
            # If multiple corpora are grouped in a list, they require to be combined
            # to form samples for their task (e.g. contrastive learning)
            if isinstance(corpus_list, list):
                need_to_combine = True
            else:
                corpus_list = [corpus_list]
                need_to_combine = False
            tmp_cids = []
            tmp_corpus_dict = {}
            tmp_corpus_itrs = {}
            for corpus in corpus_list:
                task = corpus["task"]
                if isinstance(task, dict):
                    assert (
                        len(task) == 1
                    ), "There should be only one task_name per corpus."
                    task_name = next(iter(task))
                    assert task[task_name] == 1
                else:
                    assert isinstance(task, str)
                    task_name = task

                skip_corpus = False
                # filter out tasks not selected
                if self.selected_tasks and task_name not in self.selected_tasks:
                    skip_corpus = True
                    unused_tasks.add(task_name)
                # filter out languges not selected
                if (
                    self.selected_languages
                    and corpus["source"]["language"] not in self.selected_languages
                ):
                    skip_corpus = True
                    unused_languages.add(corpus["source"]["language"])
                if "target" in corpus:
                    if (
                        self.selected_languages
                        and corpus["target"]["language"] not in self.selected_languages
                    ):
                        skip_corpus = True
                        unused_languages.add(corpus["target"]["language"])
                    if (
                        self.selected_language_pairs
                        and f"{corpus['source']['language']}-{corpus['target']['language']}"
                        not in self.selected_language_pairs
                    ):
                        skip_corpus = True
                        unused_language_pairs.add(
                            f"{corpus['source']['language']}-{corpus['target']['language']}"
                        )
                if skip_corpus:
                    continue
                # record used tasks and languages
                used_tasks.add(task_name)
                used_languages.add(corpus["source"]["language"])
                if "target" in corpus:
                    used_languages.add(corpus["target"]["language"])
                    used_language_pairs.add(
                        f"{corpus['source']['language']}-{corpus['target']['language']}"
                    )

                corpus["task_name"] = task_name

                cid = (
                    f"{i}_{task_name}_{corpus['source']['language']}-{corpus['target']['language']}"
                    if "target" in corpus
                    else f"{i}_{task_name}_{corpus['source']['language']}"
                )
                corpus["cid"] = cid
                corpus["weight"] = corpus.get("weight", 1.0)
                assert corpus["weight"] > 0

                # get corpus samples iterator for the corpus
                corpus_samples_itr = self._get_corpus_samples_iter(corpus)

                tmp_cids.append(cid)
                tmp_corpus_dict[cid] = corpus
                tmp_corpus_itrs[cid] = corpus_samples_itr
            if len(tmp_cids) == 0:
                continue
            if need_to_combine:
                cid, corpus, corpus_samples_itr = self._combine_multi_corpus_itrs(
                    tmp_cids, tmp_corpus_dict, tmp_corpus_itrs
                )
            else:
                cid = tmp_cids[0]
                corpus = tmp_corpus_dict[cid]
                corpus_samples_itr = tmp_corpus_itrs[cid]

            cids.append(cid)
            corpus_dict[cid] = corpus
            corpus_itrs[cid] = self._featurize_and_batch(corpus_samples_itr)

        if not self.evaluation:
            # If selected training tasks and languages do not exist in the corpora, raise error
            if self.selected_tasks and len(used_tasks) < len(set(self.selected_tasks)):
                raise ValueError(
                    f"Selected tasks {list(set(self.selected_tasks) - used_tasks)} do NOT exist in the corpora."
                    f"or task and language selections are incompatible."
                )
            if self.selected_languages and len(used_languages) < len(
                set(self.selected_languages)
            ):
                raise ValueError(
                    f"Selected languages {list(set(self.selected_languages) - used_languages)} \
                        do NOT exist in the corpora."
                    f"or task and language selections are incompatible."
                )
            if self.selected_language_pairs and len(used_language_pairs) < len(
                set(self.selected_language_pairs)
            ):
                raise ValueError(
                    f"Selected language pairs {list(set(self.selected_language_pairs) - used_language_pairs)} \
                        do NOT exist in the corpora."
                    f"or task and language selections are incompatible."
                )

        # If the corpora have tasks and languages not being selected, log them
        if len(unused_tasks) > 0:
            logger.info(f"Tasks {list(unused_tasks)} in the corpora are not selected.")
        if len(unused_languages) > 0:
            logger.info(
                f"Languages {list(unused_languages)} in the corpora are not selected."
            )
        if len(unused_language_pairs) > 0:
            logger.info(
                f"Language pairs {list(unused_language_pairs)} in the corpora are not selected."
            )

        # in evaluation mode simply flatten all the finite corpus iterators to one finite iterator
        if self.evaluation:
            tmp_corpus_itrs = iterators.NativeCheckpointableIterator(
                [corpus_itrs[cid] for cid in cids]
            )
            tmp_batch_iter = iterators.SelectManyIterator(tmp_corpus_itrs)
            # @TODO It's a non-standard usage of iterators. \
            # Need to realize this logic more efficiently with new Iterator classes.
            if self.opt.get("EVAL_PREFETCH_BUFFER", 100) > 0:
                logger.info(
                    f"Using eval PrefetchIterator with buffer size {self.opt.get('EVAL_PREFETCH_BUFFER', 100)}."
                )
                tmp_batch_iter = iterators.PrefetchIterator(
                    tmp_batch_iter,
                    buffer_size=self.opt.get("EVAL_PREFETCH_BUFFER", 100),
                    buffer_in_main_process=True,
                    log_empty_buffer_warning=True,
                )
            self._iter = tmp_batch_iter
            return

        # normalize the corpus weights to sum to 1
        sum_weight = sum(corpus["weight"] for corpus in corpus_dict.values())
        for cid, corpus in corpus_dict.items():
            corpus["weight"] /= sum_weight
        # group, multiplex, then zip all the corpus iterators to one iterator
        # batchs from same group should use same part of model
        grouped_cids, group_weights = self._group_corpora(cids, corpus_dict)
        group_names, group_iters = [], []
        for group_name, group_cids in sorted(
            grouped_cids.items(), key=lambda kv: kv[0]
        ):
            # iterate in the order sorted by group name to make sure it's same on all ranks
            # MultiplexIterator to sample corpus itrs in same group proportional to the corpus weights
            group_corpus_itrs = [corpus_itrs[cid] for cid in group_cids]
            group_corpus_weights = [
                corpus_dict[cid]["weight"] / group_weights[group_name]
                for cid in group_cids
            ]
            # 1000 corpus indices, repeated proportionally to their weight
            indices = sum(
                [
                    [i] * max(1, round(group_corpus_weights[i] * 1000.0))
                    for i in range(len(group_corpus_weights))
                ],
                [],
            )
            logger.debug(f"Group {group_name} corpus weights: {group_corpus_weights}")
            logger.debug(
                f"Group {group_name} corpus iterators sampling control indices length: {len(indices)}"
            )
            tmp_seed = self.seed_rng.randrange(2**32)
            logger.warning(
                f"Corpus iterator group {group_name} corpus multiplex sampler seed \
                    {tmp_seed} should be same accross all ranks."
            )
            control_itr = iterators.InfinitePermutationSourceIterator(
                indices, shuffle=True, seed=tmp_seed
            )  # this round-robins the indices
            group_iter = iterators.MultiplexIterator(control_itr, group_corpus_itrs)

            if not self.opt.get("IGNORE_GROUP_WEIGHT", False):
                # FixedBatchIterator to yield a list of batches in a group,
                # with the list length proportional to the total weigth in that group
                # only a rough appeoximation
                batch_count = max(
                    1,
                    round(
                        group_weights[group_name]
                        / min(weight for weight in group_weights.values())
                    ),
                )
            else:
                # group weight is ignored
                # every group has 1 batch in the list
                logger.info(
                    "Group weight is ignored. Every group has 1 batch in the list."
                )
                batch_count = 1
            group_iter = iterators.FixedBatchIterator(group_iter, batch_count)

            if self.opt.get("PREFETCH_BUFFER", 100) > 0:
                logger.info(
                    f"Using per-group PrefetchIterator with buffer size {self.opt.get('PREFETCH_BUFFER', 100)}."
                )
                group_iter = iterators.PrefetchIterator(
                    group_iter,
                    buffer_size=self.opt.get("PREFETCH_BUFFER", 100),
                    buffer_in_main_process=True,
                    log_empty_buffer_warning=True,
                )

            group_names.append(group_name)
            group_iters.append(group_iter)

        # ZipIterator to zip all groups into one iterator, a zipped batch contain one batch from each group
        grouped_iter = iterators.ZipIterator(*group_iters)

        def batch_tuple_to_dict(grouped_batch):
            batch_dict = {}
            for group_name, batch in zip(group_names, grouped_batch):
                batch_dict[group_name] = batch
            return batch_dict

        grouped_iter = iterators.MapIterator(
            grouped_iter, transform=batch_tuple_to_dict
        )

        # Disable final prefetcher because per-group prefetcher is sufficient
        # if self.opt.get('FINAL_PREFETCH_BUFFER', 0) > 0:
        #     logger.info(f"Using final PrefetchIterator with buffer size {self.opt.get('FINAL_PREFETCH_BUFFER', 0)}.")
        #     grouped_iter = iterators.PrefetchIterator(
        #         grouped_iter,
        #         buffer_size=self.opt.get('FINAL_PREFETCH_BUFFER', 0),
        #         buffer_in_main_process=True,
        #         log_empty_buffer_warning=True
        #         )

        self._iter = grouped_iter
        # Final iterator yields a batch in form of:
        # {<group name 1>: [<batch>, <batch>],
        #  <group name 2>: [<batch>, <batch>, <batch>],
        #  <group name 3>: [<batch>],
        # }

    def _get_corpus_samples_iter(self, corpus):
        # process the corpus into task specific format
        # return a corpus sample iterator

        # double check the corpus is for the expected task
        task_name = corpus["task_name"]

        chunks = self._get_chunks_from_corpus(
            corpus
        )  # get a chunk iterator from the corpus
        docs = iterators.SelectManyIterator(
            chunks, collection_selector=self._read_docs_from_chunk
        )
        docs = iterators.SamplingRandomMapIterator(
            docs,
            transform=self._tokenize_doc,
            seed=self.seed_rng.randrange(2**32) + self.rank,
        )
        if not self.evaluation and self.opt.get("CONCAT_SENTENCE", 0.0) > 0:
            docs = iterators.SamplingRandomMapIterator(
                docs,
                transform=self._concat_samples_in_doc,
                seed=self.seed_rng.randrange(2**32) + self.rank,
            )
        if not self.evaluation and self.opt["DOC_SHUFFLE_BUF_SIZE"] > 1:
            docs = iterators.BlockwiseShuffleIterator(
                docs,
                self.opt["DOC_SHUFFLE_BUF_SIZE"],
                seed=self.seed_rng.randrange(2**32) + self.rank,
            )
        samples = iterators.SelectManyIterator(docs)
        if not self.evaluation and self.opt["SAMPLE_SHUFFLE_BUFFER_SIZE"] > 1:
            samples = iterators.BlockwiseShuffleIterator(
                samples,
                self.opt["SAMPLE_SHUFFLE_BUFFER_SIZE"],
                seed=self.seed_rng.randrange(2**32) + self.rank,
            )

        # create task samples
        scheduling_settings = copy.deepcopy(
            self.opt.get("NOISE_SCHEDULING_SETTINGS", {}) if not self.evaluation else {}
        )
        if task_name == "mlm":
            samples = SamplingNumpyRandomMapIterator(
                samples,
                transform=self._assign_mlm_task,
                seed=self.seed_rng.randrange(2**32) + self.rank,
                scheduling_settings=scheduling_settings,
            )
        elif task_name == "dae":
            samples = SamplingNumpyRandomMapIterator(
                samples,
                transform=self._assign_dae_task,
                seed=self.seed_rng.randrange(2**32) + self.rank,
                scheduling_settings=scheduling_settings,
            )
        elif task_name == "mt":
            samples = iterators.MapIterator(samples, transform=self._assign_mt_task)
        elif task_name == "noised_mt":
            samples = SamplingNumpyRandomMapIterator(
                samples,
                transform=self._assign_noised_mt_task,
                seed=self.seed_rng.randrange(2**32) + self.rank,
                scheduling_settings=scheduling_settings,
            )
        elif task_name == "mt_dae":
            samples = SamplingNumpyRandomMapIterator(
                samples,
                transform=self._assign_mt_dae_task,
                seed=self.seed_rng.randrange(2**32) + self.rank,
                scheduling_settings=scheduling_settings,
            )
        elif task_name == "xmlm":
            samples = SamplingNumpyRandomMapIterator(
                samples,
                transform=self._assign_xmlm_task,
                seed=self.seed_rng.randrange(2**32) + self.rank,
                scheduling_settings=scheduling_settings,
            )
        elif task_name == "contrastive":
            samples = iterators.MapIterator(
                samples, transform=self._assign_contrastive_task
            )
        else:
            raise ValueError(f"Task {task_name} not supported")

        return samples

    def _featurize_and_batch(self, samples):
        # convert universal samples to model specific features (model sensitive)
        samples = iterators.MapIterator(
            samples, transform=self._convert_sample_to_feature
        )

        # batching & prefetch
        if self.evaluation:
            eval_batch_size = (
                self.opt["EVAL_MAX_TOKENS_BATCH"]
                // (
                    self.opt["MAX_LEN"]
                    + self.opt.get("MAX_GEN_LENGTH", 20) * self.opt["BEAM_WIDTH"]
                )
                // 8
            ) * 8
            eval_batch_size = max(1, eval_batch_size)
            logger.info(f"Evaluation batch size: {eval_batch_size}")
        batches = iterators.BucketedReadaheadBatchIterator(
            samples,
            read_ahead=self.opt["BATCH_READ_AHEAD"],
            key=None if self.evaluation else (lambda sample: sample["sample_length"]),
            batch_size=eval_batch_size if self.evaluation else self._dynamic_batch_size,
            shuffle=not self.evaluation,
            seed=self.seed_rng.randrange(2**32) + self.rank,
        )

        # collate & pad to tensors (model sensitive)
        batches = iterators.SelectManyIterator(
            batches, collection_selector=self._collate
        )

        # Disable per-corpus prefetcher because per-group prefetcher is sufficient
        # if self.opt.get('CORPUS_PREFETCH_BUFFER', 0) > 0:
        #     logger.info(f"Using per-corpus PrefetchIterator with buffer size
        # {self.opt.get('CORPUS_PREFETCH_BUFFER', 0)}.")
        #     batches = iterators.PrefetchIterator(
        #         batches,
        #         buffer_size=self.opt.get('CORPUS_PREFETCH_BUFFER', 0))

        return batches

    def _combine_multi_corpus_itrs(self, cids, corpus_dict, corpus_itrs):
        # for the data set that requires combining samples from multiple corpora
        corpora = [corpus_dict[cid] for cid in cids]

        # make sure the task_name are same for the corpora being combined
        for corpus in corpora:
            assert (
                corpus["task_name"] == corpora[0]["task_name"]
            ), "The corpora being combined are NOT of the same task."
        corpus_weights = [corpus["weight"] for corpus in corpora]
        total_weight = sum(corpus_weights)
        corpus_weights = [
            corpus_weight / total_weight for corpus_weight in corpus_weights
        ]
        new_cid = "_".join(cids[0].split("_")[:-1])
        new_corpus = {
            key: val
            for key, val in corpora[0].items()
            if key not in ["source", "target", "cid", "weight"]
        }
        new_corpus["cid"] = new_cid
        new_corpus["weight"] = total_weight
        corpus_samples_itrs = [corpus_itrs[cid] for cid in cids]
        # 1000 corpus indices, repeated proportionally to their weight
        indices = sum(
            [
                [i] * max(1, round(corpus_weights[i] * 1000.0))
                for i in range(len(corpus_weights))
            ],
            [],
        )
        control_itr = iterators.InfinitePermutationSourceIterator(
            indices, shuffle=True, seed=self.seed_rng.randrange(2**32) + self.rank
        )  # this round-robins the indices
        new_corpus_samples_itr = iterators.MultiplexIterator(
            control_itr, corpus_samples_itrs
        )

        if corpora[0]["task_name"] == "contrastive":
            # for contrastive learning task, combine 2 samples to form a contrastive sample
            new_corpus_samples_itr = iterators.FixedBatchIterator(
                new_corpus_samples_itr, 2
            )

            def combine_contrastive_samples(sample_pair):
                combined_sample = {
                    key: val
                    for key, val in sample_pair[0].items()
                    if key not in ["source", "target", "cid"]
                }
                combined_sample["cid"] = new_cid
                for key in ["source", "target"]:
                    combined_sample[key] = [sample[key] for sample in sample_pair]
                return combined_sample

            new_corpus_samples_itr = iterators.MapIterator(
                new_corpus_samples_itr, transform=combine_contrastive_samples
            )
        else:
            # for other tasks, simply insert the new_cid into the samples
            def insert_new_cid(sample):
                sample["cid"] = new_cid
                return sample

            new_corpus_samples_itr = iterators.MapIterator(
                new_corpus_samples_itr, transform=insert_new_cid
            )

        return new_cid, new_corpus, new_corpus_samples_itr

    def _group_corpora(self, cids, corpus_dict):
        # by default group by task name, so each mini-batch will
        # have at least one batch from each task
        grouped_cids = {}
        group_weights = {}
        for cid in cids:
            group_name = corpus_dict[cid]["task_name"]
            if group_name not in grouped_cids:
                grouped_cids[group_name] = [cid]
                group_weights[group_name] = corpus_dict[cid]["weight"]
            else:
                grouped_cids[group_name].append(cid)
                group_weights[group_name] += corpus_dict[cid]["weight"]
        logger.info(f"Grouped cids: {grouped_cids}")
        logger.info(f"Group weights: {group_weights}")
        return grouped_cids, group_weights

    def _get_chunk_ref(
        self,
        source_chunk_file,
        target_chunk_file,
        corpus_source,
        corpus_target,
        task_name,
        cid,
    ):
        chunk_ref = {
            "source": {
                "dataset": os.path.join(corpus_source["dataset"], source_chunk_file),
                "language": corpus_source["language"],
                "format": corpus_source["format"],
                "document_level": corpus_source["document_level"],
            },
            "task_name": task_name,
            "cid": cid,
        }  # corpus id for corpus based metric computation during evaluation
        if corpus_target is not None:
            chunk_ref["target"] = {
                "dataset": (
                    os.path.join(corpus_target["dataset"], target_chunk_file)
                    if corpus_target["dataset"]
                    else None
                ),
                "language": corpus_target["language"],
                "format": corpus_target["format"],
                "document_level": (
                    corpus_target["document_level"]
                    if corpus_target["dataset"]
                    else corpus_source["document_level"]
                ),
            }
        return chunk_ref

    def _get_chunks_from_corpus(self, corpus):
        task_name = corpus["task_name"]
        cid = corpus["cid"]
        max_retries = self.opt.get("FS_RETRIES", 3)

        source = corpus["source"]
        source["format"] = source.get("format", corpus.get("format", "plain"))
        assert source["format"] in [
            "plain",
            "json",
        ], f"Corpus source format '{source['format']}' is not supported."

        num_retries = 0
        while True:
            try:
                source_chunk_dir = os.path.join(self.corpus_root_dir, source["dataset"])
                if source_chunk_dir in self.chunk_cache:
                    source_chunk_files = self.chunk_cache[source_chunk_dir]
                else:
                    # enumerate all .gz files in the given paths
                    source_chunk_files = sorted(
                        [x for x in os.listdir(source_chunk_dir) if x.endswith(".gz")]
                    )
                    assert (
                        len(source_chunk_files) > 0
                    ), f"Corpus {cid} contains NO chunk file."
                    self.chunk_cache[source_chunk_dir] = source_chunk_files
                logger.info(
                    f"Corpus {cid} contains {len(source_chunk_files)} chunk files."
                )
                break
            except Exception as err:
                logger.warning(err)
                logger.warning(
                    f"Failed to list chunk files in {source_chunk_dir}, waiting for 30 seconds to retry."
                )
                num_retries += 1
                if num_retries > max_retries:
                    error_message = f"Failed to list chunk files in {source_chunk_dir} after {max_retries} retries."
                    logger.error(error_message)
                    raise Exception(error_message)
                time.sleep(30)

        if corpus.get("target", None):
            target = corpus["target"]
            target["format"] = target.get("format", corpus.get("format", "plain"))
            assert target["format"] in [
                "plain",
                "json",
            ], f"Corpus target format '{target['format']}' is not supported."

            if target.get("dataset", None):
                num_retries = 0
                while True:
                    try:
                        target_chunk_dir = os.path.join(
                            self.corpus_root_dir, target["dataset"]
                        )
                        if target_chunk_dir in self.chunk_cache:
                            target_chunk_files = self.chunk_cache[target_chunk_dir]
                        else:
                            # enumerate all .gz files in the given paths
                            target_chunk_files = sorted(
                                [
                                    x
                                    for x in os.listdir(target_chunk_dir)
                                    if x.endswith(".gz")
                                ]
                            )
                            assert len(source_chunk_files) == len(
                                target_chunk_files
                            ), f"Number of chunk files should be the same in source ({len(source_chunk_files)})\
                                and target ({len(target_chunk_files)}) datasets."
                            assert all(
                                [
                                    s == t
                                    for s, t in zip(
                                        source_chunk_files, target_chunk_files
                                    )
                                ]
                            ), f"chunk file names are not fully matching in source dir {source_chunk_dir}\
                                and target dir {target_chunk_dir}."
                            self.chunk_cache[target_chunk_dir] = target_chunk_files
                        break
                    except Exception as err:
                        logger.warning(err)
                        logger.warning(
                            f"Failed to list chunk files in {target_chunk_dir}, waiting for 30 seconds to retry."
                        )
                        num_retries += 1
                        if num_retries > max_retries:
                            error_message = f"Failed to list chunk files in {target_chunk_dir}\
                            after {max_retries} retries."
                            logger.error(error_message)
                            raise Exception(error_message)
                        time.sleep(30)
            else:
                # ignore ground truth for generation
                assert (
                    self.evaluation
                ), "Training data should always provide target dataset for a parallel corpus."
                assert (
                    task_name != "xmlm"
                ), "Crosslingual Masked LM task must have target dataset."
                assert (
                    task_name != "mt_dae"
                ), "Crosslingual Denoising Auto Encoder task must have target dataset."
                target_chunk_files = [""] * len(source_chunk_files)
                target["dataset"] = None
        else:
            target = None
            target_chunk_files = [""] * len(source_chunk_files)

        chunks = [
            self._get_chunk_ref(s, t, source, target, task_name, cid)
            for s, t in zip(source_chunk_files, target_chunk_files)
        ]

        if not self.evaluation:
            # training uses an infinite randomizing source
            chunks = iterators.InfinitePermutationSourceIterator(
                chunks,
                seed=self.seed_rng.randrange(2**32),
                shuffle=True,
                num_instances=self.world_size,
                instance_rank=self.rank,
            )
        else:
            # eval uses a source that reads chunks once in sequence
            # in evaluation mode, the files are iterated once without shuffling, but still with parallelization
            chunks = iterators.ChunkedSourceIterator(
                chunks, num_instances=self.world_size, instance_rank=self.rank
            )

        return chunks

    @staticmethod
    def _is_doc_boundary(format, sentences, is_document_level, doc_len):
        if format == "json":
            return True
        # sometimes sentence-level corpus also has empty line due to data preprocessing bug
        elif is_document_level and sentences == [""]:
            return True
        elif not is_document_level and doc_len >= 50:
            return True
        else:
            return False

    @staticmethod
    def _get_sentences_from_line(line_s, line_t, format):
        if format == "json":
            line_s = json.loads(line_s)["raw_content"]
            sentences_s = [s.strip() for s in line_s.split("\n") if s.strip() != ""]
            if line_t is not None:
                line_t = json.loads(line_t)["raw_content"]
                sentences_t = [s.strip() for s in line_t.split("\n") if s.strip() != ""]
        else:
            sentences_s = [line_s.strip()]
            if line_t is not None:
                sentences_t = [line_t.strip()]
        if line_t is None:
            sentences_t = [None] * len(sentences_s)
        return sentences_s, sentences_t

    @staticmethod
    def _append_sentence(doc, source_seq, target_seq, chunk):
        if source_seq == "":
            return

        source = chunk["source"]
        target = chunk.get("target", None)

        source_sent = {"sequence": source_seq, "language": source["language"]}

        target_sent = None
        if target is not None:
            target_sent = {"sequence": target_seq, "language": target["language"]}

        doc.append(
            {
                "source": source_sent,
                "target": target_sent,
                "task_name": chunk["task_name"],
                "cid": chunk["cid"],
            }
        )

    def _read_docs_from_chunk(self, chunk_ref):
        # logger.info(f"Reading source chunk {source['dataset']}")
        has_target_dataset = (
            chunk_ref.get("target", None) is not None
            and chunk_ref["target"]["dataset"] is not None
        )
        max_retries = self.opt.get("FS_RETRIES", 3)
        num_retries = 0
        while True:
            try:
                source = chunk_ref["source"]
                source_format = source["format"]
                source_chunk_file = os.path.join(
                    self.corpus_root_dir, source["dataset"]
                )
                with gzip.open(source_chunk_file, "rt", encoding="utf-8") as fs:
                    lines_s = fs.readlines()
                assert len(lines_s) > 0, (
                    "*************** Data Validation Error **************.\n"
                    f"Source chunk file {source_chunk_file} is empty.\n"
                    "****************************************************."
                )
                if has_target_dataset:  # parallel data
                    target = chunk_ref["target"]
                    target_format = target["format"]
                    assert source_format == target_format
                    assert (
                        source["document_level"] == target["document_level"]
                    ), f"Document level of source {source['dataset']} and target {source['dataset']} is inconsistant."
                    target_chunk_file = os.path.join(
                        self.corpus_root_dir, target["dataset"]
                    )
                    with gzip.open(target_chunk_file, "rt", encoding="utf-8") as ft:
                        lines_t = ft.readlines()
                    assert len(lines_s) == len(lines_t), (
                        "*************** Data Validation Error **************.\n"
                        f"Target chunk file {target_chunk_file} does NOT match \
                            source chunk file {source_chunk_file}.\n"
                        "****************************************************."
                    )
                else:
                    lines_t = [None] * len(lines_s)
                break
            except Exception as err:
                logger.warning(err)
                logger.warning(
                    f"Failed to read source chunk {source_chunk_file}, waiting for 30 seconds to retry."
                )
                num_retries += 1
                if num_retries > max_retries:
                    error_message = f"Failed to read source chunk {source_chunk_file} after {max_retries} \
                        retries. This chunk will be SKIPPED by the data loader."
                    logger.error(error_message)
                    return
                time.sleep(30)

        doc = []
        for line_s, line_t in zip(lines_s, lines_t):
            sentences_s, sentences_t = self._get_sentences_from_line(
                line_s, line_t, source_format
            )
            is_doc_boundary = self._is_doc_boundary(
                source_format, sentences_s, source["document_level"], len(doc)
            )
            assert line_t is None or is_doc_boundary == self._is_doc_boundary(
                source_format, sentences_t, target["document_level"], len(doc)
            ), f"Document break of source {source['dataset']} and target {source['dataset']} is inconsistant."
            if is_doc_boundary:
                if len(doc) > 0:
                    yield doc
                doc = []
            for sent_s, sent_t in zip(sentences_s, sentences_t):
                self._append_sentence(doc, sent_s, sent_t, chunk_ref)

        if len(doc) > 0:
            yield doc

    # model sensitive
    def _get_tokenizer(self, sentence):
        # return the tokenizer for encoder input and decoder input for the provided sentence
        # override this method for models that use more than one tokenizer
        return self.tokenizer, self.tokenizer

    def _tokenize_sentence(self, sentence):
        # tokenize a sentence dict (either source or target) in the sample
        encoder_tokenizer, decoder_tokenizer = self._get_tokenizer(sentence)
        if sentence["sequence"]:
            sentence["encoder_sequence"] = encoder_tokenizer.tokenize(
                sentence["sequence"]
            )
            sentence["decoder_sequence"] = decoder_tokenizer.tokenize(
                sentence["sequence"]
            )
        else:
            sentence["encoder_sequence"] = []
            sentence["decoder_sequence"] = []
        return sentence

    def _validate_tokenized_sample(self, sample):
        if not sample["source"]["encoder_sequence"]:
            return False
        if not sample["source"]["decoder_sequence"]:
            return False
        if sample["target"] is not None:
            if sample["target"]["sequence"]:
                if not sample["target"]["encoder_sequence"]:
                    return False
                if not sample["target"]["decoder_sequence"]:
                    return False
            elif sample["target"]["sequence"] is not None:
                return False
        return True

    def _tokenize_doc(self, rand: Random, doc):
        for sample in doc:
            sample["source"] = self._tokenize_sentence(sample["source"])

            if sample["target"] is not None:
                sample["target"] = self._tokenize_sentence(sample["target"])

        # filter out bad samples in the doc
        ret_doc = [sample for sample in doc if self._validate_tokenized_sample(sample)]
        return ret_doc

    @staticmethod
    def _concat_two_samples(sample, concat_sample):
        sample["source"]["sequence"] = (
            sample["source"]["sequence"] + " " + concat_sample["source"]["sequence"]
        )
        sample["source"]["encoder_sequence"].extend(
            concat_sample["source"]["encoder_sequence"]
        )
        sample["source"]["decoder_sequence"].extend(
            concat_sample["source"]["decoder_sequence"]
        )

        if sample["target"] is not None and sample["target"]["sequence"]:
            sample["target"]["sequence"] = (
                sample["target"]["sequence"] + " " + concat_sample["target"]["sequence"]
            )
            sample["target"]["encoder_sequence"].extend(
                concat_sample["target"]["encoder_sequence"]
            )
            sample["target"]["decoder_sequence"].extend(
                concat_sample["target"]["decoder_sequence"]
            )
        return sample

    @staticmethod
    def _get_max_sequence_length(sample):
        # return the (estimated) max length of the sample sequences
        max_length = max(
            len(sample["source"]["encoder_sequence"]),
            len(sample["source"]["decoder_sequence"]),
        )
        if sample["target"] is not None and sample["target"]["sequence"]:
            max_length = max(
                max_length,
                len(sample["target"]["encoder_sequence"]),
                len(sample["target"]["decoder_sequence"]),
            )
        return max_length

    def _concat_samples_in_doc(self, rand: Random, doc):
        ret_doc = []
        do_concat = rand.random() < self.opt.get("CONCAT_SENTENCE", 0.0)
        tmp_sample = None
        for sample in doc:
            if not tmp_sample:
                tmp_sample = copy.deepcopy(sample)
            else:
                tmp_sample = self._concat_two_samples(tmp_sample, sample)
            if (
                not do_concat
                or self._get_max_sequence_length(tmp_sample) >= self.opt["MAX_LEN"]
            ):
                ret_doc.append(tmp_sample)
                do_concat = rand.random() < self.opt.get("CONCAT_SENTENCE", 0.0)
                tmp_sample = None
        if tmp_sample:
            ret_doc.append(tmp_sample)
            tmp_sample = None
        return ret_doc

    def _assign_mlm_task(
        self, rand: Random, np_rand: RandomState, scheduler: NoisingScheduler, sample
    ):
        """
        apply masking

        input sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'target'   : None,
         'task_name': <task_name>,
         'cid'      : cid
        }

        return sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (masked list of tokens)
                       'decoder_sequence': None
                       'language': (str)},
         'target'   : None,
         'label'    : {'label_sequence': (list of label tokens)},
         'task_name': <task_name>,
         'cid'      : cid
        }
        """
        encoder_tokenizer, _ = self._get_tokenizer(sample["source"])
        # lazily initialize mlm_masking_scheme for different languages
        if not hasattr(self, "mlm_masking_scheme"):
            self.mlm_masking_scheme = {}
        # using tokenizer object id as a key to the masking scheme
        if id(encoder_tokenizer) not in self.mlm_masking_scheme:
            logger.info(
                f"Creating masking scheme for tokenizer object {id(encoder_tokenizer)}."
            )
            self.mlm_masking_scheme[id(encoder_tokenizer)] = (
                RandomWordMasking(
                    encoder_tokenizer,
                    mask_idx=encoder_tokenizer.mask_token_id,
                    bpe_cont_marker="sentencepiece",
                    masking_ratio=self.opt.get("MLM_MASK_RATIO", 0.35),
                    masking_prob=self.opt.get("MLM_MASK_PROB", 0.8),
                    random_token_prob=self.opt.get("MLM_RAND_TOKEN_PROB", 0.1),
                )
                if self.opt.get("WHOLE_WORD_MASKING", True)
                else RandomTokenMasking(
                    encoder_tokenizer,
                    mask_idx=encoder_tokenizer.mask_token_id,
                    bpe_cont_marker="sentencepiece",
                    masking_ratio=self.opt.get("MLM_MASK_RATIO", 0.35),
                    masking_prob=self.opt.get("MLM_MASK_PROB", 0.8),
                    random_token_prob=self.opt.get("MLM_RAND_TOKEN_PROB", 0.1),
                )
            )

        masking_scheme = self.mlm_masking_scheme[id(encoder_tokenizer)]
        input_sequence = np.array(
            encoder_tokenizer.convert_tokens_to_ids(
                sample["source"]["encoder_sequence"]
            )
        )
        masked_input_sequence, label_sequence = masking_scheme.masking(
            input_sequence,
            np_rand,
            masking_ratio=scheduler.get_scheduled_ratio(
                "MLM_MASK_RATIO", default=masking_scheme.masking_ratio
            ),
        )
        masked_input_sequence = encoder_tokenizer.convert_ids_to_tokens(
            masked_input_sequence
        )
        label_sequence = encoder_tokenizer.convert_ids_to_tokens(label_sequence)

        assert (
            "label" not in sample
        ), f"Error: sample {sample} has already been assigned a task."
        sample["source"]["encoder_sequence"] = masked_input_sequence
        sample["source"]["decoder_sequence"] = None
        sample["target"] = None
        sample["label"] = {"label_sequence": label_sequence}

        return sample

    def _assign_dae_task(
        self, rand: Random, np_rand: RandomState, scheduler: NoisingScheduler, sample
    ):
        """
        apply noising

        input sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'target'   : None,
         'task_name': <task_name>,
         'cid'      : cid
        }

        return sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (noised list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'target'   : None,
         'label'    : {'label_sequence': (list of label tokens, same as source decoder sequence)},
         'task_name': <task_name>,
         'cid'      : cid
        }
        """
        encoder_tokenizer, _ = self._get_tokenizer(sample["source"])
        # lazily initialize dae_noising_scheme for different languages
        if not hasattr(self, "dae_noising_scheme"):
            self.dae_noising_scheme = {}
        # using tokenizer object id as a key to the noising scheme
        if id(encoder_tokenizer) not in self.dae_noising_scheme:
            logger.info(
                f"Creating noising scheme for tokenizer object {id(encoder_tokenizer)}."
            )
            self.dae_noising_scheme[id(encoder_tokenizer)] = DaeNoising(
                encoder_tokenizer,
                mask_idx=encoder_tokenizer.mask_token_id,
                bpe_cont_marker="sentencepiece",
                dropout_prob=self.opt.get("DAE_DROPOUT_PROB", 0.1),
                blanking_prob=self.opt.get("DAE_BLANK_PROB", 0.1),
                max_shuffle_distance=self.opt.get("DAE_MAX_SHUFFLE_DISTANCE", 3),
                text_infilling_ratio=self.opt.get("DAE_TEXT_INFILL_RATIO", 0.3),
                text_infilling_lambda=self.opt.get("DAE_TEXT_INFILL_LAMBDA", 3),
            )

        noising_scheme = self.dae_noising_scheme[id(encoder_tokenizer)]
        input_sequence = np.array(
            encoder_tokenizer.convert_tokens_to_ids(
                sample["source"]["encoder_sequence"]
            )
        )
        noised_input_sequence, _ = noising_scheme.noising(
            input_sequence,
            np_rand,
            blanking_prob=scheduler.get_scheduled_ratio(
                "DAE_BLANK_PROB", default=noising_scheme.blanking_prob
            ),
            dropout_prob=scheduler.get_scheduled_ratio(
                "DAE_DROPOUT_PROB", default=noising_scheme.dropout_prob
            ),
            max_shuffle_distance=math.ceil(
                scheduler.get_scheduled_ratio(
                    "DAE_MAX_SHUFFLE_DISTANCE",
                    default=noising_scheme.max_shuffle_distance,
                )
            ),
            text_infilling_ratio=scheduler.get_scheduled_ratio(
                "DAE_TEXT_INFILL_RATIO", default=noising_scheme.text_infilling_ratio
            ),
        )
        noised_input_sequence = encoder_tokenizer.convert_ids_to_tokens(
            noised_input_sequence
        )

        assert (
            "label" not in sample
        ), f"Error: sample {sample} has already been assigned a task."
        sample["source"]["encoder_sequence"] = noised_input_sequence
        sample["target"] = None
        sample["label"] = {"label_sequence": sample["source"]["decoder_sequence"][:]}

        return sample

    def _assign_mt_task(self, sample):
        """
        input sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'target'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'task_name': <task_name>,
         'cid'      : cid
        }

        return sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': None
                       'language': (str)},
         'target'   : {'sequence': (str)
                       'encoder_sequence': None
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'label'    : {'label_sequence': (list of label tokens, same as target decoder sequence)},
         'task_name': <task_name>,
         'cid'      : cid
        }
        """
        assert (
            "label" not in sample
        ), f"Error: sample {sample} has already been assigned a task."
        sample["source"]["decoder_sequence"] = None
        sample["target"]["encoder_sequence"] = None
        sample["label"] = {"label_sequence": sample["target"]["decoder_sequence"][:]}

        return sample

    def _assign_noised_mt_task(
        self, rand: Random, np_rand: RandomState, scheduler: NoisingScheduler, sample
    ):
        """
        apply noising

        input sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'target'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'task_name': <task_name>,
         'cid'      : cid
        }

        return sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (noised list of tokens)
                       'decoder_sequence': None
                       'language': (str)},
         'target'   : {'sequence': (str)
                       'encoder_sequence': None
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'label'    : {'label_sequence': (list of label tokens, same as target decoder sequence)},
         'task_name': <task_name>,
         'cid'      : cid
        }
        """
        encoder_tokenizer, _ = self._get_tokenizer(sample["source"])
        # lazily initialize dae_noising_scheme for different languages
        if not hasattr(self, "dae_noising_scheme"):
            self.dae_noising_scheme = {}
        # using tokenizer object id as a key to the noising scheme
        if id(encoder_tokenizer) not in self.dae_noising_scheme:
            logger.info(
                f"Creating noising scheme for tokenizer object {id(encoder_tokenizer)}."
            )
            self.dae_noising_scheme[id(encoder_tokenizer)] = DaeNoising(
                encoder_tokenizer,
                mask_idx=encoder_tokenizer.mask_token_id,
                bpe_cont_marker="sentencepiece",
                dropout_prob=self.opt.get("DAE_DROPOUT_PROB", 0.1),
                blanking_prob=self.opt.get("DAE_BLANK_PROB", 0.1),
                max_shuffle_distance=self.opt.get("DAE_MAX_SHUFFLE_DISTANCE", 3),
                text_infilling_ratio=self.opt.get("DAE_TEXT_INFILL_RATIO", 0.3),
                text_infilling_lambda=self.opt.get("DAE_TEXT_INFILL_LAMBDA", 3),
            )

        noising_scheme = self.dae_noising_scheme[id(encoder_tokenizer)]
        input_sequence = np.array(
            encoder_tokenizer.convert_tokens_to_ids(
                sample["source"]["encoder_sequence"]
            )
        )
        noised_input_sequence, _ = noising_scheme.noising(
            input_sequence,
            np_rand,
            blanking_prob=scheduler.get_scheduled_ratio(
                "DAE_BLANK_PROB", default=noising_scheme.blanking_prob
            ),
            dropout_prob=scheduler.get_scheduled_ratio(
                "DAE_DROPOUT_PROB", default=noising_scheme.dropout_prob
            ),
            max_shuffle_distance=math.ceil(
                scheduler.get_scheduled_ratio(
                    "DAE_MAX_SHUFFLE_DISTANCE",
                    default=noising_scheme.max_shuffle_distance,
                )
            ),
            text_infilling_ratio=scheduler.get_scheduled_ratio(
                "DAE_TEXT_INFILL_RATIO", default=noising_scheme.text_infilling_ratio
            ),
        )
        noised_input_sequence = encoder_tokenizer.convert_ids_to_tokens(
            noised_input_sequence
        )

        assert (
            "label" not in sample
        ), f"Error: sample {sample} has already been assigned a task."
        sample["source"]["encoder_sequence"] = noised_input_sequence
        sample["source"]["decoder_sequence"] = None
        sample["target"]["encoder_sequence"] = None
        sample["label"] = {"label_sequence": sample["target"]["decoder_sequence"][:]}

        return sample

    def _assign_mt_dae_task(
        self, rand: Random, np_rand: RandomState, scheduler: NoisingScheduler, sample
    ):
        """
        input sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'target'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'task_name': <task_name>,
         'cid'      : cid
        }

        return sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': None
                       'language': (str)},
         'target'   : {'sequence': (str)
                       'encoder_sequence': (noised list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'label'    : {'label_sequence': (list of label tokens, same as target decoder sequence)},
         'task_name': <task_name>,
         'cid'      : cid
        }
        """
        encoder_tokenizer, _ = self._get_tokenizer(sample["target"])
        # lazily initialize dae_noising_scheme for different languages
        if not hasattr(self, "dae_noising_scheme"):
            self.dae_noising_scheme = {}
        # using tokenizer object id as a key to the noising scheme
        if id(encoder_tokenizer) not in self.dae_noising_scheme:
            logger.info(
                f"Creating noising scheme for tokenizer object {id(encoder_tokenizer)}."
            )
            self.dae_noising_scheme[id(encoder_tokenizer)] = DaeNoising(
                encoder_tokenizer,
                mask_idx=encoder_tokenizer.mask_token_id,
                bpe_cont_marker="sentencepiece",
                dropout_prob=self.opt.get("DAE_DROPOUT_PROB", 0.1),
                blanking_prob=self.opt.get("DAE_BLANK_PROB", 0.1),
                max_shuffle_distance=self.opt.get("DAE_MAX_SHUFFLE_DISTANCE", 3),
                text_infilling_ratio=self.opt.get("DAE_TEXT_INFILL_RATIO", 0.3),
                text_infilling_lambda=self.opt.get("DAE_TEXT_INFILL_LAMBDA", 3),
            )

        noising_scheme = self.dae_noising_scheme[id(encoder_tokenizer)]
        input_sequence = np.array(
            encoder_tokenizer.convert_tokens_to_ids(
                sample["target"]["encoder_sequence"]
            )
        )
        noised_input_sequence, _ = noising_scheme.noising(
            input_sequence,
            np_rand,
            blanking_prob=scheduler.get_scheduled_ratio(
                "DAE_BLANK_PROB", default=noising_scheme.blanking_prob
            ),
            dropout_prob=scheduler.get_scheduled_ratio(
                "DAE_DROPOUT_PROB", default=noising_scheme.dropout_prob
            ),
            max_shuffle_distance=math.ceil(
                scheduler.get_scheduled_ratio(
                    "DAE_MAX_SHUFFLE_DISTANCE",
                    default=noising_scheme.max_shuffle_distance,
                )
            ),
            text_infilling_ratio=scheduler.get_scheduled_ratio(
                "DAE_TEXT_INFILL_RATIO", default=noising_scheme.text_infilling_ratio
            ),
        )
        noised_input_sequence = encoder_tokenizer.convert_ids_to_tokens(
            noised_input_sequence
        )

        assert (
            "label" not in sample
        ), f"Error: sample {sample} has already been assigned a task."
        sample["source"]["decoder_sequence"] = None
        sample["target"]["encoder_sequence"] = noised_input_sequence
        sample["label"] = {"label_sequence": sample["target"]["decoder_sequence"][:]}

        return sample

    def _assign_xmlm_task(
        self, rand: Random, np_rand: RandomState, scheduler: NoisingScheduler, sample
    ):
        """
        apply masking

        input sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'target'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'task_name': <task_name>,
         'cid'      : cid
        }

        return sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (masked list of tokens)
                       'decoder_sequence': None
                       'language': (str)},
         'target'   : {'sequence': (str)
                       'encoder_sequence': (masked list of tokens)
                       'decoder_sequence': None
                       'language': (str)},
         'label'    : {'label_sequence': {'source': (list of label tokens), 'target': (list of label tokens)}},
         'task_name': <task_name>,
         'cid'      : cid
        }
        """
        masked_input_sequence = {}
        label_sequence = {}
        for part in ["source", "target"]:
            encoder_tokenizer, _ = self._get_tokenizer(sample[part])
            # lazily initialize mlm_masking_scheme for different languages
            if not hasattr(self, "mlm_masking_scheme"):
                self.mlm_masking_scheme = {}
            # using tokenizer object id as a key to the masking scheme
            if id(encoder_tokenizer) not in self.mlm_masking_scheme:
                logger.info(
                    f"Creating masking scheme for tokenizer object {id(encoder_tokenizer)}."
                )
                self.mlm_masking_scheme[id(encoder_tokenizer)] = (
                    RandomWordMasking(
                        encoder_tokenizer,
                        mask_idx=encoder_tokenizer.mask_token_id,
                        bpe_cont_marker="sentencepiece",
                        masking_ratio=self.opt.get("MLM_MASK_RATIO", 0.35),
                        masking_prob=self.opt.get("MLM_MASK_PROB", 0.8),
                        random_token_prob=self.opt.get("MLM_RAND_TOKEN_PROB", 0.1),
                    )
                    if self.opt.get("WHOLE_WORD_MASKING", True)
                    else RandomTokenMasking(
                        encoder_tokenizer,
                        mask_idx=encoder_tokenizer.mask_token_id,
                        bpe_cont_marker="sentencepiece",
                        masking_ratio=self.opt.get("MLM_MASK_RATIO", 0.35),
                        masking_prob=self.opt.get("MLM_MASK_PROB", 0.8),
                        random_token_prob=self.opt.get("MLM_RAND_TOKEN_PROB", 0.1),
                    )
                )

            masking_scheme = self.mlm_masking_scheme[id(encoder_tokenizer)]
            input_sequence = np.array(
                encoder_tokenizer.convert_tokens_to_ids(
                    sample[part]["encoder_sequence"]
                )
            )
            part_masked_input_sequence, part_label_sequence = masking_scheme.masking(
                input_sequence,
                np_rand,
                masking_ratio=scheduler.get_scheduled_ratio(
                    "MLM_MASK_RATIO", default=masking_scheme.masking_ratio
                ),
            )
            masked_input_sequence[part] = encoder_tokenizer.convert_ids_to_tokens(
                part_masked_input_sequence
            )
            label_sequence[part] = encoder_tokenizer.convert_ids_to_tokens(
                part_label_sequence
            )

        assert (
            "label" not in sample
        ), f"Error: sample {sample} has already been assigned a task."
        sample["source"]["encoder_sequence"] = masked_input_sequence["source"]
        sample["source"]["decoder_sequence"] = None
        sample["target"]["encoder_sequence"] = masked_input_sequence["target"]
        sample["target"]["decoder_sequence"] = None
        sample["label"] = {"label_sequence": label_sequence}

        return sample

    def _assign_contrastive_task(self, sample):
        """
        input sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'target'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens)
                       'language': (str)},
         'task_name': <task_name>,
         'cid'      : cid
        }

        return sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': None
                       'language': (str)},
         'target'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': None
                       'language': (str)},
         'label'    : {'label_sequence': None},
         'task_name': <task_name>,
         'cid'      : cid
        }
        """
        assert (
            "label" not in sample
        ), f"Error: sample {sample} has already been assigned a task."
        sample["source"]["decoder_sequence"] = None
        sample["target"]["decoder_sequence"] = None
        sample["label"] = {"label_sequence": None}

        return sample

    # model sensitive
    def _convert_sample_to_feature(self, sample):
        """
        convert universal samples to model specific features,
        add specail tokens (bos, eos, task prefix, language token, etc.).

        Must add 'sample_length' to sample dict to be used by dynamic batching

        input sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens) or None
                       'language': (str)},
         'target'   : {'sequence': (str) or None
                       'encoder_sequence': (list of tokens) or None
                       'decoder_sequence': (list of tokens) or None
                       'language': (str)} or None,
         'label'    : {'label_sequence': ((dict of) list of label tokens) or None},
         'task_name': <task_name>,
         'cid'      : cid
        }

        return sample
        {'source'   : {'sequence': (str)
                       'encoder_sequence': (list of tokens)
                       'decoder_sequence': (list of tokens) or None
                       'language': (str)},
         'target'   : {'sequence': (str) or None
                       'encoder_sequence': (list of tokens) or None
                       'decoder_sequence': (list of tokens) or None
                       'language': (str)} or None,
         'label'    : {'label_sequence': ((dict of) list of label tokens) or None},
         'task_name': <task_name>,
         'cid'      : cid,
         <Add any model specific input features derived from the sample>
         'sample_length'       : (int)
        }
        """
        raise NotImplementedError(
            "Model specific data loaders need to implement this model sensitive transform."
        )
        return sample

    def _dynamic_batch_size(self, sample):
        batch_size = self.opt["MAX_TOKENS_BATCH"] // sample["sample_length"]
        # Force batches to always be multiples of 8
        # This is necessary to enable usage of Nvidia Tensor cores
        batch_size = (batch_size // 8) * 8
        return max(1, batch_size)

    # model sensitive
    def _collate(self, batch):
        """
        Collate a list of samples into one or more batches in a list

        input
        a list of samples: [<sample_0>, <sample_1>, <sample_2>, <sample_3>, ... ]

        return
        a list of one or more batches: [<batch_0>, <batch_1>, ...]
        Each batch is a collated batch of samples that can be given to the model as an input,
        usually containing encoder/decoder input tensors, label tensor, etc..
        """
        raise NotImplementedError(
            "Model specific data loaders need to implement this model sensitive transform."
        )
        return ret_batches  # noqa: F821
