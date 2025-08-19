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
    TaskConstants,
    Tasks,
    STRING_DTYPES
)

from ....utils.data_utils import AzuremlDataset, clean_column_name
from ....utils.validation_utils import AzuremlValidatorMixin

from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.data.data_collator import DataCollatorForSeq2Seq

from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError

from azureml.acft.common_components import get_logger_app
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore

logger = get_logger_app(__name__)


@dataclass
class TranslationPreprocessArgs(PreprocessArgsTemplate):
    # Specify the defaults for all new attributes of TranslationPreprocessArgs + inhertied attributes from
    # _PreprocessArgsTemplate here. Otherwise, there will be issues related to ordering of default and
    # non-default attributes

    # extra args
    # default values for source_lang and target_lang are from wmt16-ro-en dataset
    source_lang: str = field(
        default="ro"
    )
    target_lang: str = field(
        default="en"
    )
    tok_prefix: str = field(
        default=""
    )
    # Text Generation args
    num_beams: int = field(
        default=1
    )
    max_generate_length: Optional[int] = field(
        default=None
    )
    #
    problem_type: Optional[str] = field(
        default=None
    )
    task_name: str = field(
        default=Tasks.TRANSLATION
    )
    batch_size: int = field(
        default=1000
    )
    placeholder_label_column: str = field(
        default="target_lang"
    )
    metric_for_best_model: str = field(
        default="bleu"
    )
    greater_is_better: bool = field(
        default=True
    )
    mlflow_task_type: str = field(
        default=MLFlowHFFlavourTasks.TRANSLATION
    )
    pad_to_max_length: bool = field(
        default=True
    )
    max_seq_length: int = field(
        default=-1
    )
    max_target_length: int = field(
        default=-1
    )

    def __post_init__(self):
        # setting the defaults for mutable arguments will cause issue in case of multiple class
        # initializations. so, placeholders are set here
        self.placeholder_required_columns = ["source_lang", "target_lang"]
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


class TranslationDataset(AzuremlDataset, AzuremlValidatorMixin):

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
        """
        Collation function for dynamic padding. If padding is happening in preprocessing such that
        all the examples are of equal length, the collation function can simply return None
        """
        return DataCollatorForSeq2Seq(self.tokenizer) if self.tokenizer is not None else None

    def encode_dataset(self):
        """
        datasets: HuggingFace datasets object
        tokenizer: HuggingFace tokenizer
        kwargs: max_seq_length, pad_to_max_length, source_lang, target_lang

        https://github.com/huggingface/notebooks/blob/main/examples/translation.ipynb
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
            inputs = [tok_prefix + lang_text for lang_text in examples[source_lang]]

            # input language tokenization
            model_inputs = self.tokenizer(
                inputs,
                padding=self.dataset_args["padding"],
                max_length=self.dataset_args["max_length"],
                truncation=self.dataset_args["truncation"]
            )

            # Setup the tokenizer for targets
            with self.tokenizer.as_target_tokenizer():
                labels = self.tokenizer(
                    examples[target_lang],
                    padding=self.dataset_args["padding"],
                    max_length=self.dataset_args["max_length"],
                    truncation=self.dataset_args["truncation"]
                )
                # ignore padding tokens in the loss calculation
                if self.dataset_args["padding"] == "max_length":
                    labels["input_ids"] = [
                        [
                            (lbl if lbl != self.tokenizer.pad_token_id else TaskConstants.TRANSLATION_IGNORE_INDEX)
                            for lbl in label
                        ]
                        for label in labels["input_ids"]
                    ]

            model_inputs["labels"] = labels["input_ids"]

            return model_inputs

        source_lang, target_lang = self.dataset_args["source_lang"], self.dataset_args["target_lang"]
        tok_prefix = self.dataset_args["tok_prefix"]

        self.dataset = self.dataset.map(
            tokenize_func,
            batched=True,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"],
            remove_columns=self.dataset.column_names
        )

    def update_dataset_columns_with_prefix(self):
        """Update the source_lang, target_lang with prefix"""
        if self.dataset_args is not None:
            self.dataset_args["source_lang"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["source_lang"]
            if self.dataset_args["target_lang"] is not None:
                self.dataset_args["target_lang"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["target_lang"]

        return super().update_dataset_columns_with_prefix()

    def translation_data_filter(self):
        """Remove the examples that contain null data. specific to translation task"""

        if self.dataset_args is None:
            logger.info(f"Dataset args is {self.dataset_args}. Skipping translation data filter")
            return

        # apply ner specific data filter
        if self.dataset_args["target_lang"] is None:
            logger.info("target language key is not present. skipping translation specific data filter")
            return

        # filter examples with empty sorce or target language
        filter_lambda = lambda example: (
            example[self.dataset_args["target_lang"]].strip() != "" or  # type: ignore
            example[self.dataset_args["source_lang"]].strip() != ""  # type:  ignore
        )
        pre_filter_rows = self.dataset.num_rows
        self.dataset = self.dataset.filter(
            filter_lambda,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"]
        )
        post_filter_rows = self.dataset.num_rows
        logger.info(f"Translation data filter | before example count: {pre_filter_rows} | after example count: {post_filter_rows}")
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
        self.check_column_contents(self.dataset_args['source_lang'], self.dataset_args['target_lang'])
        # check dtypes
        # NOTE doing dtype check before task specific data filter because :meth translation_data_filter
        # assumes the dtypes for columns
        self.check_column_dtypes()
        # using ner specific filter
        self.translation_data_filter()
