# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import os.path as osp

from PIL import Image
import torch.utils.data as data

logger = logging.getLogger(__name__)


def _get_square_bbox_lurl(bbox, scale=1.0):
    w, h = bbox[2] * scale, bbox[3] * scale
    center = (bbox[0] + w // 2, bbox[1] + h // 2)
    if w > h:
        h = w
    else:
        w = h

    left_upper_right_lower = (
        center[0] - w // 2,
        center[1] - h // 2,
        center[0] + w // 2,
        center[1] + h // 2,
    )

    return left_upper_right_lower


class COCOClassificationDataset(data.Dataset):

    def __init__(self, root, dataset, scales, balance_data, transform=None):
        # super(COCOClassificationDataset, self).__init__(dataset, transform)

        assert dataset in ["train2017", "val2017"]
        self.dataset = dataset
        self.transform = transform
        self.root = root

        assert "s" in scales or "m" in scales or "l" in scales
        self.scales = scales

        self.data_root = osp.join(root, dataset)
        ann_file = osp.join(root, "annotations", "instances_" + dataset + ".json")
        self.instances = self.loadInstances(ann_file, balance_data)
        logger.info("=> {}\titems: {}".format(dataset, len(self.instances)))

    def __getitem__(self, index):
        path, bbox, target = self.instances[index]
        img = Image.open(path).convert("RGB")
        left_upper_right_lower = _get_square_bbox_lurl(bbox, 1.25)

        left_upper_right_lower = (
            max(0, left_upper_right_lower[0]),
            max(0, left_upper_right_lower[1]),
            min(img.width, left_upper_right_lower[2]),
            min(img.height, left_upper_right_lower[3]),
        )
        img_cropped = img.crop(left_upper_right_lower).copy()

        if self.transform:
            img_cropped = self.transform(img_cropped)

        return img_cropped, target

    def __len__(self):
        return len(self.instances)

    def _get_area(self, area):
        if area < 32.0 * 32.0:
            return "s"
        elif area < 96.0 * 96:
            return "m"
        else:
            return "l"

    def loadInstances(self, ann_file, balance_data):
        from pycocotools.coco import COCO

        coco = COCO(ann_file)
        cat_ids = list(coco.getCatIds())
        cat2cat = {}

        cat_count = {}
        cat_ann_ids = {}
        max_count = 0
        for idx, cat_id in enumerate(cat_ids):
            cat2cat[cat_id] = idx
            ann_ids = coco.getAnnIds(catIds=cat_id, iscrowd=False)
            cat_ann_ids[cat_id] = ann_ids

            count = len(ann_ids)
            if count > max_count:
                max_count = count
            cat_count[cat_id] = count

        instances = []
        for idx, cat_id in enumerate(cat_ids):
            count = cat_count[cat_id]
            num_duplacate = max_count // count if balance_data else 1

            anns = coco.loadAnns(cat_ann_ids[cat_id])
            for ann in anns:
                if "bbox" in ann:
                    if self._get_area(ann["area"]) not in self.scales:
                        continue
                    bbox = ann["bbox"]

                    valid = bbox[0] > 0 and bbox[1] > 0 and bbox[2] > 0 and bbox[3] > 0
                    path = coco.loadImgs(ann["image_id"])[0]["file_name"]
                    full_path = osp.join(self.data_root, path)
                    if valid:
                        for i in range(num_duplacate):
                            instances.append(
                                (full_path, bbox, cat2cat[ann["category_id"]])
                            )

        return instances
