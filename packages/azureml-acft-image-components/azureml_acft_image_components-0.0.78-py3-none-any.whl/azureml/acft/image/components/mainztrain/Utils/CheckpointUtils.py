# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import logging
from enum import IntEnum
import torch

logger = logging.getLogger(__name__)


class SAVE_STRATEGY(IntEnum):
    PER_OPTIM_STEPS = 1
    LAST = 0
    BEST = -1
    NO_SAVE = -2


def init_Nebula_service(
    nebula_persistent_storage_path=None, nebula_persistent_time_interval=60
):
    """
    Initialize Nebula service with nebula persistent storage path and nebula persistent time interval.

    Args:
        nebula_persistent_storage_path (str): the path where the checkpoint will be persisted, usually be a path.
        nebula_persistent_time_interval (int): the time interval (seconds) that Nebula service persist the checkpoint.
    Returns:
        str: the real checkpoint' state file path for non-Nebula loading or partition for Nebula loading
    """
    try:
        import torch_nebula

        # If the NEBULA_PERSISTENT_STORAGE_PATH is Not set,
        # Nebula will not persist checkpoint to tier3 storage (like Azure Blob)
        if nebula_persistent_storage_path is not None:
            logger.warning(
                f"Initializing Nebula service with persistent storage path: {nebula_persistent_storage_path}"
            )
            os.environ["NEBULA_PERSISTENT_STORAGE_PATH"] = (
                nebula_persistent_storage_path
            )
            os.environ["NEBULA_PERSISTENT_TIME_INTERVAL"] = str(
                nebula_persistent_time_interval
            )

        torch_nebula.init()
        logger.warning("Initialization of Nebula service done.")
    except Exception as e:
        error_message = (
            f"import nebula exception: {str(e)}. "
            f"Please ref the 'NEBULA_CHECKPOINTING' section of __init__.py "
            f"under MainzTrain folder to verify if the Nabula package is installed correctly"
        )
        raise Exception(error_message)


def get_nebula_checkpoint_tag_name(checkpoint_tag):
    """
    Get Nebula checkpoint folder name with checkpoint_tag.

    Args:
        checkpoint_tag (str): the checkpoint tag which usually was set as the optim_step of the checkpoint
    Returns:
        str: the real checkpoint folder name
    """
    return "global_step" + str(checkpoint_tag)


def get_nebula_partition_name(file_name, module_name=None):
    """
    Get partition name with optional module_name.

    Args:
        file_name (str)
        module_name (str): the module_name of the module
    Returns:
        str: partition name in a nebula snapshot
    """
    if module_name is not None:
        return module_name + "_" + file_name
    else:
        return file_name


def get_relative_file_path(file_name, module_name=None):
    """
    Get relative file path with optional module_name.

    Args:
        file_name (str)
        module_name (str): the module_name of the module
    Returns:
        str: relative file path in a checkpoint folder
    """
    if module_name is not None:
        return os.path.join(module_name, file_name + ".pt")
    else:
        return os.path.join(file_name + ".pt")


def save_to_checkpoint(
    state,
    file_name,
    checkpoint_path,
    nebula_snapshot,
    module_name=None,
    is_nebula_enabled=False,
):
    if is_nebula_enabled:
        partition_name = get_nebula_partition_name(file_name, module_name)
        assert nebula_snapshot is not None, (
            f"Nebula snapshot should not be None when saving nebula_checkpoint with "
            f"module_partition: {partition_name}"
        )
        nebula_snapshot.save(partition_name, state)
    else:
        relative_file_path = get_relative_file_path(file_name, module_name)
        full_file_path = os.path.join(checkpoint_path, relative_file_path)
        os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
        torch.save(state, full_file_path)


def load_from_checkpoint(
    map_location,
    file_name,
    checkpoint_path,
    nebula_snapshot,
    module_name=None,
    is_nebula_enabled=False,
):
    if is_nebula_enabled:
        partition_name = get_nebula_partition_name(file_name, module_name)
        assert nebula_snapshot is not None, (
            f"Nebula snapshot should not be None when loading nebula_checkpoint with "
            f"module_load_path: {partition_name}"
        )
        state = nebula_snapshot.load(partition_name, map_location=map_location)
    else:
        relative_file_path = get_relative_file_path(file_name, module_name)
        full_file_path = os.path.join(checkpoint_path, relative_file_path)
        state = torch.load(full_file_path, map_location=map_location)

    return state
