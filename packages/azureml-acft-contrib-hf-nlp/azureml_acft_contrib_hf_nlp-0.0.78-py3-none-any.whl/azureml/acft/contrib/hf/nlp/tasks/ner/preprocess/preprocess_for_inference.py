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
NER
"""

from argparse import Namespace
from typing import Dict, List, Any
import copy

from .base import NerPreprocessArgs, NerDataset
from ....constants.constants import Tasks
from ....nlp_auto.tokenizer import AzuremlAutoTokenizer

from datasets.arrow_dataset import Dataset
import pandas as pd

from azureml.acft.common_components import get_logger_app

from transformers.tokenization_utils_base import PreTrainedTokenizerBase

logger = get_logger_app(__name__)


class NerPreprocessForInfer():

    def __init__(self, component_args: Namespace, preprocess_args: NerPreprocessArgs) -> None:
        # component args is combined args of
        #  - preprocess component args
        #  - model_name arg from model selector
        #  - newly constructed model_name_or_path
        self.component_args = component_args
        self.ner_preprocess_args = preprocess_args
        logger.info(self.ner_preprocess_args)

        self.tokenizer = self._init_tokenizer()

    def _init_tokenizer(self) -> PreTrainedTokenizerBase:
        """Initialize the tokenizer and set the model max length for the tokenizer if not already set"""

        tokenizer_params = {
            "task_name": Tasks.NAMED_ENTITY_RECOGNITION,
            "apply_adjust": False,
        }

        return AzuremlAutoTokenizer.from_pretrained(self.component_args.model_name_or_path, **tokenizer_params)
    
    def _get_encode_dataset_params(self) -> Dict[str, Any]:

        encode_params = {}
        # padding and truncation
        encode_params["padding"] = "max_length" if self.ner_preprocess_args.pad_to_max_length else False
        encode_params["truncation"] = True

        # max sequence length
        if self.ner_preprocess_args.max_seq_length == -1:
            self.ner_preprocess_args.max_seq_length = self.tokenizer.model_max_length
        encode_params["max_length"] = min(self.ner_preprocess_args.max_seq_length, self.tokenizer.model_max_length)

        return encode_params

    def preprocess(self, data: Dict) -> pd.DataFrame:
        """
        Preprocess the raw dataset
        """
        # encode params used for encoding dataset
        self.encode_params = self._get_encode_dataset_params()

        # initialize dataset
        dataset_args=vars(self.ner_preprocess_args)
        dataset_args.update(self.encode_params)
        # initialize dataset
        kwargs = dict(
            required_columns=self.ner_preprocess_args.required_columns,
            required_column_dtypes=self.ner_preprocess_args.required_column_dtypes,
            label_column=self.ner_preprocess_args.label_column,
            tokenizer=self.tokenizer
        )
        test_ds = NerDataset(
            data,
            dataset_args=dataset_args,
            label_column_optional=True,
           **copy.deepcopy(kwargs),
        )

        test_ds.validate()

        test_ds.encode_dataset()

        # encoded_data = [example for example in test_ds.dataset[self.ner_preprocess_args.token_key]]

        return test_ds.dataset.to_pandas()
