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
Base runner
"""

from abc import ABC, abstractmethod
from collections import OrderedDict

from transformers.models.auto.modeling_auto import (
    MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING_NAMES,
    MODEL_FOR_TOKEN_CLASSIFICATION_MAPPING_NAMES,
    MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES,
    MODEL_FOR_QUESTION_ANSWERING_MAPPING_NAMES,
    MODEL_FOR_CAUSAL_LM_MAPPING_NAMES,
)
from transformers import PretrainedConfig

from .nlp_auto.config import AzuremlAutoConfig
from .constants.constants import Tasks

from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
from azureml.acft.common_components.utils.error_handling.error_definitions import ModelIncompatibleWithTask
from azureml.acft.common_components import get_logger_app
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore


logger = get_logger_app(__name__)


TASK_SUPPORTED_MODEL_TYPES_MAP = OrderedDict([
    (Tasks.SINGLE_LABEL_CLASSIFICATION, MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING_NAMES),
    (Tasks.MULTI_LABEL_CLASSIFICATION, MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING_NAMES),
    (Tasks.REGRESSION, MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING_NAMES),
    (Tasks.NAMED_ENTITY_RECOGNITION, MODEL_FOR_TOKEN_CLASSIFICATION_MAPPING_NAMES),
    (Tasks.SUMMARIZATION, MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES),
    (Tasks.TRANSLATION, MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING_NAMES),
    (Tasks.QUESTION_ANSWERING, MODEL_FOR_QUESTION_ANSWERING_MAPPING_NAMES),
    (Tasks.TEXT_GENERATION, MODEL_FOR_CAUSAL_LM_MAPPING_NAMES),
    (Tasks.NLP_NER, MODEL_FOR_TOKEN_CLASSIFICATION_MAPPING_NAMES),
    (Tasks.NLP_MULTICLASS, MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING_NAMES),
    (Tasks.NLP_MULTILABEL, MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING_NAMES),
])


ACFT_TASK_AUTO_TASK_MAP = OrderedDict([
    (Tasks.SINGLE_LABEL_CLASSIFICATION, "AutoModelForSequenceClassification"),
    (Tasks.MULTI_LABEL_CLASSIFICATION, "AutoModelForSequenceClassification"),
    (Tasks.NAMED_ENTITY_RECOGNITION, "AutoModelForTokenClassification"),
    (Tasks.QUESTION_ANSWERING, "AutoModelForQuestionAnswering"),
    (Tasks.SUMMARIZATION, "AutoModelForSeq2SeqLM"),
    (Tasks.TRANSLATION, "AutoModelForSeq2SeqLM"),
    (Tasks.TEXT_GENERATION, "AutoModelForCausalLM"),
])


class BaseRunner(ABC):

    def check_model_task_compatibility(self, model_name_or_path: str, task_name: str, **kwargs) -> None:
        """
        Check if the given model supports the given task in the case of Hugging Face Models
        """
        supported_model_types = TASK_SUPPORTED_MODEL_TYPES_MAP[task_name]
        model_type = AzuremlAutoConfig.get_model_type(hf_model_name_or_path=model_name_or_path, **kwargs)

        if model_type not in supported_model_types:
            config_dict, _ = PretrainedConfig.get_config_dict(model_name_or_path, **kwargs)
            if "auto_map" in config_dict and ACFT_TASK_AUTO_TASK_MAP[task_name] in config_dict["auto_map"]:
                logger.info(
                    f"Task {task_name} is supported with external class - "
                    f"{config_dict['auto_map'][ACFT_TASK_AUTO_TASK_MAP[task_name]]}"
                )
            else:
                raise ACFTValidationException._with_error(
                    AzureMLError.create(
                        ModelIncompatibleWithTask, TaskName=task_name, ModelName=model_name_or_path
                    )
                )

    @abstractmethod
    def run_preprocess_for_finetune(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def run_finetune(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def run_preprocess_for_infer(self, *args, **kwargs) -> None:
        pass

    def run_modelselector(self, **kwargs) -> None:
        """
        Downloads model from azureml-preview registry if present
        Prepares model for continual finetuning
        Save model selector args
        """
        pass
