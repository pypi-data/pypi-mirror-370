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
data utils
"""
from pathlib import Path
from typing import Optional, List, Union, Dict, Tuple, Any
import shutil
import mltable

from abc import ABC, abstractmethod
from datasets.load import load_dataset
from datasets import Sequence, Value, ClassLabel
from datasets.arrow_dataset import Dataset
from transformers.tokenization_utils_base import PreTrainedTokenizerBase

from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException, ACFTDataException
from azureml.acft.common_components.utils.error_handling.error_definitions import PathNotFound, ACFTUserError
from azureml._common._error_definition.user_error import BadData
from azureml.acft.common_components import get_logger_app
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore

from ..constants.constants import AzuremlConstants, DataSliceConstants


logger = get_logger_app(__name__)


class AzuremlDataset(ABC):
    """
    All the logic related to data can be a part of this class or the subclass inheriting this
    1. loading and saving the dataset
    2. data wrangling
    3. data collation function
    4. data augmentation (TBD)
    """

    VALID_FILE_FORMATS = ["jsonl", "json", "csv", "tsv", "parquet", "txt"]
    VALID_DIRECTORY_FORMATS = ["mltable"]
    VALID_DATA_FORMATS = VALID_FILE_FORMATS + VALID_DIRECTORY_FORMATS
    VALID_DATA_FORMATS_ERROR_STRING = f"Data format not supported. Supported formats are {VALID_DATA_FORMATS}"

    def __init__(
        self,
        path_or_dict: Union[str, Path, Dict],
        label_column: Optional[str] = None,
        label_column_optional: bool = False,
        slice: str = DataSliceConstants.NO_SPLIT,
    ) -> None:
        """
        :param label_column
            The column in self.dataset to be used as label_column. Setting this value to None makes some of
            the attributes / methods invalid
                :attr `class_names` calculates the class_names of the label_column
                :method `convert_label_column_using_classlabel` converts the label column to `dataset.ClassLabel`
                format
        :param label_column_optional
            The :param `label_column` can be initialized to None in some known cases. Alternatively, if you are unsure
            whether the column exists or not, you can use the :param `label_column_optional` which will check for the
            existance of label_column after loading the dataset
        :param path_or_dict
            The input can be a path or dictionary which will be converted to `datasets.Dataset` format. The path can
            be of type str or Path. There is currently no restriction on the dictionary format
        """

        # datasets-2.3.2 library doesn't go well with Path; so converting to str
        if isinstance(path_or_dict, Path):
            self.path_or_dict = str(path_or_dict)
        else:
            self.path_or_dict = path_or_dict

        self.label_column = label_column
        self.label_column_optional = label_column_optional

        self.slice = slice

        # load the dataset
        self.dataset = self.load(self.slice)

    def load(self, slice: str = DataSliceConstants.NO_SPLIT) -> Dataset:
        """
        1. Loads the dataset
        2. kwargs
            data_format - json, csv, mltable
            dataset_type - could be dataset or torch
            sample_size
                0.1 - 1.0 percentage of data to load
                1 - len(dataset) number of samples to load
        3. Handle loading dataset from S3 URI, Azure blob store
        """

        def _load_mltable(path_or_dict: str) -> Dataset:
            """
            Load mltable from any of the permissible input port.
            """
            try:
                data_tbl = mltable.load(path_or_dict)
                df = data_tbl.to_pandas_dataframe()
                ds = Dataset.from_pandas(df)
                logger.info(f"Dataset loaded with examples = {ds.num_rows}")
                return ds
            except Exception as e:
                raise ACFTDataException._with_error(
                            AzureMLError.create(
                                ACFTUserError,
                                pii_safe_message=f"Error while loading the dataset: {e}"
                            )
                        )

        logger.info(f"Loading dataset with slice : {slice}")
        if isinstance(self.path_or_dict, str):
            # check if file exists
            if Path(self.path_or_dict).is_file():
                # check if the file format is supported
                file_format = self._get_file_format(self.path_or_dict)
                if file_format:
                    data_file_extension, dataset_kwargs = self._get_dataset_format(file_format)
                    try:
                        ds = load_dataset(data_file_extension, data_files=self.path_or_dict, split=slice, **dataset_kwargs)
                        logger.info(f"Dataset loaded with examples = {ds.num_rows}")
                    except Exception as e:
                        raise ACFTDataException._with_error(
                            AzureMLError.create(
                                ACFTUserError,
                                pii_safe_message=(
                                    f"Error while loading the dataset: {e} \n "
                                    "Please validate your data by launching run through notebooks at "
                                    "https://github.com/Azure/azureml-examples/tree/main/sdk/python/"
                                    "foundation-models/system/finetune \n"
                                    "or alternately try loading each of your data file using the following"
                                    " code snippet \n"
                                    "```\nfrom datasets.load import load_dataset\n"
                                    f"ds = load_dataset('{data_file_extension}', data_files='path_to_file',"
                                    f"split='train', **{dataset_kwargs})\n```"
                                )
                            )
                        )
                    # clean datset column names
                    ds = self._clean_dataset_columns(ds)
                    return ds
                else:
                    raise ACFTValidationException._with_error(
                        AzureMLError.create(
                            BadData,
                            data_argument_name=AzuremlDataset.VALID_DATA_FORMATS_ERROR_STRING
                        )
                    )

            elif self.path_or_dict.lower().startswith(AzuremlConstants.AZUREML_URL_PREFIX):
                # check if input is MLTable with input port as Direct and load it
                try:
                    logger.info("Azureml url detected in input. Trying to load it as mltable.")
                    ds = _load_mltable(self.path_or_dict)
                except Exception as e:
                    raise ACFTDataException._with_error(
                        AzureMLError.create(
                            ACFTUserError,
                            pii_safe_message=f"Currently input port=Direct is supported for mltable input only: {e}"
                        )
                    )

                ds = self._get_dataset_slice(ds, slice)
                # clean datset column names
                ds = self._clean_dataset_columns(ds)
                return ds
            elif Path(self.path_or_dict).is_dir():
                # check if input is MLTable with input port as RO_Mount and load it
                directory_format = self._get_directory_format(self.path_or_dict)
                logger.info(directory_format)
                if directory_format:
                    if directory_format == "mltable":
                        ds = _load_mltable(self.path_or_dict)
                        ds = self._get_dataset_slice(ds, slice)
                        # clean datset column names
                        ds = self._clean_dataset_columns(ds)
                        return ds
                    else:
                        raise ACFTValidationException._with_error(
                            AzureMLError.create(
                                BadData,
                                data_argument_name=AzuremlDataset.VALID_DATA_FORMATS_ERROR_STRING
                            )
                        )
                else:
                    raise ACFTValidationException._with_error(
                        AzureMLError.create(
                            BadData,
                            data_argument_name=AzuremlDataset.VALID_DATA_FORMATS_ERROR_STRING
                        )
                    )
            else:
                raise ACFTValidationException._with_error(AzureMLError.create(PathNotFound, path=self.path_or_dict))

        elif isinstance(self.path_or_dict, Dict):
            # TODO add logic to load data from dictionary
            ds = Dataset.from_dict(self.path_or_dict)
            logger.info(f"Dataset loaded with examples = {ds.num_rows}")
            ds = self._get_dataset_slice(ds, slice)
            # clean datset column names
            ds = self._clean_dataset_columns(ds)
            return ds

        raise ACFTValidationException._with_error(AzureMLError.create(PathNotFound, path=self.path_or_dict))

    def _clean_dataset_columns(self, ds: Dataset) -> Dataset:
        column_mapping = {}
        for column in ds.column_names:
            cleaned_column = clean_column_name(column)
            if cleaned_column != column:
                column_mapping[column] = cleaned_column
        if column_mapping:
            logger.info(f"Cleaning column names: {column_mapping}")
            ds = ds.rename_columns(column_mapping)
        return ds

    def _get_dataset_slice(self, ds: Dataset, slice: str = DataSliceConstants.NO_SPLIT) -> Dataset:
        """
        returns slice of dataset
        `slice`: The below format is followed as load_dataset() supports it.
        e.g.: slice="train[:50%]"
              slice="train[50%:75%]"
              slice="train[-25%:]"
        If slice == "train" the original dataset is returned
        """
        if not slice or slice == DataSliceConstants.NO_SPLIT:
            return ds
        
        num_rows = ds.num_rows
        try:
            slice_ratio = slice[len("train["): -1]
            x, y = slice_ratio.split(":")
            if len(x) > 0 and x[-1] == "%":
                x = float(x[:-1])
            else:
                x = 0
            if len(y) > 0 and y[-1] == "%":
                y = float(y[:-1])
            else:
                y = 100
            x = int((x/100) * num_rows)
            y = int((y/100) * num_rows)
            logger.info(f"Splicing data indexes from {x} to {y}")
            ds_new = Dataset.from_dict(ds[x:y])
            logger.info(f"Dataset after slice is with examples = {ds_new.num_rows}")
            return ds_new
        except:
            logger.warning("Unable to slice dataset")

        return ds

    def _get_file_format(self, path: str) -> Union[str, None]:
        """identify valid file format"""
        file_extension = Path(path).suffix
        file_format = file_extension.lstrip(".")
        self.data_format = file_format
        if file_format not in AzuremlDataset.VALID_FILE_FORMATS:
            file_extension = None

        logger.info(f'Identified file format: "{file_extension}"')

        return file_extension

    def _get_dataset_format(self, file_format: str) -> Tuple[str, Dict[str, Any]]:
        """find data file extension and respective dataset loading kwargs"""
        dataset_kwargs = {}
        if file_format == ".jsonl":
            data_file_extension = "json"
        elif file_format == ".json":
            data_file_extension = "json"
        elif file_format == ".csv":
            data_file_extension = "csv"
        elif file_format == ".tsv":
            data_file_extension = "csv"
            dataset_kwargs["sep"] = "\t"
        elif file_format == ".parquet":
            data_file_extension = "parquet"
        else:
            data_file_extension = None

        return data_file_extension, dataset_kwargs  # type: ignore

    def _get_directory_format(self, path: str) -> Union[str, None]:
        """identify valid directory format"""
        data_format = None
        directory_path = Path(path)
        mltable_file_path = Path.joinpath(directory_path, "MLTable")
        if mltable_file_path.is_file():
            # currently only supported format is MLTable
            data_format = "mltable"
        if data_format not in AzuremlDataset.VALID_DIRECTORY_FORMATS:
            data_format = None
        self.data_format = data_format
        logger.info(f'Identified directory format: "{data_format}"')

        return data_format

    @property
    def class_names(self) -> Optional[List[str]]:

        # Return the precomputed class names saved in a private variable
        if hasattr(self, "_class_names"):
            return self._class_names

        if self.label_column is None:
            logger.info(f"Label column is {self.label_column}. Couldn't compute class names")
            return None

        sequence_data_type = isinstance(self.dataset.features[self.label_column], Sequence)
        value_data_type = isinstance(self.dataset.features[self.label_column], Value)
        if sequence_data_type:
            class_names = set()
            label_column_uniq_data = self.dataset[self.label_column]
            for item in label_column_uniq_data:
                class_names.update(item)
            # class_names needs to be sorted for reproducibility
            self._class_names = sorted(class_names)
            return self._class_names
        elif value_data_type:
            # class_names needs to be sorted for reproducibility
            self._class_names = sorted(self.dataset.unique(self.label_column))
            return self._class_names
        else:
            raise ValueError("Feature type is invalid. Only Value or Sequence types are supported")

    @staticmethod
    def set_column_dtype(dataset: Dataset, column_name: str, to_dtype: str = "string") -> Dataset:
        """Format dataset column to required dtype"""

        if column_name not in dataset.column_names:
            raise ValueError(f"Column `{column_name}` not present in dataset with columns `{dataset.column_names}`.")

        logger.info(f"Setting column {column_name} with dtype {to_dtype}")
        sequence_data_type = isinstance(dataset.features[column_name], Sequence)
        value_data_type = isinstance(dataset.features[column_name], Value)
        if value_data_type:
            return dataset.cast_column(column_name, Value(dtype=to_dtype))
        elif sequence_data_type:
            return dataset.cast_column(column_name, Sequence(Value(dtype=to_dtype)))
        else:
            raise ValueError("Feature type is invalid. Only Value or Sequence types are supported")

    def convert_label_column_using_classlabel(self, class_names: Optional[List[str]] = None) -> None:
        """
        Cast label column (:param `self.label_column`) using class label. In the default case, the dataset class names are used for conversion.
        However, if :param `class_names` is provided, it takes precedence.
        """

        if self.label_column is None:
            raise ValueError(f"Label column is {self.label_column}. Couldn't convert label column using classlabel")

        if class_names is None:
            class_names = self.class_names
            if class_names is None:
                raise ValueError(f"Class names: {class_names}. Couldn't convert label column using classlabel")

        logger.info(f"Converting column: {self.label_column} to classlabel using class names: {class_names}")
        sequence_data_type = isinstance(self.dataset.features[self.label_column], Sequence)
        value_data_type = isinstance(self.dataset.features[self.label_column], Value)
        if value_data_type:
            self.dataset = self.dataset.cast_column(self.label_column, ClassLabel(names=class_names))
        elif sequence_data_type:
            self.dataset = self.dataset.cast_column(self.label_column, Sequence(ClassLabel(names=class_names)))
        else:
            raise ValueError("Feature type is invalid. Only Value or Sequence types are supported")

    def save(self, save_folder: str, save_name: str = "dataset", batch_size: int = 1000) -> str:
        """
        This function should take care of taking the dataset. Currently, only json lines format is being saved.
        The :param batch_size controls the number of examples to hold in memory before saving it

        TODO Handle more save strategies such as `save_to_disk` or other data formats such as csv, parquet on a need
        basis
        """

        Path(save_folder).mkdir(exist_ok=True, parents=True)

        save_path = Path(save_folder).joinpath(f"{save_name}.jsonl")
        self.dataset.to_json(save_path, batch_size=batch_size)
        return save_path.name

    def update_dataset_columns_with_prefix(self) -> None:
        """
        Add the dataset column prefix to the dataset. The prefix is added only to the 1st level of columns
        and not done recursively

        The `self.label_column` will be updated with prefix along with dataset columns
        """
        self.dataset = self.dataset.rename_columns(
            {col: AzuremlConstants.DATASET_COLUMN_PREFIX+col for col in self.dataset.column_names})

        # update the label column
        if self.label_column is not None:
            self.label_column = AzuremlConstants.DATASET_COLUMN_PREFIX + self.label_column

    def get_collation_function(self) -> None:
        """
        used for data collation during training. The default behaviour is implemented here
        None => no dynamic padding happens during training
        """
        return None

    @abstractmethod
    def encode_dataset(self) -> None:
        """
        tokenize the dataset which is task dependent and needs to be implemented by the subclass
        """
        pass


def copy_and_overwrite(from_path: str, to_path: str):
    """
    copy and overwrites the directory
    """
    if Path(to_path).is_dir():
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)


def clean_column_name(column_name: str) -> str:
    return column_name.strip()
