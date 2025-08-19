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
"""
validation utils
"""
import typing
from abc import ABC
from typing import List, Optional, Union, Set
import copy

from datasets import Value, Sequence

from azureml.acft.common_components.utils.error_handling.exceptions import ACFTDataException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError

from azureml.acft.common_components import get_logger_app
from azureml._common._error_definition.azureml_error import AzureMLError

from ..constants.constants import AzuremlConstants, DatasetSplit, ValidationConstants, Tasks


logger = get_logger_app(__name__)


class AzuremlValidatorMixin(ABC):
    """
    This is a mixin to be used with 'AzuremlDataset' class to provide common utility functions for data validation
    """

    def __init__(self, required_columns: Optional[List[str]] = None, required_column_dtypes: Optional[List[List[str]]] = None):
        """
        Azureml Dataset atleast should have the columns that are present in required_columns. The required_columns should confirm to the dtypes present in required_column_dtypes

        :param required_columns - mandatory columns to be present in Azureml Dataset
        :param required_column_dtypes - valid dtypes of required_columns
        """

        if required_column_dtypes is None:
            required_column_dtypes = []
        if required_columns is None:
            required_columns = []
        if len(required_columns) != len(required_column_dtypes):
            raise ValueError("Required columns and their dtypes should be of same length")

        self.required_columns = required_columns
        self.required_column_dtypes = required_column_dtypes
        if self.label_column_optional and self.label_column is not None and \
            self.label_column not in self.dataset.column_names:
            logger.info(f"Removing label_column {self.label_column} from required columns and its dtypes")
            label_column_index = self.required_columns.index(self.label_column)
            _ = self.required_columns.pop(label_column_index)
            _ = self.required_column_dtypes.pop(label_column_index)
            self.label_column = None

        # backup input dataset columns to log error in case the columns don't match during :meth match_columns
        self.original_datset_columns = copy.copy(self.dataset.column_names)

    def apply_common_validations(self, split, batch_size: int = 1000, task_name: Optional[str] = None) -> None:
        """
        Applies Data Validations common to all tasks
        """
        # Remove the extra columns and match the remaining columns
        self.remove_extra_columns()
        self.match_columns()
        # Check for duplicate column names
        self.check_duplicate_column_names()

        # filter data
        # null filter
        self.remove_null_examples(batch_size=batch_size)

        # check for minimum num of training samples
        if split == DatasetSplit.TRAIN:
            self.check_min_train_samples(task_name)

    def remove_extra_columns(self) -> None:
        """
        Removes columns other than required columns and updates the self.dataset
        """
        columns_to_remove = [name for name in self.dataset.column_names if name not in self.required_columns]
        self.dataset = self.dataset.remove_columns(columns_to_remove)
        logger.info(f"Removed columns: {columns_to_remove} from dataset")

    def match_columns(self) -> None:
        """
        Match the dataset columns with the keep columns and raise error otherwise
        """
        if sorted(self.required_columns) != sorted(self.dataset.column_names):
            logger.warning("Exception occured while matching dataset columns with user passed columns, scrubbing exception")
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=(
                        f"Path or dict: {self.path_or_dict}."
                        f"Dataset Columns: {self._remove_dataset_column_prefix(self.original_datset_columns)}."
                        f"User Passed Columns: {self._remove_dataset_column_prefix(self.required_columns)}."
                    )
                )
            )

    def check_column_dtypes(self) -> None:
        """
        check the keep columns with keep column dtypes and raise error otherwise
        """

        datset_features = self.dataset.features
        for column_name, valid_dtypes in zip(self.required_columns, self.required_column_dtypes):
            if column_name not in datset_features:
                logger.warning("Exception occured column name not present in dataset, scrubbing exception")
                raise ValueError(
                    f"{column_name} not present in column to dtypes map file."
                    f"The following columns are present: {list(datset_features.keys())}"
                )

            if not isinstance(datset_features[column_name], Value):
                logger.warning("Unable to validate dataset dtypes")
                raise ACFTDataException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=(
                            f"File path or data: {self.path_or_dict}\n"
                            f"Unable to validate dtype for feature {self._remove_dataset_column_prefix(column_name)}\n"
                            f"Found column type: {type(datset_features[column_name])}\n"
                            f"Expected dtypes: {valid_dtypes}"
                        )
                    )
                )

            column_dtype = datset_features[column_name].dtype
            if column_dtype not in valid_dtypes:
                logger.warning("Exception occured column dtype not valid, scrubbing exception")
                raise ACFTDataException._with_error(
                    AzureMLError.create(
                        ACFTUserError,
                        pii_safe_message=(
                            f"File path or data: {self.path_or_dict}\n"
                            f"dtype mismatch for feature {self._remove_dataset_column_prefix(column_name)}\n"
                            f"Found dtype: {column_dtype}\n"
                            f"Expected dtypes: {valid_dtypes}"
                        )
                    )
                )

    def _check_if_non_empty(self, val: Union[str, List, int, dict]) -> bool:
        """
        Checks if a value is empty based on data type
        """
        # For the supported tasks val will be the following
        # Single Label - int, str
        # Multi Label - int, str
        # NER - list
        # Summarization, Translation - str
        # QnA - str, dict
        if val is None:
            return False
        if isinstance(val, (str, List, dict)):
            return len(val) != 0

        return True

    def remove_null_examples(self, batch_size: int = 1000) -> None:
        """
        Removes the null examples and update the dataset
        Raises error if the number of examples after filter is 0
        """
        null_filter = lambda example: all([self._check_if_non_empty(value) for _, value in example.items()])
        pre_filter_rows = self.dataset.num_rows
        self.dataset = self.dataset.filter(
            null_filter,
            batch_size=batch_size,
            writer_batch_size=batch_size
        )
        post_filter_rows = self.dataset.num_rows
        logger.info(f"Null filter - examples before filter: {pre_filter_rows} | examples after filter: {post_filter_rows}")
        if post_filter_rows == 0:
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=f"Found no examples after data preprocessing for {self.path_or_dict}"
                )
            )

    def check_min_train_samples(self, task_name: Optional[str] = None) -> None:
        """
        Raises error if the number of examples in training set (after earlier checks) is lower than threshold
        """
        training_rows = self.dataset.num_rows
        logger.info(f"Number of training samples post filtration: {training_rows}")
        min_train_samples = ValidationConstants.MIN_TRAINING_SAMPLE
        # Overriding min number of samples to consider for generative tasks like Text Generation and Chat completion
        # This would allow customers to finetune on smaller datasets as we have seen 
        # customers having less than 50 rows of training data trying to do finetuning
        if task_name in [Tasks.TEXT_GENERATION, Tasks.CHAT_COMPLETION]:
            logger.info(
                "Overriding min number of training samples to be considered for generative tasks to: {}".format(ValidationConstants.MIN_TRAINING_SAMPLE_GENERATIVE_TASKS)
            )
            min_train_samples = ValidationConstants.MIN_TRAINING_SAMPLE_GENERATIVE_TASKS
        if training_rows < min_train_samples:
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=f"Training dataset has {training_rows} non-null samples, which is fewer than "\
                        f"{min_train_samples} samples, which is the min required to finetune. "\
                        f"Please check your training dataset or provide a validation dataset"\
                        f"(training dataset will be split if no validation dataset)."
                )
            )

    def check_duplicate_column_names(self) -> None:
        """
        Raises error if any duplicate column names are found
        """
        if len(self.dataset.column_names) != len(set(self.dataset.column_names)):
            logger.warning("Exception occured: duplicate column names detected, scrubbing exception")
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=(
                        f"File path or data: {self.path_or_dict}\n"
                        f"Dataset has one or more duplicate column names\n"
                    )
                )
            )

    def check_column_contents(self, column1_name: Optional[str], column2_name: Optional[str]) -> None:
        """
        Raises error if the feature columns are identical
        """
        if column1_name is not None and column2_name is not None and self.dataset[column1_name] == self.dataset[column2_name]:
            logger.warning("Exception occured: identical feature columns detected, scrubbing exception")
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=(
                        f"File path or data: {self.path_or_dict}\n"
                        f"Dataset columns are identical\n"
                    )
                )
            )

    def update_required_columns_with_prefix(self) -> None:
        """
        This function  will update the :param `required_columns` with a constant prefix
        """
        self.required_columns = [AzuremlConstants.DATASET_COLUMN_PREFIX + col for col in self.required_columns]

    def _remove_dataset_column_prefix_string_data(self, data: str) -> str:
        """Remove the dataset column prefix to data string"""
        if isinstance(data, str):
            prefix_to_remove = AzuremlConstants.DATASET_COLUMN_PREFIX
            if data.startswith(prefix_to_remove):
                return prefix_to_remove.join(data.split(prefix_to_remove)[1:])
            else:
                logger.warning("Prefix not found! Skipping removal")
                return data

    def _remove_dataset_column_prefix(self, data: Union[str, List]) -> Union[str, List]:
        """Remove the dataset column prefix from data"""

        if isinstance(data, str):
            return self._remove_dataset_column_prefix_string_data(data=data)
        elif isinstance(data, List):
            output_data = []
            for ele in data:
                output_data.append(self._remove_dataset_column_prefix_string_data(data=ele))
            return output_data
        else:
            logger.warning(f"Prefix removal is not supported for input of type: {type(data)}")
            return data


def remove_dataset_column_prefix_string_data(data: str) -> str:
    """Remove the dataset column prefix to data string"""
    if isinstance(data, str):
        prefix_to_remove = AzuremlConstants.DATASET_COLUMN_PREFIX
        if data.startswith(prefix_to_remove):
            return prefix_to_remove.join(data.split(prefix_to_remove)[1:])
        else:
            logger.warning("Prefix not found! Skipping removal")
            return data
    return data


def get_set_difference(minuend: Union[List, Set, str, dict], subtrahend: Union[List, Set, str, dict]) -> List:
    """
    Return set difference as minuend - subtrahend
    e.g. [1,2,3] - [2, 3, 9], will return [1]

    :param minuend:
    :type minuend: Union[List, Set, str, dict]
    :param subtrahend:
    :type subtrahend: Union[List, Set, str, dict]

    :return: True if all elements in <subset> are present in <superset>
    :rtype: List
    """
    if minuend and subtrahend and len(minuend) > 0:
        if not isinstance(minuend[0], typing.Hashable):
            raise ValueError("minuend parameter in get_set_difference() should be list, set or dict of hashable type.")
        if len(subtrahend) > 0 and not isinstance(subtrahend[0], typing.Hashable):
            raise ValueError("subtrahend parameter in get_set_difference() should be list, set or dict of "
                             "hashable type.")

        return list(set(minuend).difference(set(subtrahend)))

    return []
