# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class NoisingScheduler:
    """
    Generic noising scheduler. It must be initialized with a dictionary
    where each key is the parameter to schedule over time. The value is
    another dictionary with `SCHEDULING_TYPE` as a key which specifies
    the type of scheduling (linear or static supported), the remaining
    parameters depend upon the type of scheduling. For example:
    ```
    {
        "DAE_DROPOUT_PROB": {"SCHEDULING_TYPE": "linear", "MIN": 0.0001, "MAX": 0.1, "WARMUP_EXAMPLES": 100000},
        "DAE_BLANK_PROB": {"SCHEDULING_TYPE": "static", "MAX": 0.1 },
    }
    ```

    If the scheduler type is linear, it will increase linearly from MIN to MAX during the
    first WARMUP_EXAMPLES, and after that it will remain as MAX. If the scheduler type
    is static, it will remain MAX always.
    """

    def __init__(self, ratios: Dict[str, Dict]):
        """
        ratios is a dict that maps scheduled ratio names (MASK_RATIO, DROP_PROB, etc)
        to dicts with the scheduling settings, e.g.:
        {"SCHEDULING_TYPE": ***, "MIN": ***, "MAX": ***, "WARMUP_EXAMPLES": ***}.
        """
        self.setstate({}, ratios=ratios)
        self.step(0)
        logger.info(
            f"Initializing NoisingRatioScheduler with" f" example={self.ratios}"
        )

    def setstate(self, new_state, ratios=None):
        new_state = new_state if new_state else {}
        self.current_example_idx = new_state.get("current_example_idx", 0)
        self.ratios = ratios if ratios else new_state.get("ratios", {})
        assert all("SCHEDULING_TYPE" in v for v in self.ratios.values())

    def getstate(self):
        return {"current_example_idx": self.current_example_idx, "ratios": self.ratios}

    def get_scheduled_ratio(self, name, default=None):
        if name not in self.ratios:
            if default is None:
                raise ValueError(
                    f"{name} does not exist in this scheduler: "
                    f"{self.ratios} and default value is None"
                )
            return default

        settings = self.ratios[name]
        return _get_noising_ratio(self.current_example_idx, settings)

    def step(self, num_updates: int = 1):
        self.current_example_idx += num_updates


def _get_noising_ratio(example_idx, settings):

    scheduling_type = settings["SCHEDULING_TYPE"].lower()
    ratio_max = settings["MAX"]
    if scheduling_type == "static":
        return ratio_max
    if scheduling_type == "linear":
        ratio_min = settings["MIN"]
        warmup_examples = settings["WARMUP_EXAMPLES"]
        if example_idx >= warmup_examples:
            # if ratio_max < ratio_min assume linear decreasing
            return ratio_max if ratio_max > ratio_min else ratio_min
        return ratio_min + (ratio_max - ratio_min) / warmup_examples * example_idx
    raise NotImplementedError
