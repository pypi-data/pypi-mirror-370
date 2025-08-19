# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Validate LoRA weights."""

import logging
from typing import Optional, List, Any
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
from azureml.acft.common_components import (
    get_logger_app, set_logging_parameters, is_debug_logging_enabled, LoggingLiterals
)
from azureml.acft.contrib.hf.nlp.constants.constants import LOGS_TO_BE_FILTERED_IN_APPINSIGHTS
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore
from azureml.acft.common_components.utils.error_handling.swallow_all_exceptions_decorator import (
    swallow_all_exceptions,
)
from azureml.acft.contrib.hf.nlp.constants.constants import Tasks
from azureml.acft.contrib.hf import VERSION, PROJECT_NAME
import argparse
import torch
import os
import pandas as pd
import random

COMPONENT_NAME = "ACFT-Validate_lora_weights"

logger = get_logger_app(
    "azureml.acft.contrib.hf.nlp.entry_point.finetune.validate_lora_weights"
)

GENERATION_CONFIG = {
    "max_new_tokens": 256,
    "do_sample": True,
    "top_p": 0.7,
    "temperature": 0.8
}

TEST_SAMPLES = {
    Tasks.TEXT_GENERATION: ["Hello"],
    Tasks.CHAT_COMPLETION: [
        {'role': 'user', 'content': "Hello"},
        {'role': 'assistant', 'content': "Dummy assistant message"}
    ]
}

LOAD_CONFIG_KWARGS = {
    "trust_remote_code": True
}

LOAD_TOKENIZER_KWARGS = {
    "trust_remote_code": True
}

LOAD_MODEL_KWARGS = {
    "trust_remote_code": True
}


def _generate_random_k_examples(
        text_or_chat_key: str,
        jsonl_file_path: Optional[str],
        k: int = 1
    ) -> List[Any]:
    """Read the example file and randomly sample k examples."""
    if jsonl_file_path is None:
        return []

    # validate the file extension
    if not any([jsonl_file_path.endswith('json'), jsonl_file_path.endswith('jsonl')]):
        logger.warning(
            "Cannot generate examples for validation due to invalid file format. "
            f"Either of `jsonl` or `json` format is supported. Found: {jsonl_file_path.split('.')[-1]}"
        )
        return []
    
    jsonl_lines = pd.read_json(jsonl_file_path, lines=True, orient='records')
    num_records = jsonl_lines.shape[0]
    if num_records <= k:
        return jsonl_lines[text_or_chat_key].to_list()
    else:
        # NOTE Repetitions in rand_indices are not handled currently
        rand_indices = [random.randint(0, num_records-1) for _ in range(k)]
        return jsonl_lines.take(rand_indices)[text_or_chat_key].to_list()

def _supported_tasks() -> List[str]:
    """Return the list of supported tasks for validating lora input."""
    return [Tasks.TEXT_GENERATION, Tasks.CHAT_COMPLETION]

def validate_lora_weights(
    base_model_path: str,
    config_path: str,
    lora_weights_path: str,
    tokenizer_path: str,
    train_file_path: str,
    task_name: str,
    text_or_chat_key: str
):
    """Load model and make forward pass to validate lora weights."""

    # validate if the task name is supported
    supported_tasks = _supported_tasks()
    if task_name not in supported_tasks:
        logger.warning(f"Couldn't validate the finetune task {task_name}. Supported tasks are: {supported_tasks}")
        return

    test_examples = []
    if train_file_path:
        test_examples += _generate_random_k_examples(text_or_chat_key, train_file_path, 3)

    if not test_examples:
        test_examples += TEST_SAMPLES[task_name]

    logger.info("Validating lora model weights")

    config = AutoConfig.from_pretrained(config_path, **LOAD_CONFIG_KWARGS)

    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, config=config, **LOAD_TOKENIZER_KWARGS)

    logger.info("Loading base model")
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_path, device_map="auto", torch_dtype=torch.float16, config=config, **LOAD_MODEL_KWARGS
    )
    logger.info("Base model loaded")

    logger.info("Loading lora adapters")
    model = PeftModel.from_pretrained(base_model, lora_weights_path)
    logger.info("lora model loaded")

    for example_no, example in enumerate(test_examples):

        if task_name == Tasks.TEXT_GENERATION:
            input_ids = tokenizer(example, return_tensors="pt").input_ids.to("cuda")
        elif task_name == Tasks.CHAT_COMPLETION:
            logger.info(f"Example #{example_no}: The last assistant message will be removed before passing to model prediction.")
            try:
                input_ids = tokenizer.apply_chat_template(example[:-1], tokenize=True, return_tensors='pt').to(torch.device('cuda'))
            except Exception as e:
                logger.warning(f"Chat template could not be applied to message, skip validating this example: {str(e)}")
                continue

        try:
            outputs = model.generate(inputs=input_ids, **GENERATION_CONFIG)
            predictions_text = tokenizer.batch_decode(outputs)
        except Exception as e:
            raise ACFTValidationException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=(
                            f"LoRA weights validation failed in forward pass, "
                            f"model cannot be inferenced in fp16, error: {str(e)}"
                        )
                    )
                )

        logger.info(f"Validation_input:\n{example}\ngenerated text:\n{predictions_text}")
    logger.info("Outputs generated successfully, Validation successful")


def get_parser():
    """Get the parser object."""
    parser = argparse.ArgumentParser(description="Validate lora weights after finetuning")

    parser.add_argument(
        "--task_name",
        type=str,
        required=True,
        help="Finetune Task",
    )

    parser.add_argument(
        "--text_or_chat_key",
        type=str,
        required=True,
        help="text or chat key for reading train file",
    )

    parser.add_argument(
        "--base_pytorch_model_path",
        type=str,
        required=True,
        help="MLFlow Model path used for validating lora weights",
    )

    parser.add_argument(
        "--lora_weights_path",
        type=str,
        required=True,
        help="LoRA weights path",
    )

    parser.add_argument(
        "--train_file_path",
        type=str,
        required=True,
        help="Train file used for training",
    )

    return parser


@swallow_all_exceptions(time_delay=5)
def main():
    """Validate lora weights after finetuning."""
    parser = get_parser()
    args, _ = parser.parse_known_args()

    set_logging_parameters(
        task_type="TextGeneration",
        acft_custom_dimensions={
            LoggingLiterals.PROJECT_NAME: PROJECT_NAME,
            LoggingLiterals.PROJECT_VERSION_NUMBER: VERSION,
            LoggingLiterals.COMPONENT_NAME: COMPONENT_NAME
        },
        azureml_pkg_denylist_logging_patterns=[] if is_debug_logging_enabled() else LOGS_TO_BE_FILTERED_IN_APPINSIGHTS,
        log_level=logging.DEBUG if is_debug_logging_enabled() else logging.INFO,
    )

    validate_lora_weights(
        args.base_pytorch_model_path,
        args.base_pytorch_model_path,
        args.lora_weights_path,
        args.base_pytorch_model_path,
        args.train_file_path,
        args.task_name,
        args.text_or_chat_key
    )


if __name__ == "__main__":
    main()
