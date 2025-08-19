# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image finetune component - dataset adapter from runtime."""

import json
import torch

from torch import Tensor
from typing import cast, Tuple, Dict, Callable

from azureml.automl.core.shared.constants import MLTableLiterals, MLTableDataLabel

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.common.utils import get_workspace
from azureml.acft.image.components.finetune.common.constants.constants import (
    VisionDatasetConstants,
    SettingLiterals, SettingParameters,
)
from azureml.acft.common_components.image.runtime_common.common import (
    utils,
    distributed_utils,
)
from azureml.acft.common_components.image.runtime_common.common.aml_dataset_base_wrapper import (
    AmlDatasetBaseWrapper,
)
from azureml.acft.common_components.image.runtime_common.object_detection.data import (
    datasets,
)
from azureml.acft.common_components.image.runtime_common.object_detection.data.dataset_wrappers import (
    CommonObjectDetectionDatasetWrapper,
    DatasetProcessingType,
)
from azureml.acft.common_components.image.runtime_common.object_detection.data.datasets import (
    CommonObjectDetectionDataset,
)
from azureml.acft.common_components.image.runtime_common.object_detection.data.utils import (
    read_aml_dataset,
)

logger = get_logger_app(__name__)


class RuntimeDetectionDatasetAdapter(CommonObjectDetectionDatasetWrapper):
    """ Dataset adapter class that makes Runtime dataset classes suitable for finetune components."""

    def __init__(self, dataset: CommonObjectDetectionDataset) -> None:
        """
        Dataset adapter class that makes Runtime dataset classes suitable for finetune components. It prepares the
        input parameters and directs the call to corresponding methods in inherited class. It also modifies the
        output (before returning) to make it more generic and suitable for finetune components.
        :param dataset: Common object detection dataset
        :type dataset: CommonObjectDetectionDataset
        """

        # Since, we don't want to apply any augmentation from runtime dataset, setting following values.
        # We will apply augmentation/ pre-processing from finetune components.
        dataset.apply_automl_train_augmentations = False
        dataset._transform = None

        super().__init__(dataset, DatasetProcessingType.IMAGES)

    def __getitem__(self, index: int) -> Tuple[Tensor, dict, dict]:
        """ Convert output of dataset get item to make it generalized and usable in components

        :param index: Index of object
        :type index: int
        :return: Image tensor in de-normalized form [0-255], training labels and image info
        :rtype: Tuple[Tensor, dict, dict]
        """
        image, training_labels, image_info = super().__getitem__(index)

        if image is None:
            return None, {}, {}

        # CommonObjectDetectionDatasetWrapper returns the normalized image. This adapter returns
        # the image in generic de-normalized format to the frameworks (MMD need image in denormalized format).

        with torch.no_grad():
            image = torch.mul(image, 255)
        image = image.to(torch.uint8)

        return image, training_labels, image_info


def _combine_mltables(training_mltable: str, validation_mltable: str) -> str:
    """ Combine mltables to make single mltable to pass in get_tabular_dataset
    :param training_mltable: The training mltable path
    :type training_mltable: str
    :param validation_mltable: The validation mltable path
    :type validation_mltable: str
    :return: mltable in serialized json format
    :rtype: str
    """

    mltable = {
        MLTableDataLabel.TrainData.value: {
            MLTableLiterals.MLTABLE_RESOLVEDURI: training_mltable
        }
    }
    if validation_mltable is not None:
        mltable[MLTableDataLabel.ValidData.value] = {
            MLTableLiterals.MLTABLE_RESOLVEDURI: validation_mltable
        }
    return json.dumps(mltable)


def get_object_detection_dataset(
    training_mltable: str,
    object_detection_dataset: Callable[
        [CommonObjectDetectionDataset], RuntimeDetectionDatasetAdapter
    ],
    settings: Dict = {},
    validation_mltable: str = None,
    masks_required: bool = False,
) -> Tuple[RuntimeDetectionDatasetAdapter, RuntimeDetectionDatasetAdapter]:
    """
    Return training and validation dataset for object detection and instance segmentation task from mltable
    :param training_mltable: The training mltable path
    :type training_mltable: str
    :param object_detection_dataset: The dataset adapter class name to be used for creating dataset objects.
    :type object_detection_dataset: RuntimeDetectionDatasetAdapter
    :param settings: Settings dictionary
    :type settings: Dict
    :param validation_mltable: The validation mltable path
    :type validation_mltable: str
    :param masks_required: mask required or not for segmentation. Optional, default False
    :type masks_required: bool
    :return: Training dataset, validation dataset
    :rtype: Tuple[RuntimeDetectionDatasetAdapter, RuntimeDetectionDatasetAdapter]
    """

    mltable = _combine_mltables(training_mltable, validation_mltable)

    dataset_wrapper: AmlDatasetBaseWrapper = cast(
        AmlDatasetBaseWrapper, datasets.AmlDatasetObjectDetection
    )
    train_tabular_ds, validation_tabular_ds = utils.get_tabular_dataset(
        settings=settings, mltable_json=mltable
    )

    ws = get_workspace()

    utils.download_or_mount_image_files(
        settings=settings,
        train_ds=train_tabular_ds,
        validation_ds=validation_tabular_ds,
        dataset_class=dataset_wrapper,
        workspace=ws,
    )

    validation_size = settings.get(
        SettingLiterals.TRAIN_VAL_SPLIT_RATIO,
        VisionDatasetConstants.DEFAULT_VALIDATION_SIZE,
    )
    output_directory = settings.get(SettingLiterals.OUTPUT_DIR, SettingParameters.DEFAULT_OUTPUT_DIR)
    use_bg_label = settings.get(SettingLiterals.USE_BG_LABEL, False)
    ignore_data_errors = settings.get(SettingLiterals.IGNORE_DATA_ERRORS, True)
    master_process = distributed_utils.master_process()

    train_dataset, valid_dataset = read_aml_dataset(
        dataset=train_tabular_ds,
        validation_dataset=validation_tabular_ds,
        validation_size=validation_size,
        ignore_data_errors=ignore_data_errors,
        output_dir=output_directory,
        master_process=master_process,
        use_bg_label=use_bg_label,
        settings=settings,
        masks_required=masks_required,
    )

    if train_dataset.classes != valid_dataset.classes:
        all_classes = list(set(train_dataset.classes + valid_dataset.classes))
        train_dataset.reset_classes(all_classes)
        valid_dataset.reset_classes(all_classes)

    logger_msg = f"# train images: {len(train_dataset)}, # validation images: {len(valid_dataset)}, "
    logger_msg += f"# labels: {train_dataset.num_classes - 1 if use_bg_label else train_dataset.num_classes}"
    logger.info(f"{logger_msg}")

    return (
        object_detection_dataset(train_dataset),
        object_detection_dataset(valid_dataset),
    )
