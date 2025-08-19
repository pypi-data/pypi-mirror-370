# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File containing function for FTaaS data import component."""

import logging
import argparse
from argparse import Namespace
from typing import List, Optional

from pathlib import Path
from azureml.acft.contrib.hf import VERSION, PROJECT_NAME
from ...constants.constants import LOGS_TO_BE_FILTERED_IN_APPINSIGHTS
from azureml.acft.common_components import get_logger_app, set_logging_parameters, LoggingLiterals
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml.acft.common_components.utils.error_handling.swallow_all_exceptions_decorator import (
    swallow_all_exceptions,
)
from azureml._common._error_definition.azureml_error import AzureMLError
from ...utils.data_import_utils import filter_invalid_data_rows_for_jsonl

logger = get_logger_app("azureml.acft.contrib.hf.nlp.entry_point.data_import.data_import")


SUPPORTED_FILE_FORMATS = [".jsonl"]
COMPONENT_NAME = "ACFT-Data_Import"
TRAIN_FILE_NAME = "train_input.jsonl"
VALIDATION_FILE_NAME = "validation_input.jsonl"


def str2list(arg):
    """Convert string to list."""
    if len(arg) > 0:
        return [element for element in arg.split(",") if element]
    else:
        return []


def get_parser():
    """
    Add arguments and returns the parser. Here we add all the arguments for all the tasks.

    Those arguments that are not relevant for the input task should be ignored.
    """
    parser = argparse.ArgumentParser(description="Model selector for hugging face models", allow_abbrev=False)

    parser.add_argument(
        "--task_name",
        type=str,
        help="Finetuning task name",
    )

    parser.add_argument(
        "--train_file_path",
        type=str,
        help="Input train file path",
    )

    parser.add_argument(
        "--validation_file_path",
        default=None,
        type=str,
        help="Input validation file path",
    )

    parser.add_argument(
        "--user_column_names",
        default=[],
        type=str2list,
        help="User column names (Comma separated list of column names to be used for training).",
    )

    # Task settings
    parser.add_argument(
        "--output_dataset",
        type=Path,
        default=None,
        help="Folder to save the training data",
    )

    return parser


def _validate_file_paths_with_supported_formats(file_paths: List[Optional[str]]):
    """Check if the file path is in the list of supported formats."""
    global SUPPORTED_FILE_FORMATS

    for file_path in file_paths:
        if file_path:
            file_suffix = Path(file_path).suffix.lower()
            file_ext = file_suffix.split('?')[0]
        if file_ext and not file_ext in SUPPORTED_FILE_FORMATS:
            raise ACFTValidationException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=(
                        f"{file_path} is not in list of supported file formats. "
                        f"Supported file formats: {SUPPORTED_FILE_FORMATS}"
                    )
                )
            )


def data_import(args: Namespace):
    """Copy the user data to output dir."""
    # create the directory
    Path(args.output_dataset).mkdir(exist_ok=True, parents=True)

    # validate file formats
    _validate_file_paths_with_supported_formats([args.train_file_path, args.validation_file_path])
    logger.info("File format validation successful.")

    # preprocess and copy files
    logger.info(f"Import started for {args.train_file_path}")
    filter_invalid_data_rows_for_jsonl(
        args.train_file_path,
        args.output_dataset,
        mode="train",
        task_name=args.task_name,
        user_column_names=args.user_column_names,
    )
    logger.info("Import completed")
    if args.validation_file_path is not None:
        logger.info(f"Import started for {args.validation_file_path}")
        filter_invalid_data_rows_for_jsonl(
            args.validation_file_path,
            args.output_dataset,
            mode="validation",
            task_name=args.task_name,
            user_column_names=args.user_column_names,
        )
        logger.info("Import completed")


@swallow_all_exceptions(time_delay=5)
def main():
    """Parse args and import model."""
    # args
    parser = get_parser()
    args, _ = parser.parse_known_args()
    logger.info(args)

    set_logging_parameters(
        task_type=args.task_name,
        acft_custom_dimensions={
            LoggingLiterals.PROJECT_NAME: PROJECT_NAME,
            LoggingLiterals.PROJECT_VERSION_NUMBER: VERSION,
            LoggingLiterals.COMPONENT_NAME: COMPONENT_NAME
        },
        azureml_pkg_denylist_logging_patterns=LOGS_TO_BE_FILTERED_IN_APPINSIGHTS,
        log_level=logging.INFO,
    )

    data_import(args)


if __name__ == "__main__":
    main()
