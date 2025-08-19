# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File for adding all the constants"""

from dataclasses import dataclass

@dataclass
class InputJsonColumns:
    """
    Constants for input json columns.
    """

    IMAGE_PATH: str = "Figure_path"
    QUESTION: str = "Question"
    CHOICE: str = "Choice"
    ANSWER: str = "Answer"


@dataclass
class PreprocessingParams:
    TRAIN_JSONL: str = "train_jsonl"
    TEST_JSONL: str = "test_jsonl"
    VALIDATION_JSONL: str = "validation_jsonl"
    IMAGES_FOLDER: str = "images_folder"
    OUTPUT_DIR: str = "output_dir"
    BATCH_SIZE: str = "batch_size"
    MODEL_NAME_OR_PATH: str = "model_name_or_path"
    MODEL_NAME: str = "model_name"
    INSTRUCTION: str = "instruction"
    MAX_TRAINING_LENGTH: str = "max_seq_length"

class TokenizedColumns:
    """
    A class to represent feature types that are not recognized by column purpose detection from automl runtime.
    """

    INPUT_IDS = "input_ids"
    LABELS = "labels"
    INPUT_IMAGE_EMBEDS = "input_image_embeds"
    IMAGE_ATTENTION_MASK = "image_attention_mask"
    IMAGE_SIZES = "image_sizes"
    INPUT_MODE = "input_mode"
    ATTENTION_MASK = "attention_mask"
    PIXEL_VALUES = "pixel_values"
    IMAGE_PATCH_INDICES = "image_patch_indices"
    ANSWER = "Answer"

@dataclass
class SaveFileConstants:
    """
    A class to represent constants for metadata related to saving the model.
    """

    PREPROCESS_ARGS_SAVE_PATH = "preprocess_args.json"
    FINETUNE_ARGS_SAVE_PATH = "finetune_args.json"
    CLASSES_SAVE_PATH = "class_names.json"
    CLASSES_SAVE_KEY = "class_names"
    MODEL_SELECTOR_ARGS_SAVE_PATH = "model_selector_args.json"
    COLUMN_TYPES_SAVE_PATH = "column_types.json"
    TABULAR_FEATURIZER = "tabular_featurizer.pkl"
    DEFAULT_OUTPUT_DIR = "output"
    DEFAULT_PYTORCH_OUTPUT = "pytorch_output"
    DEFAULT_MLFLOW_OUTPUT = "mlflow_output"
    CONDA_YAML = "conda.yaml"
    PREPROCESSED_DATA = "preprocessed_data.parquet"
    ACFT_CONFIG_SAVE_PATH = "finetune_config.json"
    ML_CONFIGS_FOLDER = "ml_configs"


@dataclass
class DatasetSplit:
    TEST = "test"
    TRAIN = "train"
    VALIDATION = "validation"

@dataclass
class FinetuneParamLiterals:
    """
    Literals related to parameters in finetuning component.
    """

    PREPROCESS_OUTPUT = "preprocess_output"
    PYTORCH_MODEL_DIR = "pytorch_model_folder"
    OUTPUT_DIR = "output_dir"
    MLFLOW_MODEL_DIR = "mlflow_model_folder"
    MODEL_NAME = "model_name"
    MODEL_NAME_OR_PATH = "model_name_or_path"

