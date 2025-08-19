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

import numpy as np
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field
import torch

from ....constants.constants import (
    PreprocessArgsTemplate, AzuremlConstants, Tasks, MLFlowHFFlavourTasks, TaskConstants, DatasetSplit
)
from ....utils.data_utils import clean_column_name, AzuremlDataset
from ....utils.validation_utils import AzuremlValidatorMixin

from transformers.tokenization_utils_base import PreTrainedTokenizerBase

from transformers import DataCollatorForLanguageModeling

from azureml.acft.common_components.utils.error_handling.exceptions import ACFTUserException, ACFTDataException, ACFTValidationException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml.acft.common_components import get_logger_app

from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore


logger = get_logger_app(__name__)


DUMMY_VALUE = "dummy_value"

IGNORE_INDEX = -100

ZERO_ASSISTANT_TOKENS_ERROR = (
    "Unable to continue finetuning. No assistant tokens found after preprocessing.\n1. "
    "Please increase the :param `max_seq_len` to higher value and try again.\n2. "
    "This could also be an issue with ChatSpecialTokens. Please report the issue for resolution.\n"
)

@dataclass
class ChatCompletionPreprocessArgs(PreprocessArgsTemplate):
    # Specify the defaults for all new attributes of ChatCompletionPreprocessingArgs +
    # inhertied attributes from PreprocessArgsTemplate here.
    # Otherwise, there will be issues related to ordering of default and
    # non-default attributes

    # extra args
    # Makesure the extra args don't overlap with names of PreprocessArgs Template
    chat_key: str = field(
        default="messages"
    )
    placeholder_label_column: str = field(
        default=DUMMY_VALUE
    )
    problem_type: Optional[str] = field(
        default=None
    )
    task_name: str = field(
        default=Tasks.CHAT_COMPLETION
    )
    batch_size: int = field(
        default=1000
    )
    metric_for_best_model: str = field(
        default="loss"
    )
    greater_is_better: bool = field(
        default=False
    )
    mlflow_task_type: str = field(
        default=MLFlowHFFlavourTasks.CHAT_COMPLETION
    )
    pad_to_max_length: bool = field(
        default=False
    )
    max_seq_length: int = field(
        default=-1
    )

    def __post_init__(self):
        # setting the defaults for mutable arguments will cause issue in case of multiple class
        # initializations. so, placeholders are set here
        self.placeholder_required_columns = ["chat_key"]
        self.placeholder_required_column_dtypes = [[DUMMY_VALUE]]
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
        self.label_column = DUMMY_VALUE


@dataclass
class CustomToken:
    """
    Custom tokens to be used for masking user tokens after tokenization.

    :param content - The value of the token. The value is NOT always part of the vocabulary.
      The specifies the string identifier to identify specific points in the chat templated text.
        - In case of response_template, the identifier is to used to identify the start of assistant response.
        - In case of instruction_template, the identifier is used to identify the start of user instruction.
    :type str
    :param add_to_vocabulary - The flag indicates whether/not to add the add the token to the vocabualary.
    :type bool
    """
    content: str
    # NOTE Keeping the default to False as for most of the latest models we don't have to add new tokens to vocabulary
    # However, keeping this support to support legacy models like Llama-2-chat
    add_to_vocabulary: bool = False


@dataclass
class ChatSpecialTokens:
    """
    The chat special tokens are introduced to help mask user tokens and ONLY finetune on assistant tokens.

    :param instruction_template - Indicates the start of the user instruction
    :type CustomToken
    :param response_template - Indicates the start of assistant reponse
    :type CustomToken

    NOTE The chat tokens are read from :file finetune_config.json and the :attr response_template,
      :attr instruction_template are added to the vocabulary based on the :attr CustomToken.add_to_vocabulary.
    NOTE The chat tokens should be added to the vocabulary ONLY when there is a chance that either the
      :attr instruction_template.content or the :attr response_template.content interacts with the user passed text.
      Example #1: Phi-3-mini-128k-instruct - the chat special keys used are <|user|> and <|assistant|>.
        Since they are special tokens in the vocabulary, we can set add_to_vocabulary as False to both instruction
        and response template.
      Example #2: Meta-Llama-3-8B-Instruct - the chat special keys used are <|start_header_id|>user<|end_header_id|>
        and <|start_header_id|>assistant<|end_header_id|>. Though the tokens are not part of the vocabulary, the
        start and end identifiers <|start_header_id|> and <|end_header_id|> are special tokens in the vocabulary.
        As a result, we can be sure that the instruction and response template can be separately tokenized and will be
        identified in tokenized output.
      Example #3: Llama-2-chat - the chat special keys used are [INST] and [/INST]. Since these are not part of the
        vocabulary, there is a chance that these tokens can interact with the user passed text. In this case, we can
        set add_to_vocabulary as True to both the special tokens.
    """
    response_template: CustomToken
    instruction_template: CustomToken

    @classmethod
    def from_dict(cls, chat_special_tokens_dict: Dict[str, Union[str, Dict[str, str]]]):
        """Load the chat special tokens."""
        if chat_special_tokens_dict is None:
            raise ACFTUserException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message="Chat Special tokens are not set in finetune config."
                )
            )
        # Check if all fields are present
        class_data_fields = cls.__dataclass_fields__
        formatted_chat_data = {}
        for field_meta in class_data_fields.values():
            field_name = field_meta.name
            if field_name not in chat_special_tokens_dict:
                raise ACFTUserException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=(
                            f"`{field_name}` missing in :param chat_special_tokens in finetune config. "
                            "Please update the finetune config and try again."
                        )
                    )
                )
            if isinstance(chat_special_tokens_dict[field_name], str):
                formatted_chat_data[field_name] = CustomToken(
                    content=chat_special_tokens_dict[field_name]  # type: ignore
                )
            elif isinstance(chat_special_tokens_dict[field_name], dict):
                formatted_chat_data[field_name] = CustomToken(**chat_special_tokens_dict[field_name])  # type: ignore

        return cls(**formatted_chat_data)

    @classmethod
    def from_finetune_config(cls, finetune_config: Dict[str, Any]):
        """Load chat special tokens from finetune config."""
        return ChatSpecialTokens.from_dict(finetune_config.get("chat_special_tokens", None))

    def get_chat_tokens(self) -> List[CustomToken]:
        """Get the chat tokens."""
        return list(self.__dict__.values())
    
class CustomCollatorForCompletionOnlyLM(DataCollatorForLanguageModeling):
    """
    Data collator used for completion tasks. It ensures that all the tokens of the labels are set to an 'ignore_index'
    when they do not come from the assistant. This ensure that the loss is only
    calculated on the completion made by the assistant.

    Args:
        response_template (`Union[str, List[int]]`): the template form that indicates the start of the response, typically something like
            '### Response:\n'. It can also be passed as tokenized ids, which can be useful when using a tokenizer that encodes the response
            differently if it does not have proper context.
        instruction_template (`Union[str, List[int]]`): the template form that indicates the start of the human instruction, typically something like
            '### Human:\n'. Useful for assistant-style conversation datasets. It can also be passed as tokenized ids.
        mlm (`bool`, *optional*, defaults to `False`): Whether or not to use masked language modeling in the underlying
            `DataCollatorForLanguageModeling` class. Note that this option currently has no effect but is present
             for flexibility and backwards-compatibility.
        ignore_index (`int`, *optional*, defaults to `-100`):
            The index to use to ignore the initial tokens with
    """

    def __init__(
        self,
        response_template: Union[str, List[int]],
        instruction_template: Optional[Union[str, List[int]]] = None,
        *args,
        mlm: bool = False,
        ignore_index: int = -100,
        **kwargs,
    ):
        super().__init__(*args, mlm=mlm, **kwargs)

        self.instruction_template = instruction_template
        if isinstance(instruction_template, str):
            # The user provides a string, must tokenize
            self.instruction_token_ids = self.tokenizer.encode(self.instruction_template, add_special_tokens=False)
        else:
            # The user already provides the token ids
            self.instruction_token_ids = instruction_template

        self.response_template = response_template
        if isinstance(response_template, str):
            # The user provides a string, must tokenize
            self.response_token_ids = self.tokenizer.encode(self.response_template, add_special_tokens=False)
        else:
            # The user already provides the token ids
            self.response_token_ids = response_template

        if not self.mlm and self.instruction_template and self.tokenizer.pad_token_id == self.tokenizer.eos_token_id:
            logger.info(
                "The pad_token_id and eos_token_id values of this tokenizer are identical. "
                "If you are planning for multi-turn training, "
                "it can result in the model continuously generating questions and answers without eos token. "
                "To avoid this, set the pad_token_id to a different value."
            )

        self.ignore_index = ignore_index

    def torch_call(self, examples: List[Union[List[int], Any, Dict[str, Any]]]) -> Dict[str, Any]:
        batch = super().torch_call(examples)
        keep_indices = []

        if self.instruction_template is None:
            for i in range(len(examples)):
                response_token_ids_start_idx = None

                for idx in np.where(batch["labels"][i] == self.response_token_ids[0])[0]:
                    # `response_token_ids` is `'### Response:\n'`, here we are just making sure that the token IDs match
                    if (
                        self.response_token_ids
                        == batch["labels"][i][idx : idx + len(self.response_token_ids)].tolist()
                    ):
                        response_token_ids_start_idx = idx

                if response_token_ids_start_idx is None:
                    logger.info(
                        f"Could not find response key `{self.response_template}` in the "
                        f'following instance: {self.tokenizer.decode(batch["input_ids"][i])} '
                        f"This instance will be ignored in loss calculation. "
                        f"Note, if this happens often, consider increasing the `max_seq_length`."
                    )
                    #batch["labels"][i, :] = self.ignore_index
                else:
                    keep_indices.append(i)
                    response_token_ids_end_idx = response_token_ids_start_idx + len(self.response_token_ids)

                    # Make pytorch loss function ignore all tokens up through the end of the response key
                    batch["labels"][i, :response_token_ids_end_idx] = self.ignore_index

        else:
            for i in range(len(examples)):
                response_token_ids_idxs = []
                human_token_ids_idxs = []

                for assistant_idx in np.where(batch["labels"][i] == self.response_token_ids[0])[0]:
                    # find the indexes of the start of a response.
                    if (
                        self.response_token_ids
                        == batch["labels"][i][assistant_idx : assistant_idx + len(self.response_token_ids)].tolist()
                    ):
                        response_token_ids_idxs.append(assistant_idx + len(self.response_token_ids))

                if len(response_token_ids_idxs) == 0:
                    logger.info(
                        f"Could not find response key `{self.response_template}` in the "
                        f'following instance: {self.tokenizer.decode(batch["input_ids"][i])} '
                        f"This instance will be ignored in loss calculation. "
                        f"Note, if this happens often, consider increasing the `max_seq_length`."
                    )
                    #batch["labels"][i, :] = self.ignore_index
                    continue
                human_token_ids = self.instruction_token_ids
                for human_idx in np.where(batch["labels"][i] == human_token_ids[0])[0]:
                    # find the indexes of the start of a human answer.
                    if human_token_ids == batch["labels"][i][human_idx : human_idx + len(human_token_ids)].tolist():
                        human_token_ids_idxs.append(human_idx)
                if len(human_token_ids_idxs) == 0:
                    logger.info(
                        f"Could not find instruction key `{self.instruction_template}` in the "
                        f'following instance: {self.tokenizer.decode(batch["input_ids"][i])} '
                        f"This instance will be ignored in loss calculation. "
                        f"Note, if this happens often, consider increasing the `max_seq_length`."
                    )
                    #batch["labels"][i, :] = self.ignore_index
                    continue
                keep_indices.append(i)

                if (
                    len(human_token_ids_idxs) > 0
                    and len(response_token_ids_idxs) > 0
                    and human_token_ids_idxs[0] > response_token_ids_idxs[0]
                ):
                    human_token_ids_idxs = [0] + human_token_ids_idxs

                for idx, (start, end) in enumerate(zip(human_token_ids_idxs, response_token_ids_idxs)):
                    # Make pytorch loss function ignore all non response tokens
                    if idx != 0:
                        batch["labels"][i, start:end] = self.ignore_index
                    else:
                        batch["labels"][i, :end] = self.ignore_index

                if len(response_token_ids_idxs) < len(human_token_ids_idxs):
                    batch["labels"][i, human_token_ids_idxs[-1] :] = self.ignore_index
        # Filter batch to only keep valid indices
        for key in batch:
            batch[key] = batch[key][keep_indices]

        return batch


class ChatCompletionDataset(AzuremlDataset, AzuremlValidatorMixin):

    # TODO Add support for only JSONL files
    def __init__(
        self,
        path_or_dict: Union[str, Path],
        tokenizer: PreTrainedTokenizerBase,
        dataset_args: Dict[str, Any],
        chat_special_tokens: ChatSpecialTokens,
        finetune_chat_template: Union[str, None] = None,
        required_columns: Optional[List[str]] = None,
        required_column_dtypes: Optional[List[List[str]]] = None,
        label_column: Optional[str] = None,
        label_column_optional: bool = False,
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
        self.chat_special_tokens = chat_special_tokens
        self.finetune_chat_template = finetune_chat_template

    def get_collation_function(self) -> Callable:
        """Collation function for dynamic padding"""
        response_template = self.chat_special_tokens.response_template.content
        instruction_template = self.chat_special_tokens.instruction_template.content
        # `mlm` is whether or not to use masked language modeling. If set to False, the labels are the
        # same as the inputs with the padding tokens ignored (by setting them to -100). Otherwise, the
        # labels are -100 for non-masked tokens and the value to predict for the masked token.
        return CustomCollatorForCompletionOnlyLM(response_template, instruction_template, self.tokenizer, mlm=False)

    def update_dataset_columns_with_prefix(self):
        """Update the chat_key"""
        self.dataset_args["chat_key"] = AzuremlConstants.DATASET_COLUMN_PREFIX + self.dataset_args["chat_key"]

        return super().update_dataset_columns_with_prefix()

    @staticmethod
    def apply_chat_template(
        tokenizer: PreTrainedTokenizerBase,
        dialog: List[Dict[str, str]],
        finetune_chat_template: Union[str, None] = None,
    ) -> str:
        """
        :param dialog - List of messages, where each message is a dictionary with `role` and `content` fields.
        :type List[Dict[str, str]]
        :return Chat templated dialog
        :rtype str
        """
        return tokenizer.apply_chat_template(  # type: ignore
            dialog,
            chat_template=finetune_chat_template,
            tokenize=False,
        )

    def _tokenize_chat_data(
        self,
        dialog: List[Dict[str, str]],
        tokenize_kwargs: Dict[str, Union[bool, int]]
    ) -> List[int]:
        """
        :param dialog - Dialog to be tokenized.
        :type List[Dict[str, str]]
        :param tokenize_kwargs - List of parameters to be used for encoding
        :type Dict[str, Union[bool, int]]
        :return Tokenized chat data.
        :rtype BatchEncoding
        """
        return self.tokenizer.apply_chat_template(  # type: ignore
            dialog,
            chat_template=self.finetune_chat_template,
            tokenize=True,
            **tokenize_kwargs
        )

    def _calculate_labels_using_input_ids(self, input_ids: List[int]) -> List[int]:
        """Calculate the labels to be used for chat completion using input ids and data collator."""
        data_collator = self.get_collation_function()
        collated = data_collator([input_ids])
        if "labels" not in collated or len(collated["labels"]) == 0:
            return []
        return collated["labels"][0].tolist()

    def encode_dataset(self):
        """
        datasets: HuggingFace datasets object
        tokenizer: HuggingFace tokenizer
        kwargs: max_seq_length, pad_to_max_length, text_key
        """
        def _encode_helper(single_example: Dict[str, Any]) -> Dict[str, Union[List[int], np.ndarray]]:
            # get input ids
            input_ids = self._tokenize_chat_data(single_example[self.dataset_args["chat_key"]], tokenizer_kwargs)
            # calculate labels and attention mask
            # Find assistant response spans and build completion_mask
            labels = self._calculate_labels_using_input_ids(input_ids)
            # FIXME logic could be improved for attention_mask calc
            attention_mask = torch.Tensor(input_ids).ne(self.tokenizer.pad_token_id).numpy().astype('int').tolist()
            # attention_mask = np.where(np.array(labels) == TaskConstants.TEXT_GENERATION_IGNORE_INDEX, 0, 1)
            # If input_ids or labels are missing or invalid, return None to filter out the record
            if not input_ids or not labels or all(label == IGNORE_INDEX for label in labels):
                return None

            # construct tokenized dialog
            return dict(
                input_ids=input_ids,
                labels=labels,
                attention_mask=attention_mask
            )

        tokenizer_kwargs = dict(
            padding=self.dataset_args["padding"],
            max_length=self.dataset_args["max_length"],
            truncation=self.dataset_args["truncation"]
        )
        self.dataset = self.dataset.map(_encode_helper, batched=False, remove_columns=self.dataset.column_names)
        
    def chat_completion_data_filter(self):
        """Remove the examples that contain null data, empty_list or only one role"""

        if self.dataset_args is None:
            logger.info(f"Dataset args is {self.dataset_args}. Skipping chat-completion data filter")
            return

        # filter examples with empty messages
        # dataset_args is not None at this point
        filter_lambda = lambda example: (
            example[self.dataset_args["chat_key"]] != ""
        )

        # filter columns which have less than two roles in the messages list
        filter_only_single_role = lambda example: (
            len(example[self.dataset_args["chat_key"]]) > 1 if isinstance(example[self.dataset_args["chat_key"]], list) else True
        )

        pre_filter_rows = self.dataset.num_rows

        self.dataset = self.dataset.filter(
            filter_lambda,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"]
        )

        self.dataset = self.dataset.filter(
            filter_only_single_role,
            batch_size=self.dataset_args["batch_size"],
            writer_batch_size=self.dataset_args["batch_size"]
        )

        post_filter_rows = self.dataset.num_rows
        logger.info(f"Chat completion data filter | before example count: {pre_filter_rows} | "
                    f"after example count: {post_filter_rows}"
                )
        if post_filter_rows == 0:
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=f"Found no examples after data preprocessing for {self.path_or_dict}"
                )
            )

    def _apply_chat_template_validation(self, input_ds):
        """Apply chat template to the dataset for validation."""
        def _helper(example: Dict[str, Any]):
            try:
                self.apply_chat_template(
                    self.tokenizer,
                    example[self.dataset_args["chat_key"]],
                    finetune_chat_template=self.finetune_chat_template,
                )
            except Exception as e:
                raise ACFTValidationException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=f"Failure while applying chat template to dataset: {str(e)}"
                    )
                )
        input_ds.map(_helper, batched=False)

    def validate(self, split: str, task_name: Optional[str] = None) -> None:
        """Validate the dataset."""

        # common validations
        # - remove extra columns
        # - match columns
        # - check for duplicate columns
        # - remove null examples
        # - check min samples
        self.apply_common_validations(split, batch_size=self.dataset_args["batch_size"], task_name=task_name)

        # remove examples with empty text
        self.chat_completion_data_filter()

        # check for minimum num of training samples after chat_completion data filter
        if split == DatasetSplit.TRAIN:
            self.check_min_train_samples(task_name)

        # apply chat template to all rows
        self._apply_chat_template_validation(self.dataset)
