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

import copy
import json
from pathlib import Path
from argparse import Namespace
from typing import Dict, Any, Tuple, Optional, List
from functools import partial

from dataclasses import asdict, replace

from datasets.load import Dataset

from .base import ChatCompletionPreprocessArgs, ChatSpecialTokens, ChatCompletionDataset, CustomToken
from ....nlp_auto.config import AzuremlAutoConfig
from ....nlp_auto.tokenizer import AzuremlAutoTokenizer
from ....constants.constants import (
    Tasks, DatasetSplit, SaveFileConstants, MLFlowHFFlavourConstants, TokenDistributionConstants
)

from azureml.acft.accelerator.utils.run_utils import add_run_properties

from azureml.acft.common_components.utils.error_handling.exceptions import (
    ACFTUserException, ACFTValidationException
)
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml.acft.common_components.utils.data_metrics import calculate_token_distribution
from azureml.acft.common_components import get_logger_app
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore

from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.tokenization_utils_base import AddedToken


logger = get_logger_app(__name__)


RAW_DATA_SAVE_FOLDER = "raw_data"
PROCESSED_DATA_SAVE_FOLDER = "data"
CHAT_TEMPLATED_RAW_DATA_SAVE_FOLDER = "chat_templated_raw_data"
CHAT_TEMPLATE_MESSAGE_KEY = "chat_template_message"
SYSTEM_ROLE_SUPPORTED_KEY = "system_role_supported"
ROLE_KEY = "role"
CONTENT_KEY = "content"


class ChatCompletionPreprocessForFinetune:

    def __init__(self, component_args: Namespace, preprocess_args: ChatCompletionPreprocessArgs) -> None:
        # component args is combined args of
        #  - preprocess component args
        #  - model_name arg from model selector
        #  - newly constructed model_name_or_path
        self.component_args = component_args
        self.preprocess_args = preprocess_args
        self.ft_config = getattr(component_args, "finetune_config", {})

        # Identify response and instruction templates. These are the start markers useful to identify
        # start of response and instruction
        self.chat_special_tokens = ChatSpecialTokens.from_finetune_config(self.ft_config)

        # Fetch finetune specific chat template. This will not be saved in finetuned model.
        self.finetune_chat_template = self.ft_config.get("finetune_chat_template", None)

        logger.info(f"Task name: {Tasks.CHAT_COMPLETION}")

        self.config = AzuremlAutoConfig.from_pretrained(
            hf_model_name_or_path=component_args.model_name_or_path,
            **self.ft_config.get("load_config_kwargs", {})
        )
        self.model_type = AzuremlAutoConfig.get_model_type(self.config)
        logger.info(self.preprocess_args)

        self.tokenizer = self._init_tokenizer()

        self.num_train_epochs = component_args.num_train_epochs

    def _init_tokenizer(self) -> PreTrainedTokenizerBase:
        """Initialize the tokenizer and set the model max length for the tokenizer if not already set"""

        # Apply adjust is set to false as in case of text generation special tokens are handled here
        tokenizer_params = {
            "task_name": Tasks.CHAT_COMPLETION,
            "apply_adjust": False,
            "max_sequence_length": self.preprocess_args.max_seq_length,
        }

        tokenizer_params.update(self.ft_config.get("load_tokenizer_kwargs", {}))
        tokenizer_params.update({"load_config_kwargs": self.ft_config.get("load_config_kwargs", {})})

        tokenizer = AzuremlAutoTokenizer.from_pretrained(self.component_args.model_name_or_path, **tokenizer_params)

        # sanity check for eos and bos token
        if tokenizer.eos_token is None:
            if self.config.eos_token_id is not None:
                eos_token_kwargs = {
                    "eos_token": AddedToken(tokenizer.decode(self.config.eos_token_id))
                }
                logger.info(f"Adding eos token to tokenizer: {eos_token_kwargs}")
                tokenizer.add_special_tokens(eos_token_kwargs)
            else:
                raise ACFTUserException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=(
                            "Invalid Model artifacts. Data preprocessing requires EOS token and cannot be None. "
                            "Set the EOS token in the tokenizer_config.json"
                        )
                    )
                )
        if tokenizer.bos_token is None:
            if self.config.bos_token_id is not None:
                bos_token_kwargs = {
                    "bos_token": AddedToken(tokenizer.decode(self.config.bos_token_id))
                }
                logger.info(f"Adding bos token to tokenizer: {bos_token_kwargs}")
                tokenizer.add_special_tokens(bos_token_kwargs)
            else:
                raise ACFTUserException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=(
                            "Invalid Model artifacts. Data preprocessing requires BOS token and cannot be None. "
                            "Set the BOS token in the tokenizer_config.json"
                        )
                    )
                )

        # add pad special token
        if (
            tokenizer.pad_token is None or
            tokenizer.pad_token in [tokenizer.bos_token, tokenizer.eos_token, tokenizer.unk_token]
        ):
            logger.info(f'Identified pad token: {getattr(tokenizer, "pad_token", None)}')
            pad_token_kwargs = {
                "pad_token": AddedToken("<pad>")
            }
            logger.info(f"Adding pad token to tokenizer: {pad_token_kwargs}")
            tokenizer.add_special_tokens(pad_token_kwargs)

        # add chat special tokens to the vocabulary
        # https://github.com/huggingface/transformers/blob/ae49b218c3d718df90d8e4a109016450fb8f0632/docs/source/en/chat_templating.md
        # fmt: off
        """Excerpt from the above doc. \
        If you're fine-tuning a model for chat, in addition to setting a chat template, you should probably \
        add any new chat control tokens as special tokens in the tokenizer. Special tokens are never split, ensuring \
        that your control tokens are always handled as single tokens rather than being tokenized in pieces. \
        You should also set the tokenizer's `eos_token` attribute to the token that marks the end of assistant \
        generations in your template. This will ensure that text generation tools can correctly figure out when to \
        stop generating text.
        """
        # fmt: on
        chat_special_tokens: List[CustomToken] = self.chat_special_tokens.get_chat_tokens()
        if chat_special_tokens:
            chat_special_tokens_to_add = []
            for token in chat_special_tokens:
                if token.add_to_vocabulary:
                    chat_special_tokens_to_add.append(token.content)

            # Adding tokens not present in vocabulary
            if chat_special_tokens_to_add:
                logger.info(f"Adding the following tokens to the vocabulary: {chat_special_tokens_to_add}")
                tokenizer.add_tokens(chat_special_tokens_to_add, special_tokens=True)

        return tokenizer

    def _get_encode_dataset_params(self) -> Dict[str, Any]:

        encode_params = {}
        # padding and truncation
        encode_params["padding"] = "max_length" if self.preprocess_args.pad_to_max_length else False
        encode_params["truncation"] = True

        # max sequence length
        if self.preprocess_args.max_seq_length == -1:
            self.preprocess_args.max_seq_length = self.tokenizer.model_max_length
        encode_params["max_length"] = min(self.preprocess_args.max_seq_length, self.tokenizer.model_max_length)

        # clean up tokenization spaces used for model prediction
        encode_params["clean_up_tokenization_spaces"] = True

        return encode_params

    def _save_raw_data(self) -> Tuple[str, str, Optional[str]]:
        # save the raw train and valid dataset
        # NOTE call this function before encoding the dataset else this will save encoded datasaet
        logger.info("Saving the raw datasets")
        raw_folder_name = RAW_DATA_SAVE_FOLDER
        raw_data_save_folder = str(Path(self.component_args.output_dir, raw_folder_name))
        raw_train_data_fname = str(
            Path(
                raw_folder_name,
                self.train_ds.save(
                    save_folder=raw_data_save_folder,
                    save_name=DatasetSplit.TRAIN,
                    batch_size=self.preprocess_args.batch_size
                )
            )
        )
        raw_validation_data_fname = str(
            Path(
                raw_folder_name,
                self.valid_ds.save(
                    save_folder=raw_data_save_folder,
                    save_name=DatasetSplit.VALIDATION,
                    batch_size=self.preprocess_args.batch_size
                )
            )
        )
        raw_test_data_fname = None
        if self.test_ds is not None:
            raw_test_data_fname = str(
                Path(
                    raw_folder_name,
                    self.test_ds.save(
                        save_folder=raw_data_save_folder,
                        save_name=DatasetSplit.TEST,
                        batch_size=self.preprocess_args.batch_size
                    )
                )
            )

        return (raw_train_data_fname, raw_validation_data_fname, raw_test_data_fname)

    def _apply_chat_template_to_dataset(self, input_ds: Dataset, chat_key: str) -> Dataset:
        """Apply chat template to the dataset."""
        def _helper(single_example: Dict[str, Any]):
            chat_templated_example = {}
            for key, value in single_example.items():
                if key not in chat_key:
                    chat_templated_example[key] = value
                else:
                    chat_templated_example[CHAT_TEMPLATE_MESSAGE_KEY] = ChatCompletionDataset.apply_chat_template(
                        self.tokenizer, value, self.finetune_chat_template
                    )
            return chat_templated_example
        return input_ds.map(_helper, batched=False)

    def _save_chat_templated_raw_data(self) -> Tuple[str, str, Optional[str]]:
        # save the chat templated raw train and valid dataset
        # NOTE call this function before encoding the dataset else this will save encoded datasaet

        logger.info("Saving the chat templated raw datasets")
        chat_template_raw_folder_name = CHAT_TEMPLATED_RAW_DATA_SAVE_FOLDER
        chat_template_raw_data_save_path = str(Path(self.component_args.output_dir, chat_template_raw_folder_name))
        Path(chat_template_raw_data_save_path).mkdir(exist_ok=True, parents=True)

        # datasets to save
        datasets_to_save = [self.train_ds.dataset, self.valid_ds.dataset]
        dataset_chat_keys = [self.train_ds.dataset_args["chat_key"], self.valid_ds.dataset_args["chat_key"]]
        dataset_save_paths = [
            Path(chat_template_raw_data_save_path, DatasetSplit.TRAIN + '.jsonl'),
            Path(chat_template_raw_data_save_path, DatasetSplit.VALIDATION + '.jsonl')
        ]
        if self.test_ds is not None:
            datasets_to_save.append(self.test_ds.dataset)
            dataset_chat_keys.append(self.test_ds.dataset_args["chat_key"])
            dataset_save_paths.append(Path(chat_template_raw_data_save_path, DatasetSplit.TEST + '.jsonl'))
        for (ds, chat_key, ds_save_path) in zip(datasets_to_save, dataset_chat_keys, dataset_save_paths):
            self._apply_chat_template_to_dataset(ds, chat_key).to_json(ds_save_path, self.preprocess_args.batch_size)

        relative_save_paths = [str(pth).replace(self.component_args.output_dir, '') for pth in dataset_save_paths]

        return (
            relative_save_paths[0],
            relative_save_paths[1],
            relative_save_paths[2] if len(relative_save_paths) > 2 else None
        )

    def _load_data_splits(
        self, save_raw_data: bool = False
    ) -> Optional[Tuple[str, str, Optional[str]]]:
        """
        1. Load train, validation and test data splits
        2. Add column prefix for the data
        """
        # encode params used for encoding dataset
        self.encode_params = self._get_encode_dataset_params()

        # initialize dataset
        dataset_args = asdict(self.preprocess_args)
        dataset_args.update(self.encode_params)
        kwargs = dict(
            required_columns=self.preprocess_args.required_columns,
            required_column_dtypes=self.preprocess_args.required_column_dtypes,
            label_column=self.preprocess_args.label_column,
        )
        args = (dataset_args, self.chat_special_tokens, self.finetune_chat_template)
        logger.info("Loading train dataset")
        self.train_ds = ChatCompletionDataset(
            self.component_args.train_data_path,
            self.tokenizer,
            *copy.deepcopy(args),
            **copy.deepcopy(kwargs),
            slice=self.component_args.train_slice,
        )
        logger.info("Loading validation dataset")
        self.valid_ds = ChatCompletionDataset(
            self.component_args.validation_data_path,
            self.tokenizer,
            *copy.deepcopy(args),
            **copy.deepcopy(kwargs),
            slice=self.component_args.validation_slice,
        )
        if self.component_args.test_data_path is not None:
            logger.info("Loading test dataset")
            self.test_ds = ChatCompletionDataset(
                self.component_args.test_data_path,
                self.tokenizer,
                *copy.deepcopy(args),
                **copy.deepcopy(kwargs),
                label_column_optional=False,
                slice=self.component_args.test_slice,
            )
        else:
            self.test_ds = None

        # save raw data
        if save_raw_data:
            # save raw data
            (
                raw_train_data_fname,
                raw_validation_data_fname,
                raw_test_data_fname
            ) = self._save_raw_data()

        # add dataset prefix
        self.train_ds.update_dataset_columns_with_prefix()
        self.train_ds.update_required_columns_with_prefix()
        self.valid_ds.update_dataset_columns_with_prefix()
        self.valid_ds.update_required_columns_with_prefix()
        if not self.component_args.skip_test_data_processing and self.test_ds is not None:
            self.test_ds.update_dataset_columns_with_prefix()
            self.test_ds.update_required_columns_with_prefix()

        if save_raw_data:
            return (
                raw_train_data_fname, raw_validation_data_fname, raw_test_data_fname
            )

    def _validate_data_splits(self):
        """
        1. validate the datasets
        2. Identify the classnames and do some validations on them
        """
        # validate the datasets
        logger.info("Validating the train dataset")
        self.train_ds.validate(split=DatasetSplit.TRAIN, task_name=Tasks.CHAT_COMPLETION)
        logger.info("Validating the validation dataset")
        self.valid_ds.validate(split=DatasetSplit.VALIDATION)
        if not self.component_args.skip_test_data_processing and self.test_ds is not None:
            logger.info("Validating the test dataset")
            self.test_ds.validate(split=DatasetSplit.TEST)

    def _encode_data_splits(self):
        """
        Encode the dataset
        """
        logger.info("Encoding the train dataset")
        self.train_ds.encode_dataset()
        logger.info("Encoding the validation dataset")
        self.valid_ds.encode_dataset()
        if not self.component_args.skip_test_data_processing and self.test_ds is not None:
            logger.info("Encoding the test dataset")
            self.test_ds.encode_dataset()

    def calculate_token_distribution(self) -> Optional[Dict[str, int]]:
        """
        Calculate token distribution.
        Token calculation is correct only when we are configuring num_train_epochs.
        TODO: Need to handle this for MaaP where both num_train_epochs and max_steps are configurable.
        """
        logger.info("Calculating train dataset token distribution.")
        # Add robust error handling for empty datasets
        if (
            self.train_ds.dataset.num_rows == 0 or "input_ids" not in self.train_ds.dataset.column_names
            or self.valid_ds.dataset.num_rows == 0 or "input_ids" not in self.valid_ds.dataset.column_names
        ):
                raise ACFTUserException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=(
                            "Unable to continue finetuning. No assistant tokens found after preprocessing.\n"
                            "1. Please increase the :param `max_seq_len` to higher value and try again.\n"
                            "2. This could also be an issue with ChatSpecialTokens. Please report the issue for "
                            "resolution.\n"
                        )
                    )
                )

        train_token_dist = calculate_token_distribution(self.train_ds.dataset)
        train_token_dist = replace(train_token_dist,
                                   cumulative_tokens = train_token_dist.cumulative_tokens * self.num_train_epochs)
        logger.info(train_token_dist)
        logger.info("Calculating train dataset assistant token distribution.")
        train_assistant_token_dist = calculate_token_distribution(self.train_ds.dataset, column_to_use="labels")
        train_assistant_token_dist = replace(train_assistant_token_dist,
                                             cumulative_tokens = train_assistant_token_dist.cumulative_tokens * self.num_train_epochs)
        logger.info(train_assistant_token_dist)

        logger.info("Calculating validation dataset token distribution.")
        validation_token_dist = calculate_token_distribution(self.valid_ds.dataset)
        validation_token_dist = replace(validation_token_dist,
                                        cumulative_tokens = validation_token_dist.cumulative_tokens * self.num_train_epochs)
        logger.info(validation_token_dist)
        logger.info("Calculating validation dataset assistant token distribution.")
        validation_assistant_token_dist = calculate_token_distribution(self.valid_ds.dataset, column_to_use="labels")
        validation_assistant_token_dist = replace(validation_assistant_token_dist,
                                                  cumulative_tokens = validation_assistant_token_dist.cumulative_tokens * self.num_train_epochs)
        logger.info(validation_assistant_token_dist)

        # add finetune tokens
        finetune_tokens_dict = None
        if train_token_dist is not None and validation_token_dist is not None:
            finetune_tokens_dict = {
                # the dict must have `int` values instead of `int64` values as this data will be saved into json
                # the `cumulative_tokens` datatype is `int`
                TokenDistributionConstants.TRAINING_PLUS_VALIDATION_TOKENS: int(
                    validation_token_dist.cumulative_tokens + train_token_dist.cumulative_tokens
                ),
                TokenDistributionConstants.ASSISTANT_TOKENS: int(
                    validation_assistant_token_dist.cumulative_tokens + train_assistant_token_dist.cumulative_tokens
                )
            }
            add_run_properties(properties_to_add=finetune_tokens_dict)
            add_run_properties(properties_to_add=finetune_tokens_dict, add_to_root=True)
            # Fail the run when the assistant tokens is empty
            if finetune_tokens_dict[TokenDistributionConstants.ASSISTANT_TOKENS] == 0:
                raise ACFTUserException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=(
                            "Unable to continue finetuning. No assistant tokens found after preprocessing.\n"
                            "1. Please increase the :param `max_seq_len` to higher value and try again.\n"
                            "2. This could also be an issue with ChatSpecialTokens. Please report the issue for "
                            "resolution.\n"
                        )
                    )
                )
        if self.test_ds and not self.component_args.skip_test_data_processing:
            logger.info("Calculating test dataset token distribution.")
            test_token_dist = calculate_token_distribution(self.test_ds.dataset)
            logger.info(test_token_dist)
            logger.info("Calculating test dataset assistant token distribution.")
            test_assistant_token_dist = calculate_token_distribution(self.test_ds.dataset, column_to_use="labels")
            logger.info(test_assistant_token_dist)

        return finetune_tokens_dict

    def _validate_system_role(self):
        def _mapper(example, chat_key):
            # check if system_role is present it should be only at the beginning of messages
            # also check if atleast one user role should be present
            is_user_role_present = False
            is_system_role_present = False
            dialog = example.get(chat_key)
            if not dialog:
                return example

            # handles checking of system role, fails if any system role occur after first message
            # in which case either there are multiple system role messages, or system role is not at beginning
            for idx, msg in enumerate(dialog):
                if msg.get(ROLE_KEY) == "system":
                    is_system_role_present = True
                    if idx > 0:
                        raise ACFTValidationException._with_error(
                            AzureMLError.create(
                                ACFTUserError,
                                pii_safe_message="Only one system role should be present and should be at the beginning of messages"
                            )
                        )

                if msg.get(ROLE_KEY) == "user":
                    is_user_role_present = True

            # Fail if system role is present but no user role is present
            if is_user_role_present == False and is_system_role_present == True:
                raise ACFTValidationException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message="messages should contain user role to process system message"
                    )
                )

        logger.info("Validating system message before preprocessing")
        self.train_ds.dataset.map(partial(_mapper, chat_key=self.train_ds.dataset_args["chat_key"]))
        self.valid_ds.dataset.map(partial(_mapper, chat_key=self.valid_ds.dataset_args["chat_key"]))
        if not self.component_args.skip_test_data_processing and self.test_ds is not None:
            self.test_ds.dataset.map(partial(_mapper, chat_key=self.test_ds.dataset_args["chat_key"]))

    def _process_system_role(self):

        def _mapper(example, chat_key):
            dialog = example.get(chat_key)
            if not dialog:
                return example
            if dialog[0].get(ROLE_KEY) != "system":
                return example
            # get index of first user messasge
            first_user_role_index = next(idx for idx, msg in enumerate(dialog) if msg[ROLE_KEY] == "user")
            # prepend system message to first user message
            dialog[first_user_role_index][CONTENT_KEY] = (
                dialog[0].get(CONTENT_KEY, "") +
                "\n\n" +
                dialog[first_user_role_index].get(CONTENT_KEY, "")
            )

            # Remove system message from list
            dialog = dialog[1:]
            example[chat_key] = dialog
            return example

        logger.info("processing and adding system message to user message")
        self.train_ds.dataset = self.train_ds.dataset.map(partial(_mapper, chat_key=self.train_ds.dataset_args["chat_key"]))
        self.valid_ds.dataset = self.valid_ds.dataset.map(partial(_mapper, chat_key=self.valid_ds.dataset_args["chat_key"]))
        if not self.component_args.skip_test_data_processing and self.test_ds is not None:
            self.test_ds.dataset = self.test_ds.dataset.map(partial(_mapper, chat_key=self.test_ds.dataset_args["chat_key"]))

    def preprocess(self) -> None:
        """
        Preprocess the raw dataset
        """

        # load, validate and encode the datasets
        (
            raw_train_data_fname,
            raw_validation_data_fname,
            raw_test_data_fname
        ) = self._load_data_splits(save_raw_data=True)

        if self.ft_config.get(SYSTEM_ROLE_SUPPORTED_KEY) == "false":
            self._validate_system_role()
            self._process_system_role()

        self._validate_data_splits()
        # save chat templated splits
        (
            chat_templated_raw_train_data_fname,
            chat_templated_raw_validation_data_fname,
            chat_templated_raw_test_data_fname
        ) = self._save_chat_templated_raw_data()
        self._encode_data_splits()

        # calculate token distribution
        finetune_tokens_dict = self.calculate_token_distribution()

        # Save
        # 1. encoded datasets
        # 2. Arguments
        # 3. tokenizer
        # 4. mlflow inference data

        # 1. Encoded datasets
        logger.info("Saving the encoded datasets")
        encoded_train_data_fname = self.train_ds.save(
            save_folder=self.component_args.output_dir,
            save_name=DatasetSplit.TRAIN,
            batch_size=self.preprocess_args.batch_size
        )
        encoded_validation_data_fname = self.valid_ds.save(
            save_folder=self.component_args.output_dir,
            save_name=DatasetSplit.VALIDATION,
            batch_size=self.preprocess_args.batch_size
        )
        if not self.component_args.skip_test_data_processing and self.test_ds is not None:
            encoded_test_data_fname = self.test_ds.save(
                save_folder=self.component_args.output_dir,
                save_name=DatasetSplit.TEST,
                batch_size=self.preprocess_args.batch_size
            )

        # 2. Arguments: save the preprocess args, model_type, encoded datasets
        preprocess_args = vars(self.component_args)
        preprocess_args.update(vars(self.preprocess_args))
        # add the model path
        preprocess_args["model_type"] = self.model_type
        # add the paths for raw train, validation and test paths
        preprocess_args["raw_train_data_fname"] = raw_train_data_fname
        preprocess_args["chat_templated_raw_train_data_fname"] = chat_templated_raw_train_data_fname
        preprocess_args["raw_validation_data_fname"] = raw_validation_data_fname
        preprocess_args["chat_templated_raw_validation_data_fname"] = chat_templated_raw_validation_data_fname
        if self.test_ds is not None:
            preprocess_args["raw_test_data_fname"] = raw_test_data_fname
            preprocess_args["chat_templated_raw_test_data_fname"] = chat_templated_raw_test_data_fname
        # add the paths for encoded train, validation and test paths
        preprocess_args["encoded_train_data_fname"] = encoded_train_data_fname
        preprocess_args["encoded_validation_data_fname"] = encoded_validation_data_fname
        if not self.component_args.skip_test_data_processing and self.test_ds is not None:
            preprocess_args["encoded_test_data_fname"] = encoded_test_data_fname
        preprocess_args_save_path = Path(self.component_args.output_dir, SaveFileConstants.PREPROCESS_ARGS_SAVE_PATH)
        preprocess_args["model_name_or_path"] = str(preprocess_args["model_name_or_path"])
        # add the finetune tokens added
        preprocess_args["finetune_tokens"] = finetune_tokens_dict
        logger.info(f"Saving the preprocess args to {preprocess_args_save_path}")
        with open(preprocess_args_save_path, 'w') as fp:
            json.dump(preprocess_args, fp, indent=2)

        # 3. tokenizer
        self.tokenizer.save_pretrained(self.component_args.output_dir)

        # 4. save the mlflow inference params
        save_key = MLFlowHFFlavourConstants.INFERENCE_PARAMS_SAVE_KEY_TEXTGEN
        save_key_generation = MLFlowHFFlavourConstants.INFERENCE_PARAMS_SAVE_KEY
        model_max_length = self.encode_params.pop("max_length")
        save_data = {
            save_key: self.encode_params,
            save_key_generation: {
                # "return_full_text": False,
                "max_length": model_max_length
            }
        }
        mlflow_inference_params_save_path = Path(
            self.component_args.output_dir, MLFlowHFFlavourConstants.INFERENCE_PARAMS_SAVE_NAME_WITH_EXT)
        logger.info(f"Saving the mlflow inference params at {mlflow_inference_params_save_path}")
        with open(mlflow_inference_params_save_path, 'w') as wptr:
            json.dump(save_data, wptr)
