# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image Components package - finetuning component common."""
__path__ = __import__("pkgutil").extend_path(__path__, __name__)

from azureml.acft.common_components.image.runtime_common.object_detection.common import (
    masktools,
)

__all__ = [masktools]
