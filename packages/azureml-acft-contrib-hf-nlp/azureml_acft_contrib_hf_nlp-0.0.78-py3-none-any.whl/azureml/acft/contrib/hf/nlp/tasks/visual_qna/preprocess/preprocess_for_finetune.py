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

import json
from pathlib import Path
from typing import Optional,Dict,Any
from transformers import AutoProcessor
from ....nlp_auto.config import AzuremlAutoConfig
from ....constants.constants import MLFlowHFFlavourConstants
from azureml.acft.common_components import get_logger_app
from .base import VisualQnAPreprocessArgs
from .base import VisualQnADataset
from ..constants import (
    InputJsonColumns,
    SaveFileConstants,
    DatasetSplit,
)

logger = get_logger_app(__name__)


class VisualQnAPreprocessForFinetune:
    """Preprocess Visual QnA data for finetuning."""

    def __init__(self, preprocess_args: VisualQnAPreprocessArgs, unused_args: dict) -> None:

        self.preprocess_args = preprocess_args
        self.unused_args = unused_args
        self.processor = AutoProcessor.from_pretrained(
            self.preprocess_args.model_name_or_path, trust_remote_code=True
        )
        self.output_dir = Path(self.preprocess_args.output_dir)
        self.train_ds: Optional[VisualQnADataset] = None
        self.valid_ds: Optional[VisualQnADataset] = None
        self.test_ds: Optional[VisualQnADataset] = None 

        self.train_file_path = Path(self.preprocess_args.train_file_path)
        self.validation_file_path = (
            Path(self.preprocess_args.validation_file_path) if self.preprocess_args.validation_file_path else None
        )
        self.test_file_path = Path(self.preprocess_args.test_file_path) if self.preprocess_args.test_file_path else None
        self.images_folder = Path(self.preprocess_args.images_folder)
        self.label_column = self.preprocess_args.label_column
        self.instruction = self.preprocess_args.instruction
        self.batch_size = self.preprocess_args.batch_size
        self.max_seq_length = self.preprocess_args.max_seq_length

        logger.info(f"Initialized preprocessing with model: {self.preprocess_args.model_name_or_path}")
        logger.info(f"Using label column: {self.label_column}")
        logger.info(f"Using instruction: {self.instruction}")


    def _load_dataset(self, jsonl_path: Path, split: str) -> VisualQnADataset:
        """Helper method to load a dataset split."""
        required_columns = [
            InputJsonColumns.IMAGE_PATH,
            InputJsonColumns.QUESTION,
            self.label_column,
        ]
        required_column_dtypes = [["string"], ["string"], ["string"]]

        logger.info(f"Loading {split} dataset from {jsonl_path}")
        dataset_args=vars(self.preprocess_args)
        dataset_args["instruction"] = self.instruction
        dataset_args["batch_size"] = self.batch_size
        dataset_args["max_seq_length"] = self.max_seq_length
        return VisualQnADataset(
            path=jsonl_path,
            images_folder=self.images_folder,
            required_columns=required_columns,
            label_column=self.label_column,
            required_column_dtypes=required_column_dtypes,
            processor=self.processor,
            dataset_args=dataset_args,
            slice=split,
            model_name_or_path=self.preprocess_args.model_name_or_path,
        )

    def _load_data_splits(self) -> None:
        """Load datasets for train, validation, and test splits."""
        self.train_ds = self._load_dataset(self.train_file_path, DatasetSplit.TRAIN)

        if self.validation_file_path:
            self.valid_ds = self._load_dataset(
                self.validation_file_path, DatasetSplit.VALIDATION
            )

        if self.test_file_path:
            self.test_ds = self._load_dataset(self.test_file_path, DatasetSplit.TEST)

    def _get_encode_dataset_params(self) -> Dict[str, Any]:

        encode_params = {}
        # padding and truncation
        encode_params["padding"] = "max_length" if self.preprocess_args.pad_to_max_length else False
        encode_params["truncation"] = True

        # max sequence length
        if self.preprocess_args.max_seq_length == -1:
            self.preprocess_args.max_seq_length = self.processor.tokenizer.model_max_length
        encode_params["max_length"] = min(int(self.preprocess_args.max_seq_length), 
                                          self.processor.tokenizer.model_max_length)

        # clean up tokenization spaces used for model prediction
        encode_params["clean_up_tokenization_spaces"] = True

        return encode_params
    def preprocess(self) -> None:
        """Main preprocessing method."""
        logger.info("Starting preprocessing of Visual QnA data.")
        self._load_data_splits()
        logger.info("Saving the encoded datasets")
        batch_size = int(self.preprocess_args.batch_size)
        encoded_train_data_fname = self.train_ds.save(
            save_folder=self.preprocess_args.output_dir,
            save_name=DatasetSplit.TRAIN,
            batch_size=batch_size
        )
        encoded_validation_data_fname = self.valid_ds.save(
            save_folder=self.preprocess_args.output_dir,
            save_name=DatasetSplit.VALIDATION,
            batch_size=batch_size
        )
        if not self.unused_args.get('skip_test_data_processing', False) and self.test_ds is not None:
            encoded_test_data_fname = self.test_ds.save(
                save_folder=self.preprocess_args.output_dir,
                save_name=DatasetSplit.TEST,
                batch_size=batch_size
            )
        self.config = AzuremlAutoConfig.from_pretrained(
            hf_model_name_or_path=self.preprocess_args.model_name_or_path,
           # **self.ft_config.get("load_config_kwargs", {})
        )
        self.model_type = AzuremlAutoConfig.get_model_type(self.config)
        self.unused_args["model_type"] = self.model_type
        preprocess_args_save_path = (   
            self.output_dir / SaveFileConstants.PREPROCESS_ARGS_SAVE_PATH
        )
        logger.info(f"Saving preprocessing arguments to {preprocess_args_save_path}")
        self.unused_args["encoded_train_data_fname"] = encoded_train_data_fname
        self.unused_args["encoded_validation_data_fname"] = encoded_validation_data_fname
        if not self.unused_args.get('skip_test_data_processing', False) and self.test_ds is not None:
            self.preprocess_args["encoded_test_data_fname"] = encoded_test_data_fname

        all_args = {**vars(self.preprocess_args), **self.unused_args}
        with open(preprocess_args_save_path, "w") as fp:
            json.dump(all_args, fp, indent=2)

        save_key = MLFlowHFFlavourConstants.INFERENCE_PARAMS_SAVE_KEY_TEXTGEN
        save_key_generation = MLFlowHFFlavourConstants.INFERENCE_PARAMS_SAVE_KEY
        self.encode_params = self._get_encode_dataset_params()
        model_max_length = self.encode_params.pop("max_length")
        save_data = {
            save_key: self.encode_params,
            save_key_generation: {
                # "return_full_text": False,
                "max_length": model_max_length
            }
        }
        mlflow_inference_params_save_path = Path(
            self.preprocess_args.output_dir, MLFlowHFFlavourConstants.INFERENCE_PARAMS_SAVE_NAME_WITH_EXT)
        logger.info(f"Saving the mlflow inference params at {mlflow_inference_params_save_path}")
        with open(mlflow_inference_params_save_path, 'w') as wptr:
            json.dump(save_data, wptr)

        logger.info("Preprocessing completed successfully.")
