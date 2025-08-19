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

import shutil
from typing import Dict, Any, List, Tuple
from pathlib import Path
from transformers.integrations.deepspeed import is_deepspeed_zero3_enabled
from azureml.acft.accelerator.finetune import (
    AzuremlFinetuneArgs,
    AzuremlDatasetArgs,
    AzuremlTrainer,
)
from azureml.acft.accelerator.constants import HfTrainerType
from azureml.acft.common_components import get_logger_app
from ...base.finetune.finetune import FinetuneBase
from ....constants.constants import MLFlowHFFlavourConstants
from ..constants import SaveFileConstants, FinetuneParamLiterals
from transformers import AutoProcessor
from ....nlp_auto.model import AzuremlAutoModelForCausalLM
from azureml.acft.contrib.hf.nlp.tasks.visual_qna.collators.collators import (
    CollatorFactory,
)
from ..preprocess.base import PreprocessedDataset
from peft.utils.peft_types import TaskType
from ....utils.common_utils import write_dict_to_json_file
import torch.nn as nn

logger = get_logger_app(__name__)


class VisualQnAFinetune(FinetuneBase):
    """Class to handle finetuning for Visual Question Answering."""

    def __init__(self, finetune_params: Dict[str, Any]) -> None:
        logger.info(
            f"Initializing Visual QnA finetuning with params: {finetune_params}"
        )
        self.finetune_params = finetune_params
        self.ft_config = finetune_params.get("finetune_config", {})
        self.model_name = finetune_params["model_name_or_path"]
        self.finetune_args = self._get_finetune_args()

    def _get_finetune_args(self) -> AzuremlFinetuneArgs:
        """Prepare finetune arguments."""
        logger.info("Preparing finetune arguments.")
        self.finetune_params["peft_task_type"] = TaskType.CAUSAL_LM
        logger.info(f"Finetune parameters: {self.finetune_params}")
        return AzuremlFinetuneArgs(
            self.finetune_params,
            trainer_type=HfTrainerType.DEFAULT,
        )

    def _get_dataset_args(self) -> AzuremlDatasetArgs:
        """Prepare dataset arguments."""
        logger.info("Preparing dataset arguments.")

        train_file_path = Path(
            self.finetune_params[FinetuneParamLiterals.PREPROCESS_OUTPUT],
            self.finetune_params["encoded_train_data_fname"],
        )

        validation_file_path = Path(
            self.finetune_params[FinetuneParamLiterals.PREPROCESS_OUTPUT],
            self.finetune_params["encoded_validation_data_fname"],
        )
        train_ds = PreprocessedDataset(train_file_path)
        valid_ds = (
            PreprocessedDataset(validation_file_path)
            if validation_file_path.exists()
            else None
        )
        # Remove the labels column to fix PeftModel warning
        label_column = "labels"
        logger.info(
            f"Train dataset columns before removal: {train_ds.dataset.column_names}"
        )
        if label_column in train_ds.dataset.column_names:
            logger.info(f"Removing {label_column} column from train dataset")
            train_ds.dataset = train_ds.dataset.remove_columns([label_column])
        if len(train_ds.dataset) == 0:
            logger.warning("Train dataset is empty after removing labels column.")
            return None
        logger.info(
            f"Train dataset columns after removal: {train_ds.dataset.column_names}"
        )
        logger.info(f"Train dataset size: {len(train_ds.dataset)}")

        if valid_ds and label_column in valid_ds.dataset.column_names:
            logger.info(f"Removing {label_column} column from validation dataset")
            valid_ds.dataset = valid_ds.dataset.remove_columns([label_column])
            if valid_ds and len(valid_ds.dataset) == 0:
                logger.warning("Validation dataset is empty after removing labels column.")
                valid_ds = None
            logger.info(
                f"Validation dataset columns after removal: {valid_ds.dataset.column_names}"
            )
            logger.info(f"Validation dataset size: {len(valid_ds.dataset)}")
        processor = AutoProcessor.from_pretrained(
            self.model_name, trust_remote_code=True
        )
        tokenizer = processor.tokenizer
        collator = CollatorFactory.get_collator(tokenizer)
        dataset_args = AzuremlDatasetArgs(
            train_dataset=train_ds.dataset,
            validation_dataset=valid_ds.dataset if valid_ds else None,
            data_collator=collator,
        )

        return dataset_args

    def _load_model(self) -> Tuple[nn.Module, str, List[str]]:

        model_params = {
            "ignore_mismatched_sizes": self.finetune_params["ignore_mismatched_sizes"],
            "resume_from_checkpoint": self.finetune_params["resume_from_checkpoint"],
            "load_in_8bit": self.finetune_params["finetune_in_8bit"],
            "load_in_4bit": self.finetune_params["finetune_in_4bit"],
        }

        model_params.update(self.ft_config.get("load_model_kwargs", {}))
        model_params.update(
            {"load_config_kwargs": self.ft_config.get("load_config_kwargs", {})}
        )
        logger.info(f"Loading model with following args: {model_params}")

        model, model_type, new_initalized_layers = (
            AzuremlAutoModelForCausalLM.from_pretrained(
                self.finetune_params["model_name_or_path"], **model_params
            )
        )

        return model, model_type, new_initalized_layers

    def finetune(self) -> None:
        """Main finetuning method."""
        logger.info("Starting Visual QnA finetuning process.")

        self.finetune_params = self.resolve_resume_from_checkpoint(self.finetune_params)
        dataset_args = self._get_dataset_args()
        model, model_type, new_initialized_params = self._load_model()
        setattr(self.finetune_args.optimization_args, "model_type", model_type)
        self.finetune_params["model_type"] = model_type
        model.config.use_cache = False
        model.config.pretraining_tp = 1
        processor = AutoProcessor.from_pretrained(
            self.model_name, trust_remote_code=True
        )
        tokenizer = processor.tokenizer

        trainer = AzuremlTrainer(
            finetune_args=self.finetune_args,
            dataset_args=dataset_args,
            model=model,
            tokenizer=tokenizer,
            new_initalized_layers=new_initialized_params,
        )

        self._save_mininum_finetune_args(self.finetune_args)

        # Torch barrier is used to complete the training on a distributed setup
        # Use callbacks for adding steps to be done at the end of training
        # NOTE Avoid adding any logic after trainer.train()
        # Test the distributed scenario in case you add any logic beyond trainer.train()
        trainer.train()
        logger.info("Finetuning completed.")
        # Save the model
        logger.info(f"trainer.should_save: {trainer.should_save}")
        # save files only once by Rank-0 process
        if trainer.should_save:
            self.finetune_params["model_name_or_path"] = str(
                self.finetune_params["model_name_or_path"]
            )
            # save if model is trained via deepspeed stage 3
            self.finetune_params["is_deepspeed_zero3_enabled"] = (
                is_deepspeed_zero3_enabled()
            )
            # save finetune args
            finetune_args_path = str(
                Path(
                    self.finetune_params["pytorch_model_folder"],
                    SaveFileConstants.FINETUNE_ARGS_SAVE_PATH,
                )
            )
            write_dict_to_json_file(self.finetune_params, finetune_args_path)

            # save finetune_config file
            ft_config_path = str(
                Path(
                    self.finetune_params["pytorch_model_folder"],
                    SaveFileConstants.ACFT_CONFIG_SAVE_PATH,
                )
            )
            write_dict_to_json_file(self.ft_config, ft_config_path)

            # copy mlflow inference params file to pytorch output for model converter
            mlflow_infer_params_file_path = Path(
                self.finetune_params["preprocess_output"],
                MLFlowHFFlavourConstants.INFERENCE_PARAMS_SAVE_NAME_WITH_EXT,
            )
            shutil.copy(
                mlflow_infer_params_file_path,
                self.finetune_params["pytorch_model_folder"],
            )
            logger.info(f"Saved finetune args to {finetune_args_path}")
