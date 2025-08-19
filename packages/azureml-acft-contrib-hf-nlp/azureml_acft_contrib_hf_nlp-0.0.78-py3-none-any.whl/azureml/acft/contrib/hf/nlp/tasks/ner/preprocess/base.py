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

from pathlib import Path

from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field

from ....constants.constants import (
    AzuremlConstants,
    MLFlowHFFlavourTasks,
    PreprocessArgsTemplate,
    TaskConstants,
    Tasks,
    STRING_DTYPES
)

from ....utils.data_utils import AzuremlDataset, clean_column_name
from ....utils.validation_utils import AzuremlValidatorMixin

from datasets import Sequence

from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.data.data_collator import DataCollatorForTokenClassification

from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError

from azureml.acft.common_components import get_logger_app
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore

logger = get_logger_app(__name__)


@dataclass
class NerPreprocessArgs(PreprocessArgsTemplate):
    # Specify the defaults for all new attributes of NerPreprocessArgs + inhertied attributes from
    # _PreprocessArgsTemplate here. Otherwise, there will be issues related to ordering of default and
    # non-default attributes

    # extra args
    # default values for token_key and tag_key are from conll2003 dataset
    token_key: str = field(
        default="tokens"
    )
    tag_key: str = field(
        default="ner_tags"
    )
    label_all_tokens: bool = field(
        default=False
    )
    #
    problem_type: Optional[str] = field(
        default=None
    )
    task_name: str = field(
        default=Tasks.NAMED_ENTITY_RECOGNITION
    )
    batch_size: int = field(
        default=1000
    )
    placeholder_label_column: str = field(
        default="tag_key"
    )
    metric_for_best_model: str = field(
        default="f1"
    )
    greater_is_better: bool = field(
        default=True
    )
    mlflow_task_type: str = field(
        default=MLFlowHFFlavourTasks.NAMED_ENTITY_RECOGNITION
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
        self.placeholder_required_columns = ["token_key", "tag_key"]
        self.placeholder_required_column_dtypes = [STRING_DTYPES, STRING_DTYPES]
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


class NerDataset(AzuremlDataset, AzuremlValidatorMixin):

    def __init__(
        self,
        path_or_dict: Union[str, Path, Dict],
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
        return DataCollatorForTokenClassification(self.tokenizer) if self.tokenizer is not None else None

    def encode_dataset(self, class_names_train_plus_valid: Optional[List[str]] = None):
        """
        datasets: HuggingFace datasets object
        kwargs: max_seq_length, pad_to_max_length, token_key, tag_key, label_all_tokens

        https://github.com/huggingface/notebooks/blob/main/examples/token_classification.ipynb
        """

        if self.tokenizer is None or self.dataset_args is None:
            raise

        def tokenize_and_align_labels(examples):
            # is_split_into_words=True as the input is already a list of words
            if self.tokenizer is None or self.dataset_args is None:
                raise
            tokenized_inputs = self.tokenizer(
                examples[token_key],
                truncation=self.dataset_args["truncation"],
                is_split_into_words=True,
                padding=self.dataset_args["padding"],
                max_length=self.dataset_args["max_length"],
            )

            if tag_key is not None:
                extended_tags = []
                for i, str_tags in enumerate(examples[tag_key]):
                    word_ids = tokenized_inputs.word_ids(batch_index=i)  # Map tokens to their respective word.
                    previous_word_idx = None
                    int_tags = []
                    for word_idx in word_ids:  # Set the special tokens to -100.
                        if word_idx is None:
                            int_tags.append(TaskConstants.NER_IGNORE_INDEX)
                        elif word_idx != previous_word_idx:  # Only label the first token of a given word.
                            int_tags.append(label2id[str_tags[word_idx]])
                        else:
                            int_tags.append(label2id[str_tags[word_idx]] if label_all_tokens else TaskConstants.NER_IGNORE_INDEX)
                        previous_word_idx = word_idx
                    extended_tags.append(int_tags)

                tokenized_inputs["labels"] = extended_tags

            return tokenized_inputs

        # token and tag keys
        token_key, tag_key = self.dataset_args["token_key"], self.dataset_args["tag_key"]
        label_all_tokens = self.dataset_args["label_all_tokens"]
        # convert label column using class label
        if tag_key is not None and class_names_train_plus_valid is not None:
            # Currently, the examples are casted from string to integers using `datasets.ClassLabel`
            # This is time consuming as it takes a backup of all the existing data and updates the feature
            # and the arrow table metadata. Additionally we are not using all the features of ClassLabel
            # self.convert_label_column_using_classlabel(class_names=class_names_train_plus_valid)
            label2id = {label: idx for idx, label in enumerate(class_names_train_plus_valid)}
        else:
            logger.info("Skipping data casting from string -> int")

        self.dataset = self.dataset.map(
            tokenize_and_align_labels,
            batched=True,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"],
            remove_columns=self.dataset.column_names
        )

    def update_dataset_columns_with_prefix(self):
        """Update the token_key, tag_key with prefix"""
        if self.dataset_args is not None:
            self.dataset_args["token_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["token_key"]
            if self.dataset_args["tag_key"] is not None:
                self.dataset_args["tag_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["tag_key"]

        return super().update_dataset_columns_with_prefix()

    def ner_data_filter(self):
        """Remove the examples that contain null data. specific to ner task"""

        if self.dataset_args is None:
            logger.info(f"Dataset args is {self.dataset_args}. Skipping ner data filter")
            return

        # apply ner specific data filter
        if self.dataset_args["tag_key"] is None:
            logger.info("tag key is not present. skipping ner specific data filter")
            return

        # filter examples with empty lists for either tokens or tags
        # filter examples with length of tokens != length of tags
        filter_lambda = lambda example: (
            len(example[self.dataset_args["token_key"]]) == len(example[self.dataset_args["tag_key"]]) != 0  # type: ignore
        )
        pre_filter_rows = self.dataset.num_rows
        self.dataset = self.dataset.filter(
            filter_lambda,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"]
        )
        post_filter_rows = self.dataset.num_rows
        logger.info(f"Ner data filter | before example count: {pre_filter_rows} | after example count: {post_filter_rows}")
        if post_filter_rows == 0:
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=f"Found no examples after data preprocessing for {self.path_or_dict}"
                )
            )

    def check_column_dtypes(self) -> None:
        """
        check the keep columns with keep column dtypes and raise error otherwise
        """

        datset_features = self.dataset.features
        for column_name, valid_dtypes in zip(self.required_columns, self.required_column_dtypes):
            if column_name not in datset_features:
                raise ValueError(
                    f"{column_name} not present in column to dtypes map file."
                    f"The following columns are present: {list(datset_features.keys())}"
                )

            sequence_column_type = isinstance(datset_features[column_name], Sequence)
            if not sequence_column_type:
                raise ACFTDataException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=(
                            f"File path or data: {self.path_or_dict}\n"
                            f"type mismatch for feature {self._remove_dataset_column_prefix(column_name)}\n"
                            f"Found type: {type(datset_features[column_name])}\n"
                            f"Expected type: {Sequence}"
                        )
                    )
                )
            column_dtype = datset_features[column_name].feature.dtype
            if column_dtype not in valid_dtypes:
                raise ACFTDataException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=(
                            f"File path or data: {self.path_or_dict}\n"
                            f"dtype mismatch for feature {self._remove_dataset_column_prefix(column_name)}\n"
                            f"Found dtype: {column_dtype}\n"
                            f"Expected dtypes: {valid_dtypes}"
                        )
                    )
                )

    def validate(self, split: Optional[str] = None):
        self.apply_common_validations(split, batch_size=self.dataset_args["batch_size"])

        # check dtypes
        # NOTE doing dtype check before task specific data filter because :meth ner_data_filter
        # assumes the dtypes for columns
        self.check_column_dtypes()
        # using ner specific filter
        self.ner_data_filter()
