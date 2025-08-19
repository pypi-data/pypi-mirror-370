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

from ....constants.constants import AzuremlConstants, PreprocessArgsTemplate
from ....constants.constants import Tasks, MLFlowHFFlavourTasks
from ....constants.constants  import STRING_DTYPES, INT_DTYPES

from ....utils.data_utils import AzuremlDataset, clean_column_name
from ....utils.validation_utils import AzuremlValidatorMixin

from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers import DataCollatorForLanguageModeling

from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError

from azureml.acft.common_components import get_logger_app
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore


logger = get_logger_app(__name__)


@dataclass
class TextGenerationPreprocessArgs(PreprocessArgsTemplate):
    # Specify the defaults for all new attributes of TextGenerationPreprocessArgs +
    # inhertied attributes from PreprocessArgsTemplate here.
    # Otherwise, there will be issues related to ordering of default and
    # non-default attributes

    # extra args
    # Makesure the extra args don't overlap with names of PreprocessArgs Template
    text_key: str = field(
        default="text"
    )
    ground_truth_key: str = field(
        default=None
    )
    #
    problem_type: Optional[str] = field(
        default="text_generation"
    )
    task_name: str = field(
        default=Tasks.TEXT_GENERATION
    )
    batch_size: int = field(
        default=1000
    )
    placeholder_label_column: str = field(
        default="ground_truth_key"
    )
    metric_for_best_model: str = field(
        default="loss"
    )
    greater_is_better: bool = field(
        default=False
    )
    mlflow_task_type: str = field(
        default=MLFlowHFFlavourTasks.TEXT_GENERATION
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
        self.placeholder_required_columns = ["text_key", "ground_truth_key"]
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


class TextGenerationDataset(AzuremlDataset, AzuremlValidatorMixin):

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
        # `mlm` is whether or not to use masked language modeling. If set to False, the labels are the
        # same as the inputs with the padding tokens ignored (by setting them to -100). Otherwise, the
        # labels are -100 for non-masked tokens and the value to predict for the masked token.
        return DataCollatorForLanguageModeling(self.tokenizer, mlm=False) if self.tokenizer is not None else None

    def update_dataset_columns_with_prefix(self):
        """Update the text_key"""
        if self.dataset_args is not None:
            self.dataset_args["text_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["text_key"]
            if self.dataset_args.get("ground_truth_key"):
                self.dataset_args["ground_truth_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["ground_truth_key"]

        return super().update_dataset_columns_with_prefix()

    def concatenate_ground_truth(self):

        def concat(example):
            example[text_key] = example[text_key] + example[ground_truth_key]
            return example

        if self.dataset_args is not None and self.dataset_args.get("ground_truth_key"):
            text_key = self.dataset_args["text_key"]
            ground_truth_key = self.dataset_args["ground_truth_key"]
            self.dataset = self.dataset.map(
                concat,
                batched=False,
            )

    def encode_dataset(self):
        """
        datasets: HuggingFace datasets object
        tokenizer: HuggingFace tokenizer
        kwargs: max_seq_length, pad_to_max_length, text_key

        https://github.com/huggingface/notebooks/blob/main/examples/language_modeling.ipynb
        """

        if self.tokenizer is None or self.dataset_args is None:
            raise

        def update_examples_with_bos_eos_token(examples):
            if self.tokenizer is None:
                raise

            prefix_to_add = self.tokenizer.bos_token if add_bos_token else ""
            suffix_to_add = self.tokenizer.eos_token if add_eos_token else ""
            modified_examples = {}
            for col_name in examples:
                # Appending the bos and eos token to all the examples
                modified_examples[col_name] = [
                    prefix_to_add + ex + suffix_to_add
                    for ex in examples[col_name]
                ]

            return modified_examples

        def tokenize_func(examples):
            if self.tokenizer is None or self.dataset_args is None:
                raise

            # Tokenize text
            result = self.tokenizer(
                examples[text_key],
                padding=self.dataset_args["padding"],
                max_length=self.dataset_args["max_length"],
                truncation=self.dataset_args["truncation"]
            )

            if add_eos_token:
                # Add eos token to examples for which the example text is greater than max length that are truncated
                # This is when we truncation happens to the right
                for ex_id in range(len(result["input_ids"])):
                    if len(result["input_ids"][ex_id]) > 0 and result["input_ids"][ex_id][-1] not in [self.tokenizer.pad_token_id, self.tokenizer.eos_token_id]:
                        result["input_ids"][ex_id][-1] = self.tokenizer.eos_token_id

            if add_bos_token:
                # Add bos token to examples for which the example text is greater than max length that are truncated
                # This is when truncation happens to the left
                for ex_id in range(len(result["input_ids"])):
                    if len(result["input_ids"][ex_id]) > 0 and result["input_ids"][ex_id][0] not in [self.tokenizer.pad_token_id, self.tokenizer.bos_token_id]:
                        result["input_ids"][ex_id][0] = self.tokenizer.bos_token_id

            return result

        def _batch_max_input_ids_count(examples):
            return {
                'batch_max_input_ids_count': [
                    max(map(len, examples['input_ids']))
                ]
            }

        def group_texts(examples):
            # Concatenate all texts.
            concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
            total_length = len(concatenated_examples[list(examples.keys())[0]])
            # We drop the small remainder,
            # we could add padding if the model supported it instead of this drop,
            # this part can be customized as per needs.
            if total_length >= block_size:
                total_length = (total_length // block_size) * block_size
            # Split by chunks of block_size.
            result = {
                k: [t[i : i + block_size] for i in range(0, total_length, block_size)]
                for k, t in concatenated_examples.items()
            }
            result["labels"] = result["input_ids"].copy()
            return result

        # text key and block size
        text_key = self.dataset_args["text_key"]
        block_size = self.dataset_args["max_seq_length"]

        # manually add bos and eos token if not already added
        sample_tokenized_text = self.tokenizer("hello world")
        add_bos_token = sample_tokenized_text["input_ids"][0] != self.tokenizer.bos_token_id
        if add_bos_token:
            logger.info("The default tokenizer doesn't add the bos token. Manually adding the bos token.")
        add_eos_token = sample_tokenized_text["input_ids"][-1] != self.tokenizer.eos_token_id
        if add_eos_token:
            logger.info("The default tokenizer doesn't add the eos token. Manually adding the eos token.")
        if add_bos_token or add_eos_token:
            self.dataset = self.dataset.map(
                update_examples_with_bos_eos_token,
                batched=True,
                batch_size=self.dataset_args["batch_size"],
                writer_batch_size=self.dataset_args["batch_size"],
            )

        # tokenize the data
        self.dataset = self.dataset.map(
            tokenize_func,
            batched=True,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"],
            remove_columns=self.dataset.column_names,
        )

        # calculate the max sequence length in the user examples
        # NOTE Separate this into a common utility function to be used for all tasks
        collated_batch_max_input_ids_count = self.dataset.map(
            _batch_max_input_ids_count,
            batched=True,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"],
            remove_columns=self.dataset.column_names,
        )
        calculated_max_sequence_len = 0
        for item in collated_batch_max_input_ids_count['batch_max_input_ids_count']:
            calculated_max_sequence_len = max(calculated_max_sequence_len, item)
        logger.info(f"Calculated sequence length: {calculated_max_sequence_len}")

        # This dataset contains the token sequences, but some of these are
        # longer than the maximum input length for the model.
        # You can now use a second preprocessing function to
        # (i) concatenate all the sequences
        # (ii) split the concatenated sequences into shorter chunks defined by `block_size``,
        #   which should be both shorter than the maximum input length and short enough for your GPU RAM.
        # XXX This preprocessing logic of batching the examples will be added in next iteration

        # prepare the data of `block_size` length
        # self.dataset = self.dataset.map(
        #     group_texts,
        #     batched=True,
        #     batch_size=self.dataset_args["batch_size"],
        #     writer_batch_size=self.dataset_args["batch_size"],
        # )

    def text_generation_data_filter(self):
        """Remove the examples that contain null data. specific to text-generation task"""

        if self.dataset_args is None:
            logger.info(f"Dataset args is {self.dataset_args}. Skipping text-generation data filter")
            return

        # filter examples with empty sentence1 or sentence2
        # dataset_args is not None at this point
        filter_lambda = lambda example: (
            example[self.dataset_args["text_key"]] != ""  # type: ignore
        )
        pre_filter_rows = self.dataset.num_rows
        self.dataset = self.dataset.filter(
            filter_lambda,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"]
        )
        post_filter_rows = self.dataset.num_rows
        logger.info(f"Text generation data filter | before example count: {pre_filter_rows} | "
                    f"after example count: {post_filter_rows}"
                )
        if post_filter_rows == 0:
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=f"Found no examples after data preprocessing for {self.path_or_dict}"
                )
            )

    def validate(self, split: Optional[str] = None, task_name: Optional[str] = None) -> None:

        # common validations
        # - remove extra columns
        # - match columns
        # - check for duplicate columns
        # - remove null examples
        # - check min samples
        self.apply_common_validations(split, batch_size=self.dataset_args["batch_size"], task_name=task_name)

        # filter data
        # check dtypes
        # NOTE doing dtype check before task specific data filter because :meth text_generation_data_filter
        # assumes the dtypes for columns
        self.check_column_dtypes()
        # remove examples with empty text
        self.text_generation_data_filter()
