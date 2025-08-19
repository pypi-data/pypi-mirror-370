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

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field

from ....constants.constants import (
    AzuremlConstants,
    MLFlowHFFlavourTasks,
    PreprocessArgsTemplate,
    Tasks,
    INT_DTYPES,
    STRING_DTYPES
)

from ....utils.data_utils import AzuremlDataset, clean_column_name
from ....utils.validation_utils import AzuremlValidatorMixin

from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.data.data_collator import DataCollatorWithPadding

from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError

from azureml.acft.common_components import get_logger_app
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore


logger = get_logger_app(__name__)


@dataclass
class SingleLabelPreprocessArgs(PreprocessArgsTemplate):
    # Specify the defaults for all new attributes of SingleLabelPreprocessArgs +
    # inhertied attributes from PreprocessArgsTemplate here.
    # Otherwise, there will be issues related to ordering of default and
    # non-default attributes

    # extra args
    # Makesure the extra args don't overlap with names of PreprocessArgs Template
    sentence1_key: str = field(
        default="sentence1"
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
        default=Tasks.SINGLE_LABEL_CLASSIFICATION
    )
    batch_size: int = field(
        default=1000
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
        default=-1
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
                    cleaned_name = clean_column_name(decoded_arg)
                    setattr(self, col_name, cleaned_name)  # reset with cleaned name for further use
                    self.required_columns.append(cleaned_name)
                    self.required_column_dtypes.append(self.placeholder_required_column_dtypes[idx])
        self.validate_required_columns()
        self.label_column = getattr(self, self.placeholder_label_column)


class SingleLabelDataset(AzuremlDataset, AzuremlValidatorMixin):

    def __init__(
        self,
        path_or_dict: Union[str, Path],
        dataset_args: Optional[Dict[str, Any]] = None,
        required_columns: Optional[List[str]] = None,
        required_column_dtypes: Optional[List[List[str]]] = None,
        label_column: Optional[str] = None,
        label_column_optional: bool = False,
        tokenizer: Optional[PreTrainedTokenizerBase] = None,
        slice: str = "train",
    ) -> None:
        # required_columns, required_column_dtypes are made optional to support loading the dataset
        # without the need for validation

        # initialize the dataset class
        super().__init__(
            path_or_dict,
            label_column=label_column,
            label_column_optional=label_column_optional,
            slice=slice,
        )

        # initialze the validator mixin class
        super(AzuremlDataset, self).__init__(
            required_columns=required_columns,
            required_column_dtypes=required_column_dtypes
        )

        self.dataset_args = dataset_args
        self.tokenizer = tokenizer

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

    def encode_dataset(self, class_names_train_plus_valid: Optional[List[str]] = None):
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
                result["labels"] = examples[label_key]

            return result

        # sentence and label keys
        sentence1_key, sentence2_key = self.dataset_args["sentence1_key"], self.dataset_args["sentence2_key"]
        label_key = self.dataset_args["label_key"]

        # convert label column to string and converting it to classlabel
        if label_key is not None:
            self.dataset = SingleLabelDataset.set_column_dtype(self.dataset, label_key, to_dtype="string")
            self.convert_label_column_using_classlabel(class_names=class_names_train_plus_valid)

        # tokenize the data
        self.dataset = self.dataset.map(
            tokenize_func,
            batched=True,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"],
            remove_columns=self.dataset.column_names
        )

    def single_label_data_filter(self):
        """Remove the examples that contain null data. specific to singlelabel task"""

        if self.dataset_args is None:
            logger.info(f"Dataset args is {self.dataset_args}. Skipping singlelabel data filter")
            return

        # apply singlelabel specific data filter
        if self.label_column is None:
            logger.info("label key is not present. skipping singlelabel specific data filter")
            return

        # filter examples with empty sentence1 or sentence2
        # dataset_args is not None at this point
        filter_lambda = lambda example: (
            example[self.dataset_args["sentence1_key"]] != "" or  # type: ignore
            example.get(self.dataset_args["sentence2_key"], "ignore") != ""  # type: ignore
        )
        pre_filter_rows = self.dataset.num_rows
        self.dataset = self.dataset.filter(
            filter_lambda,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"]
        )
        post_filter_rows = self.dataset.num_rows
        logger.info(f"Singlelabel data filter | before example count: {pre_filter_rows} | after example count: {post_filter_rows}")
        if post_filter_rows == 0:
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=f"Found no examples after data preprocessing for {self.path_or_dict}"
                )
            )

    def validate(self, split: Optional[str] = None):
        self.apply_common_validations(split, batch_size=self.dataset_args["batch_size"])

        # check if feature columns are identical
        self.check_column_contents(self.dataset_args["sentence1_key"], self.dataset_args["sentence2_key"])
        # check dtypes
        # NOTE doing dtype check before task specific data filter because :meth single_label_data_filter
        # assumes the dtypes for columns
        self.check_column_dtypes()
        # remove examples with empty sentence1 or sentence2
        self.single_label_data_filter()
