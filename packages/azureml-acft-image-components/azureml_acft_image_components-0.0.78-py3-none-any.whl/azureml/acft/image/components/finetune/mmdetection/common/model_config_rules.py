# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Rules configuration to apply on model for exporting"""

from abc import ABC, abstractmethod
from typing import Dict, List

from azureml.acft.image.components.finetune.mmdetection.common.constants import (
    MmDetectionModelLiterals,
)


class BaseRules(ABC):
    """Rules for model config while exporting model, to be implemented by each model."""

    @abstractmethod
    def _get_rules(self) -> List[callable]:
        """Get the rules to apply to the model config while exporting model

        :return: List of functions to modify the model config
        :rtype: List[callable]
        """
        pass

    def apply(self, model_config: Dict):
        """Apply the rule to the model config while exporting model"""
        rules = self._get_rules()
        for rule in rules:
            rule(model_config)


class DetrRules(BaseRules):
    """Rules for detr model."""

    def _modify_class_weight_of_loss_cls_in_bbox_head(self, model_config: Dict):
        """Modify the class weight of loss_cls in bbox_head

        :param model_config: Model config
        :type model_config: Dict
        """
        model_config[MmDetectionModelLiterals.BBOX_HEAD][
            MmDetectionModelLiterals.LOSS_CLS
        ][MmDetectionModelLiterals.CLASS_WEIGHT] = 1.0

    def _get_rules(self) -> List[callable]:
        """Get the rules to apply to the model config while exporting model

        :return: List of functions to modify the model config
        :rtype: List[callable]
        """
        return [self._modify_class_weight_of_loss_cls_in_bbox_head]


# TODO: Add rules for deformable detr model

MODEL_RULES_MAP = {"DETR": DetrRules}
