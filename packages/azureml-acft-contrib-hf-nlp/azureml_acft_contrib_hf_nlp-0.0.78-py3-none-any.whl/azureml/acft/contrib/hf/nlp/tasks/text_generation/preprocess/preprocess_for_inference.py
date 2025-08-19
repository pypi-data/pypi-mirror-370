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

from argparse import Namespace

from .base import TextGenerationPreprocessArgs
from ....constants.constants import Tasks
from ....nlp_auto.tokenizer import AzuremlAutoTokenizer

from azureml.acft.common_components import get_logger_app
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore

from transformers.tokenization_utils_base import PreTrainedTokenizerBase

logger = get_logger_app(__name__)


class TextGenerationForInfer():

    def __init__(self, component_args: Namespace, preprocess_args: TextGenerationPreprocessArgs) -> None:
        # component args is combined args of
        #  - preprocess component args
        #  - model_name arg from model selector
        #  - newly constructed model_name_or_path
        self.component_args = component_args
        self.text_generation_preprocess_args = preprocess_args
        logger.info(self.text_generation_preprocess_args)

        self.tokenizer = self._init_tokenizer()

    def _init_tokenizer(self) -> PreTrainedTokenizerBase:
        """Initialize the tokenizer and set the model max length for the tokenizer if not already set"""

        tokenizer_params = {
            "task_name": Tasks.TEXT_GENERATION,
            "apply_adjust": False,
        }

        return AzuremlAutoTokenizer.from_pretrained(self.component_args.model_name_or_path, **tokenizer_params)

    def preprocess(self) -> None:
        """
        Preprocess the raw dataset
        """
        pass
