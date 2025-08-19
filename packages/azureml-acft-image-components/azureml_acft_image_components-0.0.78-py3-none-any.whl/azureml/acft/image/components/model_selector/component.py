# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""AzureML ACFT Image Components - model selector component code."""
import glob
import json
import os
from azureml.acft.common_components.utils.license_utils import save_license_file
from azureml.acft.image.components.common.utils import download_file
import yaml
from os.path import dirname
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore

from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.model_selector.component import ModelSelector
from azureml.acft.common_components.model_selector.constants import (
    ModelSelectorDefaults,
    ModelSelectorConstants,
    ModelRepositoryURLs,
)
from azureml.acft.common_components.utils.constants import MlflowMetaConstants
from azureml.acft.common_components.utils.error_handling.error_definitions import (
    ACFTUserError,
    ACFTSystemError,
    ValidationError,
)
from azureml.acft.common_components.utils.error_handling.exceptions import (
    ACFTValidationException,
    ACFTSystemException,
)
from azureml.acft.image.components.finetune.factory.mappings import MODEL_FAMILY_CLS
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune import (
    UNSUPPORTED_HF_MODEL,
    UNSUPPORTED_MMDETECTION_MODEL,
    UNSUPPORTED_MMTRACKING_MODEL,
)
from azureml.acft.image.components.model_selector.constants import (
    ImageModelSelectorConstants,
    MMDetectionModelZooConfigConstants,
    MMDSupportedTasks,
    MMTSupportedTasks,
)


logger = get_logger_app(__name__)


class ImageModelSelector(ModelSelector):
    """Implementation for image model selector."""

    def __init__(
        self,
        pytorch_model: str = None,
        mlflow_model: str = None,
        model_family: str = None,
        model_name: str = None,
        output_dir: str = None,
        download_from_source: bool = False,
        **kwargs,
    ) -> None:
        """Implementation for image model selector.

        :param pytorch_model: asset path of pytorch model, defaults to None
        :type pytorch_model: str, optional
        :param mlflow_model: asset path of mlflow model, defaults to None
        :type mlflow_model: str, optional
        :param model_family: model family (like HuggingFace, MMDetection), defaults to None
        :type model_family: str, optional
        :param model_name: model name from the framework (i.e., HF), defaults to None
        :type model_name: str, optional
        :param output_dir: path to store arguments and model, defaults to None
        :type output_dir: str, optional
        """
        unsupported_model_list = []
        if model_family == MODEL_FAMILY_CLS.HUGGING_FACE_IMAGE:
            unsupported_model_list = UNSUPPORTED_HF_MODEL
        elif model_family == MODEL_FAMILY_CLS.MMDETECTION_IMAGE:
            unsupported_model_list = UNSUPPORTED_MMDETECTION_MODEL
        elif model_family == MODEL_FAMILY_CLS.MMTRACKING_VIDEO:
            unsupported_model_list = UNSUPPORTED_MMTRACKING_MODEL
        super().__init__(
            pytorch_model=pytorch_model,
            mlflow_model=mlflow_model,
            model_name=model_name,
            output_dir=output_dir,
            model_family=model_family,
            unsupported_model_list=unsupported_model_list,
            download_from_source=download_from_source,
            **kwargs,
        )

    def _is_acft_model(self):
        """Check whether i/p model is an acft model"""
        is_acft_model = False
        if self.mlflow_model:
            is_acft_model = self.metadata.get(MlflowMetaConstants.IS_ACFT_MODEL, False)
        elif self.pytorch_model:
            # pytorch models that are produced by finetuning components(hf trainer) contain pytorch_model.bin
            model_path = os.path.join(
                self.output_dir, ModelSelectorDefaults.PYTORCH_MODEL_DIRECTORY
            )
            checkpoint_file = os.path.join(
                model_path, ModelSelectorDefaults.MODEL_CHECKPOINT_FILE_NAME
            )
            is_acft_model = os.path.isfile(checkpoint_file)

        model_type = "acft_model" if is_acft_model else "non_acft_model"
        logger.info(f"Input model type: {model_type}")
        return is_acft_model

    def _is_mmd_2x_model(self, config_file_path) -> None:
        """Validate if it is MMD 2.x model."""
        if (
            os.path.exists(config_file_path)
            and self.model_family == MODEL_FAMILY_CLS.MMDETECTION_IMAGE
        ):
            # Check and warn if it is MMD 2.x model.
            with open(config_file_path, "r") as f:
                config_data = f.read()
                # In MMD 3.x model config, img_norm_cfg is moved to data_preprocessor.
                # Source: https://mmdetection.readthedocs.io/en/latest/migration/config_migration.html
                if (
                    "img_norm_cfg" in config_data
                    and "data_preprocessor" not in config_data
                ):
                    error_string = (
                        f"Model {self.model_name} is a MMDetection 2.x model and this component"
                        " only supports MMDectection 3.x models. We strongly recommend MMD 3.x models from the"
                        " model zoo but if 2.x models need be finetuned, use finetuning component version <=0.0.8"
                    )
                    raise ACFTValidationException._with_error(
                        AzureMLError.create(
                            ACFTUserError, pii_safe_message=error_string
                        )
                    )

    def raise_relevant_error(self, error_string):
        """raise system/user error based on model_type.

        :param error_string: error string to be logged
        :type error_string: str
        """
        logger.error(error_string)
        if not self.is_acft_model:
            raise ACFTValidationException._with_error(
                AzureMLError.create(ACFTUserError, pii_safe_message=error_string)
            )
        else:
            raise ACFTSystemException._with_error(
                AzureMLError.create(ACFTSystemError, pii_safe_message=error_string)
            )

    def _prepare_mmlab_arguments_from_input_model(self) -> dict:
        """Prepare arguments for MMLAB/MMDetection models.

        :return: A dictinary conatining argument name to value mapping to update.
        :rtype: dictionary
        """
        input_model_path = None
        if self.pytorch_model is not None:
            input_model_path = self.pytorch_model
        elif self.mlflow_model is not None:
            input_model_path = self.mlflow_model

        abs_input_model_path = os.path.join(self.output_dir, input_model_path)

        model_metafile_json_path = os.path.join(
            abs_input_model_path, ImageModelSelectorConstants.MODEL_METAFILE_NAME
        )
        if os.path.exists(model_metafile_json_path):
            # If model_metafile.json exists, then read the model name from it.
            with open(model_metafile_json_path, "r") as jsonFile:
                model_metadata = json.load(jsonFile)

            for name in [
                ModelSelectorConstants.FINETUNING_TASKS,
                ModelSelectorConstants.MODEL_NAME,
            ]:
                if name not in model_metadata:
                    error_string = (
                        f"Ensure provided model path {input_model_path} contains "
                        f"{ImageModelSelectorConstants.MODEL_METAFILE_NAME} with "
                        f"{name} in it."
                    )
                    self.raise_relevant_error(error_string)
            if (
                self.model_name is not None
                and self.model_name != model_metadata[ModelSelectorConstants.MODEL_NAME]
            ):
                error_string = (
                    f"Ensure provided model_name ({self.model_name}) matches with what's in "
                    f"{ImageModelSelectorConstants.MODEL_METAFILE_NAME} - "
                    f"{model_metadata[ModelSelectorConstants.MODEL_NAME]}."
                )
                self.raise_relevant_error(error_string)
            else:
                self.model_name = model_metadata[ModelSelectorConstants.MODEL_NAME]
        else:
            error_string = (
                f"Input model path {input_model_path} does not contain "
                f"{ImageModelSelectorConstants.MODEL_METAFILE_NAME}."
            )
            self.raise_relevant_error(error_string)

        self.model_name = (
            self.model_name
            if not self.model_name.endswith(".py")
            else self.model_name[:-3]
        )

        if self.model_name is None:
            error_string = (
                f"We could not identify {ModelSelectorConstants.MODEL_NAME}'s value {self.model_name}. "
                f"Ensure to either pass model name in {ModelSelectorConstants.MODEL_NAME}, or in "
                f"{ImageModelSelectorConstants.MODEL_METAFILE_NAME} as "
                f"{{{ModelSelectorConstants.MODEL_NAME}: <NAME_OF_MODEL>}}"
            )
            self.raise_relevant_error(error_string)
        self.model_name = (
            self.model_name
            if not self.model_name.endswith(".py")
            else self.model_name[:-3]
        )

        abs_mmlab_config_path = os.path.join(
            abs_input_model_path, f"{self.model_name}.py"
        )
        # Assume that model config is in the parent folder
        mmlab_config_path = abs_mmlab_config_path.replace(
            abs_input_model_path, input_model_path
        )
        # Check existance of mmlab config python file
        if not os.path.exists(abs_mmlab_config_path):
            error_string = (
                f"Ensure that {self.model_name}.py exists in your registered input model folder. "
                f"Found list of files: {os.listdir(abs_input_model_path)}"
            )
            self.raise_relevant_error(error_string)
        self._is_mmd_2x_model(abs_mmlab_config_path)
        # Get the model weight file path
        checkpoint_files = glob.glob(
            os.path.join(abs_input_model_path, "*.pth"), recursive=True
        )
        if len(checkpoint_files) == 0:
            checkpoint_files = glob.glob(
                os.path.join(
                    abs_input_model_path,
                    ModelSelectorDefaults.MODEL_CHECKPOINT_FILE_NAME,
                ),
                recursive=True,
            )
        if len(checkpoint_files) != 1:
            error_string = (
                f"Ensure that you have only one .pth or {ModelSelectorDefaults.MODEL_CHECKPOINT_FILE_NAME} "
                f"checkpoint file in your registered model. Found {len(checkpoint_files)}"
            )
            self.raise_relevant_error(error_string)
        # Assume checkpoint is in the parent folder
        checkpoint_file_name = checkpoint_files[0].replace(
            abs_input_model_path, input_model_path
        )

        if self.pytorch_model is not None:
            self.pytorch_model = mmlab_config_path
        elif self.mlflow_model is not None:
            self.mlflow_model = mmlab_config_path

        # copy license file
        save_license_file(
            model_name_or_path=input_model_path,
            license_file_name=ModelSelectorDefaults.LICENSE_FILE_NAME,
            destination_paths=[abs_input_model_path],
        )

        self.metadata.update(**model_metadata)
        return {
            ModelSelectorConstants.MODEL_NAME: self.model_name,
            ModelSelectorConstants.MLFLOW_MODEL_PATH: self.mlflow_model,
            ModelSelectorConstants.PYTORCH_MODEL_PATH: self.pytorch_model,
            ImageModelSelectorConstants.MMLAB_MODEL_WEIGHTS_PATH_OR_URL: checkpoint_file_name,
            ModelSelectorConstants.MODEL_METADATA: self.metadata,
        }

    def _load_and_save_mm_config_file(self, mm_config_file: str) -> str:
        """Load and save MMLAB/MMDetection config file
        :param mm_config_file: path to MMLAB/MMDetection config file in repository
        :type mm_config_file: str
        :return: config file name
        :rtype: str
        """
        from mmengine.config import Config

        config = Config.fromfile(mm_config_file)
        file_name = os.path.join(
            ModelSelectorDefaults.PYTORCH_MODEL_DIRECTORY, self.model_name + ".py"
        )
        config.dump(os.path.join(self.output_dir, file_name))
        return file_name

    def _fetch_finetuning_tasks(self, model_data: dict) -> list:
        """Fetch finetuning tasks from model_data

        :param model_data: model_data
        :type model_data: dict
        :return: list of finetuning tasks
        :rtype: list
        """
        finetuning_tasks = [
            result[MMDetectionModelZooConfigConstants.TASK].lower()
            for result in model_data[MMDetectionModelZooConfigConstants.RESULTS]
        ]

        # supporting object detection and instance segmentation
        if self.model_family == MODEL_FAMILY_CLS.MMDETECTION_IMAGE:
            for task in finetuning_tasks:
                if task not in [
                    MMDSupportedTasks.OBJECT_DETECTION,
                    MMDSupportedTasks.INSTANCE_SEGMENTATION,
                ]:
                    error_string = (
                        f"Finetuning for {MMDSupportedTasks.OBJECT_DETECTION}/"
                        f"{MMDSupportedTasks.INSTANCE_SEGMENTATION} is supported."
                        f"Provided Model: {self.model_name} supports {task}"
                    )
                    logger.error(error_string)
                    raise ACFTValidationException._with_error(
                        AzureMLError.create(
                            ACFTUserError, pii_safe_message=error_string
                        )
                    )
        elif self.model_family == MODEL_FAMILY_CLS.MMTRACKING_VIDEO:
            for task in finetuning_tasks:
                if task not in [MMTSupportedTasks.MULTI_OBJECT_TRACKING]:
                    error_string = (
                        f"Finetuning for {MMTSupportedTasks.MULTI_OBJECT_TRACKING}  is supported."
                        f"Provided Model: {self.model_name} supports {task}"
                    )
                    logger.error(error_string)
                    raise ACFTValidationException._with_error(
                        AzureMLError.create(
                            ACFTUserError, pii_safe_message=error_string
                        )
                    )

        # models which support instance_segmentation always expects gt_masks from the data.
        # results in model_data contain od but finetuning for od is not supported.
        if MMDSupportedTasks.INSTANCE_SEGMENTATION in finetuning_tasks:
            finetuning_tasks = [MMDSupportedTasks.INSTANCE_SEGMENTATION]

        return finetuning_tasks

    def _prepare_mmlab_arguments_from_model_zoo_config(self) -> dict:
        """Prepared arguments for MMLAB/MMDetection models using the model name as in MMDetection model zoo.

        :return: A dictinary conatining argument name to value mapping to update.
        :rtype: dictionary
        """
        if (
            self.pytorch_model is None
            and self.mlflow_model is None
            and self.model_name is None
        ):
            error_string = (
                "All, model_name, mlflow_model, pytorch_model can not be None at the same time."
                "Please provide either a model via pytorch_model or mlflow_model port; Or, "
                "provide name of the model from MMDetection model zoo, as specified in respective model"
                "family's metafile.yaml."
            )
            raise ACFTValidationException._with_error(
                AzureMLError.create(ValidationError, error=error_string)
            )

        abs_config_folder_path = self._get_config_path()

        meta_file = ImageModelSelector._search_model_name_in_mmd_model_zoo(
            self.model_name, abs_config_folder_path, self._get_model_zoo_link()
        )
        model_data = None
        if meta_file is not None:
            # read yml file and get the model data
            with open(meta_file, "r") as f:
                metafile_dict = yaml.safe_load(f)
                models_dict_list = (
                    metafile_dict
                    if isinstance(metafile_dict, list)
                    else metafile_dict[
                        MMDetectionModelZooConfigConstants.MODEL_ZOO_MODELS
                    ]
                )
                for model in models_dict_list:
                    if (
                        self.model_name
                        == model[
                            MMDetectionModelZooConfigConstants.MODEL_ZOO_MODEL_NAME
                        ]
                    ):
                        model_data = model
                        break
        else:
            error_string = f"Not able to find the meta file {meta_file}."
            raise ACFTValidationException._with_error(
                AzureMLError.create(ValidationError, error=error_string)
            )

        if model_data is None:
            error_string = (
                f"Ensure that {self.model_name} data exists in the meta file."
            )
            raise ACFTValidationException._with_error(
                AzureMLError.create(ValidationError, error=error_string)
            )
        abs_mmlab_config_path = os.path.join(
            dirname(abs_config_folder_path),
            model_data[MMDetectionModelZooConfigConstants.MODEL_ZOO_CONFIG],
        )

        if not os.path.exists(abs_mmlab_config_path):
            error_string = (
                f"Ensure that {self.model_name}.py exists in the model zoo configs folder. "
                f"The model zoo used is the following:{self._get_model_zoo_link()}."
            )
            raise ACFTValidationException._with_error(
                AzureMLError.create(ValidationError, error=error_string)
            )

        if self.model_name.endswith(".py"):
            self.model_name = self.model_name[:-3]

        os.makedirs(
            os.path.join(
                self.output_dir, ModelSelectorDefaults.PYTORCH_MODEL_DIRECTORY
            ),
            exist_ok=True,
        )

        self.pytorch_model = self._load_and_save_mm_config_file(abs_mmlab_config_path)
        self._is_mmd_2x_model(os.path.join(self.output_dir, self.pytorch_model))

        # Get the model weight file path
        url = model_data.get(MMDetectionModelZooConfigConstants.MODEL_ZOO_WEIGHTS, None)
        if not url:
            error_str = (
                f"{MMDetectionModelZooConfigConstants.MODEL_ZOO_WEIGHTS} key is not found in the"
                f"metafile: {meta_file}. please select any other model for image finetuning."
            )
            logger.error(error_str)
            raise ACFTValidationException._with_error(
                AzureMLError.create(ValidationError, error=error_str)
            )
        weights_file_name = os.path.join(
            ModelSelectorDefaults.PYTORCH_MODEL_DIRECTORY,
            self.model_name + "_weights.pth",
        )
        # download the file
        download_file(url, os.path.join(self.output_dir, weights_file_name))

        # fetch fine tuning tasks to dump in the model_metafile
        finetuning_tasks = self._fetch_finetuning_tasks(model_data)
        self.metadata.update(
            {ModelSelectorConstants.FINETUNING_TASKS: finetuning_tasks}
        )

        model_metadata_path = os.path.join(
            ModelSelectorDefaults.PYTORCH_MODEL_DIRECTORY,
            ModelSelectorDefaults.MODEL_METADATA_PATH,
        )
        model_metadata_dict = {
            ModelSelectorConstants.MODEL_NAME: self.model_name,
            ModelSelectorConstants.FINETUNING_TASKS: finetuning_tasks,
        }
        if not os.path.exists(os.path.join(self.output_dir, model_metadata_path)):
            # only dump the model metadata if it does not exist
            with open(os.path.join(self.output_dir, model_metadata_path), "w") as fp:
                json.dump(model_metadata_dict, fp)

        return {
            ModelSelectorConstants.MODEL_NAME: self.model_name,
            ModelSelectorConstants.MLFLOW_MODEL_PATH: self.mlflow_model,
            ModelSelectorConstants.PYTORCH_MODEL_PATH: self.pytorch_model,
            ImageModelSelectorConstants.MMLAB_MODEL_WEIGHTS_PATH_OR_URL: weights_file_name,
            ModelSelectorConstants.MODEL_METADATA: self.metadata,
            ModelSelectorConstants.MODEL_METAFILE_PATH: model_metadata_path,
        }

    def _prepare_mmlab_arguments(self) -> dict:
        """Prepare an update for the keyword arguments (if present) with required key-val items for MMLab/MMDetection
        models.

        :return: A dictinary conatining argument name to value mapping to update.
        :rtype: dictionary
        """

        if self.pytorch_model is not None or self.mlflow_model is not None:
            return self._prepare_mmlab_arguments_from_input_model()
        else:
            return self._prepare_mmlab_arguments_from_model_zoo_config()

    def _prepare_and_logs_arguments(self) -> None:
        """Update the keyword arguments (if present) with required key-val items and
        Store the model selector arguments to json file.
        """

        self.is_acft_model = self._is_acft_model()
        if self.is_acft_model:
            task_type = self.metadata.get(MlflowMetaConstants.FINETUNING_TASK, None)
            # check if the input model supports image finetuning tasks
            if task_type and task_type not in [i for i in Tasks.__dict__.values()]:
                error_string = "Input model does not support finetuning of image tasks"
                raise ACFTValidationException._with_error(
                    AzureMLError.create(ACFTUserError, pii_safe_message=error_string)
                )

        arguments = {
            ModelSelectorConstants.MLFLOW_MODEL_PATH: self.mlflow_model,
            ModelSelectorConstants.PYTORCH_MODEL_PATH: self.pytorch_model,
            ModelSelectorConstants.MODEL_NAME: self.model_name,
            ImageModelSelectorConstants.MODEL_FAMILY: self.model_family,
            ModelSelectorConstants.MODEL_METADATA: self.metadata,
        }

        if self.model_family in (
            MODEL_FAMILY_CLS.MMDETECTION_IMAGE,
            MODEL_FAMILY_CLS.MMTRACKING_VIDEO,
        ):
            arguments.update(self._prepare_mmlab_arguments())

        if self.keyword_arguments:
            self.keyword_arguments.update(arguments)
        else:
            self.keyword_arguments = arguments

        os.makedirs(self.output_dir, exist_ok=True)
        model_selector_args_save_path = os.path.join(
            self.output_dir, ModelSelectorDefaults.MODEL_SELECTOR_ARGS_SAVE_PATH
        )
        logger.info(
            f"Saving the model selector args to {model_selector_args_save_path}"
        )
        with open(model_selector_args_save_path, "w") as output_file:
            json.dump(self.keyword_arguments, output_file, indent=2)

    @staticmethod
    def _search_model_name_in_mmd_model_zoo(
        model_name, config_path=None, model_zoo_link=None
    ):
        """
        Search for model name in all the metafile.yaml files present in model zoo configs folder
        """
        if config_path is None:  # set mmd path as default
            config_path = ImageModelSelector._get_mmdet_config_path()
        for dirpath, _, filenames in os.walk(config_path):
            for file_name in filenames:
                file_path = os.path.abspath(os.path.join(dirpath, file_name))
                if file_path.endswith("metafile.yml"):
                    with open(file_path, "r") as metafile:
                        metafile_dict = yaml.safe_load(metafile)
                        models_dict_list = (
                            metafile_dict
                            if isinstance(metafile_dict, list)
                            else metafile_dict[
                                MMDetectionModelZooConfigConstants.MODEL_ZOO_MODELS
                            ]
                        )
                        for model_config in models_dict_list:
                            if (
                                model_config[
                                    MMDetectionModelZooConfigConstants.MODEL_ZOO_MODEL_NAME
                                ]
                                and model_config[
                                    MMDetectionModelZooConfigConstants.MODEL_ZOO_MODEL_NAME
                                ].lower()
                                == model_name.lower()
                            ):
                                return file_path

        if model_name.startswith(ModelSelectorDefaults.FAST_RCNN_MODEL_PREFIX):
            error_string = (
                f"{model_name} seems to be fast-rcnn model since the model name starts with "
                f"{ModelSelectorDefaults.FAST_RCNN_MODEL_PREFIX} "
                f"The fast-rcnn family of models should be trained with RPN family of models, therefore "
                f"please use a model name from the RPN family of models. For more details, please refer to "
                f"{ModelRepositoryURLs.MMDETECTION}/fast_rcnn#introduction"
            )
        else:
            error_string = (
                f"Model {model_name} was not found in the metafile.yml files of the model zoo "
                f"configs folder. Please use a valid model name from the model zoo."
            )
            if model_zoo_link is not None:
                error_string += (
                    f"The model zoo used is the following:{model_zoo_link}.To find the correct "
                    f"model name, go to {model_zoo_link}, click on the model type, and you will find the "
                    f"model name in the metafile.yml file which is present at "
                    f"configs/<MODEL_TYPE>/metafile.yml location."
                )

        raise ACFTValidationException._with_error(
            AzureMLError.create(ACFTUserError, pii_safe_message=error_string)
        )

    @staticmethod
    def _get_mmdet_config_path() -> str:
        """Get the path to the MMDetection config file.

        :return: Path to the MMDetection config file.
        :rtype: str
        """
        import mmdet

        # Note: mmdet should be installed via mim to access the model zoo config folder.
        CONFIG_FOLDER_PATH = os.path.join(mmdet.__path__[0], ".mim", "configs")
        return CONFIG_FOLDER_PATH

    @staticmethod
    def _get_mmtrack_config_path() -> str:
        """Get the path to the MmTracking config file.

        :return: Path to the MmTracking config file.
        :rtype: str
        """
        import mmtrack

        # Note: mmtrack should be installed via mim to access the model zoo config folder.
        CONFIG_FOLDER_PATH = os.path.join(mmtrack.__path__[0], ".mim", "configs")
        return CONFIG_FOLDER_PATH

    def _get_config_path(self) -> str:
        """Get the path to the config file by model family

        :return: Path to config file by model_family
        :rtype: str
        """
        if self.model_family == MODEL_FAMILY_CLS.MMDETECTION_IMAGE:
            return ImageModelSelector._get_mmdet_config_path()
        elif self.model_family == MODEL_FAMILY_CLS.MMTRACKING_VIDEO:
            return ImageModelSelector._get_mmtrack_config_path()

    def _get_model_zoo_link(self) -> str:
        """Get the model zoo link by model family

        :return: model zoo link by model_family
        :rtype: str
        """
        if self.model_family == MODEL_FAMILY_CLS.MMDETECTION_IMAGE:
            return ModelRepositoryURLs.MMDETECTION
        elif self.model_family == MODEL_FAMILY_CLS.MMTRACKING_VIDEO:
            return ModelRepositoryURLs.MMTRACKING
