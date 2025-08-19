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

"""File for adding all the constants"""

from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml._common._error_definition.azureml_error import AzureMLError

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class DatasetSplit:
    TEST = "test"
    TRAIN = "train"
    VALIDATION = "validation"


@dataclass
class DataSliceConstants:
    """
    Constants related to slice specification in class NLPMulticlassDataset
    """
    NO_SPLIT = "train"


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
    ACFT_CONFIG_SAVE_PATH = "finetune_config.json"


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
    INFERENCE_PARAMS_SAVE_KEY_TEXTGEN = "tokenizer_hf_load_kwargs"
    MISC_CONFIG_FILE = "MLmodel"
    CONDA_YAML_FILE = "conda.yaml"
    MODEL_ROOT_DIRECTORY = "mlflow_model_folder"
    HUGGINGFACE_ID = "huggingface_id"
    LICENSE_FILE = "LICENSE"
    DEFAULT_MODEL_NAME = "default_model_name"


@dataclass
class AzuremlConstants:
    """
    General constants
    """
    DATASET_COLUMN_PREFIX = "Azureml_"
    AZUREML_URL_PREFIX = "azureml://"


@dataclass
class HfModelTypes:
    GPT2 = "gpt2"
    ROBERTA = "roberta"
    DEBERTA = "deberta"
    DISTILBERT = "distilbert"
    BERT = "bert"
    BART = "bart"
    MBART = "mbart"
    T5 = "t5"
    CAMEMBERT = "camembert"
    LLAMA = "llama"
    GPT_NEOX = "gpt_neox"
    FALCON = "falcon"
    REFINEDWEBMODEL = "RefinedWebModel"
    REFINED_WEB = "RefinedWeb"
    MIXFORMER_SEQUENTIAL = "mixformer-sequential"   # Phi models
    MISTRAL = "mistral"
    MIXTRAL = "mixtral"
    PHI_LONGROPE = "phi_longrope"   # Phi3 models
    LLAMA_4 = "llama4"


@dataclass
class Tasks:
    """Supported Tasks"""
    SINGLE_LABEL_CLASSIFICATION = "SingleLabelClassification"
    MULTI_LABEL_CLASSIFICATION = "MultiLabelClassification"
    REGRESSION = "regression"
    NAMED_ENTITY_RECOGNITION = "NamedEntityRecognition"
    PARTS_OF_SPEECH_TAGGING = "PartsOfSpeechTagging"
    CHUNKING = "Chunking"
    SUMMARIZATION = "Summarization"
    TRANSLATION = "Translation"
    QUESTION_ANSWERING = "QuestionAnswering"
    TEXT_GENERATION = "TextGeneration"
    CHAT_COMPLETION = "ChatCompletion"
    NLP_NER = "NLPNER"
    NLP_MULTICLASS = "NLPMulticlass"
    NLP_MULTILABEL = "NLPMultilabel"
    VISUAL_QUESTION_ANSWERING = "VisualQuestionAnswering"

class MLFlowHFFlavourTasks:
    """
    A class to represent constants for MLFlow HF-Flavour supported tasks.
    """
    SINGLE_LABEL_CLASSIFICATION = "text-classification"
    MULTI_LABEL_CLASSIFICATION = "text-classification"
    NAMED_ENTITY_RECOGNITION = "token-classification"
    QUESTION_ANSWERING = "question-answering"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    TEXT_GENERATION = "text-generation"
    # FIXME This is a dummy value for now.
    CHAT_COMPLETION = "chat-completion"
    REGRESSION = "regression"
    CHUNKING = "chunking"
    PARTS_OF_SPEECH_TAGGING = "pos-tagging"
    VISUAL_QUESTION_ANSWERING = "chat-completion"


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
    placeholder_required_columns: List[str] = field(
        init=False,
        default_factory=list
    )
    placeholder_required_column_dtypes: List[List[str]] = field(
        init=False,
        default_factory=list
    )
    placeholder_label_column: str
    required_columns: List[str] = field(
        init=False,
        default_factory=list
    )
    required_column_dtypes: List[List[str]] = field(
        init=False,
        default_factory=list
    )
    label_column: str = field(
        init=False
    )
    task_name: str
    mlflow_task_type: str
    problem_type: Optional[str]
    metric_for_best_model: str = field(
        metadata={
            "help": (
                "Use in conjunction with `load_best_model_at_end` to specify the metric to use to compare two"
                "different models. Must be the name of a metric returned by the evaluation with or without the prefix "
                '`"eval_"`. Will default to `"loss"` if unspecified and `load_best_model_at_end=True` '
                '(to use the evaluation loss). If you set this value, `greater_is_better` will default to `True`.'
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
    pad_to_max_length: str = field(
        metadata={
            "help": (
                "If true, all samples get padded to `max_seq_length`."
                "If false, will pad the samples dynamically when batching to the maximum length in the batch."
            )
        }
    )
    max_seq_length: int = field(
        metadata={
            "help": (
                "Max tokens of single example, set the value to -1 to use the default value."
                "Default value will be max seq length of pretrained model tokenizer"
            )
        }
    )
    batch_size: int = field(
        metadata={
            "help": (
                "Number of examples to batch before calling the tokenization function. "
                "This also controls the number of examples to batch while writing to cache and saving to the json file."
            )
        }
    )

    def validate_required_columns(self):
        if len(self.required_columns) != len(set(self.required_columns)):
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=(
                        f"Duplicate column name passed:  {(','.join(self.required_columns))}"
                    )
                )
            )


@dataclass
class TaskConstants:
    NER_IGNORE_INDEX = -100
    TRANSLATION_IGNORE_INDEX = -100
    SUMMARIZATION_IGNORE_INDEX = -100
    TEXT_GENERATION_IGNORE_INDEX = -100
    MULTI_LABEL_THRESHOLD = 0.5
    MULTI_LABEL_NEW_COLUMN_SUFFIX = "_list"


@dataclass
class DataConstants:
    ENCODING = 'utf-8'
    ERRORS = "replace"


@dataclass
class AutomlConstants:
    DEFAULT_SEQ_LEN = 128
    LONG_RANGE_MAX = 256
    MIN_PROPORTION_LONG_RANGE = 0.1
    TEXT_CLASSIFICATION_COLUMN_NAME = "sentences"
    TEXT_NER_TOKEN_KEY = "tokens"
    TEXT_NER_TAG_KEY = "ner_tags_str"
    NER_IGNORE_TOKENS = ["", " ", "\n"]
    BATCH_SIZE = 32


class ValidationConstants:
    """All constants related to data validation."""
    MIN_TRAINING_SAMPLE = 50
    MIN_TRAINING_SAMPLE_GENERATIVE_TASKS = 10


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
        "Component Args:",
        "Using client id:",
        "Validation_input:"
    ]


class MLFLOW_FLAVORS:
    """
    A class to represent constants for mlflow flavours.
    """
    TRANSFORMERS = "transformers"
    HFTRANSFORMERSV2 = "hftransformersv2"
    HFTRANSFORMERS = "hftransformers"


@dataclass
class SaveStrategy:
    EVALUATION_STRATEGY = "evaluation_strategy"
    EPOCH = "epoch"
    STEPS = "steps"


@dataclass
class TokenDistributionConstants:
    """Keys to store along with run properties."""
    TRAINING_PLUS_VALIDATION_TOKENS = "__azureml_ft_training_tokens"
    ASSISTANT_TOKENS = "__azureml_ft_assistant_tokens"
