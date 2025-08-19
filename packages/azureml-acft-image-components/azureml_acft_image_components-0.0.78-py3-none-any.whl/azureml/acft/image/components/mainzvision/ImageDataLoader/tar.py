# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import re
import tarfile

from PIL import Image
import torch
import torch.utils.data as data


IMG_EXTENSIONS = [".png", ".jpg", ".jpeg"]


def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r"(\d+)", string_.lower())]


def _extract_tar_info(tarfile):
    class_to_idx = {}
    files = []
    labels = []
    for ti in tarfile.getmembers():
        if not ti.isfile():
            continue
        dirname, basename = os.path.split(ti.path)
        label = os.path.basename(dirname)
        class_to_idx[label] = None
        ext = os.path.splitext(basename)[1]
        if ext.lower() in IMG_EXTENSIONS:
            files.append(ti)
            labels.append(label)
    for idx, c in enumerate(sorted(class_to_idx.keys(), key=natural_key)):
        class_to_idx[c] = idx
    tarinfo_and_targets = zip(files, [class_to_idx[la] for la in labels])
    tarinfo_and_targets = sorted(
        tarinfo_and_targets, key=lambda k: natural_key(k[0].path)
    )
    return tarinfo_and_targets


class TarDataset(data.Dataset):

    def __init__(self, root, load_bytes=False, transform=None):

        assert os.path.isfile(root)
        self.root = root
        with tarfile.open(
            root
        ) as tf:  # cannot keep this open across processes, reopen later
            self.imgs = _extract_tar_info(tf)
        self.tarfile = None  # lazy init in __getitem__
        self.load_bytes = load_bytes
        self.transform = transform

    def __getitem__(self, index):
        if self.tarfile is None:
            self.tarfile = tarfile.open(self.root)
        tarinfo, target = self.imgs[index]
        iob = self.tarfile.extractfile(tarinfo)
        img = iob.read() if self.load_bytes else Image.open(iob).convert("RGB")
        if self.transform is not None:
            img = self.transform(img)
        if target is None:
            target = torch.zeros(1).long()
        return img, target

    def __len__(self):
        return len(self.imgs)
