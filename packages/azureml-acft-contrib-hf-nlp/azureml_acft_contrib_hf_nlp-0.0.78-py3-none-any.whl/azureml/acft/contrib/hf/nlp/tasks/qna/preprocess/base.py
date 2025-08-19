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

from datasets import Sequence

from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError

from azureml.acft.common_components import get_logger_app
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore


logger = get_logger_app(__name__)


@dataclass
class QnAPreprocessArgs(PreprocessArgsTemplate):
    # Specify the defaults for all new attributes of QnAPreprocessArgs +
    # inhertied attributes from PreprocessArgsTemplate here.
    # Otherwise, there will be issues related to ordering of default and
    # non-default attributes

    # extra args
    # Makesure the extra args don't overlap with names of PreprocessArgs Template
    # The default values for dataset placeholder keys is from SQuAD / SQuADv2
    question_key: str = field(
        default="question"
    )
    context_key: str = field(
        default="context"
    )
    answers_key: Optional[str] = field(
        default="answers"
    )
    answer_start_key: Optional[str] = field(
        default="answer_start"
    )
    answer_text_key: Optional[str] = field(
        default="text"
    )
    doc_stride: int = field(
        default=128
    )
    placeholder_nested_columns: List[str] = field(
        init=False,
        default_factory=list
    )
    nested_columns: List[str] = field(
        init=False,
        default_factory=list
    )
    # used for metric calculation
    n_best_size: int = field(
        default=20
    )
    max_answer_length_in_tokens: int = field(
        default=30
    )
    #
    problem_type: Optional[str] = field(
        default=None
    )
    task_name: str = field(
        default=Tasks.QUESTION_ANSWERING

    )
    batch_size: int = field(
        default=1000
    )
    placeholder_label_column: str = field(
        default="answers_key"
    )
    metric_for_best_model: str = field(
        default="f1"
    )
    greater_is_better: bool = field(
        default=True
    )
    mlflow_task_type: str = field(
        default=MLFlowHFFlavourTasks.QUESTION_ANSWERING
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
        self.placeholder_required_columns = [
            "question_key", "context_key", "answers_key", "answer_start_key", "answer_text_key"
        ]
        self.placeholder_nested_columns = ["answer_start_key", "answer_text_key"]
        self.placeholder_required_column_dtypes = [
            STRING_DTYPES, STRING_DTYPES, "NOT_VALIDATED", INT_DTYPES, STRING_DTYPES
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

        if self.placeholder_nested_columns is not None:
            self.nested_columns = []
            for idx, col_name in enumerate(self.placeholder_nested_columns):
                decoded_arg = getattr(self, col_name, None)
                if decoded_arg is not None:
                    self.nested_columns.append(decoded_arg)

        self.validate_required_columns()
        self.label_column = getattr(self, self.placeholder_label_column)


class QnADataset(AzuremlDataset, AzuremlValidatorMixin):

    def __init__(
        self,
        path_or_dict: Union[str, Path],
        dataset_args: Optional[Dict[str, Any]] = None,
        required_columns: Optional[List[str]] = None,
        required_column_dtypes: Optional[List[List[str]]] = None,
        label_column: Optional[str] = None,
        label_column_optional: bool = False,
        tokenizer: Optional[PreTrainedTokenizerBase] = None,
        dataset_split_kwargs: Optional[Dict[str, Any]] = None,
        nested_columns: Optional[List[str]] = None,
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
        self.nested_columns = nested_columns or []

    def get_collation_function(self) -> Optional[Callable]:
        """
        Collation function for dynamic padding.
        No collation function is needed as the examples are padded during encoding.
        """
        return None

    def update_dataset_columns_with_prefix(self):
        """Update the question_key, context_key, answers_key, answer_start_key, answer_text_key with prefix"""
        # update the dataset columns
        def update_datset_columns(examples: Dict[str, Any]) -> Dict[str, Any]:
            if self.dataset_args is None:
                raise ValueError("Dataset args is needed to update dataset columns")
            return_examples = {}
            for column_name, column_data in examples.items():
                if column_name != self.dataset_args["answers_key"]:
                    return_examples.update(
                        {
                            AzuremlConstants.DATASET_COLUMN_PREFIX+column_name: column_data
                        }
                    )
                else:
                    answers_col_data = []
                    for item in column_data:
                        if not isinstance(item, dict):
                            raise ValueError(
                                f"answers column is incorrectly formatted: expected: {dict} | found: {type(item)}")
                        old_keys = list(item.keys())
                        new_keys = [AzuremlConstants.DATASET_COLUMN_PREFIX+k for k in old_keys]
                        answers_col_data.append({nk: item[ok] for ok, nk in zip(old_keys, new_keys)})
                    return_examples.update(
                        {
                            AzuremlConstants.DATASET_COLUMN_PREFIX+column_name: answers_col_data
                        }
                    )
            return return_examples

        try:
            self.dataset = self.dataset.map(
                update_datset_columns,
                batched=True,
                remove_columns=self.dataset.column_names,
                batch_size=self.dataset_args["batch_size"],
                writer_batch_size=self.dataset_args["batch_size"]
            )
        except Exception as e:
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=f"Data is incorrectly formatted. Error while updating dataset columns: {e}"
                )
            )

        # update label column
        if self.label_column is not None:
            self.label_column = AzuremlConstants.DATASET_COLUMN_PREFIX + self.label_column

        # update nested columns
        for idx, _ in enumerate(self.nested_columns):
            self.nested_columns[idx] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.nested_columns[idx]

        # updating the placeholder column names
        if self.dataset_args is not None:
            self.dataset_args["question_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["question_key"]
            self.dataset_args["context_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["context_key"]
            if self.dataset_args["answers_key"] is not None:
                self.dataset_args["answers_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["answers_key"]
            if self.dataset_args["answer_start_key"] is not None:
                self.dataset_args["answer_start_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["answer_start_key"]
            if self.dataset_args["answer_text_key"] is not None:
                self.dataset_args["answer_text_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["answer_text_key"]

    def encode_dataset(self):
        """
        datasets: HuggingFace datasets object
        tokenizer: HuggingFace tokenizer
        kwargs: max_seq_length, pad_to_max_length, question_key, answers_key, context_key, doc_stride

        https://github.com/huggingface/notebooks/blob/main/examples/question_answering.ipynb
        """

        if self.tokenizer is None or self.dataset_args is None:
            raise ValueError(
                "Both tokenizer and dataset args needed encode the dataset. "
                "Either or both of them is not defined."
            )

        def tokenize_func(examples):
            # This is a redundant check. Adding this to avoid linting issues
            if self.tokenizer is None or self.dataset_args is None:
                raise ValueError(
                    "Both tokenizer and dataset args needed encode the dataset. "
                    "Either or both of them is not defined."
                )

            nonlocal example_count
            # Some of the questions have lots of whitespace on the left, which is not useful and will make the
            # truncation of the context fail (the tokenized question will take a lots of space). So we remove that
            # left whitespace
            # NOTE see if this assumption holds good
            # Check if doing strip() instead of lstrip() changes the accuracy
            # Check if removing the spaces, strip(), for the context changes the accuracy
            # NOTE Removing the question strip to be consistent with HF pipelines
            # examples[question_key] = [q.lstrip() for q in examples[question_key]]

            # Tokenize our examples with truncation and padding, but keep the overflows using a stride. This results
            # in one example possible giving several features when a context is long, each of those features having a
            # context that overlaps a bit the context of the previous feature.
            tokenized_examples = self.tokenizer(
                examples[question_key if pad_on_right else context_key],
                examples[context_key if pad_on_right else question_key],
                truncation=self.dataset_args["truncation"],
                max_length=self.dataset_args["max_length"],
                stride=self.dataset_args["doc_stride"],
                return_overflowing_tokens=True,
                return_offsets_mapping=True,  # token to char map
                padding=self.dataset_args["padding"],
            )

            # Since one example might give us several features if it has a long context, we need a map from a feature to
            # its corresponding example. This key gives us just that.
            sample_mapping = tokenized_examples.pop("overflow_to_sample_mapping")
            # The offset mappings will give us a map from token to character position in the original context. This will
            # help us compute the start_positions and end_positions.
            offset_mapping = tokenized_examples.pop("offset_mapping")

            # Let's label those examples!
            if answers_key is not None:
                tokenized_examples["start_positions"] = []
                tokenized_examples["end_positions"] = []

            # [validation] We keep the example_id that gave us this feature and we will store the offset mappings.
            # the context and answers are duplicated across different features of each example so that they can be used in
            # metric calculation
            context_index = 1 if pad_on_right else 0
            tokenized_examples["example_id"] = []
            tokenized_examples["offset_mapping_validation"] = []

            for i, offsets in enumerate(offset_mapping):
                # We will label impossible answers with the index of the CLS token.
                input_ids = tokenized_examples["input_ids"][i]
                if self.tokenizer.cls_token_id is not None:
                    cls_index = input_ids.index(self.tokenizer.cls_token_id)
                else:
                    cls_index = 0

                # Grab the sequence corresponding to that example (to know what is the context and what is the question)
                sequence_ids = tokenized_examples.sequence_ids(i)

                # One example can give several spans, this is the index of the example containing this span of text.
                sample_index = sample_mapping[i]
                if answers_key is not None:
                    answers = examples[answers_key][sample_index]
                context = examples[context_key][sample_index]

                # Columns required during validation. The `example_id` helps in grouping all the context splits for
                # an example
                tokenized_examples["example_id"].append(example_count + sample_index)
                # Using [-1, -1] instead of None as the dummy value. This is bcoz there is a mismatch in the loaded data
                # after saving with None using `datasets.to_json`
                tokenized_examples["offset_mapping_validation"].append([
                    (o if sequence_ids[k] == context_index else [-1, -1]) for k, o in enumerate(offsets)])

                # If no answers are given, set the cls_index as answer.
                if answers_key is not None:
                    if len(answers[answer_start_key]) == 0:
                        tokenized_examples["start_positions"].append(cls_index)
                        tokenized_examples["end_positions"].append(cls_index)
                    else:
                        # Start/end character index of the answer in the text.
                        start_char = answers[answer_start_key][0]
                        end_char = start_char + len(answers[answer_text_key][0])

                        # Start token index of the current span in the text.
                        # TODO check if we can optimize using np
                        token_start_index = 0
                        while sequence_ids[token_start_index] != (1 if pad_on_right else 0):
                            token_start_index += 1
                            if token_start_index == len(sequence_ids):
                                token_start_index -= 1
                                break

                        # End token index of the current span in the text.
                        token_end_index = len(input_ids) - 1
                        while sequence_ids[token_end_index] != (1 if pad_on_right else 0):
                            token_end_index -= 1
                            if token_end_index < 0:
                                token_end_index += 1
                                break

                        # Detect if the answer is out of the span (in which case this feature is labeled with the CLS index).
                        # offsets[token_start_index][0] <= start_char < end_char <= offsets[token_end_index][1]
                        if not (offsets[token_start_index][0] <= start_char and offsets[token_end_index][1] >= end_char):
                            tokenized_examples["start_positions"].append(cls_index)
                            tokenized_examples["end_positions"].append(cls_index)
                        else:
                            # Otherwise move the token_start_index and token_end_index to the two ends of the answer.
                            # Note: we could go after the last offset if the answer is the last word (edge case).
                            while token_start_index < len(offsets) and offsets[token_start_index][0] <= start_char:
                                token_start_index += 1
                            tokenized_examples["start_positions"].append(token_start_index - 1)
                            while offsets[token_end_index][1] >= end_char:
                                token_end_index -= 1
                            tokenized_examples["end_positions"].append(token_end_index + 1)

            example_count += (1 if isinstance(examples[question_key], str) else len(examples[question_key]))

            return tokenized_examples

        # Dataset keys
        question_key, context_key = self.dataset_args['question_key'], self.dataset_args["context_key"]
        answers_key = self.dataset_args["answers_key"]
        answer_start_key = self.dataset_args["answer_start_key"]
        answer_text_key = self.dataset_args["answer_text_key"]
        pad_on_right = self.tokenizer.padding_side == "right"

        if self.dataset_args["max_seq_length"] == -1:
            # hardcoding the value for 384 based on HF pipeline preprocessing
            # https://github.com/huggingface/transformers/blob/5764efe544de909e93bfde16489b5a0975fce1c2/src/transformers/pipelines/question_answering.py#L403
            self.dataset_args["max_seq_length"] = 384
        self.dataset_args["max_seq_length"] = min(self.dataset_args["max_seq_length"], self.tokenizer.model_max_length)  # input seq length

        # filter examples greater than max length
        pre_filter_count = len(self.dataset)
        self.dataset = self.dataset.filter(
            self._filter_questions_ge_max_len,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"]
        )
        post_filter_count = len(self.dataset)
        logger.info(
            "Questions greater than model max length are filtered - "
            f"Before filter count: {pre_filter_count} | After filter count: {post_filter_count}"
        )
        example_count = 0
        self.dataset = self.dataset.map(
            tokenize_func,
            batched=True,
            remove_columns=self.dataset.column_names,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"]
        )

    def _filter_questions_ge_max_len(self, example: Dict[str, Any]):
        if self.tokenizer is None or self.dataset_args is None:
            raise ValueError(
                "Tokenizer and dataset_args are needed to filter questions greater than max length"
            )
        tokenized_example = self.tokenizer(
            example[self.dataset_args["question_key"]],
            add_special_tokens=False,
            truncation=False
        )
        return True if len(tokenized_example["input_ids"]) <= self.dataset_args["max_seq_length"] else False

    def match_columns(self) -> None:
        """
        Match the dataset columns with the keep columns and raise error otherwise
        """

        # first match outer columns as inner column might or might not always present
        outer_columns = [name for name in self.required_columns if name not in self.nested_columns]
        if sorted(outer_columns) != sorted(self.dataset.column_names):
            logger.warning(
                "Exception occured while matching outer dataset columns with user passed columns, scrubbing exception")
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=(
                        f"Path or dict: {self.path_or_dict}."
                        f"Dataset Columns: {self._remove_dataset_column_prefix(self.original_datset_columns)}."
                        f"User Passed Columns: {self._remove_dataset_column_prefix(self.required_columns)}."
                    )
                )
            )

        # match nested columns
        answers_key = self.dataset_args["answers_key"]
        if self.label_column is not None:
            if not isinstance(self.dataset.features[answers_key], dict):
                logger.warning(
                    "Invalid dataset format found during match columns, scrubbing exception")
                raise ACFTDataException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=(
                            f"Path or dict: {self.path_or_dict}."
                            f"Answers format: {type(self.dataset.features[answers_key])}."
                            "Expected format: dict."
                        )
                    )
                )

            nested_answer_keys = list(self.dataset.features[answers_key].keys())
            if sorted(nested_answer_keys) != sorted(self.nested_columns):
                logger.warning(
                    "Exception occured while matching nested dataset columns with user passed columns, scrubbing exception")
                raise ACFTDataException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=(
                            f"Path or dict: {self.path_or_dict}."
                            f"Dataset Columns: {self._remove_dataset_column_prefix(nested_answer_keys)}."
                            f"User Passed Columns: {self._remove_dataset_column_prefix(self.nested_columns)}."
                        )
                    )
                )

    def check_column_dtypes(self) -> None:
        """
        check the keep columns with keep column dtypes and raise error otherwise
        """

        datset_features = self.dataset.features
        for column_name, valid_dtypes in zip(self.required_columns, self.required_column_dtypes):
            # ignore answers key validation
            if column_name == self.dataset_args["answers_key"]:
                continue
            if self.label_column is None and column_name in self.nested_columns:
                logger.info(f"Label column not present. Skipping nested column verification!")
                continue

            # special handling for nested columns
            if column_name in self.nested_columns:
                answers_key = self.dataset_args["answers_key"]
                sequence_column_type = isinstance(datset_features[answers_key][column_name], Sequence)
                # Check if answers key is of sequence type
                if not sequence_column_type:
                    logger.warning("Found invalid feature type for nested column")
                    raise ACFTDataException._with_error(
                        AzureMLError.create(
                            ACFTUserError,
                            pii_safe_message=(
                                f"File path or data: {self.path_or_dict}\n"
                                f"type mismatch for feature {self._remove_dataset_column_prefix(column_name)}\n"
                                f"Found type: {type(datset_features[answers_key][column_name])}\n"
                                f"Expected type: {Sequence}"
                            )
                        )
                    )

                # check for the presence of column name in answers nested dict
                column_dtype = datset_features[answers_key][column_name].feature.dtype

            else:
                # outer column keys handling
                if column_name not in datset_features:
                    logger.warning("Exception occured column name not present in dataset features, scrubbing exception")
                    raise ACFTDataException._with_error(
                        AzureMLError.create(
                            ACFTUserError,
                            pii_safe_message=(
                                f"{column_name} not present in column to dataset features. "
                                f"The following columns are present: {list(datset_features.keys())}"
                            )
                        )
                    )
                else:
                    column_dtype = datset_features[column_name].dtype

            if column_dtype not in valid_dtypes:
                logger.warning("Exception occured column dtype not valid, scrubbing exception")
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

    def qna_data_filter(self):
        """Remove the examples that contain null data. specific to ner task"""

        if self.dataset_args is None:
            logger.info(f"Dataset args is {self.dataset_args}. Skipping qna data filter")
            return
        
        answers_key = self.dataset_args["answers_key"]
        answer_start_key = self.dataset_args["answer_start_key"]
        answer_text_key = self.dataset_args["answer_text_key"]
        
        # filter examples with mismatched sizes for answer_text_key and answer_start_key
        def mismatched_start_text_key(example):
            if len(example[answers_key][answer_start_key]) != len(example[answers_key][answer_text_key]):
                return False
            return True

        pre_filter_rows = self.dataset.num_rows
        self.dataset = self.dataset.filter(
            mismatched_start_text_key,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"]
        )
        post_filter_rows = self.dataset.num_rows
        logger.info(f"mismatched answer_start and answer_text sizes filter | before example count: {pre_filter_rows} | after example count: {post_filter_rows}")
        
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
        self.check_column_contents(self.dataset_args["question_key"], self.dataset_args["context_key"])
        # check dtypes
        # NOTE doing dtype check before task specific data filter because :meth single_label_data_filter
        # assumes the dtypes for columns
        self.check_column_dtypes()
        # remove examples with empty sentence1 or sentence2
        self.qna_data_filter()
