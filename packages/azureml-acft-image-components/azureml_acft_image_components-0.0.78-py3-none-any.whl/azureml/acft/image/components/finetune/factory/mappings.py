# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image finetune component - factory mappings."""
from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class MODEL_FAMILY_CLS:
    """A class to represent model family constants."""
    HUGGING_FACE_IMAGE = "HuggingFaceImage"
    MMDETECTION_IMAGE = "MmDetectionImage"
    MMTRACKING_VIDEO = "MmTrackingVideo"


MODEL_FAMILY_MODULE_IMPORT_PATH_MAP = OrderedDict([
    (MODEL_FAMILY_CLS.HUGGING_FACE_IMAGE, "azureml.acft.image.components.finetune.huggingface"),
    (MODEL_FAMILY_CLS.MMDETECTION_IMAGE, "azureml.acft.image.components.finetune.mmdetection"),
    (MODEL_FAMILY_CLS.MMTRACKING_VIDEO, "azureml.acft.image.components.finetune.mmtracking"),

])
