# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Model specific settings literals."""


class Literals:
    """Model specific settings literals."""

    # Model loading specific constants
    MODEL_NAME_OR_PATH = "model_name_or_path"
    NOISE_SCHEDULER_NAME = "noise_scheduler_name"
    EXTRA_NOISE_SCHEDULER_ARGS = "extra_noise_scheduler_args"
    PREDICTION_TYPE = "prediction_type"
    TEXT_ENCODER_NAME = "text_encoder_name"
    TEXT_ENCODER_TYPE = "text_encoder_type"
    TOKENIZER_NAME_OR_PATH = "tokenizer_name_or_path"
    REVISION = "revision"
    FREEZE_WEIGHTS = "freeze_weights"
    DEVICE = "device"
    CUDA = "cuda"
    CPU = "cpu"
    WEIGHT_DTYPE = "weight_dtype"
    NON_EMA_REVISION = "non_ema_revision"
    MODEL = "model"
    UNET = "unet"
    VAE = "vae"
    OFFSET_NOISE = "offset_noise"
    TEXT_ENCODER_USE_ATTENTION_MASK = "text_encoder_use_attention_mask"
    WITH_PRIOR_PRESERVATION = "with_prior_preservation"
    TOKENIZER_MAX_LENGTH = "tokenizer_max_length"
    SNR_GAMMA = "snr_gamma"
    PRE_COMPUTE_TEXT_EMBEDDINGS = "pre_compute_text_embeddings"
    PRIOR_LOSS_WEIGHT = "prior_loss_weight"
    CLASS_LABELS_CONDITIONING = "class_labels_conditioning"
    TRAIN_TEXT_ENCODER = "train_text_encoder"
    CLASS_PROMPT = "class_prompt"
    INSTANCE_PROMPT = "instance_prompt"
    NUM_CLASS_IMAGES = "num_class_images"
    NUM_VALIDATION_IMAGES = "num_validation_images"
    SAMPLE_BATCH_SIZE = "sample_batch_size"
    INSTANCE_DATA_DIR = "instance_data_dir"
    TRAIN_MLTABLE_PATH = "train_mltable_path"
    CLASS_DATA_DIR = "class_data_dir"
    RESOLUTION = "resolution"
    CENTER_CROP = "center_crop"
    RANDOM_FLIP = "random_flip"
    CLASS_ATTENTION_MASK = "class_attention_mask"
    CLASS_IMAGES = "class_images"
    CLASS_PROMPT_IDS = "class_prompt_ids"
    INSTANCE_ATTENTION_MASK = "instance_attention_mask"
    INSTANCE_IMAGES = "instance_images"
    INSTANCE_PROMPT_IDS = "instance_prompt_ids"
    DATALOADER_NUM_WORKERS = "dataloader_num_workers"
    PRIOR_GENERATION_PRECISION = "prior_generation_precision"

    # Text encoder model names
    CLIP_TEXT_MODEL = "CLIPTextModel"
    T5ENCODER_MODEL = "T5EncoderModel"

    # tokenizer names
    OPENAI_CLIP_VIT_LARGE_PATCH14 = "openai/clip-vit-large-patch14"

    # Precisions
    FP16 = "fp16"
    FP32 = "fp32"
    BFP16 = "bfp16"


class SettingParameters:
    """A class for default settings."""

    TIMESTEPS = "timesteps"
    DEFAULT_PRIOR_LOSS_WEIGHT = 1.0


class PredictionType:
    """Prediction type literals."""

    EPSILON = "epsilon"
    V_PREDICTION = "v_prediction"


class DataLiterals:
    """Data specific literals."""

    INPUT_IDS = "input_ids"
    PIXEL_VALUES = "pixel_values"
    ATTENTION_MASK = "attention_mask"
