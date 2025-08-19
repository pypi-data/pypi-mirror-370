# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Common utils."""

import base64
import inspect
import torch
import urllib.request

from io import BytesIO
from PIL import Image
from typing import List

from azureml.automl.core.automl_utils import retry_with_backoff
from azureml.core import Workspace
from azureml.core.run import Run

from azureml.acft.common_components.utils.logging_utils import get_logger_app

logger = get_logger_app(__name__)


def get_workspace() -> Workspace:
    """Get current workspace either from Run or Config.

    :return: Current workspace
    :rtype: Workspace
    """
    try:
        ws = Run.get_context().experiment.workspace
        return ws
    except Exception:
        return Workspace.from_config()


@retry_with_backoff(retries=3)
def download_file(url: str, destination: str):
    """Download file from url to destination.
    :param url: Url to download from.
    :type url: str
    :param destination: Destination to download to.
    :type destination: str
    :raises Exception: If download fails.
    """
    urllib.request.urlretrieve(url, destination)
    logger.info(f"Downloaded {url} to {destination}.")


def get_random_base64_decoded_image() -> str:
    """ get random base64 decoded image

    :return: base64 decoded image
    :rtype: string
    """
    buffered = BytesIO()
    im = torch.rand((256, 256, 3))
    image = Image.fromarray(im.numpy().astype('uint8'), 'RGB')
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


def get_input_params_name(function: callable) -> List[str]:
    """Get input parameters name for function.
    :param function: Function to get input parameters name for.
    :type function: callable
    :return: List of input parameters name.
    :rtype: List[str]
    """
    params = inspect.signature(function).parameters
    params = dict(params)
    params.pop("self", "")
    params.pop("kwargs", "")
    return list(params.keys())
