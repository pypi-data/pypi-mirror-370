# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------

"""Common image interfaces for huggingface."""

import os
import time
from azureml.acft.common_components.utils.error_handling.error_definitions import (
    TaskNotSupported,
    ACFTUserError,
)
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
import transformers

from transformers import (
    AutoConfig,
    AutoImageProcessor,
    PretrainedConfig,
    PreTrainedModel,
)
from transformers.image_processing_utils import BaseImageProcessor
from typing import Optional, Tuple, Union

from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals,
    HfProcessorParamNames
)
from azureml.acft.image.components.finetune.huggingface.common.constants import (
    HfImageInterfaceConstants,
    HfImageModelConstants,
)
from azureml.acft.image.components.finetune.interfaces.azml_interface import (
    AzmlTokenizerInterface,
    AzmlModelInterface,
)

logger = get_logger_app(__name__)


class AzmlHfImageFeatureExtractor(AzmlTokenizerInterface):
    """Get FeatureExtractor based on the model_name"""

    @staticmethod
    def _compute_fractions_for_resize_update(
        resize_size: Union[dict, int], crop_size: dict
    ) -> Tuple[Optional[float], Optional[float]]:
        """ Compute the fraction using which the resize size should be updated if user input is different.
        The general sequence of preprocessing is RGB -> resize -> center_crop -> rescale -> normalize.
        Example:
        Original Preprocessing:
        {
            "do_resize": true,
            ...
            "size": {"height": 288, "width": 288},
            "crop_size": {"height": 256, "width": 256}
        }
        User input:
            image_height: 320
            image_width: 320
        Update to Preprocessing:
        For updating, we use the fraction by which the the resize size is larger than model input.
            new_size.height = image_height * (size.height - crop_size.height) / crop_size.height + image_height

        :param resize_size: Resize size dictionary from preprocessor
        :param resize_size: dict or int
        :param crop_size: Crop size dictionary
        :param crop_size: dict

        :return: A tuple containing one of the below, depending on the case
            - (size_fraction, None) or (height_fraction, width_fraction) or (longest_edge_fraction, None),
               or (shortest_edge_fraction, None), (shortest_edge_fraction, longest_edge_fraction)
        :rtype: tuple
        """
        if isinstance(resize_size, int):
            max_crop_size = min(
                crop_size[HfProcessorParamNames.HEIGHT_KEY],
                crop_size[HfProcessorParamNames.WIDTH_KEY],
            )
            size_fraction = (resize_size - max_crop_size) / max_crop_size
            return 1.0 + size_fraction, None

        if (
            HfProcessorParamNames.HEIGHT_KEY in resize_size
            and HfProcessorParamNames.WIDTH_KEY in resize_size
        ):
            height_fraction = (
                resize_size[HfProcessorParamNames.HEIGHT_KEY]
                - crop_size[HfProcessorParamNames.HEIGHT_KEY]
            ) / crop_size[HfProcessorParamNames.HEIGHT_KEY]
            width_fraction = (
                resize_size[HfProcessorParamNames.WIDTH_KEY]
                - crop_size[HfProcessorParamNames.WIDTH_KEY]
            ) / crop_size[HfProcessorParamNames.WIDTH_KEY]
            return 1.0 + height_fraction, 1.0 + width_fraction
        elif (
            HfProcessorParamNames.SHORTEST_EDGE_KEY in resize_size
            and HfProcessorParamNames.LONGEST_EDGE_KEY not in resize_size
        ):
            min_crop_size = min(
                crop_size[HfProcessorParamNames.HEIGHT_KEY],
                crop_size[HfProcessorParamNames.WIDTH_KEY],
            )
            shortest_edge_fraction = (
                resize_size[HfProcessorParamNames.SHORTEST_EDGE_KEY] - min_crop_size
            ) / min_crop_size
            return 1.0 + shortest_edge_fraction, None
        elif (
            HfProcessorParamNames.SHORTEST_EDGE_KEY not in resize_size
            and HfProcessorParamNames.LONGEST_EDGE_KEY in resize_size
        ):
            max_crop_size = max(
                crop_size[HfProcessorParamNames.HEIGHT_KEY],
                crop_size[HfProcessorParamNames.WIDTH_KEY],
            )
            longest_edge_fraction = (
                resize_size[HfProcessorParamNames.SHORTEST_EDGE_KEY] - max_crop_size
            ) / max_crop_size
            return 1.0 + longest_edge_fraction, None
        elif (
            HfProcessorParamNames.SHORTEST_EDGE_KEY in resize_size
            and HfProcessorParamNames.LONGEST_EDGE_KEY in resize_size
        ):
            min_crop_size = min(
                crop_size[HfProcessorParamNames.HEIGHT_KEY],
                crop_size[HfProcessorParamNames.WIDTH_KEY],
            )
            max_crop_size = max(
                crop_size[HfProcessorParamNames.HEIGHT_KEY],
                crop_size[HfProcessorParamNames.WIDTH_KEY],
            )
            shortest_edge_fraction = (
                resize_size[HfProcessorParamNames.SHORTEST_EDGE_KEY] - min_crop_size
            ) / min_crop_size
            longest_edge_fraction = (
                resize_size[HfProcessorParamNames.LONGEST_EDGE_KEY] - max_crop_size
            ) / max_crop_size
            return 1.0 + shortest_edge_fraction, 1.0 + longest_edge_fraction

    @staticmethod
    def update_resize_size_dict(
        image_processor: BaseImageProcessor,
        image_height: int,
        image_width: int,
        do_center_crop: bool,
    ):
        """ Compute update to resize size dict according to user input.
        The general sequence of preprocessing is RGB -> resize -> center_crop -> rescale -> normalize.
        Example:
        Original Preprocessing:
        {
            "do_resize": true,
            ...
            "size": {"height": 288, "width": 288},
            "crop_size": {"height": 256, "width": 256}
        }
        User input:
            image_height: 320
            image_width: 320
        Update to Preprocessing:
        For updating, we use the fraction by which the the resize size is larger than model input.
            new_size.height = image_height * (size.height - crop_size.height) / crop_size.height + image_height

        :param image_processor: Image Processor or Feature extractor
        :param image_processor: BaseImageProcessor
        :param image_height: User input image height
        :param image_height: int
        :param image_width: User input image wwidth
        :param image_width: int

        :return: A dictionary for updating the "size" dictionary in feature extractor.
        :rtype: dict
        """
        fractions = (1.0, 1.0)
        if do_center_crop:
            fractions = AzmlHfImageFeatureExtractor._compute_fractions_for_resize_update(
                resize_size=image_processor.size,
                crop_size=image_processor.crop_size,
            )

        resize_size = image_processor.size
        if isinstance(resize_size, int):
            longest_edge = max(image_height, image_width)
            image_processor.size = round(longest_edge * fractions[0])
            return image_processor.size

        assert (
            isinstance(image_processor.size, dict)
        ), f"Got unsupported format for {image_processor.size}"

        if (
            HfProcessorParamNames.HEIGHT_KEY in resize_size
            and HfProcessorParamNames.WIDTH_KEY in resize_size
        ):
            # Update resize size according to the original fraction
            image_processor.size = {
                HfProcessorParamNames.HEIGHT_KEY: round(image_height * fractions[0]),
                HfProcessorParamNames.WIDTH_KEY: round(image_width * fractions[1]),
            }
        elif (
            HfProcessorParamNames.SHORTEST_EDGE_KEY in resize_size
            and HfProcessorParamNames.LONGEST_EDGE_KEY not in resize_size
        ):
            shortest_edge = min(image_height, image_width)
            image_processor.size = {
                HfProcessorParamNames.SHORTEST_EDGE_KEY: round(shortest_edge * fractions[0],)
            }
        elif (
            HfProcessorParamNames.SHORTEST_EDGE_KEY not in resize_size
            and HfProcessorParamNames.LONGEST_EDGE_KEY in resize_size
        ):
            longest_edge = max(image_height, image_width)
            image_processor.size = {
                HfProcessorParamNames.LONGEST_EDGE_KEY: round(longest_edge * fractions[0]),
            }
        elif (
            HfProcessorParamNames.SHORTEST_EDGE_KEY in resize_size
            and HfProcessorParamNames.LONGEST_EDGE_KEY in resize_size
        ):
            in_shortest_edge = min(image_height, image_width)
            in_longest_edge = max(image_height, image_width)
            # Update resize size according to the original fraction
            image_processor.size = {
                HfProcessorParamNames.SHORTEST_EDGE_KEY: round(in_shortest_edge * fractions[0]),
                HfProcessorParamNames.LONGEST_EDGE_KEY: round(in_longest_edge * fractions[1]),
            }
        return image_processor.size

    @classmethod
    def from_pretrained(
        cls, hf_image_model_name_or_path: Union[str, os.PathLike], **kwargs
    ) -> BaseImageProcessor:
        """
        :param hf_image_model_name_or_path: Hugging face image model name or path
        :type hf_image_model_name_or_path: Union[str, os.PathLike]
        :return: Feature Extractor for image models.
        :rtype: BaseImageProcessor
        """
        # this function is to be used by all hugging face image models
        # task_name and model_specific_args is to facilitate any future
        # model_specific requirements.
        task_name = kwargs.pop(SettingLiterals.TASK_NAME, None)
        if task_name is None:
            raise ACFTValidationException._with_error(
                AzureMLError.create(TaskNotSupported,
                                    TaskName=task_name))
        start_time = time.time()

        model_specific_args = {}

        image_processor = AutoImageProcessor.from_pretrained(
            hf_image_model_name_or_path, **model_specific_args,
        )
        logger.info(f"Original feature extractor: {image_processor.to_dict()}")
        # The general order in which the transforms are applied in HF
        # RGB -> resize -> center_crop -> rescale -> normalize
        do_center_crop = hasattr(
            image_processor, HfProcessorParamNames.DO_CENTER_CROP_KEY
        ) and getattr(image_processor, HfProcessorParamNames.DO_CENTER_CROP_KEY)
        do_resize = hasattr(
            image_processor, HfProcessorParamNames.DO_RESIZE_KEY
        ) and getattr(image_processor, HfProcessorParamNames.DO_RESIZE_KEY)

        if kwargs[SettingLiterals.IMAGE_HEIGHT] != -1 and kwargs[SettingLiterals.IMAGE_WIDTH] != -1:
            # User has provided image height and width, Updating feature extractor values for height and width
            if do_center_crop and do_resize:
                image_processor.size = AzmlHfImageFeatureExtractor.update_resize_size_dict(
                    image_processor=image_processor,
                    image_height=kwargs[SettingLiterals.IMAGE_HEIGHT],
                    image_width=kwargs[SettingLiterals.IMAGE_WIDTH],
                    do_center_crop=do_center_crop,
                )
                image_processor.crop_size = {
                    HfProcessorParamNames.HEIGHT_KEY: kwargs[
                        SettingLiterals.IMAGE_HEIGHT
                    ],
                    HfProcessorParamNames.WIDTH_KEY: kwargs[
                        SettingLiterals.IMAGE_WIDTH
                    ],
                }
            elif do_center_crop:
                image_processor.crop_size = {
                    HfProcessorParamNames.HEIGHT_KEY: kwargs[
                        SettingLiterals.IMAGE_HEIGHT
                    ],
                    HfProcessorParamNames.WIDTH_KEY: kwargs[
                        SettingLiterals.IMAGE_WIDTH
                    ],
                }
            elif do_resize:
                image_processor.size = AzmlHfImageFeatureExtractor.update_resize_size_dict(
                    image_processor=image_processor,
                    image_height=kwargs[SettingLiterals.IMAGE_HEIGHT],
                    image_width=kwargs[SettingLiterals.IMAGE_WIDTH],
                    do_center_crop=False,
                )
        logger.info(
            f"Updating Feature Extractor with: {image_processor.to_dict()}"
        )
        # Todo - if we find a better way, update it.
        # Get the feature extractor using the updated dict. This way save_pretrained will save the right values.
        image_processor = AutoImageProcessor.from_pretrained(
            hf_image_model_name_or_path, **image_processor.to_dict()
        )

        end_time = time.time()
        logger.info(
            f"Feature Extractor loaded for model_name_or_path {hf_image_model_name_or_path} "
            f"in {round(end_time - start_time, 3)} seconds."
        )
        logger.info(f"Loaded Feature Extractor : {image_processor.to_dict()}")

        return image_processor


class AzmlHfImageConfig:
    """Get Config based on the model_name or path."""

    @classmethod
    def from_pretrained(
        cls, hf_image_model_name_or_path: Union[str, os.PathLike], **kwargs
    ) -> PretrainedConfig:
        """
        :param hf_image_model_name_or_path: Hugging face image model name or path
        :type hf_image_model_name_or_path: Union[str, os.PathLike]
        :return: config object containing information about the model.
        :rtype: PretrainedConfig
        """
        config = AutoConfig.from_pretrained(hf_image_model_name_or_path, **kwargs)
        # No need to manipulate the image_size in model config since the image_size is used to
        # construct the positional embeddings layer of the network, manipulating it will lead to
        # suboptimal performance for model families such as DinoV2 which uses positional embeddings.
        return config


class AzmlHfImageModel(AzmlModelInterface):
    """Get model based on the model_name or path."""
    @classmethod
    def from_pretrained(
        cls, hf_image_model_name_or_path: Union[str, os.PathLike], **kwargs
    ) -> PreTrainedModel:
        """Apply model specific hacks before calling the Base Feature Extractor

        :param hf_image_model_name_or_path: Hugging face image model name or path
        :type hf_image_model_name_or_path: Union[str, os.PathLike]
        :return: model object.
        :rtype: PreTrainedModel
        """
        # Initialize the config
        problem_type = kwargs[SettingLiterals.PROBLEM_TYPE]
        num_labels = kwargs["num_labels"]

        hf_image_model_cls_str = kwargs.pop(
            HfImageInterfaceConstants.HF_IMAGE_MODEL_CLS
        )
        if hasattr(transformers, hf_image_model_cls_str):
            hf_model_cls = getattr(transformers, hf_image_model_cls_str)
        else:
            raise AttributeError(f"Invalid model class: {hf_image_model_cls_str}")

        # get the config based on the model
        config = AzmlHfImageConfig.from_pretrained(
            hf_image_model_name_or_path,
            problem_type=problem_type,
            num_labels=num_labels,
            label2id=kwargs["label2id"],
            id2label=kwargs["id2label"],
            image_height=kwargs[SettingLiterals.IMAGE_HEIGHT],
            image_width=kwargs[SettingLiterals.IMAGE_WIDTH],
        )

        # Initialize the model
        model = hf_model_cls.from_pretrained(
            hf_image_model_name_or_path,
            config=config,
            output_loading_info=True,
            ignore_mismatched_sizes=True,
        )
        return model
