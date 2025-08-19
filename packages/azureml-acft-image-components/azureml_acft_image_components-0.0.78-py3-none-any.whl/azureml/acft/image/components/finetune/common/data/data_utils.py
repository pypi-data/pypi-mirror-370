# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image finetune component - runtime classification dataset."""

from __future__ import annotations
import json
import numpy as np
from typing import Dict, List
from azureml.data.abstract_dataset import AbstractDataset
from azureml.automl.core.shared.constants import MLTableLiterals, MLTableDataLabel
from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.common.utils import get_workspace
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals,
)
from azureml.acft.common_components.image.runtime_common.common import (
    utils
)
from azureml.acft.common_components.image.runtime_common.common.aml_dataset_base_wrapper import (
    AmlDatasetBaseWrapper,
)
from azureml.acft.common_components.image.runtime_common.common.dataset_helper import AmlDatasetHelper
from azureml._common._error_definition import AzureMLError
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException

logger = get_logger_app(__name__)


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


def get_dataset_helper(tabular_dataset: AbstractDataset,
                       ignore_data_errors: bool,
                       image_column_name: str,
                       stream_image_files: bool) -> AmlDatasetHelper:
    """ get dataset helper. if `stream_image_files` is false, files will be downloaded
    :param tabular_dataset: dataset
    :type tabular_dataset: AbstractDataset
    :param ignore_data_errors: Setting this ignores and files in the dataset that fail to download.
    :type ignore_data_errors: bool
    :param image_column_name: The column name for the image file.
    :type image_column_name: str
    :param stream_image_files: If no, download the files on local, else mount the files
    :type stream_image_files: str
    :return: dataset helper
    :rtype: AmlDatasetHelper
    """
    if stream_image_files:
        logger.info("Mounting datastores containing image files in train dataset.")
        workspace = get_workspace()
        dataset_helper = AmlDatasetHelper(tabular_dataset, ignore_data_errors,
                                          image_column_name=image_column_name,
                                          download_files=False)
        dataset_helper.mount_image_file_datastores(tabular_dataset,
                                                   image_column_name=image_column_name,
                                                   workspace=workspace)
    else:
        logger.info(
            "Downloading dataset files to local disk. Note: if the dataset is larger than available disk "
            "space, the run will fail.")
        # download image files, check existence
        dataset_helper = AmlDatasetHelper(tabular_dataset, ignore_data_errors,
                                          image_column_name=image_column_name,
                                          download_files=True)
    return dataset_helper


def get_dataset(training_mltable: str,
                settings: Dict = {},
                validation_mltable: str = None):
    """
    Return training and validation dataset tabular dataset
    :param training_mltable: The training mltable path
    :type training_mltable: str
    :param settings: Settings dictionary
    :type settings: Dict
    :param validation_mltable: The validation mltable path
    :type validation_mltable: str
    :return: Training dataset, validation dataset
    :rtype: Tuple[TabularDataset, TabularDataset]
    """

    mltable = _combine_mltables(training_mltable, validation_mltable)

    train_tabular_ds, validation_tabular_ds = utils.get_tabular_dataset(
        settings=settings, mltable_json=mltable
    )

    ignore_data_errors = settings.get(SettingLiterals.IGNORE_DATA_ERRORS, True)
    stream_image_files = settings.get(SettingLiterals.STREAM_IMAGE_FILES, False)
    image_column_name = AmlDatasetBaseWrapper.DATASET_IMAGE_COLUMN_NAME
    train_tabular_ds.dataset_helper = get_dataset_helper(train_tabular_ds,
                                                         ignore_data_errors,
                                                         image_column_name,
                                                         stream_image_files)

    if validation_tabular_ds is not None:
        validation_tabular_ds.dataset_helper = get_dataset_helper(validation_tabular_ds,
                                                                  ignore_data_errors,
                                                                  image_column_name,
                                                                  stream_image_files)

    return train_tabular_ds, validation_tabular_ds


def filter_invalid_images(examples: List[Dict[str, Dict]], image_column_name: str) -> Dict[str, Dict]:
    """ Remove invalid examples from the list of examples and return the valid examples
    :param examples: List of examples
    :type examples: List[Dict[str, Dict]]
    :param image_column_name: The column name for the image file.
    :type image_column_name: str
    :return: Valid examples
    :rtype: Dict[str, Dict]
    """
    # Filter out invalid examples
    valid_examples = [example for example in examples if example is not None
                      and image_column_name in example]
    if len(valid_examples) == 0:
        raise ACFTDataException._with_error(
            AzureMLError.create(ACFTUserError,
                                pii_safe_message="All images in the current batch are invalid.")
        )
    if len(valid_examples) != len(examples):
        num_invalid_examples = len(examples) - len(valid_examples)
        logger.info(f"{num_invalid_examples} invalid images found.")
        logger.info("Replacing invalid images with randomly selected valid images from the current batch")
        new_example_indices = np.random.choice(np.arange(len(valid_examples)), num_invalid_examples)
        for ind in new_example_indices:
            # Padding the batch with valid examples
            valid_examples.append(valid_examples[ind])
    return valid_examples
