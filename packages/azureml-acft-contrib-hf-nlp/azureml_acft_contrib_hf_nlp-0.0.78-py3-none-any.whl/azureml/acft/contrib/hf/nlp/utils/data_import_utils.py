# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
common utils
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

from ..constants.constants import Tasks

from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml.acft.common_components.utils.run_utils import post_warning
from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.core.run import Run


logger = get_logger_app(__name__)


TRAIN_FILE_NAME = "train_input.jsonl"
VALIDATION_FILE_NAME = "validation_input.jsonl"


def task_specific_example_validation(
    example: Dict[str, Any],
    task_name: Optional[str] = None,
    user_column_names: List[str] = [],
):
    if task_name == Tasks.CHAT_COMPLETION:
        if "messages" not in example:
            raise KeyError("Dataset example missing 'messages' key.")
        if type(example["messages"]) != list:
            raise TypeError("Dataset example doesn't have 'messages' as list.")
        for sample in example["messages"]:
            if "role" not in sample:
                raise KeyError("Dataset example missing 'role' key in 'messages'.")
            if "content" not in sample:
                raise KeyError("Dataset example missing 'content' key in 'messages'.")
            if type(sample["role"]) != str:
                raise TypeError("Dataset example expect 'string' for messages['role'].")
            if type(sample["content"]) != str:
                raise TypeError("Dataset example expect 'string' for messages['content'].")
    elif task_name == Tasks.TEXT_GENERATION:
        for column in user_column_names:
            if column not in example:
                raise KeyError(f"Dataset example missing '{column}' key.")
            if type(example[column]) != str:
                raise TypeError(f"Dataset example expect 'string' for {column}.")


def filter_invalid_data_rows_for_jsonl(
        file_path: str,
        destination_folder_path: str,
        mode: str = "train",
        task_name: Optional[str] = None,
        user_column_names: List[str] = [],
    ):
    """Processes a file, appends its lines to destination_file, returns # lines."""

    if not os.path.exists(file_path):
        raise ACFTValidationException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=(
                        f"The provided file does not exist: {file_path}"
                    )
                )
            )

    if mode == "train":
        destination_file_path = (Path(destination_folder_path) / TRAIN_FILE_NAME).resolve()
    else:
        destination_file_path = (Path(destination_folder_path) / VALIDATION_FILE_NAME).resolve()

    if os.path.exists(destination_file_path):
        os.remove(destination_file_path)
        logger.info("Output file already exists, wipe it before writing data into it.")

    # Read the file using UTF-8-sig encoding to remove BOM
    invalid_json_ct = 0
    with open(file_path, "rt", encoding="UTF-8-sig") as f_in, \
         open(destination_file_path, "a", encoding="UTF-8") as f_out:

        try:
            for index, line in enumerate(f_in):
                # Check for empty lines in dataset rows
                if not line.strip():
                    msg = f"Line number {index} is empty. Skipping"
                    invalid_json_ct += 1
                    logger.warning(msg)
                    continue

                # Check if the line is a valid json
                try:
                    logger.info(f"Loading file {file_path}")
                    example = json.loads(line)
                    task_specific_example_validation(example, task_name, user_column_names)
                except Exception as e:
                    # logger.info(f"Failed to load file {file_path}")
                    error_type = type(e).__name__
                    error_msg = str(e)
                    logger.warning(f"Bad input data {file_path} on line {index}. {error_type}: {error_msg}, skipping..")
                    invalid_json_ct += 1
                    continue

                f_out.write(json.dumps(example))
                f_out.write("\n")

        except (UnicodeDecodeError, UnicodeEncodeError) as e:
            raise ACFTValidationException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=(
                            f"Invalid file passed, Failure while reading from file with error: {str(e)}"
                        )
                    )
                )

    # Post warning to Run level about number of lines skipped
    if invalid_json_ct > 0:
        warning_message = (f"Total {invalid_json_ct} json lines skipped in your dataset," +
                           "due to either empty or invalid format of json.")
        logger.warning(warning_message)
        try:
            run = Run.get_context()
            top_level_run = run
            while top_level_run.parent:
                top_level_run = top_level_run.parent
            post_warning(top_level_run, warning_message)
        except Exception as e:
            logger.warning(f"Post warning to parent pipeline run failed with exception {e}")
