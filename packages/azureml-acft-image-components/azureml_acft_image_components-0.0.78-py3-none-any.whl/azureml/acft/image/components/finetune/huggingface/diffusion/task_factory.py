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
"""
File for factory method for all NLP HF tasks
This file is called by component scripts files to fetch the corresponding task runners
"""

from .constants.constants import Tasks
from .base_runner import BaseRunner


def get_task_runner(task_name: str):
    """
    returns hf task related runner
    """
    if task_name == Tasks.STABLE_DIFFUSION:
        from .tasks.stable_diffusion.runner import StableDiffusionRunner

        return StableDiffusionRunner

    raise NotImplementedError(f"HF runner for the task {task_name} is not supported")
