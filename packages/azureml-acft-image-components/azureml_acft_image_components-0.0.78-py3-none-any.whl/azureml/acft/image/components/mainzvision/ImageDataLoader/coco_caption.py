# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os

import torch
from PIL import Image


class COCOCaptionDataset(torch.utils.data.Dataset):
    def __init__(
        self,
        root,
        caption_file,
        split,
        transform,
        tokenizer,
        context_length=77,
        num_of_captions=5,
        use_vision_benchmark=False,
    ):
        # self.img_labels = pd.read_csv(annotations_file)
        self.use_vision_benchmark = use_vision_benchmark
        if not self.use_vision_benchmark:
            self.img_dir = os.path.join(root, split)
            self.imgs = list(os.listdir(self.img_dir))

            with open(os.path.join(root, caption_file), "r") as file:
                captions = file.read().splitlines()
            self.captions = {}
            for caption in captions:
                imgid, _, sentence = caption.split("\t")
                if imgid not in self.captions:
                    self.captions[imgid] = []
                if len(self.captions[imgid]) < num_of_captions:
                    self.captions[imgid].append(sentence)

        else:
            self.num_of_captions = num_of_captions
            # vision-benchmark version
            # from torchvision import transforms
            # from PIL import Image
            from vision_datasets import Usages
            # from vision_benchmark.common.constants import get_dataset_hub
            from vision_benchmark.common.constants import (
                get_dataset_hub,
                VISION_DATASET_STORAGE,
            )

            hub = get_dataset_hub()

            download_dir = "DATASET"
            dataset_info = hub.dataset_registry.get_dataset_info(root)
            assert dataset_info, "Dataset not exist."
            self.test_set = hub.create_manifest_dataset(
                VISION_DATASET_STORAGE, download_dir, root, usage=Usages.TEST_PURPOSE
            )

        self.transform = transform
        self.tokenizer = tokenizer
        self.context_length = context_length

    def __len__(self):
        if not self.use_vision_benchmark:
            return len(self.imgs)
        else:
            return len(self.test_set)

    def __getitem__(self, idx):
        if not self.use_vision_benchmark:
            img_path = os.path.join(self.img_dir, self.imgs[idx])
            image = self.pil_loader(img_path)
            if self.transform:
                image = self.transform(image)

            captions = self.captions[self.imgs[idx].split(".")[0]]
            tokens = self.tokenizer(
                captions,
                padding="max_length",
                truncation=True,
                max_length=self.context_length,
                return_tensors="pt",
            )

            tokens["input_ids"].squeeze_()
            tokens["attention_mask"].squeeze_()
        else:
            data = self.test_set[idx]
            # (<PIL.Image.Image image mode=RGB size=480x640 at 0x7F59C70B1880>,
            # ['A row of seats on the plane is empty.'], '0')
            image, captions, _ = data
            if self.transform:
                image = self.transform(image)

            captions = captions[: self.num_of_captions]
            tokens = self.tokenizer(
                captions,
                padding="max_length",
                truncation=True,
                max_length=self.context_length,
                return_tensors="pt",
            )

            tokens["input_ids"].squeeze_()
            tokens["attention_mask"].squeeze_()

        return image, tokens

    def pil_loader(self, path: str):
        # open path as file to avoid ResourceWarning (https://github.com/python-pillow/Pillow/issues/835)
        with open(path, "rb") as f:
            img = Image.open(f)
            return img.convert("RGB")
