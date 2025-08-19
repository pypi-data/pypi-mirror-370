# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from PIL import Image
import numpy as np
import torch
import torch.utils.data as data


class SyntheticDataset(data.Dataset):

    def __init__(self, root, input_size, transform=None):
        self.transform = transform
        self.size = input_size
        self.num_samples = 1000000 if "train" in root else 100

    def __getitem__(self, index):
        # img = np.zeros((3, self.size[1], self.size[0]))
        img = Image.fromarray(
            np.zeros(
                (int(self.size[1] * 1.25), int(self.size[0] * 1.25), 3), dtype=np.uint8
            ),
            "RGB",
        )
        if self.transform:
            img = self.transform(img)
        target = 1
        return img, target

    def __len__(self):
        return self.num_samples


class SyntheticPairDataset(data.Dataset):

    def __init__(
        self, root, input_size, context_length=77, vocab_size=49408, transform=None
    ):
        self.transform = transform
        self.size = input_size
        self.context_length = context_length
        self.vocab_size = vocab_size
        self.num_samples = 100000000

    def __getitem__(self, index):
        # img = np.zeros((3, self.size[1], self.size[0]))
        img = Image.fromarray(
            np.zeros(
                (int(self.size[1] * 1.25), int(self.size[0] * 1.25), 3), dtype=np.uint8
            ),
            "RGB",
        )
        if self.transform:
            img = self.transform(img)

        txt = {}
        txt["input_ids"] = torch.randint(
            0, self.vocab_size, (1, self.context_length), dtype=torch.long
        )
        txt["input_ids"].squeeze_()
        txt["attention_mask"] = torch.ones(txt["input_ids"].size())

        return img, txt

    def __len__(self):
        return self.num_samples


class SyntheticPairDatasetV2(data.Dataset):

    def __init__(
        self, root, input_size, context_length=77, vocab_size=49408, transform=None
    ):
        self.transform = transform
        self.size = input_size
        self.context_length = context_length
        self.vocab_size = vocab_size
        self.num_samples = 100000000

    def __getitem__(self, index):
        # img = np.zeros((3, self.size[1], self.size[0]))
        img = Image.fromarray(
            np.zeros(
                (int(self.size[1] * 1.25), int(self.size[0] * 1.25), 3), dtype=np.uint8
            ),
            "RGB",
        )
        if self.transform:
            img = self.transform(img)

        txt = {}
        txt["input_ids"] = torch.randint(
            1, self.vocab_size - 2, (1, self.context_length), dtype=torch.long
        )
        txt["input_ids"].squeeze_()
        txt["input_ids"][-2] = self.vocab_size - 1
        txt["input_ids"][0] = 0

        txt["attention_mask"] = torch.ones(txt["input_ids"].size())

        target = 1

        return img, txt, target

    def __len__(self):
        return self.num_samples
