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
import shutil
from functools import partial

from typing import Any, Dict, List, Tuple

from ...base.finetune.finetune import FinetuneBase
from ....constants.constants import SaveFileConstants, MLFlowHFFlavourConstants, Tasks, TaskConstants
from ....nlp_auto.model import AzuremlAutoModelForCausalLM
from ....nlp_auto.tokenizer import AzuremlAutoTokenizer
from ..preprocess.base import ChatCompletionDataset, ChatSpecialTokens
from ....utils.common_utils import write_dict_to_json_file

import torch.nn as nn
import torch

import numpy as np

from azureml.acft.common_components import get_logger_app

from azureml.acft.accelerator.finetune import AzuremlFinetuneArgs, AzuremlDatasetArgs
from azureml.acft.accelerator.finetune import AzuremlTrainer
from azureml.acft.accelerator.constants import HfTrainerType

from transformers.tokenization_utils_base import PreTrainedTokenizerBase
from transformers.integrations.deepspeed import is_deepspeed_zero3_enabled
from transformers.trainer_utils import EvalPrediction

from peft.utils.peft_types import TaskType

logger = get_logger_app(__name__)


_METRICS_TO_COMPUTE = ['bleu_1', 'bleu_2', 'bleu_3', 'bleu_4', 'rouge1', 'rouge2', 'rougeL', 'rougeLsum']


class ChatCompletionFinetune(FinetuneBase):

    def __init__(self, finetune_params: Dict[str, Any]) -> None:
        # finetune params is finetune component args + args saved as part of preprocess
        self.finetune_params = finetune_params
        self.ft_config = finetune_params.get("finetune_config", {})

        logger.info(f"Task name: {Tasks.CHAT_COMPLETION}")

        # set log_metrics_at_root=False to not to log to parent
        self.finetune_params["log_metrics_at_root"] = True

    def _get_finetune_args(self, model_type: str) -> AzuremlFinetuneArgs:

        self.finetune_params["model_type"] = model_type
        self.finetune_params["peft_task_type"] = TaskType.CAUSAL_LM
        azml_trainer_finetune_args = AzuremlFinetuneArgs(
            self.finetune_params,
            trainer_type=HfTrainerType.DEFAULT,
        )

        return azml_trainer_finetune_args

    def _get_dataset_args(self, tokenizer: PreTrainedTokenizerBase) -> AzuremlDatasetArgs:

        # chat special tokens
        chat_special_tokens = ChatSpecialTokens.from_finetune_config(self.ft_config)
        encoded_train_ds = ChatCompletionDataset(
            Path(self.finetune_params["preprocess_output"], self.finetune_params["encoded_train_data_fname"]),
            tokenizer,
            dataset_args={},
            chat_special_tokens=chat_special_tokens
        )
        encoded_validation_ds = ChatCompletionDataset(
            Path(self.finetune_params["preprocess_output"], self.finetune_params["encoded_validation_data_fname"]),
            tokenizer,
            dataset_args={},
            chat_special_tokens=chat_special_tokens
        )

        # remove extra columns added in the preprocessing - labels and attention_mask. The columns are added to
        # calculate metrics for assistant tokens.
        # This is needed as the collator doesn't handle collation for labels column for non int data types.
        label_column = ['labels']
        encoded_train_ds.dataset = encoded_train_ds.dataset.remove_columns(label_column)
        encoded_validation_ds.dataset = encoded_validation_ds.dataset.remove_columns(label_column)
        azml_trainer_dataset_args = AzuremlDatasetArgs(
            train_dataset=encoded_train_ds.dataset,
            validation_dataset=encoded_validation_ds.dataset,
            data_collator=None if tokenizer is None else encoded_train_ds.get_collation_function()
        )

        return azml_trainer_dataset_args

    def _load_model(self) -> Tuple[nn.Module, str, List[str]]:

        model_params = {
            "ignore_mismatched_sizes": self.finetune_params["ignore_mismatched_sizes"],
            "resume_from_checkpoint": self.finetune_params["resume_from_checkpoint"],
            "load_in_8bit": self.finetune_params["finetune_in_8bit"],
            "load_in_4bit": self.finetune_params["finetune_in_4bit"],
        }

        model_params.update(self.ft_config.get("load_model_kwargs", {}))
        model_params.update({"load_config_kwargs": self.ft_config.get("load_config_kwargs", {})})
        logger.info(f"Loading model with following args: {model_params}")

        model, model_type, new_initalized_layers = AzuremlAutoModelForCausalLM.from_pretrained(
            self.finetune_params["model_name_or_path"], **model_params)

        return model, model_type, new_initalized_layers

    def _get_tokenizer(self) -> PreTrainedTokenizerBase:
        """This method loads the tokenizer as is w/o any modifications to it"""

        tokenizer_params = {
            "apply_adjust": False,
            "task_name": self.finetune_params["task_name"],
        }

        tokenizer_params.update(self.ft_config.get("load_tokenizer_kwargs", {}))
        tokenizer_params.update({"load_config_kwargs": self.ft_config.get("load_config_kwargs", {})})
        logger.info(f"Loading tokenizer with following params: {tokenizer_params}")

        return AzuremlAutoTokenizer.from_pretrained(self.finetune_params["preprocess_output"], **tokenizer_params)

    def finetune(self) -> None:

        self.finetune_params = self.resolve_resume_from_checkpoint(self.finetune_params)

        self.finetune_params["model_name_or_path"] = str(self.finetune_params["model_name_or_path"])

        # Initializing the finetune args with dummy_model_type to enable the
        # deepspeed stage3 which is used in :meth _load_model
        finetune_args = self._get_finetune_args("dummy_model_type")
        model, model_type, new_initialized_params = self._load_model()
        # Replacing the dummy_model_type -> original model_type information
        setattr(finetune_args.optimization_args, "model_type", model_type)
        self.finetune_params["model_type"] = model_type

        tokenizer = self._get_tokenizer()

        FinetuneBase.resize_token_embeddings_and_reset_pad_token_embedding(
            model, tokenizer=tokenizer, token_resize_kwargs=self.ft_config.get("model_resize_embeddings_kwargs", {})
        )

        # dataset args
        dataset_args = self._get_dataset_args(tokenizer)

        trainer = AzuremlTrainer(
            finetune_args=finetune_args,
            dataset_args=dataset_args,
            model=model,
            tokenizer=tokenizer,
            new_initalized_layers=new_initialized_params,
            preprocess_logits_for_metrics_callback=preprocess_logits_for_metrics
        )

        self._save_mininum_finetune_args(finetune_args)

        # Torch barrier is used to complete the training on a distributed setup
        # Use callbacks for adding steps to be done at the end of training
        # NOTE Avoid adding any logic after trainer.train()
        # Test the distributed scenario in case you add any logic beyond trainer.train()
        trainer.train()

        # save files only once by Rank-0 process
        if trainer.should_save:
            self.finetune_params["model_name_or_path"] = str(self.finetune_params["model_name_or_path"])
            # save if model is trained via deepspeed stage 3
            self.finetune_params["is_deepspeed_zero3_enabled"] = is_deepspeed_zero3_enabled()
            # save finetune args
            finetune_args_path = str(
                Path(self.finetune_params["pytorch_model_folder"], SaveFileConstants.FINETUNE_ARGS_SAVE_PATH)
            )
            write_dict_to_json_file(self.finetune_params, finetune_args_path)

            # save finetune_config file
            ft_config_path = str(
                Path(self.finetune_params["pytorch_model_folder"], SaveFileConstants.ACFT_CONFIG_SAVE_PATH))
            write_dict_to_json_file(self.ft_config, ft_config_path)

            # copy mlflow inference params file to pytorch output for model converter
            mlflow_infer_params_file_path = Path(
                self.finetune_params["preprocess_output"],
                MLFlowHFFlavourConstants.INFERENCE_PARAMS_SAVE_NAME_WITH_EXT,
            )
            shutil.copy(mlflow_infer_params_file_path, self.finetune_params["pytorch_model_folder"])


def preprocess_logits_for_metrics(logits, labels):
    """
    Callback for preprocessing logits after every evaluation step
    """

    if isinstance(logits, tuple):
        # Depending on the model and config, logits may contain extra tensors,
        # like past_key_values, but logits always come first
        logits = logits[0]

    return torch.argmax(logits, dim=2)


def split_1d_array_using_sentinel_token(
    labels: np.ndarray,
    sentinel_token: int = TaskConstants.TEXT_GENERATION_IGNORE_INDEX
) -> List[np.ndarray]:
    """Split input array into multiple subarray's based on sentinel token.

    Note that consecutive sentinel tokens are treated as single token i.e. the split doesn't change when there is
    1 or multiple sentinel tokens. See the below example for reference.
    Example #1:
      labels = np.array([-100, -100, 2, 3, -100]) -> [np.array([2,3])]
    Example #2:
      labels = np.array([-100, 2, 3]) -> [np.array([2,3])]
    """
    if labels.ndim > 1:
        ValueError("The array split doesn't work for multiple dimensions for now.")
    # [for reference purpose]
    # 1 -> assistant tokens
    # 0 -> user tokens
    binary_label_tokens = np.where(labels == sentinel_token, 0, 1)
    # identify all the transistion points
    split_token_ids = np.where(np.ediff1d(binary_label_tokens) != 0)[0] + 1
    return [
        split
        for split in np.split(labels, split_token_ids)
        if not np.any(split == sentinel_token)
    ]


def decode_prediction_tokens_and_format_metric_calculation(
    prediction_tokens: List[np.ndarray], tokenizer: PreTrainedTokenizerBase
) -> List[List[Dict[str, Any]]]:
    """Prepare predictions for metric calculation."""
    assistant_texts = tokenizer.batch_decode(prediction_tokens)

    return [
        [
            {"role": "assistant", "content": text}
        ]
        for text in assistant_texts
    ]


def decode_label_tokens(
    label_tokens: List[np.ndarray], tokenizer: PreTrainedTokenizerBase
) -> List[List[str]]:
    """Prepare labels for metric calculation."""
    return [[decode_str] for decode_str in tokenizer.batch_decode(label_tokens)]


def chat_completion_metrics_func(
    eval_pred: EvalPrediction,
    tokenizer: PreTrainedTokenizerBase,
    return_avg_assistant_to_example_rat: bool = False
):
    """
    compute and return metrics for chat completion.

    azureml-metrics package only compute metrics on the last assistant message.
    To bypass this behavior, we are splitting each example into multiple sub examples equal to the number of
    assistant messages. The final metrics is calculated over the number of assistant messages present in all
    examples.
    """
    if tokenizer.pad_token_id is None:
        raise ValueError("Pad token id cannot be None for tokenizer. The metrics calculation goes wrong.")

    from azureml.metrics import compute_metrics, constants as azureml_metric_constants

    predictions, labels = eval_pred
    # Filter prediction indices where labels has -100 token id
    predictions = np.where(
        labels != TaskConstants.TEXT_GENERATION_IGNORE_INDEX,
        predictions,
        TaskConstants.TEXT_GENERATION_IGNORE_INDEX
    )

    all_assistant_predictions = []
    all_assistant_gts = []
    for each_prediction, each_label in zip(predictions, labels):
        each_example_assistant_predictions = split_1d_array_using_sentinel_token(each_prediction)
        each_example_assistant_gts = split_1d_array_using_sentinel_token(each_label)

        all_assistant_predictions.extend(
            decode_prediction_tokens_and_format_metric_calculation(
                each_example_assistant_predictions, tokenizer=tokenizer
            )
        )
        all_assistant_gts.extend(
            decode_label_tokens(
                each_example_assistant_gts, tokenizer=tokenizer
            )
        )

    metrics = compute_metrics(
        task_type=azureml_metric_constants.Tasks.CHAT_COMPLETION,
        y_test=all_assistant_gts,
        y_pred=all_assistant_predictions,
        metrics=_METRICS_TO_COMPUTE
    ).get("metrics")

    if return_avg_assistant_to_example_rat:
        return (metrics, len(all_assistant_predictions) / np.shape(predictions)[0])
    return metrics
