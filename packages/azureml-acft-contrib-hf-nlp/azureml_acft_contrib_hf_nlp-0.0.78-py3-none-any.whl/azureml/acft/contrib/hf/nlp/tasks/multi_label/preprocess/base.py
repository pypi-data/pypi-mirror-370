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

import ast
from pathlib import Path

from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
from sklearn.preprocessing import MultiLabelBinarizer

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

from datasets.arrow_dataset import Dataset
from datasets import Sequence

from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.data.data_collator import DataCollatorWithPadding

from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError

from azureml.acft.common_components import get_logger_app
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore
from azureml.acft.contrib.hf.nlp.constants.constants import DataSliceConstants


logger = get_logger_app(__name__)


@dataclass
class MultiLabelPreprocessArgs(PreprocessArgsTemplate):
    # Specify the defaults for all new attributes of MultiLabelPreprocessArgs +
    # inhertied attributes from _PreprocessArgsTemplate here.
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
        default="multi_label_classification"
    )
    task_name: str = field(
        default=Tasks.MULTI_LABEL_CLASSIFICATION

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
        default=MLFlowHFFlavourTasks.MULTI_LABEL_CLASSIFICATION
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
            STRING_DTYPES, STRING_DTYPES, STRING_DTYPES
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


class MultiLabelDataset(AzuremlDataset, AzuremlValidatorMixin):

    def __init__(
        self,
        path_or_dict: Union[str, Path],
        dataset_args: Optional[Dict[str, Any]] = None,
        required_columns: Optional[List[str]] = None,
        required_column_dtypes: Optional[List[List[str]]] = None,
        label_column: Optional[str] = None,
        label_column_optional: bool = False,
        tokenizer: Optional[PreTrainedTokenizerBase] = None,
        slice: str = DataSliceConstants.NO_SPLIT,
    ) -> None:
        # required_columns, required_column_dtypes are made optional to support loading the dataset
        # without the need for validation

        # special column is added for multi-label after the label_data is decoded and converted to list of string
        new_label_column = None
        if label_column is not None and dataset_args is not None and required_columns is not None and required_column_dtypes is not None:
            new_label_column = label_column + TaskConstants.MULTI_LABEL_NEW_COLUMN_SUFFIX
            dataset_args["label_key"] = new_label_column
            required_columns.append(new_label_column)
            required_column_dtypes.append(STRING_DTYPES)
            logger.info(f"Updated label column: {new_label_column}")
            logger.info(f"Updated required columns: {required_columns}")
            logger.info(f"Updated required column dtypes: {required_column_dtypes}")

        # initialize the dataset class
        super().__init__(
            path_or_dict,
            label_column=(
                new_label_column
                if new_label_column is not None else
                label_column
            ),
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
        self.old_label_column = label_column

    def get_collation_function(self) -> Optional[Callable]:
        """Collation function for dynamic padding"""
        return DataCollatorWithPadding(self.tokenizer) if self.tokenizer is not None else None

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
                # format the label key using multi-label binarizer. It gets converted to 1-hot vector
                result["labels"] = []
                for labels_list in examples[label_key]:
                    result["labels"].append(mlb.transform([labels_list])[0])

            return result

        # sentence and label keys
        sentence1_key, sentence2_key = self.dataset_args["sentence1_key"], self.dataset_args["sentence2_key"]
        label_key = self.dataset_args["label_key"]

        # convert label column to string
        if label_key is not None:
            # initialize sklearn multi label binarizer
            mlb = MultiLabelBinarizer()
            mlb.fit([class_names_train_plus_valid])

        # tokenize the data
        self.dataset = self.dataset.map(
            tokenize_func,
            batched=True,
            remove_columns=self.dataset.column_names,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"]
        )

    def decode_label_column(self, examples: Dict[str, Any]) -> Dict[str, Any]:
        """
        The label column of multi-label is a list of class names encoded as string i.e. of type string of list of string
        This function encodes the old label column and populates the new label column
        :param examples
            Dictionary of dataset examples
        """
        if self.old_label_column is None:
            logger.info(f"label column is {self.old_label_column}. skipping label column decoding")
            return examples

        item_decode_list = []
        for item in examples[self.old_label_column]:
            try:
                item_decode = ast.literal_eval(item)
            except Exception as e:
                raise ACFTDataException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=f"Data is incorrectly formatted. Error while using ast eval: {e}"
                    )
                )

            if not (
                isinstance(item_decode, List) and
                (item_decode and isinstance(item_decode[0], str))
            ):
                raise ValueError(f"Example data is incorrectly formatted. Expected list of strings. Found: {type(item_decode)}")
            item_decode_list.append(item_decode)

        # label column is created ONLY when old_label_column is present
        examples[self.label_column] = item_decode_list  # type: ignore

        return examples

    def update_dataset_columns_with_prefix(self):
        """Update the sentence1_key, sentece2_key and label_keys with prefix"""
        if self.dataset_args is not None:
            self.dataset_args["sentence1_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["sentence1_key"]
            if self.dataset_args["sentence2_key"] is not None:
                self.dataset_args["sentence2_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["sentence2_key"]
            if self.dataset_args["label_key"] is not None:
                self.dataset_args["label_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["label_key"]

        return super().update_dataset_columns_with_prefix()

    def load(self, slice: str = DataSliceConstants.NO_SPLIT) -> Dataset:
        """
        Load the dataset and add a dummy column for the new column
        new column will a list of strings which will be a decoded column of string input
        """
        dataset = super().load(slice)

        # add a dummy column with list of strings dtype
        dataset = dataset.add_column(
            name=self.label_column,
            column=[[""]] * len(dataset)
        )

        return dataset

    def multi_label_data_filter(self):
        """Remove the examples that contain null data. specific to multilabel task"""

        if self.dataset_args is None:
            logger.info(f"Dataset args is {self.dataset_args}. Skipping multilabel data filter")
            return

        # apply multilabel specific data filter
        if self.label_column is None:
            logger.info("label key is not present. skipping multilabel specific data filter")
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
        logger.info(f"Multilabel data filter | before example count: {pre_filter_rows} | after example count: {post_filter_rows}")
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

            if column_name == self.label_column:
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
            else:
                column_dtype = datset_features[column_name].dtype
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
        if self.dataset_args is None:
            logger.info(f"Dataset args is {self.dataset_args}. Skipping multilabel validate")
            return

        self.apply_common_validations(split, batch_size=self.dataset_args["batch_size"])

        # check if feature columns are identical
        self.check_column_contents(self.dataset_args["sentence1_key"], self.dataset_args["sentence2_key"])
        # check dtypes
        # NOTE doing dtype check before task specific data filter because :meth multi_label_data_filter
        # assumes the dtypes for columns
        self.check_column_dtypes()
        # remove empty sentence1 or sentence2
        self.multi_label_data_filter()
