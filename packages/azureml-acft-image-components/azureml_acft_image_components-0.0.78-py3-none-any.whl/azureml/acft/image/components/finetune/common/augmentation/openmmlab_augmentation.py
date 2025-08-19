# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""AzureML ACFT Image finetune component - albumentation augmentation."""


from azureml.acft.common_components import get_logger_app
from azureml.acft.image.components.finetune.factory.task_definitions import Tasks
from azureml.acft.image.components.finetune.common.augmentation.base_augmentation import (
    BaseAugmentation,
)
try:
    from azureml.acft.image.components.finetune.common.mlflow.custom_augmentations_openmm import (
        Compose
    )
except Exception:
    # this is required for mmtracking modules.
    # added this to fix mmdet uts where mmtrack is not installed
    pass
from azureml.acft.image.components.finetune.common.constants.augmentation_constants import (
    AugmentationConfigKeys, OpenmmlabAugmentationNames
)
from azureml.acft.image.components.finetune.common.constants.constants import (
    SettingLiterals
)
from azureml.acft.image.components.finetune.common.mlflow.augmentation_helper import (
    save_augmentations_to_disk
)

logger = get_logger_app(__name__)


class MmlabAugmentation(BaseAugmentation):
    """
    This class expects a openmmlab configurations to be passed as `model_preprocessing_params_dict`.
     And composes openmmlab native transforms from it.
    """

    def __init__(
        self,
        model_preprocessing_params_dict: dict,
        **kwargs,
    ) -> None:
        """ See the doc string for BaseAugmentations class """

        super().__init__(
            config_path=None,
            model_preprocessing_params_dict=model_preprocessing_params_dict,
            **kwargs,
        )

        # Bounding box is only required for Object Tracking task as of now.
        self.is_bbox_required = kwargs[SettingLiterals.TASK_NAME] in \
            [Tasks.MM_MULTI_OBJECT_TRACKING]

        output_directory = kwargs.get(SettingLiterals.OUTPUT_DIR, None)
        if output_directory:
            # Dump the augmentation dictionary to disk so that it could be reconstructed later for inference
            save_augmentations_to_disk(output_directory, self.model_preprocessing_params_dict)

    def get_train_transform(self) -> list:
        """ Get training transform

        :return: openmmlab transform
        :rtype: list
        """
        from azureml.acft.image.components.finetune.mmtracking.common.constants import MmTrackingDatasetLiterals

        train_transforms_load = self.model_preprocessing_params_dict.train.dataset.pipeline
        train_transforms_aug = self.model_preprocessing_params_dict.train.pipeline
        train_transforms_aug[-1] = dict(type="Collect", keys=[MmTrackingDatasetLiterals.IMG,
                                                              MmTrackingDatasetLiterals.GT_BBOXES,
                                                              MmTrackingDatasetLiterals.GT_LABELS,
                                                              MmTrackingDatasetLiterals.GT_CROWDS])
        train_transforms = [Compose(train_transforms_load),
                            Compose(train_transforms_aug)]
        return train_transforms

    def get_valid_transform(self) -> list:
        """ Get validation transform

        :return: openmmlab transform
        :rtype: list
        """
        if AugmentationConfigKeys.VALID_PHASE_KEY not in self.model_preprocessing_params_dict:
            valid_transforms = None
        else:
            valid_transforms = [dict(type=OpenmmlabAugmentationNames.LOAD_ANNOTATIONS, with_bbox=True),
                                dict(type=OpenmmlabAugmentationNames.LOAD_TRACK)]
            valid_transforms += self.update_collect_fn(self.model_preprocessing_params_dict.val.pipeline)
            valid_transforms = [Compose(valid_transforms)]
        # logger.info(f"Valid transform: {valid_transforms}")
        return valid_transforms

    def get_test_transform(self) -> list:
        """ Get test transform

        :return: openmmlab transform
        :rtype: list
        """
        test_transforms = [Compose(self.model_preprocessing_params_dict.test.pipeline)]
        logger.info(f"Test transform: {test_transforms}")
        return test_transforms

    def update_collect_fn(self, pipelines: list) -> list:
        """
        originally in openmm, the collect function doesn't introduce label details
        to have this to work, we will need to update collect function to VideoColelctForModel

        :param pipelines: a list of openmmlab transform dicts
        :type pipelines: list
        :return: a list of openmmlab transform dicts
        :rtype: list
        """
        transforms = []
        for pipeline in pipelines:
            if "Collect" in pipeline.type:
                pipeline = dict(type=OpenmmlabAugmentationNames.VIDEO_COLLECT_FOR_MODELS)
            elif hasattr(pipeline, "transforms"):
                for i, transform in enumerate(pipeline.transforms):
                    if "Collect" in transform.type:
                        pipeline.transforms[i] = dict(type=OpenmmlabAugmentationNames.VIDEO_COLLECT_FOR_MODELS)
            transforms.append(pipeline)
        return transforms
