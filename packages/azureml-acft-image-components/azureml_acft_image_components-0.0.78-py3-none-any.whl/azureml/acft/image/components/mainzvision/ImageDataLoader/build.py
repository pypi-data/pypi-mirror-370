# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import os
import json
import pathlib
from os.path import basename

from timm.data import create_loader
import torch
import torch.utils.data
import torch.distributed as dist
import torchvision.datasets as datasets

# from torchvision.io import read_image
# import torch.distributed as dist
from pathlib import Path
from yacs.config import CfgNode as CN

from .coco import COCOClassificationDataset
from ..Networks.LangEncoder import build_tokenizer
from .inat import INatDataset
from .multitask import MultiTaskSampler, MultiTaskDataloader
from .samplers import build_sampler
from .synthetic import SyntheticDataset
from .synthetic import SyntheticPairDataset
from .synthetic import SyntheticPairDatasetV2
from .tar import TarDataset
from .tsv import TSVDataset
from .tsv import TSVImageTextDataset
from .tsv import TSVImageTextDatasetV2
from .tsv import TSVMeta
from .transforms import build_transforms
from .coco_caption import COCOCaptionDataset

logger = logging.getLogger(__name__)


def build_dataset(cfg, is_train):
    if "vision-datasets-ic" == cfg["DATASET"].get("DATA_FORMAT"):
        from vision_datasets import DatasetHub, Usages

        dataset_hub = DatasetHub(
            pathlib.Path(cfg["DATASET"]["DATA_REG_JSON_PATH"]).read_text()
        )
        usages = (
            [Usages.TRAIN_PURPOSE, Usages.VAL_PURPOSE]
            if is_train
            else Usages.TEST_PURPOSE
        )

        manifest_dataset = dataset_hub.create_manifest_dataset(
            container_sas=cfg["DATASET"]["BLOB_CONTAINER"],
            local_dir=cfg["DATASET"]["ROOT"],
            name=cfg["DATASET"]["DATASET"],
            usage=usages,
        )
        transforms = build_transforms(cfg, is_train)
        from .vision_dataset import MultiClassTorchDatasetWrapper

        dataset = MultiClassTorchDatasetWrapper(manifest_dataset, transforms)

        total_batch_size = cfg["TRAIN"]["BATCH_SIZE_TOTAL"]

        if is_train and len(dataset) < total_batch_size * 1.5:
            logger.info(
                f"""Dataset is smaller than batch size {total_batch_size} x 1.5, which will fail training.
                Spawn from {len(dataset)} to {total_batch_size * 4} images."""
            )
            dataset.spawn(total_batch_size * 4)
    elif "coco" == cfg["DATASET"]["DATASET"]:
        dataset = _build_coco_dataset(cfg, is_train)
    elif "imagenet" in cfg["DATASET"]["DATASET"]:
        dataset = _build_imagenet_dataset(cfg, is_train)
    elif "visdataset" == cfg["DATASET"]["DATASET"]:
        dataset = _build_vis_dataset(cfg, is_train)
    elif "cifar-100" == cfg["DATASET"]["DATASET"]:
        dataset = _build_cifar100(cfg, is_train)
    elif "cifar-10" == cfg["DATASET"]["DATASET"]:
        dataset = _build_cifar10(cfg, is_train)
    elif cfg["DATASET"]["DATASET"] in ["cars", "pet37", "flower102"]:
        dataset = _build_image_folder_dataset(cfg, is_train)
    elif cfg["DATASET"]["DATASET"] in ["inat18", "inat19"]:
        dataset = _build_inat_dataset(cfg, is_train)
    elif cfg["DATASET"]["DATASET"] == "image_text_pairs":
        dataset = _build_pairs_dataset(cfg, is_train)
    elif cfg["DATASET"]["DATASET"] == "image_text_pairs_v2":
        if cfg.get("MULTITASK_DATALOADER", None) is not None and is_train:
            dataset = _build_multitask_pairs_dataset_v2(cfg, is_train)
        else:
            dataset = _build_pairs_dataset_v2(cfg, is_train)
    else:
        raise ValueError(f'Unknown dataset: {cfg["DATASET"]["DATASET"]}')
    return dataset


def _build_inat_dataset(cfg, is_train):
    transforms = build_transforms(cfg, is_train)

    year = {"inat18": 2018, "inat19": 2019}

    dataset = INatDataset(
        cfg["DATASET"]["ROOT"],
        year=year[cfg["DATASET"]["DATASET"]],
        train=is_train,
        transform=transforms,
    )

    assert (
        cfg["IMAGE_ENCODER"]["NUM_CLASSES"] == dataset.nb_classes
    ), "numbers of class does not match"

    return dataset


def _build_image_folder_dataset(cfg, is_train):
    transforms = build_transforms(cfg, is_train)

    dataset_name = (
        cfg["DATASET"]["TRAIN_SET"] if is_train else cfg["DATASET"]["TEST_SET"]
    )
    dataset = datasets.ImageFolder(
        os.path.join(cfg["DATASET"]["ROOT"], dataset_name), transforms
    )
    logger.info("=> load samples: {}, is_train: {}".format(len(dataset), is_train))

    return dataset


def _build_cifar10(cfg, is_train):
    transforms = build_transforms(cfg, is_train)
    dataset = datasets.CIFAR10(
        root=cfg["DATASET"]["ROOT"], train=is_train, transform=transforms, download=True
    )
    logger.info("=> load samples: {}, is_train: {}".format(len(dataset), is_train))

    return dataset


def _build_cifar100(cfg, is_train):
    transforms = build_transforms(cfg, is_train)
    dataset = datasets.CIFAR100(
        root=cfg["DATASET"]["ROOT"], train=is_train, transform=transforms, download=True
    )

    logger.info("=> load samples: {}, is_train: {}".format(len(dataset), is_train))

    return dataset


def _build_imagenet_dataset(cfg, is_train):
    transforms = build_transforms(cfg, is_train)

    dataset_name = (
        cfg["DATASET"]["TRAIN_SET"] if is_train else cfg["DATASET"]["TEST_SET"]
    )
    if cfg["DATASET"]["DATA_FORMAT"] == "synthetic":
        dataset = SyntheticDataset(
            os.path.join(cfg["DATASET"]["ROOT"], dataset_name + ".tar"),
            input_size=cfg["IMAGE_ENCODER"]["IMAGE_SIZE"],
            transform=transforms,
        )
    elif cfg["DATASET"]["DATA_FORMAT"] == "tar":
        dataset = TarDataset(
            os.path.join(cfg["DATASET"]["ROOT"], dataset_name + ".tar"),
            transform=transforms,
        )
    elif cfg["DATASET"]["DATA_FORMAT"] == "zip":
        if is_train:
            datapath = os.path.join(cfg["DATASET"]["ROOT"], "train.zip")
            data_map = os.path.join(cfg["DATASET"]["ROOT"], "train_map.txt")
        else:
            datapath = os.path.join(cfg["DATASET"]["ROOT"], "val.zip")
            data_map = os.path.join(cfg["DATASET"]["ROOT"], "val_map.txt")
        from .zipdata import ZipData

        dataset = ZipData(datapath, data_map, transforms)
    elif cfg["DATASET"]["DATA_FORMAT"] == "tsv":
        if cfg["DATASET"]["DATASET"] == "imagenet22k":
            map_file = os.path.join(cfg["DATASET"]["ROOT"], "labelmap_22k_reorder.txt")
        else:
            map_file = None
        dataset = TSVDataset(
            os.path.join(cfg["DATASET"]["ROOT"], dataset_name + ".tsv"),
            transform=transforms,
            map_file=map_file,
        )
    else:
        dataset = datasets.ImageFolder(
            os.path.join(cfg["DATASET"]["ROOT"], dataset_name), transforms
        )

    return dataset


def _build_vis_dataset(cfg, is_train):
    transforms = build_transforms(cfg, is_train)

    dataset_name = (
        cfg["DATASET"]["TRAIN_SET"] if is_train else cfg["DATASET"]["TEST_SET"]
    )
    if cfg["DATASET"]["DATA_FORMAT"] == "tsv":
        if cfg["DATASET"]["LABELMAP"] != "":
            map_file = os.path.join(cfg["DATASET"]["ROOT"], cfg["DATASET"]["LABELMAP"])
        elif cfg["DATASET"]["DATASET"] == "imagenet22k":
            map_file = os.path.join(cfg["DATASET"]["ROOT"], "labelmap_22k_reorder.txt")
        else:
            map_file = None

        if os.path.isfile(os.path.join(cfg["DATASET"]["ROOT"], dataset_name + ".tsv")):
            tsv_path = os.path.join(cfg["DATASET"]["ROOT"], dataset_name + ".tsv")
        elif os.path.isdir(os.path.join(cfg["DATASET"]["ROOT"], dataset_name)):
            tsv_list = (
                cfg["DATASET"].get("TRAIN_TSV_LIST", "")
                if is_train
                else cfg["DATASET"].get("TEST_TSV_LIST", "")
            )
            if len(tsv_list) > 0:
                tsv_path = [
                    os.path.join(cfg["DATASET"]["ROOT"], dataset_name, f)
                    for f in tsv_list
                ]
            else:
                data_path = os.path.join(cfg["DATASET"]["ROOT"], dataset_name)
                tsv_path = [str(path) for path in Path(data_path).glob("*.tsv")]
            logger.info(f"=> Found {len(tsv_path)} tsv file(s) to load.")
        else:
            raise ValueError(f"Invalid TSVDataset format: {cfg['DATASET']['DATASET']}")

        sas_token_file = _get_token_file(cfg)
        logger.info(f"=> SAS token path: {sas_token_file}")

        dataset = TSVDataset(
            tsv_path,
            is_train=is_train,
            transform=transforms,
            map_file=map_file,
            token_file=sas_token_file,
            azcopy_path=cfg["DATASET"].get("AZCOPY_PATH", None),
        )
    else:
        dataset = datasets.ImageFolder(
            os.path.join(cfg["DATASET"]["ROOT"], dataset_name), transforms
        )

    logger.info("{} set size: {}".format("train" if is_train else "val", len(dataset)))

    return dataset


def _build_coco_dataset(cfg, is_train):
    transforms = build_transforms(cfg, is_train)
    logger.info("transforms: {}".format(transforms))

    dataset_name = (
        cfg["DATASET"]["TRAIN_SET"] if is_train else cfg["DATASET"]["TEST_SET"]
    )
    balance_data = True if is_train else False
    if cfg["DATASET"]["DATASET"] == "coco":
        dataset = COCOClassificationDataset(
            cfg["DATASET"]["ROOT"],
            dataset_name,
            cfg["DATASET"]["COCO.SCALES"],
            balance_data,
            transforms,
        )

    return dataset


def _get_tsv_list(cfg, is_train):
    tmp_list = []
    if is_train and "TRAIN_TSV_LIST" in cfg["DATASET"]:
        tmp_list = cfg["DATASET"]["TRAIN_TSV_LIST"]
    elif "TEST_TSV_LIST" in cfg["DATASET"]:
        tmp_list = cfg["DATASET"]["TEST_TSV_LIST"]

    tsv_list = []
    for la in tmp_list:
        if la.endswith(".list"):
            with open(la, "r") as f:
                tsv_list.extend([i.strip() for i in f])
        else:
            tsv_list.append(la)

    logger.info(f"tsv list: {tsv_list}")

    return tsv_list


def _get_multitask_tsv_list(cfg, is_train):
    tmp_list = []
    if is_train and "TRAIN_TSV_LIST" in cfg["DATASET"]:
        tmp_list = cfg["DATASET"]["TRAIN_TSV_LIST"]
    elif "TEST_TSV_LIST" in cfg["DATASET"]:
        tmp_list = cfg["DATASET"]["TEST_TSV_LIST"]

    tsv_list = {}
    for la in tmp_list:
        if isinstance(la, str):
            if la not in tsv_list:
                tsv_list[la] = []
            if la.endswith(".list"):
                with open(la, "r") as f:
                    tsv_list[la].extend([i.strip() for i in f])
            else:
                tsv_list[la].append(la)
        else:  # a list of tsv files, e.g., image and text tsv pair
            assert isinstance(la, list), f"Unknown tsv list format: {la}"
            k = ",".join(la)
            if k not in tsv_list:
                tsv_list[k] = []
            for t in la:
                if t.endswith(".list"):
                    with open(t, "r") as f:
                        tsv_list[k].extend([i.strip() for i in f])
                else:
                    tsv_list[k].append(t)

    logger.info(f"tsv list: {tsv_list}")

    return tsv_list


def _get_token_file(cfg):
    num_nodes = dist.get_world_size() // torch.cuda.device_count()
    if isinstance(cfg["DATASET"]["TOKEN_FILE"], list):
        if num_nodes == 1:
            logger.warning(
                "=> Multi token files are provided, but only one node is used for training"
            )
            sas_token_file = cfg["DATASET"]["TOKEN_FILE"][0]
        else:
            rank = dist.get_rank()
            node_idx = rank // torch.cuda.device_count()
            num_token_files = len(cfg["DATASET"]["TOKEN_FILE"])
            sas_token_file = cfg["DATASET"]["TOKEN_FILE"][node_idx % num_token_files]
    else:
        sas_token_file = cfg["DATASET"]["TOKEN_FILE"]

    sas_token_file = os.path.join(cfg["DATASET"]["ROOT"], sas_token_file)

    if cfg["DATASET"]["LOADER"] == "blobfuse" or not os.path.isfile(sas_token_file):
        sas_token_file = None

    return sas_token_file


def _build_pairs_dataset(cfg, is_train):
    transforms = build_transforms(cfg, is_train)
    logger.info("transforms: {}".format(transforms))

    dataset_name = (
        cfg["DATASET"]["TRAIN_SET"] if is_train else cfg["DATASET"]["TEST_SET"]
    )

    if cfg["DATASET"]["DATA_FORMAT"] == "synthetic":
        dataset = SyntheticPairDataset(
            None, cfg["IMAGE_ENCODER"]["IMAGE_SIZE"], 77, transform=transforms
        )
    elif cfg["DATASET"]["DATA_FORMAT"] == "tsv":
        tsv_list = _get_tsv_list(cfg, is_train)

        if len(tsv_list) > 0:
            tsv_filenames = sorted(
                [
                    os.path.join(cfg["DATASET"]["ROOT"], dataset_name, f)
                    for f in tsv_list
                ]
            )
        else:
            dataset_path = os.path.join(cfg["DATASET"]["ROOT"], dataset_name)
            tsv_files = Path(dataset_path).glob("**/*.tsv")

            tsv_filenames = sorted([str(path) for path in tsv_files])

        image_tsv_files = [
            filename
            for filename in tsv_filenames
            if "image-" in basename(filename) or "_image" in basename(filename)
        ]
        text_tsv_files = [
            filename
            for filename in tsv_filenames
            if "text-" in basename(filename) or "_text" in basename(filename)
        ]

        logger.info(
            "=> found %d/%d tsv file(s) to load.",
            len(image_tsv_files),
            len(text_tsv_files),
        )

        tokenobj = build_tokenizer(cfg["LANG_ENCODER"])

        num_captions = 1 if is_train else cfg["DATASET"].get("NUM_CAPTIONS", 1)
        text_format = cfg["DATASET"].get("TEXT_FORMAT", "json")

        sas_token_file = _get_token_file(cfg)
        logger.info("=> SAS token path: %s", sas_token_file)

        if "coco-caption" in dataset_name:
            logger.info("=> coco caption data is used")
            logger.info("=> update num_captions: 5, text_format: json")
            num_captions = 5
            text_format = "json"

        dataset = TSVImageTextDataset(
            image_tsv_files,
            text_tsv_files,
            transform=transforms,
            tokenize=tokenobj,
            context_length=cfg["LANG_ENCODER"]["CONTEXT_LENGTH"],
            num_captions=num_captions,
            text_format=text_format,
            is_train=is_train,
            sas_token_path=sas_token_file,
        )
    else:
        raise ValueError("Unknown format for Image/Text pairs dataset")

    logger.info("=> %s set size: %d", "train" if is_train else "val", len(dataset))

    return dataset


def _build_pairs_dataset_v2(cfg, is_train):
    transforms = build_transforms(cfg, is_train)
    logger.info("transforms: {}".format(transforms))

    dataset_name = (
        cfg["DATASET"]["TRAIN_SET"] if is_train else cfg["DATASET"]["TEST_SET"]
    )

    if cfg["DATASET"]["DATA_FORMAT"] == "synthetic":
        dataset = SyntheticPairDatasetV2(
            None, cfg["IMAGE_ENCODER"]["IMAGE_SIZE"], 77, transform=transforms
        )
        return dataset

    tokenobj = build_tokenizer(cfg["LANG_ENCODER"])
    if cfg["DATASET"]["DATA_FORMAT"] == "vision-datasets":
        from ..ImageDataLoader.vision_dataset import VDImageTextDataset

        logger.info(f"Create vision-datasets {dataset_name}")
        vd_it_data = VDImageTextDataset(
            dataset_name=dataset_name,
            local_dir=cfg["DATASET"]["ROOT"],
            dataset_json=pathlib.Path(cfg["DATASET"]["DATA_REG_JSON_PATH"]).read_text(),
            blob_container=cfg["DATASET"]["BLOB_CONTAINER"],
            is_train=is_train,
            n_few_shot=cfg["DATASET"].get("N_FEW_SHOT"),
            few_shot_rnd_seed=cfg["DATASET"].get("FEW_SHOT_RND_SEED"),
            transform=transforms,
            tokenize=tokenobj,
            context_length=cfg["LANG_ENCODER"]["CONTEXT_LENGTH"],
        )

        total_batch_size = cfg["TRAIN"]["BATCH_SIZE_TOTAL"]
        if len(vd_it_data) < total_batch_size * 1.5:
            logger.info(
                f"""Dataset is smaller than batch size {total_batch_size} x 1.5,
                which will fail training. Spawn from {len(vd_it_data)} to {total_batch_size * 4} images."""
            )
            vd_it_data.spawn(total_batch_size * 4)

        return vd_it_data

    if cfg["DATASET"]["DATA_FORMAT"] != "tsv":
        raise ValueError("Only support tsv format for pairs dataset v2")

    tsv_list = _get_tsv_list(cfg, is_train)

    if len(tsv_list) > 0:
        tsv_filenames = sorted(
            [os.path.join(cfg["DATASET"]["ROOT"], dataset_name, f) for f in tsv_list]
        )
    else:
        dataset_path = os.path.join(cfg["DATASET"]["ROOT"], dataset_name)
        tsv_files = Path(dataset_path).glob("**/*.tsv")

        tsv_filenames = sorted([str(path) for path in tsv_files])

    image_tsv_files = [
        filename
        for filename in tsv_filenames
        if (
            "image-" in basename(filename)
            or "image_" in basename(filename)
            or "_image" in basename(filename)
            or "-image" in basename(filename)
            or "images-" in basename(filename)
        )
    ]
    text_tsv_files = [
        filename
        for filename in tsv_filenames
        if (
            "text-" in basename(filename)
            or "text_" in basename(filename)
            or "_text" in basename(filename)
            or "-text" in basename(filename)
            or "texts-" in basename(filename)
        )
    ]

    logger.info(
        "=> found %d/%d tsv file(s) to load.", len(image_tsv_files), len(text_tsv_files)
    )

    num_captions = 1 if is_train else cfg["DATASET"].get("NUM_CAPTIONS", 1)
    text_format = cfg["DATASET"].get("TEXT_FORMAT", "json")

    sas_token_file = _get_token_file(cfg)
    logger.info("=> SAS token path: %s", sas_token_file)

    metas = []
    cfg_data = cfg["DATASET"]
    if "CLASSIFICATION_SETS" in cfg_data and "NUM_CLASSES" in cfg_data:
        for source, num_classes in zip(
            cfg_data["CLASSIFICATION_SETS"], cfg_data["NUM_CLASSES"]
        ):
            metas.append(
                TSVMeta(source=source, num_classes=num_classes, task="classification")
            )
            logger.info("=> add meta: {}".format(metas[-1]))

    if "coco-caption" in dataset_name:
        logger.info("=> coco caption data is used")
        logger.info("=> update num_captions: 5, text_format: json")
        logger.warning("=> set sas token to None for coco evaluation")
        sas_token_file = None
        num_captions = 5
        text_format = "json"

    dataset = TSVImageTextDatasetV2(
        image_tsv_files,
        text_tsv_files,
        transform=transforms,
        tokenize=tokenobj,
        context_length=cfg["LANG_ENCODER"]["CONTEXT_LENGTH"],
        num_captions=num_captions,
        text_format=text_format,
        is_train=is_train,
        sas_token_path=sas_token_file,
        metas=metas,
        prompt_engineering=cfg["DATASET"].get("PROMPT_ENGINEERING", True),
        concat_queries=cfg["DATASET"].get("CONCAT_QUERIES", False),
        text_augmentation=cfg["DATASET"].get("TEXT_AUGMENTATION", 0),
        cfg_dataset=cfg["DATASET"],
    )

    logger.info("=> %s set size: %d", "train" if is_train else "val", len(dataset))

    return dataset


def _build_multitask_pairs_dataset_v2(cfg, is_train):
    transforms = build_transforms(cfg, is_train)
    logger.info("transforms: {}".format(transforms))

    dataset_name = (
        cfg["DATASET"]["TRAIN_SET"] if is_train else cfg["DATASET"]["TEST_SET"]
    )
    if cfg["DATASET"]["DATA_FORMAT"] == "synthetic":
        dataset = SyntheticPairDatasetV2(
            None, cfg["IMAGE_ENCODER"]["IMAGE_SIZE"], 77, transform=transforms
        )
        return {"synthetic": dataset}
    elif cfg["DATASET"]["DATA_FORMAT"] != "tsv":
        raise ValueError("Only support tsv format for pairs dataset v2")

    tsv_list = _get_multitask_tsv_list(cfg, is_train)

    if len(tsv_list) > 0:
        tsv_filenames = {
            k: sorted(
                [
                    os.path.join(cfg["DATASET"]["ROOT"], dataset_name, f)
                    for f in tsv_list[k]
                ]
            )
            for k in tsv_list
        }
    else:
        dataset_path = os.path.join(cfg["DATASET"]["ROOT"], dataset_name)
        tsv_files = Path(dataset_path).glob("**/*.tsv")

        tsv_filenames = {dataset_name: sorted([str(path) for path in tsv_files])}

    image_tsv_files = {
        k: [
            filename
            for filename in tsv_filenames[k]
            if (
                "image-" in basename(filename)
                or "image_" in basename(filename)
                or "_image" in basename(filename)
                or "-image" in basename(filename)
            )
        ]
        for k in tsv_filenames
    }
    text_tsv_files = {
        k: [
            filename
            for filename in tsv_filenames[k]
            if (
                "text-" in basename(filename)
                or "text_" in basename(filename)
                or "_text" in basename(filename)
                or "-text" in basename(filename)
            )
        ]
        for k in tsv_filenames
    }

    from collections import OrderedDict

    image_tsv_files = OrderedDict(sorted(image_tsv_files.items()))
    text_tsv_files = OrderedDict(sorted(text_tsv_files.items()))

    logger.info(
        f"""=> found
        {[(k, len(v)) for k, v in image_tsv_files.items()]}
        /{[(k, len(v)) for k, v in text_tsv_files.items()]}
        tsv file(s) to load.""",
    )

    tokenobj = build_tokenizer(cfg["LANG_ENCODER"])

    num_captions = 1 if is_train else cfg["DATASET"].get("NUM_CAPTIONS", 1)
    text_format = cfg["DATASET"].get("TEXT_FORMAT", "json")

    sas_token_file = _get_token_file(cfg)
    logger.info("=> SAS token path: %s", sas_token_file)

    metas = []
    cfg_data = cfg["DATASET"]
    if "CLASSIFICATION_SETS" in cfg_data and "NUM_CLASSES" in cfg_data:
        for source, num_classes in zip(
            cfg_data["CLASSIFICATION_SETS"], cfg_data["NUM_CLASSES"]
        ):
            metas.append(
                TSVMeta(source=source, num_classes=num_classes, task="classification")
            )
            logger.info("=> add meta: {}".format(metas[-1]))

    if "coco-caption" in dataset_name:
        logger.info("=> coco caption data is used")
        logger.info("=> update num_captions: 5, text_format: json")
        logger.warning("=> set sas token to None for coco evaluation")
        sas_token_file = None
        num_captions = 5
        text_format = "json"

    dataset = {
        k: TSVImageTextDatasetV2(
            image_tsv_files[k],
            text_tsv_files[k],
            transform=transforms,
            tokenize=tokenobj,
            context_length=cfg["LANG_ENCODER"]["CONTEXT_LENGTH"],
            num_captions=num_captions,
            text_format=text_format,
            is_train=is_train,
            sas_token_path=sas_token_file,
            metas=metas,
        )
        for k in image_tsv_files
    }

    logger.info(
        f"=> {'train' if is_train else 'val'} set size: {[(k, len(v)) for k, v in dataset.items()]}"
    )

    logger.info("=> Barrier for dataset init for all processes...")
    dist.barrier()
    logger.info("=> All processes are synced.")


def _load_spec_jsons(data_spec_files):
    dataset_spec = None
    if isinstance(data_spec_files, list):
        dataset_spec = {
            "total_chunks": 0,
            "examples_per_chunk": 1000,
            "data_sources": [],
        }

        for data_spec_file in data_spec_files:
            _spec = json.load(open(data_spec_file, "r"))
            dataset_spec["total_chunks"] += _spec["total_chunks"]
            assert (
                dataset_spec["examples_per_chunk"] == _spec["examples_per_chunk"]
            ), f"examples_per_chunk should be 1000 ({data_spec_file})"
            dataset_spec["data_sources"] += _spec["data_sources"]
    else:
        dataset_spec = json.load(open(data_spec_files, "r"))

    logger.debug(f"data spec: {dataset_spec}")

    return dataset_spec


def build_dataloader(cfg, is_train=True, distributed=False):
    dataset = build_dataset(cfg, is_train)

    if is_train and "TIMM_AUG" in cfg["AUG"] and cfg["AUG"]["TIMM_AUG"]["USE_LOADER"]:
        logger.info("=> use timm loader for training")
        timm_cfg = CN(init_dict=cfg["AUG"]["TIMM_AUG"])
        data_loader = create_loader(
            dataset,
            input_size=cfg["IMAGE_ENCODER"]["IMAGE_SIZE"][0],
            batch_size=cfg["TRAIN"]["BATCH_SIZE_PER_GPU"],
            is_training=True,
            use_prefetcher=True,
            no_aug=False,
            re_prob=timm_cfg.RE_PROB,
            re_mode=timm_cfg.RE_MODE,
            re_count=timm_cfg.RE_COUNT,
            re_split=timm_cfg.RE_SPLIT,
            scale=cfg["AUG"]["SCALE"],
            ratio=cfg["AUG"]["RATIO"],
            hflip=timm_cfg.HFLIP,
            vflip=timm_cfg.VFLIP,
            color_jitter=timm_cfg.COLOR_JITTER,
            auto_augment=timm_cfg.AUTO_AUGMENT,
            num_aug_splits=0,
            interpolation=cfg["AUG"]["INTERPOLATION"],
            mean=cfg["IMAGE_ENCODER"]["IMAGE_MEAN"],
            std=cfg["IMAGE_ENCODER"]["IMAGE_STD"],
            num_workers=cfg["WORKERS"],
            distributed=distributed,
            collate_fn=None,
            pin_memory=cfg["PIN_MEMORY"],
            use_multi_epochs_loader=True,
        )
    else:
        if is_train:
            batch_size_per_gpu = cfg["TRAIN"]["BATCH_SIZE_PER_GPU"]
            shuffle = cfg["TRAIN"].get("SHUFFLE", True)
        else:
            batch_size_per_gpu = cfg["TEST"]["BATCH_SIZE_PER_GPU"]
            shuffle = cfg["TEST"].get("SHUFFLE", False)

        if distributed or cfg.get("ALWAYS_ENABLE_SAMPLER", False):
            sampler = build_sampler(cfg, dataset, is_train, shuffle)
            shuffle = False
        else:
            sampler = None

        data_loader = torch.utils.data.DataLoader(
            dataset,
            batch_size=batch_size_per_gpu,
            shuffle=shuffle,
            num_workers=cfg["WORKERS"],
            pin_memory=cfg["PIN_MEMORY"],
            sampler=sampler,
            drop_last=True if is_train else False,
            prefetch_factor=cfg.get("PREFETCH_FACTOR", 2),
        )

    return data_loader


def build_multitask_dataloader(cfg, is_train=True, distributed=False):
    dataset = build_dataset(cfg, is_train)

    if is_train and "TIMM_AUG" in cfg["AUG"] and cfg["AUG"]["TIMM_AUG"]["USE_LOADER"]:
        logger.info("=> use timm loader for training")
        timm_cfg = CN(init_dict=cfg["AUG"]["TIMM_AUG"])
        data_loader = {
            k: create_loader(
                dataset[k],
                input_size=cfg["MODEL"]["IMAGE_SIZE"][0],
                batch_size=cfg["TRAIN"]["BATCH_SIZE_PER_GPU"],
                is_training=True,
                use_prefetcher=True,
                no_aug=False,
                re_prob=timm_cfg.RE_PROB,
                re_mode=timm_cfg.RE_MODE,
                re_count=timm_cfg.RE_COUNT,
                re_split=timm_cfg.RE_SPLIT,
                scale=cfg["AUG"]["SCALE"],
                ratio=cfg["AUG"]["RATIO"],
                hflip=timm_cfg.HFLIP,
                vflip=timm_cfg.VFLIP,
                color_jitter=timm_cfg.COLOR_JITTER,
                auto_augment=timm_cfg.AUTO_AUGMENT,
                num_aug_splits=0,
                interpolation=cfg["AUG"]["INTERPOLATION"],
                mean=cfg["INPUT"]["MEAN"],
                std=cfg["INPUT"]["STD"],
                num_workers=cfg["WORKERS"],
                distributed=distributed,
                collate_fn=None,
                pin_memory=cfg["PIN_MEMORY"],
                use_multi_epochs_loader=True,
            )
            for k in dataset
        }
    else:
        if is_train:
            batch_size_per_gpu = cfg["TRAIN"]["BATCH_SIZE_PER_GPU"]
            shuffle = cfg["TRAIN"].get("SHUFFLE", True)
        else:
            batch_size_per_gpu = cfg["TEST"]["BATCH_SIZE_PER_GPU"]
            shuffle = False

        if distributed:
            sampler = {
                k: build_sampler(cfg, dataset[k], is_train, shuffle) for k in dataset
            }
            shuffle = False
        else:
            sampler = {k: None for k in dataset}

        data_loader = {
            k: torch.utils.data.DataLoader(
                dataset[k],
                batch_size=batch_size_per_gpu,
                shuffle=shuffle,
                num_workers=cfg["WORKERS"],
                pin_memory=cfg["PIN_MEMORY"],
                sampler=sampler[k],
                drop_last=True if is_train else False,
            )
            for k in dataset
        }

        multitask_sampler = MultiTaskSampler(
            cfg, data_loader, tau=cfg["MULTITASK_DATALOADER"].get("TAU", 1.0)
        )
        data_loader = MultiTaskDataloader(cfg, multitask_sampler, data_loader)

    return data_loader


def build_coco_caption_universal_dataloader(cfg, is_train=True, distributed=False):
    assert is_train is False, "support eval now"
    transform = build_transforms(cfg, is_train)

    tokenobj = build_tokenizer(cfg["LANG_ENCODER"])
    dataset = COCOCaptionDataset(
        root=cfg["COCO_CAPTION_UNIVERSAL"]["ROOT"],
        caption_file=cfg["COCO_CAPTION_UNIVERSAL"]["CAPTION"],
        split="test",
        transform=transform,
        tokenizer=tokenobj,
        num_of_captions=cfg["COCO_CAPTION_UNIVERSAL"]["NUM_CAPTIONS"],
        use_vision_benchmark=cfg["COCO_CAPTION_UNIVERSAL"].get(
            "USE_VISION_BENCHMARK", False
        ),
    )

    # loader
    batch_size_per_gpu = cfg["TEST"]["BATCH_SIZE_PER_GPU"]
    shuffle = False
    sampler = None
    data_loader = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size_per_gpu,
        shuffle=shuffle,
        num_workers=cfg["WORKERS"],
        pin_memory=cfg["PIN_MEMORY"],
        sampler=sampler,
        drop_last=True if is_train else False,
        prefetch_factor=1,
    )
    return data_loader
