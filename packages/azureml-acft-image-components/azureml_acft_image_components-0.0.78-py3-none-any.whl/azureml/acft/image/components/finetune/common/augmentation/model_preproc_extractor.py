# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image finetune component - model preprocessing extractor."""

from abc import abstractmethod, ABC
from typing import Any, Dict, List

from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.common.constants.augmentation_constants import (
    AugmentationConfigKeys,
    AlbumentationParamNames,
)
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals,
    HfProcessorParamNames,
    MmLabPreprocessorParamNames,
    MmDetectionPreprocessorParamNames
)

logger = get_logger_app(__name__)


class ModelPreProcExtractor(ABC):
    """Helper class to extract parameter update (dict) from model preprocessing config, and overwritting
    with the task input values if provided.
    """

    AUGMENTATION_LIB_NAME_TO_PARAMNAMES_CLS_MAPPING = {
        "albumentations": AlbumentationParamNames
    }

    def __init__(
        self, model_preprocessing_params: dict, augmentation_library_name: str
    ) -> None:
        """Helper class to extract parameter update from model preprocessing config.
        And, overwritting with the task input values if provided.

        :param model_preprocessing_params: models's preprocessing parameters dict
                - image_processor.to_dict() containing preprocess_config.json in case of HF
                - dict containing preprocessing params in case of other frameworks
                - dict containing preprocessing params in case of other approaches for augmentation,
                  this key:value pairs in the dict can be used while preparing transforms.
        :type model_preprocessing_params: dict
        :param augmentation_library_name: Name of augmentation lib from augmentatin config.
        :type augmentation_library_name: str

        :return: None
        :rtype: None
        """
        self.model_preprocessing_params = model_preprocessing_params
        self.augmentation_library_name = augmentation_library_name
        self.augmentation_param_names_cls = (
            self.get_augmentation_library_param_names_cls()
        )

    def get_augmentation_library_param_names_cls(self) -> AlbumentationParamNames:
        """ Get the ParamNames class corresponding to augmentation_library_name used in config file

        :param augmentation_library_name: name of augmentaion library
        :type augmentation_library_name: string

        :return: <Lib>ParamNames class object, which contains specific param names for this <Lib>
        :rtype: Union[AlbumentationParamNames, ...]
        """
        if (
            self.augmentation_library_name
            not in self.AUGMENTATION_LIB_NAME_TO_PARAMNAMES_CLS_MAPPING.keys()
        ):
            logger.error(
                f"{self.augmentation_library_name} not in "
                f"{self.AUGMENTATION_LIB_NAME_TO_PARAMNAMES_CLS_MAPPING.keys()}"
            )
            raise NotImplementedError(
                f"{self.augmentation_library_name} not in "
                f"{self.AUGMENTATION_LIB_NAME_TO_PARAMNAMES_CLS_MAPPING.keys()}"
            )

        return self.AUGMENTATION_LIB_NAME_TO_PARAMNAMES_CLS_MAPPING[
            self.augmentation_library_name
        ]

    def get_augmentation_param_from_task_input(
        self, phase_name: str, task_input_params_dict: dict
    ):
        """Helper function to get a mapping from user input params to augmentation param names

        :param phase_name: Name of the phase - train/valid.
        :type phase_name: str
        :param task_params_dict: A dictionary containing task input param names and their values.
        :type task_params_dict: dict

        return: A dictionary with a mapping from augmentation library parameter names to parameter values
                from task input
                {<aug_lib_param_name>: <aug_lib_param_value_extracted_from_task>, ...}
        rtype: dict
        """
        input_image_label_dict = {}
        if SettingLiterals.IMAGE_HEIGHT in task_input_params_dict and \
                SettingLiterals.IMAGE_WIDTH in task_input_params_dict:
            input_image_label_dict = {
                **input_image_label_dict,
                self.augmentation_param_names_cls.HEIGHT_KEY: task_input_params_dict[
                    SettingLiterals.IMAGE_HEIGHT
                ],
                self.augmentation_param_names_cls.WIDTH_KEY: task_input_params_dict[
                    SettingLiterals.IMAGE_WIDTH
                ],
            }
        # Returning same for train and validation case, to be updated as per need later
        if phase_name == AugmentationConfigKeys.TRAINING_PHASE_KEY:
            return input_image_label_dict
        else:
            return input_image_label_dict

    @abstractmethod
    def get_height_width_from_model_preproc_params(self) -> Dict[str, int]:
        """ Get height/width from model's preprocessing params

        :return: A dictionary containing height and width extracted from model's preprocessing params
        :rtype: dict
        """
        pass

    @abstractmethod
    def get_mean_std_from_model_preproc_params(self, **kwargs) -> Dict[str, List[float]]:
        """ Get mean/std from model's preprocessing params

        :param phase_name: Name of the phase - train/valid.
        :type phase_name: str
        :return: A dictionary containing mean and standard deviation extracted from model's preprocessing params
        :rtype: dict
        """
        pass

    @staticmethod
    def update_model_preproc_dict_with_task_input(
        model_preproc_dict: dict, task_input_dict: dict
    ) -> dict:
        """ Update the model preprocessing dictionary with the task input params

        :param model_preproc_dict: A dictionary with key-value pairs extracted from model preprocessing config.
                Note that the key here is name of param in augmentation function.
        :type model_preproc_dict: dict
        :param task_input_dict: A dictionary with key-value pairs from task input params.
                Note that the key here is name of param in augmentation function.
        :type task_input_dict: dict

        return: model preprocessing dictionary updated with task input param values.
        rtype: dict
        """
        for aug_param_key, task_input_value in task_input_dict.items():
            # Note - Add input validation
            if task_input_value is None:
                continue
            logger.info(
                f"Updating {aug_param_key} from model config value: {model_preproc_dict[aug_param_key]}, "
                f"to input value: {task_input_value}"
            )
            model_preproc_dict[aug_param_key] = task_input_value

        return model_preproc_dict

    def extract_augmentation_params_dict(
        self,
        augmentation_function_name: str,
        augmentation_function_params_dict: dict,
        phase_name: str,
        task_input_params_dict: dict,
    ) -> dict:
        """Extract the augmentation parameters dict from model's preprocessing config updated with task input params

        :param augmentation_function_name: name of augmentation function
        :type augmentation_function_name: str
        :param augmentation_function_params_dict: a dictionary containing parameter name and parameter value as
               specified in config
        :type augmentation_function_params_dict: dict
        :param phase_name: Name of the phase for which augmentation params are extracted
        :type phase_name: str

        :return: a dictionary containing parameter name and updated parameter value as per
                 task input params and feature extractor / preprocess_config for specific model.
                 Please note that the task input params take precendece over the model preprocessing params.
                 Empty dictionary if nothing to be updated.
        :rtype: dict
        """
        if (
            self.augmentation_param_names_cls.HEIGHT_KEY
            in augmentation_function_params_dict
            or self.augmentation_param_names_cls.WIDTH_KEY
            in augmentation_function_params_dict
        ):
            # Update height width for aug from the model's config
            height_width_dict = self.get_height_width_from_model_preproc_params()
            # Get height width dict from task input
            task_input_height_width_dict = self.get_augmentation_param_from_task_input(
                phase_name=phase_name, task_input_params_dict=task_input_params_dict
            )
            # Update height width values with task input values
            return self.update_model_preproc_dict_with_task_input(
                model_preproc_dict=height_width_dict,
                task_input_dict=task_input_height_width_dict,
            )

        elif (
            augmentation_function_name.lower()
            == self.augmentation_param_names_cls.NORMALIZE_FUNC_NAME.lower()
        ):
            # Update mean and std for normalise
            mean_std_dict = self.get_mean_std_from_model_preproc_params(phase_name=phase_name)
            return mean_std_dict
        elif (
            self.augmentation_param_names_cls.CONSTRAINT_RESIZE_KEY
            in augmentation_function_params_dict
        ):
            image_min_size = task_input_params_dict.get(SettingLiterals.IMAGE_MIN_SIZE, None)
            image_max_size = task_input_params_dict.get(SettingLiterals.IMAGE_MAX_SIZE, None)
            if image_min_size and image_max_size and image_min_size > 0 and image_max_size > 0:
                # Image min and max size are specified in component yaml, use them
                # else use the values from model's config.
                constraint_resize_params_dict = {
                    self.augmentation_param_names_cls.CONSTRAINT_RESIZE_KEY: (
                        image_max_size, image_min_size
                    )
                }
            else:
                # update img_scale and keep_ratio parameters from model's config.
                # This is required for MMdetection constraint resize transformation.
                constraint_resize_params_dict = self.get_image_scale_from_model_preproc_params(
                    phase_name=phase_name
                )
            return constraint_resize_params_dict
        elif (
            augmentation_function_name.lower()
            == self.augmentation_param_names_cls.PAD_IF_NEEDED_FUNC_NAME.lower()
        ):
            # update pad size divisor
            pad_size_divisor = self.get_pad_size_divisor_from_model_preproc_params()
            return pad_size_divisor

        return dict()


class HfModelPreProcExtractor(ModelPreProcExtractor):
    """Helper class to extract parameter update (dict) from model preprocessing config for HF"""

    def __init__(
        self, model_preprocessing_params: dict, augmentation_library_name: str
    ) -> None:
        """Helper class to extract parameter update from model preprocessing config.
        And, overwritting with the task input values if provided.

        :param model_preprocessing_params: models's preprocessing parameters dict
                - image_processor.to_dict() containing preprocess_config.json in case of HF
                - dict containing preprocessing params in case of other frameworks
                - dict containing preprocessing params in case of other approaches for augmentation,
                  this key:value pairs in the dict can be used while preparing transforms.
        :type model_preprocessing_params: dict
        :param augmentation_library_name: Name of augmentation lib from augmentatin config.
        :type augmentation_library_name: str

        :return: None
        :rtype: None
        """
        super().__init__(
            model_preprocessing_params=model_preprocessing_params,
            augmentation_library_name=augmentation_library_name,
        )

    def get_height_width_from_model_preproc_params(self) -> Dict[str, int]:
        """ Get height/width from feature extractor

        :return: A dictionary containing height and width extracted form feature extractor / preprocess_config
        :rtype: dict
        """

        if HfProcessorParamNames.SIZE_KEY not in self.model_preprocessing_params:
            logger.error(
                f"{HfProcessorParamNames.SIZE_KEY} is not present in model preprocess config - "
                f"{self.model_preprocessing_params}. "
                f"We don't know what size to use for the model."
            )
            raise KeyError(
                f"{HfProcessorParamNames.SIZE_KEY} is not present in model preprocess config - "
                f"{self.model_preprocessing_params}. "
                f"We don't know what size to use for the model."
            )

        # get the model specific height/width from preprocess_config
        # The general order in which the transforms are applied in HF
        # RGB -> resize -> center_crop -> rescale -> normalize
        if (
            HfProcessorParamNames.DO_CENTER_CROP_KEY in self.model_preprocessing_params
            and self.model_preprocessing_params[
                HfProcessorParamNames.DO_CENTER_CROP_KEY
            ]
            and HfProcessorParamNames.CROP_SIZE_KEY in self.model_preprocessing_params
        ):
            if isinstance(
                self.model_preprocessing_params[HfProcessorParamNames.CROP_SIZE_KEY],
                dict,
            ):
                size_dict = self.model_preprocessing_params[
                    HfProcessorParamNames.CROP_SIZE_KEY
                ]
                height = size_dict[HfProcessorParamNames.HEIGHT_KEY]
                width = size_dict[HfProcessorParamNames.WIDTH_KEY]
            else:
                height = self.model_preprocessing_params[
                    HfProcessorParamNames.CROP_SIZE_KEY
                ]
                width = self.model_preprocessing_params[
                    HfProcessorParamNames.CROP_SIZE_KEY
                ]

        elif (
            HfProcessorParamNames.DO_RESIZE_KEY in self.model_preprocessing_params
            and self.model_preprocessing_params[HfProcessorParamNames.DO_RESIZE_KEY]
            and HfProcessorParamNames.SIZE_KEY in self.model_preprocessing_params
        ):
            if isinstance(
                self.model_preprocessing_params[HfProcessorParamNames.SIZE_KEY], dict
            ):
                size_dict = self.model_preprocessing_params[
                    HfProcessorParamNames.SIZE_KEY
                ]
                if (
                    HfProcessorParamNames.HEIGHT_KEY in size_dict
                    and HfProcessorParamNames.WIDTH_KEY in size_dict
                ):
                    height = size_dict[HfProcessorParamNames.HEIGHT_KEY]
                    width = size_dict[HfProcessorParamNames.WIDTH_KEY]
                elif (
                    HfProcessorParamNames.SHORTEST_EDGE_KEY in size_dict
                    and HfProcessorParamNames.LONGEST_EDGE_KEY not in size_dict
                ):
                    height = size_dict[HfProcessorParamNames.SHORTEST_EDGE_KEY]
                    width = size_dict[HfProcessorParamNames.SHORTEST_EDGE_KEY]
                elif (
                    HfProcessorParamNames.SHORTEST_EDGE_KEY not in size_dict
                    and HfProcessorParamNames.LONGEST_EDGE_KEY in size_dict
                ):
                    height = size_dict[HfProcessorParamNames.LONGEST_EDGE_KEY]
                    width = size_dict[HfProcessorParamNames.LONGEST_EDGE_KEY]
                elif (
                    HfProcessorParamNames.SHORTEST_EDGE_KEY in size_dict
                    and HfProcessorParamNames.LONGEST_EDGE_KEY in size_dict
                ):
                    # Todo - which side is height/width? Or, how should we handle it?
                    height = size_dict[HfProcessorParamNames.SHORTEST_EDGE_KEY]
                    width = size_dict[HfProcessorParamNames.SHORTEST_EDGE_KEY]
            else:
                height = self.model_preprocessing_params[HfProcessorParamNames.SIZE_KEY]
                width = self.model_preprocessing_params[HfProcessorParamNames.SIZE_KEY]

        else:
            logger.error(
                f"Neither {HfProcessorParamNames.CROP_SIZE_KEY}, nor {HfProcessorParamNames.SIZE_KEY} "
                f"is being used in preprocess_config.json of the model. Please check model's"
                f"preprocess_config.json file."
            )
            raise KeyError(
                f"Neither {HfProcessorParamNames.CROP_SIZE_KEY}, nor {HfProcessorParamNames.SIZE_KEY} "
                f"is being used in preprocess_config.json of the model. Please check model's"
                f"preprocess_config.json file."
            )

        height_width_dict = {
            self.augmentation_param_names_cls.HEIGHT_KEY: height,
            self.augmentation_param_names_cls.WIDTH_KEY: width,
        }
        return height_width_dict

    def get_mean_std_from_model_preproc_params(self, **kwargs) -> Dict[str, List[float]]:
        """ Get mean/std from model config for HF

        :param phase_name: Name of the phase - train/valid.
        :type phase_name: str
        :return: A dictionary containing height and width extracted from model config
        :rtype: dict
        """
        mean_std_dict = {
            self.augmentation_param_names_cls.MEAN_KEY: self.model_preprocessing_params.get(
                HfProcessorParamNames.MEAN_KEY
            ),
            self.augmentation_param_names_cls.STD_KEY: self.model_preprocessing_params.get(
                HfProcessorParamNames.STD_KEY
            ),
        }
        return mean_std_dict


class MmLabModelPreProcExtractor(ModelPreProcExtractor):
    """Helper class to extract parameter update (dict) from model preprocessing config for MMLAB"""

    def __init__(
        self, model_preprocessing_params: dict, augmentation_library_name: str
    ) -> None:
        """Helper class to extract parameter update from model preprocessing config.
        And, overwritting with the task input values if provided.

        :param model_preprocessing_params: models's preprocessing parameters dict
                - image_processor.to_dict() containing preprocess_config.json in case of HF
                - dict containing preprocessing params in case of other frameworks
                - dict containing preprocessing params in case of other approaches for augmentation,
                  this key:value pairs in the dict can be used while preparing transforms.
        :type model_preprocessing_params: dict
        :param augmentation_library_name: Name of augmentation lib from augmentatin config.
        :type augmentation_library_name: str

        :return: None
        :rtype: None
        """
        super().__init__(
            model_preprocessing_params=model_preprocessing_params,
            augmentation_library_name=augmentation_library_name,
        )

    def get_mean_std_from_model_preproc_params(self, **kwargs) -> Dict[str, List[float]]:
        """ Get mean/std from model config for MMLAB

        :return: A dictionary containing mean and std extracted from model config
        :rtype: dict
        """
        mean_std_dict = {
            self.augmentation_param_names_cls.MEAN_KEY: self.model_preprocessing_params.get(
                MmLabPreprocessorParamNames.MEAN_KEY
            ),
            self.augmentation_param_names_cls.STD_KEY: self.model_preprocessing_params.get(
                MmLabPreprocessorParamNames.STD_KEY
            ),
        }
        return mean_std_dict


class MMDModelPreProcExtractor(ModelPreProcExtractor):
    """Helper class to extract parameter update (dict) from model preprocessing config for MMDetection"""

    def __init__(
        self, model_preprocessing_params: dict, augmentation_library_name: str
    ) -> None:
        """Helper class to extract parameter update (dict) from model preprocessing config for MMDetection.

        :param model_preprocessing_params: models's preprocessing parameters dict
            - dict containing preprocessing params in case of other frameworks
            - dict containing preprocessing params in case of other approaches for augmentation,
                this key:value pairs in the dict can be used while preparing transforms.
        :type model_preprocessing_params: dict
        :param augmentation_library_name: Name of augmentation lib from augmentatin config.
        :type augmentation_library_name: str

        :return: None
        :rtype: None
        """
        super().__init__(
            model_preprocessing_params=model_preprocessing_params,
            augmentation_library_name=augmentation_library_name,
        )

    def get_model_preprocessing_params(self, phase_name: str) -> Dict[str, Any]:
        """Get model preprocessing params for MMDetection
        :param phase_name: Name of the phase - train/valid.
        :type phase_name: str

        :return: A dictionary containing model preprocessing params
        :rtype: dict
        """
        # to handle circular dependency
        from azureml.acft.image.components.finetune.mmdetection.common.constants import (
            MmDetectionConfigLiterals
        )

        phase_name_mapping = {
            AugmentationConfigKeys.TRAINING_PHASE_KEY: MmDetectionConfigLiterals.TRAIN_PIPELINE,
            AugmentationConfigKeys.VALIDATION_PHASE_KEY: MmDetectionConfigLiterals.TEST_PIPELINE,
            "val": "val",
            AugmentationConfigKeys.MODEL_KEY: MmDetectionConfigLiterals.MODEL
        }
        if phase_name in phase_name_mapping:
            mapped_phase = phase_name_mapping[phase_name]
            return self.model_preprocessing_params.get(mapped_phase, None)
        return None

    def _get_step_by_name(self, pipeline: List, step_name: str) -> Dict:
        """ Get the desired step from the given list of steps
        :param pipeline: List of transformation steps
        :param type: List
        :param step_name
        :param type: str

        :return: A dictionary containing the step
        :rtype: Dict
        """
        if not pipeline:
            return {}
        for step in pipeline:
            if isinstance(step, list):
                for item in step:
                    if item.get('type', None) == step_name:
                        return item
            elif isinstance(step, dict) and step['type'] == step_name:
                return step
            else:
                transforms = step.get(MmDetectionPreprocessorParamNames.TRANSFORMS, [])
                if transforms:
                    normalization_step = self._get_step_by_name(transforms, step_name)
                    if normalization_step:
                        return normalization_step
        return {}

    def get_pad_size_divisor_from_model_preproc_params(self) -> Dict[str, int]:
        """ Get pad_size_divisor from model's preprocessing params

        :return: A integer denoting the required pad size divisor for the model.
        :rtype: dict
        """
        model_preprocessing_params = self.get_model_preprocessing_params(AugmentationConfigKeys.MODEL_KEY)
        if model_preprocessing_params:
            data_preprocess = model_preprocessing_params[MmDetectionPreprocessorParamNames.DATA_PREPROCESSOR]
            if not data_preprocess or MmDetectionPreprocessorParamNames.PAD_SIZE_DIVISOR not in data_preprocess:
                return {}
            pad_size_divisor = data_preprocess.get(MmDetectionPreprocessorParamNames.PAD_SIZE_DIVISOR)
            pad_size_divisor_dict = {
                self.augmentation_param_names_cls.PAD_HEIGHT_DIVISOR_KEY: pad_size_divisor,
                self.augmentation_param_names_cls.PAD_WIDTH_DIVISOR_KEY: pad_size_divisor,
            }
            return pad_size_divisor_dict
        return {}

    def get_mean_std_from_model_preproc_params(self, **kwargs) -> Dict[str, List[float]]:
        """ Get mean/std for normalization from model config for MMDetection

        :param phase_name: Whether it is training phase or test
        :param type: str

        :return: A dictionary containing mean and std extracted from model config
        :rtype: dict
        """
        model_preprocessing_params = self.get_model_preprocessing_params(AugmentationConfigKeys.MODEL_KEY)
        if model_preprocessing_params:
            data_preprocess = model_preprocessing_params[MmDetectionPreprocessorParamNames.DATA_PREPROCESSOR]
            if not data_preprocess or MmDetectionPreprocessorParamNames.MEAN_KEY not in data_preprocess:
                return {}
            mean = data_preprocess.get(MmDetectionPreprocessorParamNames.MEAN_KEY)
            std = data_preprocess.get(MmDetectionPreprocessorParamNames.STD_KEY)
            to_rgb = data_preprocess.get(MmDetectionPreprocessorParamNames.TO_RGB_KEY, True)
            if not to_rgb:
                # Whether to convert the image from BGR to RGB
                mean = mean[::-1]
                std = std[::-1]

            if max(mean) > 1:
                # If mean and std values are > 1, normalize them to get them on scale between 0 and 1.
                mean = [round(x / 255, 3) for x in mean]
                std = [round(x / 255, 3) for x in std]

            mean_std_dict = {
                self.augmentation_param_names_cls.MEAN_KEY: mean,
                self.augmentation_param_names_cls.STD_KEY: std,
            }
            return mean_std_dict
        return {}

    def get_height_width_from_model_preproc_params(self) -> Dict[str, int]:
        """ Get height/width from feature extractor

        :return: A dictionary containing height and width extracted form feature extractor / preprocess_config
        :rtype: dict
        """
        # Returning empty since these height and width are not used in MMDetection. Instead, we resize it to
        # image_scale which is a range of sizes (min_size, max_size)
        return {}

    def get_image_scale_from_model_preproc_params(self, phase_name: str) -> Dict[str, Any]:
        """ Get parameters for resizing the image from preprocess_config.
        This will overwrite the ConstriantResize transform parameters.

        :param phase_name: Whether it is training phase or test
        :param type: str

        :return: A dictionary containing img_scale and/or keep_ratio extracted from
         feature extractor / preprocess_config
        :rtype: dict
        """

        model_preprocessing_params = self.get_model_preprocessing_params(phase_name)
        if model_preprocessing_params:
            resize_step = self._get_step_by_name(model_preprocessing_params, MmDetectionPreprocessorParamNames.RESIZE)
            aug_constants = self.augmentation_param_names_cls
            if not resize_step:
                # return empty dict if resize step is not present.
                return {}
            constraint_resize_params_dict = {}

            if aug_constants.KEEP_RATIO in resize_step:
                constraint_resize_params_dict = {
                    **constraint_resize_params_dict,
                    aug_constants.KEEP_RATIO: resize_step.get(aug_constants.KEEP_RATIO),
                }
            # Get img_scale from resize step or MULTISCALE_FLIP_AUG step
            if aug_constants.CONSTRAINT_RESIZE_KEY in resize_step:
                # Get img_scale from resize step
                constraint_resize_params_dict = {
                    **constraint_resize_params_dict,
                    aug_constants.CONSTRAINT_RESIZE_KEY: resize_step.get(aug_constants.CONSTRAINT_RESIZE_KEY)
                }
            else:
                # Get img_scale from MULTISCALE_FLIP_AUG step
                multiscale_aug_step = self._get_step_by_name(
                    model_preprocessing_params, MmDetectionPreprocessorParamNames.MULTISCALE_FLIP_AUG
                )
                if aug_constants.CONSTRAINT_RESIZE_KEY in multiscale_aug_step:
                    constraint_resize_params_dict = {
                        **constraint_resize_params_dict,
                        aug_constants.CONSTRAINT_RESIZE_KEY: multiscale_aug_step.get(
                            aug_constants.CONSTRAINT_RESIZE_KEY
                        )
                    }

            return constraint_resize_params_dict
        return {}
