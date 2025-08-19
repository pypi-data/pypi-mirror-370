# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
common utils
"""

import json
from typing import Dict, Any, TypeVar
from copy import deepcopy
from pathlib import Path

import torch


from azureml.acft.common_components import get_logger_app


logger = get_logger_app(__name__)

KeyType = TypeVar('KeyType')


def deep_update(src_mapping: Dict[KeyType, Any], *updating_mappings: Dict[KeyType, Any]) -> Dict[KeyType, Any]:
    updated_mapping = src_mapping.copy()
    for updating_mapping in updating_mappings:
        for k, v in updating_mapping.items():
            if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
                updated_mapping[k] = deep_update(updated_mapping[k], v)
            else:
                updated_mapping[k] = v
    return updated_mapping


def dict_to_json_serializable(d: Dict[str, Any]) -> None:
    """
    Convert the passed dictionary to JSON serializable format by removing unsupported data types as values
    so that the dictionary can be saved as json file
    """
    UNSUPPORTED_JSON_DATA_FORMATS = [
        torch.dtype,
        Path,
    ]

    for key in list(d.keys()):
        if any([isinstance(d[key], data_format) for data_format in UNSUPPORTED_JSON_DATA_FORMATS]):
            d.pop(key)

    # do the same for nested dictionary
    for value in d.values():
        if isinstance(value, dict):
            dict_to_json_serializable(value)


def write_dict_to_json_file(d: Dict[str, Any], file_name: str) -> None:
    """
    Convert the passed dictionary to JSON serializable and write to json file
    """
    Path(file_name).parent.mkdir(exist_ok=True, parents=True)

    json_dict = deepcopy(d)
    # convert dictionary to JSON serializable
    dict_to_json_serializable(json_dict)
    # write dictionary to json file
    with open(file_name, 'w') as rptr:
        json.dump(json_dict, rptr, indent=2)
