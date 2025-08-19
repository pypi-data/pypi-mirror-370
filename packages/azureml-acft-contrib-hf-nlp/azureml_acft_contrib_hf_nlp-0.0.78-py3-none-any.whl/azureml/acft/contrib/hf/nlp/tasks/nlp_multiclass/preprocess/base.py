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
NLP Multiclass
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datasets.arrow_dataset import Dataset

from ....constants.constants import (
    AzuremlConstants,
    PreprocessArgsTemplate,
    Tasks,
    MLFlowHFFlavourTasks,
    STRING_DTYPES,
    INT_DTYPES,
    AutomlConstants
)

from ....utils.data_utils import AzuremlDataset
from ....utils.validation_utils import AzuremlValidatorMixin

from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.data.data_collator import DataCollatorWithPadding

from azureml.acft.common_components import get_logger_app
from azureml.acft.contrib.hf.nlp.constants.constants import DataSliceConstants
from azureml.acft.contrib.hf.nlp.utils.preprocess_utils import restructure_columns


logger = get_logger_app(__name__)


@dataclass
class NLPMulticlassPreprocessArgs(PreprocessArgsTemplate):
    # Specify the defaults for all new attributes of SingleLabelPreprocessArgs +
    # inherited attributes from PreprocessArgsTemplate here.
    # Otherwise, there will be issues related to ordering of default and
    # non-default attributes

    # extra args
    # Makesure the extra args don't overlap with names of PreprocessArgs Template
    sentence1_key: str = field(
        default=AutomlConstants.TEXT_CLASSIFICATION_COLUMN_NAME
    )
    sentence2_key: Optional[str] = field(
        default=None
    )
    label_key: Optional[str] = field(
        default=None
    )
    #
    problem_type: Optional[str] = field(
        default="single_label_classification"
    )
    task_name: str = field(
        default=Tasks.NLP_MULTICLASS
    )
    batch_size: int = field(
        default=AutomlConstants.BATCH_SIZE
    )
    placeholder_label_column: str = field(
        default="label_key"
    )
    metric_for_best_model: str = field(
        default="f1"
    )
    greater_is_better: bool = field(
        default=True
    )
    mlflow_task_type: str = field(
        default=MLFlowHFFlavourTasks.SINGLE_LABEL_CLASSIFICATION
    )
    pad_to_max_length: bool = field(
        default=True
    )
    max_seq_length: int = field(
        default=AutomlConstants.DEFAULT_SEQ_LEN
    )
    enable_long_range_text: bool = field(
        default=True
    )

    def __post_init__(self):
        # setting the defaults for mutable arguments will cause issue in case of multiple class
        # initializations. so, placeholders are set here
        self.placeholder_required_columns = ["sentence1_key", "sentence2_key", "label_key"]
        self.placeholder_required_column_dtypes = [
            STRING_DTYPES, STRING_DTYPES, STRING_DTYPES+INT_DTYPES
        ]
        #
        if self.placeholder_required_columns is not None:
            for idx, col_name in enumerate(self.placeholder_required_columns):
                decoded_arg = getattr(self, col_name, None)
                if decoded_arg is not None:
                    self.required_columns.append(decoded_arg)
                    self.required_column_dtypes.append(self.placeholder_required_column_dtypes[idx])

        self.label_column = getattr(self, self.placeholder_label_column)


class NLPMulticlassDataset(AzuremlDataset, AzuremlValidatorMixin):

    def __init__(
        self,
        path_or_dict: Union[str, Path],
        dataset_args: Optional[Dict[str, Any]] = None,
        required_columns: Optional[List[str]] = None,
        required_column_dtypes: Optional[List[List[str]]] = None,
        label_column: Optional[str] = None,
        label_column_optional: bool = False,
        tokenizer: Optional[PreTrainedTokenizerBase] = None,
        preprocess: bool = False,
        pass_through_columns: List[str] = None,  # columns that are passed throgh to the next component.
        ignore_columns: List[str] = None,  # columns to be ignored while concat, to be ignored for next component.
        dataset_columns: List[str] = None,  # full list of dataset columns to be considered while processing.
        slice: str = DataSliceConstants.NO_SPLIT
    ) -> None:
        # required_columns, required_column_dtypes are made optional to support loading the dataset
        # without the need for validation

        # initialize the dataset class
        super().__init__(
            path_or_dict,
            label_column=label_column,
            label_column_optional=label_column_optional,
            slice=slice
        )

        # initialize the validator mixin class
        super(AzuremlDataset, self).__init__(
            required_columns=required_columns,
            required_column_dtypes=required_column_dtypes
        )
        self._set_fields(dataset_args, required_columns, required_column_dtypes,
                         label_column, label_column_optional, tokenizer, preprocess,
                         pass_through_columns, ignore_columns, dataset_columns)

        if preprocess:
            restructure_columns(self)
    

    def _set_fields(self,
                    dataset_args: Optional[Dict[str, Any]] = None,
                    required_columns: Optional[List[str]] = None,
                    required_column_dtypes: Optional[List[List[str]]] = None,
                    label_column: Optional[str] = None,
                    label_column_optional: bool = False,
                    tokenizer: Optional[PreTrainedTokenizerBase] = None,
                    preprocess: bool = True,
                    pass_through_columns: List[str] = None,
                    ignore_columns: List[str] = None,
                    dataset_columns: List[str] = None,):
        self.dataset_args = dataset_args
        self.required_columns = required_columns
        self.required_column_dtypes = required_column_dtypes
        self.label_column_optional = label_column_optional
        self.preprocess = preprocess
        self.tokenizer = tokenizer
        self.pass_through_columns = pass_through_columns if pass_through_columns is not None else []
        self.ignore_columns = ignore_columns if ignore_columns is not None else []
        self.dataset_columns = dataset_columns if dataset_columns is not None else []
        self.label_column = label_column

    def get_collation_function(self) -> Optional[Callable]:
        """Collation function for dynamic padding"""
        return DataCollatorWithPadding(self.tokenizer) if self.tokenizer is not None else None

    def update_dataset_columns_with_prefix(self):
        """Update the sentence1_key, sentece2_key and label_keys with prefix"""
        if self.dataset_args is not None:
            self.dataset_args["sentence1_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["sentence1_key"]
            if self.dataset_args["sentence2_key"] is not None:
                self.dataset_args["sentence2_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["sentence2_key"]
            if self.dataset_args["label_key"] is not None:
                self.dataset_args["label_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["label_key"]

        return super().update_dataset_columns_with_prefix()

    def encode_dataset(self, label_to_id: Optional[dict] = None):
        """
        datasets: HuggingFace datasets object
        tokenizer: HuggingFace tokenizer
        kwargs: max_seq_length, pad_to_max_length, sentence1_key, sentence2_key, label_key

        https://github.com/huggingface/notebooks/blob/main/examples/text_classification.ipynb
        """

        if self.tokenizer is None or self.dataset_args is None:
            raise

        def tokenize_func(examples):
            if self.tokenizer is None or self.dataset_args is None:
                raise

            # Tokenize text
            args = (
                (examples[sentence1_key],) if sentence2_key is None else (examples[sentence1_key], examples[sentence2_key])
            )
            result = self.tokenizer(
                *args,
                padding=self.dataset_args["padding"],
                max_length=self.dataset_args["max_length"],
                truncation=self.dataset_args["truncation"]
            )

            if label_key is not None:
                result["labels"] = [label_to_id[label.lower()] for label in examples[label_key]]

            return result

        # sentence and label keys
        sentence1_key, sentence2_key = self.dataset_args["sentence1_key"], self.dataset_args["sentence2_key"]
        label_key = self.dataset_args["label_key"]

        # convert label column to string and converting it to classlabel
        if label_key is not None:
            self.dataset = NLPMulticlassDataset.set_column_dtype(self.dataset, label_key, to_dtype="string")

        # tokenize the data
        self.dataset = self.dataset.map(
            tokenize_func,
            batched=True,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"],
        )


class NLPMulticlassDatasetInference(NLPMulticlassDataset):
    def __init__(
        self,
        df,
        dataset_args: Optional[Dict[str, Any]] = None,
        required_columns: Optional[List[str]] = None,
        required_column_dtypes: Optional[List[List[str]]] = None,
        label_column: Optional[str] = None,
        tokenizer: Optional[PreTrainedTokenizerBase] = None,
        pass_through_columns: List[str] = None,
        ignore_columns: List[str] = None,
        dataset_columns:List[str] = None,
    ) -> None:
        self._set_fields(dataset_args, required_columns, required_column_dtypes,
                         label_column, True, tokenizer, True,
                         pass_through_columns, ignore_columns, dataset_columns)
        
        self.dataset = Dataset.from_pandas(df)
        restructure_columns(self)
        self.update_dataset_columns_with_prefix()
        