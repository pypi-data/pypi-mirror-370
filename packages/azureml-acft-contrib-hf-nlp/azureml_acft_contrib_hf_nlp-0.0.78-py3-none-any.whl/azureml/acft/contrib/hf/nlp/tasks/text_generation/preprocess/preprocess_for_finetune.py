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
from pathlib import Path
from argparse import Namespace
from typing import Dict, Any, Tuple, Optional
from dataclasses import asdict, replace

import json

from .base import TextGenerationPreprocessArgs, TextGenerationDataset
from ....nlp_auto.config import AzuremlAutoConfig
from ....nlp_auto.tokenizer import AzuremlAutoTokenizer
from ....constants.constants import Tasks, DatasetSplit, SaveFileConstants, MLFlowHFFlavourConstants

from azureml.acft.accelerator.utils.run_utils import add_run_properties

from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.data_metrics import calculate_token_distribution

from transformers.tokenization_utils_base import PreTrainedTokenizerBase


logger = get_logger_app(__name__)


class TextGenerationPreprocessForFinetune:

    def __init__(self, component_args: Namespace, preprocess_args: TextGenerationPreprocessArgs) -> None:
        # component args is combined args of
        #  - preprocess component args
        #  - model_name arg from model selector
        #  - newly constructed model_name_or_path
        self.component_args = component_args
        self.preprocess_args = preprocess_args
        self.ft_config = getattr(component_args, "finetune_config", {})

        logger.info(f"Task name: {Tasks.TEXT_GENERATION}")

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
            "task_name": Tasks.TEXT_GENERATION,
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
                    "eos_token": tokenizer.decode(self.config.eos_token_id)
                }
                logger.info(f"Adding eos token to tokenizer: {eos_token_kwargs}")
                tokenizer.add_special_tokens(eos_token_kwargs)
            else:
                raise ValueError(
                    "Data preprocessing requires EOS token and cannot be None. Set the EOS token in the tokenizer_config.json")
        if tokenizer.bos_token is None:
            if self.config.bos_token_id is not None:
                bos_token_kwargs = {
                    "bos_token": tokenizer.decode(self.config.bos_token_id)
                }
                logger.info(f"Adding bos token to tokenizer: {bos_token_kwargs}")
                tokenizer.add_special_tokens(bos_token_kwargs)
            else:
                raise ValueError(
                    "Data preprocessing requires BOS token and cannot be None. Set the BOS token in the tokenizer_config.json")

        # add pad special token
        if (
            tokenizer.pad_token is None or
            tokenizer.pad_token in [tokenizer.bos_token, tokenizer.eos_token, tokenizer.unk_token]
        ):
            logger.info(f'Identified pad token: {getattr(tokenizer, "pad_token", None)}')
            pad_token_kwargs = {
                "pad_token": "<pad>"
            }
            logger.info(f"Adding pad token to tokenizer: {pad_token_kwargs}")
            tokenizer.add_special_tokens(pad_token_kwargs)

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
        raw_folder_name = "raw_data"
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

    def _load_data_splits(self, save_raw_data: bool = False) -> Optional[Tuple[str, str, str]]:
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
            dataset_args=dataset_args,
            required_columns=self.preprocess_args.required_columns,
            required_column_dtypes=self.preprocess_args.required_column_dtypes,
            label_column=self.preprocess_args.label_column,
            tokenizer=self.tokenizer,
        )
        logger.info("Loading train dataset")
        self.train_ds = TextGenerationDataset(
            self.component_args.train_data_path,
            **copy.deepcopy(kwargs),
            slice=self.component_args.train_slice,
        )
        logger.info("Loading validation dataset")
        self.valid_ds = TextGenerationDataset(
            self.component_args.validation_data_path,
            **copy.deepcopy(kwargs),
            slice=self.component_args.validation_slice,
        )
        if self.component_args.test_data_path is not None:
            logger.info("Loading test dataset")
            self.test_ds = TextGenerationDataset(
                self.component_args.test_data_path,
                **copy.deepcopy(kwargs),
                label_column_optional=False,
                slice=self.component_args.test_slice,
            )
        else:
            self.test_ds = None

        # save raw data
        if save_raw_data:
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
            return (raw_train_data_fname, raw_validation_data_fname, raw_test_data_fname)

    def _validate_data_splits(self):
        """
        1. validate the datasets
        2. Identify the classnames and do some validations on them
        """
        # validate the datasets
        logger.info("Validating the train dataset")
        self.train_ds.validate(split=DatasetSplit.TRAIN, task_name=Tasks.TEXT_GENERATION)
        logger.info("Validating the validation dataset")
        self.valid_ds.validate(split=DatasetSplit.VALIDATION)
        if not self.component_args.skip_test_data_processing and self.test_ds is not None:
            logger.info("Validating the test dataset")
            self.test_ds.validate(split=DatasetSplit.TEST)

    def _encode_data_splits(self):
        """
        Encode the dataset
        """
        logger.info("concatenating text and ground_truth if ground_truth present")
        self.train_ds.concatenate_ground_truth()
        self.valid_ds.concatenate_ground_truth()
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
        train_token_dist = calculate_token_distribution(self.train_ds.dataset)
        train_token_dist = replace(train_token_dist,
                                   cumulative_tokens = train_token_dist.cumulative_tokens * self.num_train_epochs)
        logger.info(train_token_dist)

        logger.info("Calculating validation dataset token distribution.")
        validation_token_dist = calculate_token_distribution(self.valid_ds.dataset)
        validation_token_dist = replace(validation_token_dist,
                                        cumulative_tokens = validation_token_dist.cumulative_tokens * self.num_train_epochs)
        logger.info(validation_token_dist)

        # add finetune tokens
        finetune_tokens_dict = None
        if train_token_dist is not None and validation_token_dist is not None:
            finetune_tokens_dict = {
                # the dict must have `int` values instead of `int64` values as this data will be saved into json
                # the `cumulative_tokens` datatype is `int`
                '__azureml_ft_training_tokens': int(
                    validation_token_dist.cumulative_tokens + train_token_dist.cumulative_tokens
                ),
            }
            add_run_properties(properties_to_add=finetune_tokens_dict, add_to_root=True)
        if self.test_ds and not self.component_args.skip_test_data_processing:
            logger.info("Calculating test dataset token distribution.")
            test_token_dist = calculate_token_distribution(self.test_ds.dataset)
            logger.info(test_token_dist)

        return finetune_tokens_dict

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
        self._validate_data_splits()
        self._encode_data_splits()

        # calculate token distribution
        finetune_tokens_dict = self.calculate_token_distribution()

        # Save
        # 1. encoded datasets
        # 2. Arguments
        # 3. class names
        # 4. tokenizer
        # 5. mlflow inference data

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
        preprocess_args["raw_validation_data_fname"] = raw_validation_data_fname
        # Only processing the test data is controlled using the flag; we will still save the raw dataset for test
        if self.test_ds is not None:
            preprocess_args["raw_test_data_fname"] = raw_test_data_fname
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
                "return_full_text": False,
                "max_length": model_max_length
            }
        }
        mlflow_inference_params_save_path = Path(
            self.component_args.output_dir, MLFlowHFFlavourConstants.INFERENCE_PARAMS_SAVE_NAME_WITH_EXT)
        logger.info(f"Saving the mlflow inference params at {mlflow_inference_params_save_path}")
        with open(mlflow_inference_params_save_path, 'w') as wptr:
            json.dump(save_data, wptr)
