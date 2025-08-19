# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import numpy as np

from .MaskingUtils import TextInfilling

logger = logging.getLogger(__name__)


class WordNoising(object):
    """Generate a noisy version of a sentence, without changing words themselves."""

    def __init__(self, tokenizer, bpe_cont_marker=None, bpe_end_marker=None):
        self.tokenizer = tokenizer
        self.special_symbols = self.tokenizer.all_special_ids
        self.pad_idx = self.tokenizer.pad_token_id
        self.bos_idx = self.tokenizer.bos_token_id
        self.eos_idx = self.tokenizer.eos_token_id

        self.bpe_start, self.bpe_end = None, None
        if bpe_cont_marker and bpe_cont_marker == "sentencepiece":
            self.bpe_start = np.array(
                [
                    self.tokenizer.convert_ids_to_tokens(i).startswith("\u2581")
                    or i in self.special_symbols
                    for i in range(len(self.tokenizer))
                ]
            )
        elif bpe_cont_marker:
            self.bpe_end = np.array(
                [
                    not self.tokenizer.convert_ids_to_tokens(i).endswith(
                        bpe_cont_marker
                    )
                    for i in range(len(self.tokenizer))
                ]
            )
        elif bpe_end_marker:
            self.bpe_end = np.array(
                [
                    self.tokenizer.convert_ids_to_tokens(i).endswith(bpe_end_marker)
                    for i in range(len(self.tokenizer))
                ]
            )

        if self.bpe_start is not None:
            self.get_word_idx = self._get_spm_word_idx
        elif self.bpe_end is not None:
            self.get_word_idx = self._get_bpe_word_idx
        else:
            self.get_word_idx = self._get_token_idx

    def noising(self, x, np_random_state, noising_prob=0.0):
        raise NotImplementedError()

    def _get_spm_word_idx(self, x):
        """
        return:
            word_idx: [0, 1, 1, 1, 2, 2, 3]
            word_start_idx: {0: 0, 1: 1, 2: 4, 3: 6, 4: 7}
        """
        bpe_start = np.array(self.bpe_start[x])

        if len(x) == 1:
            return np.array([0]), {0: 0, 1: 1}

        word_idx = bpe_start.cumsum(0) - 1
        if min(word_idx) < 0:
            # logger.warning(f"[WARNING] no spm start in sample:
            # {self.tokenizer.convert_ids_to_tokens(x)}, word_idx = {word_idx}")
            word_idx += 1

        start_pos = np.argwhere(bpe_start).squeeze(1)
        word_start_idx = {i: start_pos[i] for i in range(len(start_pos))}
        word_start_idx[len(start_pos)] = len(x)

        return word_idx, word_start_idx

    def _get_bpe_word_idx(self, x):
        """
        return:
            word_idx: [0, 1, 1, 1, 2, 2, 3]
            word_start_idx: {0: 0, 1: 1, 2: 4, 3: 6, 4: 7}
        """
        bpe_end = np.array(self.bpe_end[x])

        if len(x) == 1:
            return np.array([0]), {0: 0}

        end_pos = np.argwhere(bpe_end).squeeze()
        word_start_idx = {i + 1: end_pos[i] + 1 for i in range(len(end_pos) - 1)}
        word_start_idx[0] = 0
        word_start_idx[len(end_pos)] = len(x)

        # do a reduce front sum to generate word ids
        word_idx = bpe_end[::-1].cumsum(0)[::-1]
        word_idx = word_idx.max(0) - word_idx
        return word_idx, word_start_idx

    def _get_token_idx(self, x):
        return np.array(range(len(x))), None


class WordDropout(WordNoising):
    """Randomly drop input words. If not passing blank_idx (default is None),
    then dropped words will be removed. Otherwise, it will be replaced by the
    blank_idx."""

    def __init__(
        self, tokenizer, bpe_cont_marker=None, bpe_end_marker=None, dropout_prob=0.1
    ):
        super().__init__(tokenizer, bpe_cont_marker, bpe_end_marker)
        self.dropout_prob = dropout_prob

    def noising(self, x, np_random_state, dropout_prob=None, blank_idx=None):
        if dropout_prob is None:
            dropout_prob = self.dropout_prob

        if dropout_prob == 0:
            return x, x

        assert 0 < dropout_prob < 1

        # be sure to drop entire words
        word_idx, _ = self.get_word_idx(x)

        # We want to drop whole words based on word_idx grouping
        num_words = max(word_idx) + 1

        # example: [x0, x1, ..., eos, pad, ..., pad]
        # We should only generate keep probs for non-EOS tokens. Thus if the
        # input sentence ends in EOS, the last word idx is not included in
        # the dropout mask generation and we append True to always keep EOS.
        # Otherwise, just generate the dropout mask for all word idx
        # positions.
        has_eos = x[-1] == self.eos_idx
        if has_eos:  # has eos?
            keep = np_random_state.rand(num_words - 1) >= dropout_prob
            keep = np.append(keep, [True])  # keep EOS symbol
        else:
            keep = np_random_state.rand(num_words) >= dropout_prob

        # TODO: speed up the following loop
        # drop words from the input according to keep
        modified_x = [w if keep[word_idx[j]] else blank_idx for j, w in enumerate(x)]
        modified_x = [w for w in modified_x if w is not None]
        # we need to have at least one word in the sentence (more than the
        # start / end sentence symbols)
        if len(modified_x) <= 1:
            # insert at beginning in case the only token left is EOS
            # EOS should be at end of list.
            modified_x.insert(0, x[np_random_state.randint(0, len(x))])
        assert len(modified_x) >= 1 and (
            not has_eos
            or (len(modified_x) >= 2 and modified_x[-1] == self.eos_idx)
            # Either don't have EOS at end or last token is EOS
        ), "New sentence is invalid."

        modified_x = np.array(modified_x)

        return modified_x, x


class WordShuffle(WordNoising):
    """Shuffle words by no more than k positions."""

    def __init__(
        self,
        tokenizer,
        bpe_cont_marker=None,
        bpe_end_marker=None,
        max_shuffle_distance=3,
    ):
        super().__init__(tokenizer, bpe_cont_marker, bpe_end_marker)
        self.max_shuffle_distance = max_shuffle_distance

    def noising(self, x, np_random_state, max_shuffle_distance=None):
        if max_shuffle_distance is None:
            max_shuffle_distance = self.max_shuffle_distance

        if max_shuffle_distance == 0:
            return x, x

        # max_shuffle_distance < 1 will return the same sequence
        assert max_shuffle_distance > 1

        # define noise word scores
        noise = np_random_state.uniform(
            0,
            max_shuffle_distance,
            size=x.shape,
        )
        noise[0] = -1  # do not move start sentence symbol
        # be sure to shuffle entire words
        word_idx, _ = self.get_word_idx(x)
        modified_x = np.copy(x)
        length_no_eos = (len(x) - 1) if (x[-1] == self.eos_idx) else len(x)
        # generate a random permutation
        scores = word_idx[:length_no_eos] + noise[word_idx[:length_no_eos]]
        # ensure no reordering inside a word
        scores += 1e-6 * np.arange(length_no_eos)
        permutation = scores.argsort()
        # shuffle words
        modified_x[:length_no_eos] = modified_x[:length_no_eos][permutation]

        return modified_x, x


class DaeNoising(WordNoising):
    def __init__(
        self,
        tokenizer,
        mask_idx,
        bpe_cont_marker=None,
        bpe_end_marker=None,
        dropout_prob=0.1,
        blanking_prob=0.1,
        max_shuffle_distance=3,
        text_infilling_ratio=0.3,
        text_infilling_lambda=3,
    ):
        super().__init__(tokenizer, bpe_cont_marker, bpe_end_marker)
        self.mask_idx = mask_idx
        self.dropout_prob = dropout_prob
        self.blanking_prob = blanking_prob
        self.max_shuffle_distance = max_shuffle_distance
        self.text_infilling_ratio = text_infilling_ratio
        self.text_infilling_lambda = text_infilling_lambda

        self.word_dropout = WordDropout(
            tokenizer=self.tokenizer,
            bpe_cont_marker=bpe_cont_marker,
            bpe_end_marker=bpe_end_marker,
            dropout_prob=self.dropout_prob,
        )
        self.word_shuffle = WordShuffle(
            tokenizer=self.tokenizer,
            bpe_cont_marker=bpe_cont_marker,
            bpe_end_marker=bpe_end_marker,
            max_shuffle_distance=self.max_shuffle_distance,
        )
        self.text_infilling = TextInfilling(
            tokenizer=self.tokenizer,
            mask_idx=self.mask_idx,
            bpe_cont_marker=bpe_cont_marker,
            bpe_end_marker=bpe_end_marker,
            masking_ratio=self.text_infilling_ratio,
            span_len_lambda=self.text_infilling_lambda,
        )

    def noising(self, x, np_random_state, **kwargs):
        dropout_prob = kwargs.get("dropout_prob", self.dropout_prob)
        blanking_prob = kwargs.get("blanking_prob", self.blanking_prob)
        max_shuffle_distance = kwargs.get(
            "max_shuffle_distance", self.max_shuffle_distance
        )
        text_infilling_ratio = kwargs.get(
            "text_infilling_ratio", self.text_infilling_ratio
        )
        text_infilling_lambda = kwargs.get(
            "text_infilling_lambda", self.text_infilling_lambda
        )

        # Word Shuffle
        modified_x, _ = self.word_shuffle.noising(
            x,
            np_random_state,
            max_shuffle_distance=max_shuffle_distance,
        )

        # Text Infilling
        modified_x, _ = self.text_infilling.masking(
            modified_x,
            np_random_state,
            masking_ratio=text_infilling_ratio,
            span_len_lambda=text_infilling_lambda,
        )

        # Word Dropout
        modified_x, _ = self.word_dropout.noising(
            modified_x,
            np_random_state,
            dropout_prob=dropout_prob,
        )

        # Word Blanking (equiv to masking, no replacing yet)
        modified_x, _ = self.word_dropout.noising(
            modified_x,
            np_random_state,
            dropout_prob=blanking_prob,
            blank_idx=self.mask_idx,
        )

        return modified_x, x
