# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image finetune component - albumentation augmentation."""

import os


from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.common.augmentation.base_augmentation import (
    BaseAugmentation,
)
from azureml.acft.image.components.finetune.common.mlflow.custom_augmentations import albumentations
from azureml.acft.image.components.finetune.common.augmentation.augmentation_config_utils import (
    update_augmentation_dict_with_model_preproc_config,
)
from azureml.acft.image.components.finetune.common.constants.augmentation_constants import (
    AugmentationConfigKeys,
    AugmentationConfigFileNames
)
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals
)
from azureml.acft.image.components.finetune.common.mlflow.augmentation_helper import (
    get_transform, save_augmentations_to_disk
)

logger = get_logger_app(__name__)


class AlbumentationsAugmentation(BaseAugmentation):
    """
    This class expects a yaml file in following format. And composes albumentation transforms from it.

    train:
        - <albumentations_function_name_1>:
              <function_1_parameter_1>: <value_1>
              <function_1_parameter_2>: <value_2>
              ...
        - <albumentations_function_name_2>:
              <function_2_parameter_1>: <value_3>
              <function_2_parameter_2>: <value_4>
              ...
        ...
    validation:
        - <albumentations_function_name_1>:
              <function_1_parameter_1>: <value_1>
              <function_1_parameter_2>: <value_2>
              ...
        - <albumentations_function_name_2>:
              <function_2_parameter_1>: <value_3>
              <function_2_parameter_2>: <value_4>
              ...
        ...
    """

    TASK_TYPE_AUGMENTATION_CONFIG_MAP = {
        Tasks.HF_MULTI_CLASS_IMAGE_CLASSIFICATION: os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            AugmentationConfigFileNames.CLASSIFICATION_ALBUMENTATIONS_CONFIG,
        ),
        Tasks.HF_MULTI_LABEL_IMAGE_CLASSIFICATION: os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            AugmentationConfigFileNames.CLASSIFICATION_ALBUMENTATIONS_CONFIG,
        ),
        Tasks.MM_OBJECT_DETECTION: os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            AugmentationConfigFileNames.OD_IS_ALBUMENTATIONS_CONFIG,
        ),
        Tasks.MM_INSTANCE_SEGMENTATION: os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            AugmentationConfigFileNames.OD_IS_ALBUMENTATIONS_CONFIG,
        ),
    }

    def __init__(
        self,
        config_path: str,
        model_preprocessing_params_dict: dict = dict(),
        **kwargs,
    ) -> None:
        """ See the doc string for BaseAugmentations class """

        config_path = (
            config_path
            or self.TASK_TYPE_AUGMENTATION_CONFIG_MAP[kwargs[SettingLiterals.TASK_NAME]]
        )
        super().__init__(
            config_path=config_path,
            model_preprocessing_params_dict=model_preprocessing_params_dict,
            **kwargs,
        )

        # Bounding box is only required for OD and IS tasks
        self.is_bbox_required = kwargs[SettingLiterals.TASK_NAME] in \
            [Tasks.MM_OBJECT_DETECTION, Tasks.MM_INSTANCE_SEGMENTATION]

        # read the yaml, get processed dictionary
        self.augmentation_dict = self._get_augmentation_dict()

        output_directory = kwargs.get(SettingLiterals.OUTPUT_DIR, None)
        if output_directory:
            # Dump the augmentation dictionary to disk so that it could be reconstructed later for inference
            save_augmentations_to_disk(output_directory, self.augmentation_dict)

    def _get_augmentation_dict(self) -> dict:
        """ Get the augmentation dictionary from augmentation-config updated with the model
        preprocessing param values.

        :return: augmentation config dictionary containing function name, updated function param's values
                 & values for train and valid
                {
                    "train": {"function_name": {function_param_name: value, ...}, ...},
                    "valid": {"function_name": {function_param_name: value, ...}, ...},
                }
        :rtype: dict
        """
        return update_augmentation_dict_with_model_preproc_config(
            config_path=self.config_path,
            model_preprocessing_params_dict=self.model_preprocessing_params_dict,
            **self.task_params,
        )

    def get_train_transform(self) -> albumentations.core.composition.Compose:
        """ Get training transform

        :return: Albumentation transform
        :rtype: albumentations.core.composition.Compose
        """
        train_transforms = get_transform(
            phase_key=AugmentationConfigKeys.TRAINING_PHASE_KEY,
            augmentation_dict=self.augmentation_dict,
            is_bbox_required=self.is_bbox_required
        )
        logger.info(f"Train transform: {train_transforms}")
        return train_transforms

    def get_valid_transform(self) -> albumentations.core.composition.Compose:
        """ Get validation transform

        :return: Albumentation transform
        :rtype: albumentations.core.composition.Compose
        """
        if AugmentationConfigKeys.VALIDATION_PHASE_KEY not in self.augmentation_dict:
            valid_transforms = None
        else:
            valid_transforms = get_transform(
                phase_key=AugmentationConfigKeys.VALIDATION_PHASE_KEY,
                augmentation_dict=self.augmentation_dict,
                is_bbox_required=self.is_bbox_required
            )
        logger.info(f"Valid transform: {valid_transforms}")
        return valid_transforms
