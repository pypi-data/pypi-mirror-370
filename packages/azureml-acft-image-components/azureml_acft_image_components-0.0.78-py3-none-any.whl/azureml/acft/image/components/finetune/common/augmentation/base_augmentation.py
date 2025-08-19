# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image finetune component - base augmentation."""

from abc import abstractmethod, ABC
from collections.abc import Callable
from typing import Optional

from azureml.acft.common_components import get_logger_app

logger = get_logger_app(__name__)


class BaseAugmentation(ABC):
    """Base augmentation class for image models"""

    def __init__(
        self,
        config_path: Optional[str] = None,
        model_preprocessing_params_dict: dict = dict(),
        **kwargs,
    ) -> None:
        """
        :param config_path: If config file is used, path to augmentation config.
                            None, otherwise
        :type config_path: string
        :param model_preprocessing_params_dict: models's preprocessing
                 parameters dict
                - image_processor.to_dict() containing preprocess_config.json
                  in case of HF
                - dict containing preprocessing params in case of other frameworks
                - dict containing preprocessing params in case of other approaces for augmentation,
                  this key:value pairs in the dict can be used while preparing transforms.
        :type model_preprocessing_params_dict: dict
        :param kwargs: A dictionary of task input params. This can be used to prepare the augmentation dict.
        :type kwargs: dict

        :return: None
        :rtype: None

        Example for getting model_preprocessing_params_dict for HF:
        ```
        from transformers import AutoImageProcessor
        pretrained_model_name = "google/vit-base-patch16-224"
        image_processor = AutoImageProcessor.from_pretrained( pretrained_model_name_or_path=pretrained_model_name )
        model_preprocessing_params_dict = image_processor.to_dict()
        ```
        Sample outcome:
        {
            '_processor_class': None, 'do_resize': True, 'do_rescale': True, 'do_normalize': True,
            'size': {'height': 224, 'width': 224}, 'resample': <Resampling.BILINEAR: 2>,
            'rescale_factor': 0.00392156862745098, 'image_mean': [0.5, 0.5, 0.5],
            'image_std': [0.5, 0.5, 0.5], 'image_processor_type': 'ViTImageProcessor'
        }
        """
        self.config_path = config_path
        self.model_preprocessing_params_dict = model_preprocessing_params_dict
        self.task_params = kwargs

    @abstractmethod
    def get_train_transform() -> Callable:
        """Implementation for getting train transform using albumentations/torchvision/kornia/custom

        :return: A callable augmentation transform
        :rtype: Callable
        """
        pass

    @abstractmethod
    def get_valid_transform() -> Callable:
        """Implementation for getting validation transform using albumentations/torchvision/kornia/custom

        :return: A callable augmentation transform
        :rtype: Callable
        """
        pass
