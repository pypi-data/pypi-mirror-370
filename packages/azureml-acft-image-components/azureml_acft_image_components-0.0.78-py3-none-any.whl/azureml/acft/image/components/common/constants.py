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

"""File for adding all the common constants"""


# Following is the deny-list of messages to avoid logging in app-insight.
# Dev Notes: Add only PII messages to denylist from azureml packages.
LOGS_TO_BE_FILTERED_IN_APPINSIGHTS = [
    "Dataset columns after pruning",
    "loading configuration file",
    "Model config",
    "loading file",
    "Namespace(",
    "output type to python objects for",
    "class Names:",
    "Class names : ",
    "Metrics calculator:",
    "The following columns in the training set",
    # validation filter strings
    "Dataset Columns: ",
    "Data formating",
    "dtype mismatch for feature",
    "Removing label_column",
    "Removed columns:",
    "Converting column:",
    "Component Args",
    "Using client id:",
]
