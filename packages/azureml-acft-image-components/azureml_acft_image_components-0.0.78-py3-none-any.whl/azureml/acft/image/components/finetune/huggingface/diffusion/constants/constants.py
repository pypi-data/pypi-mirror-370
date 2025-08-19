# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File for adding all the constants"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class DatasetSplit:
    """Dataset split constants."""
    TEST = "test"
    TRAIN = "train"
    VALIDATION = "validation"


@dataclass
class DataConstants:
    """Data constants."""

    PROMPT = "prompt"
    INDEX = "index"


@dataclass
class SaveFileConstants:
    """
    A class to represent constants for metadata related to saving the model.
    """

    PREPROCESS_ARGS_SAVE_PATH = "preprocess_args.json"
    FINETUNE_ARGS_SAVE_PATH = "finetune_args.json"
    CLASSES_SAVE_PATH = "class_names.json"
    ID2LABEL_SAVE_PATH = "id2label.json"
    LABEL2ID_SAVE_PATH = "label2id.json"
    CLASSES_SAVE_KEY = "class_names"
    MODEL_SELECTOR_ARGS_SAVE_PATH = "model_selector_args.json"


@dataclass
class HfConstants:
    """
    A class to represent constants for hugging face files.
    """

    LARGE_MODEL_MAX_LENGTH = 1e6
    DEFAULT_MAX_SEQ_LENGTH = 512
    MODEL_MAX_LENGTH_KEY = "model_max_length"


@dataclass
class MLFlowHFFlavourConstants:
    """
    A class to represent constants for parameters of HF Flavour mlflow.
    """

    TRAIN_LABEL_LIST = "train_label_list"
    TASK_TYPE = "task_type"
    # NOTE ONLY used for Summarization and Translation tasks
    PREFIX_AND_TASK_FILE_SAVE_NAME_WITH_EXT = "azureml_tokenizer_prefix_mlflow_task.json"
    PREFIX_SAVE_KEY = "tokenizer_prefix"
    #
    TASK_SAVE_KEY = "mlflow_task"
    INFERENCE_PARAMS_SAVE_NAME_WITH_EXT = "azureml_mlflow_inference_params.json"
    INFERENCE_PARAMS_SAVE_KEY = "tokenizer_config"
    MISC_CONFIG_FILE = "MLmodel"
    MODEL_ROOT_DIRECTORY = "mlflow_model_folder"
    HUGGINGFACE_ID = "huggingface_id"
    LICENSE_FILE = "LICENSE"


@dataclass
class AzuremlConstants:
    """
    General constants
    """

    DATASET_COLUMN_PREFIX = "Azureml_"


@dataclass
class Tasks:
    """Supported Tasks"""

    STABLE_DIFFUSION = "StableDiffusion"


class MLFlowHFFlavourTasks:
    """
    A class to represent constants for MLFlow HF-Flavour supported tasks.
    """

    STABLE_DIFFUSION = "text-to-image"


# Pyarrow ref
# https://github.com/huggingface/datasets/blob/9f9f0b536e128710115c486b0b9c319c3f0a570f/src/datasets/features/features.py#L404
INT_DTYPES = ["int8", "int16", "int32", "int64"]
STRING_DTYPES = ["string", "large_string"]
FLOAT_DTYPES = ["float16", "float32", "float64"]


@dataclass
class PreprocessArgsTemplate:
    """
    This is a template dataclass for preprocess arguments. This is inherited by respective
    task preprocess args class and most of the fields are populated there.

    placeholder_required_columns - dummy strings to represent the column names of the data. For instance,
    the dummy values for NER are `token_key`, `tag_key` i.e. placeholder_required_columns will be
    ["token_key", "tag_key"].
    """

    # init=False => this argument is not required during initialization but needs to be set in post init
    placeholder_required_columns: List[str] = field(init=False, default_factory=list)
    placeholder_required_column_dtypes: List[List[str]] = field(init=False, default_factory=list)
    placeholder_label_column: str
    required_columns: List[str] = field(init=False, default_factory=list)
    required_column_dtypes: List[List[str]] = field(init=False, default_factory=list)
    label_column: str = field(init=False)
    task_name: str
    mlflow_task_type: str
    problem_type: Optional[str]
    metric_for_best_model: str = field(
        metadata={
            "help": (
                "Use in conjunction with `load_best_model_at_end` to specify the metric to use to compare two"
                "different models. Must be the name of a metric returned by the evaluation with or without the prefix "
                '`"eval_"`. Will default to `"loss"` if unspecified and `load_best_model_at_end=True` '
                "(to use the evaluation loss). If you set this value, `greater_is_better` will default to `True`."
                " Don't forget to set it to `False` if your metric is better when lower."
            )
        }
    )
    greater_is_better: bool = field(
        metadata={
            "help": (
                "Use in conjunction with `load_best_model_at_end` and `metric_for_best_model`"
                "to specify if better models should have a greater metric or not. Will default to:"
                '- `True` if `metric_for_best_model` is set to a value that isnt `"loss"` or `"eval_loss"`.'
                '- `False` if `metric_for_best_model` is not set, or set to `"loss"` or `"eval_loss"`.'
            )
        }
    )
    # pad_to_max_length: str = field(
    #     metadata={
    #         "help": (
    #             "If true, all samples get padded to `max_seq_length`."
    #             "If false, will pad the samples dynamically when batching to the maximum length in the batch."
    #         )
    #     }
    # )
    # max_seq_length: int = field(
    #     metadata={
    #         "help": (
    #             "Max tokens of single example, set the value to -1 to use the default value."
    #             "Default value will be max seq length of pretrained model tokenizer"
    #         )
    #     }
    # )
