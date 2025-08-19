# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Run Model Registration module."""
import time
import argparse
from argparse import Namespace
from typing import Dict, Optional
import logging

import json
import re

from pathlib import Path
from azureml.core.model import Model
from peft import __version__ as peft_version
from peft.utils import CONFIG_NAME as PEFT_ADAPTER_CONFIG_FILE_NAME

from .register_presets_model import registermodel_entrypoint

from azureml.core import Workspace
from azureml.core.run import Run, _OfflineRun

from azureml.acft.common_components import (
    get_logger_app, set_logging_parameters, is_debug_logging_enabled, LoggingLiterals
)
from azureml.acft.contrib.hf import VERSION, PROJECT_NAME
from azureml.acft.contrib.hf.nlp.constants.constants import LOGS_TO_BE_FILTERED_IN_APPINSIGHTS
from azureml.acft.accelerator.utils.code_utils import update_json_file_and_overwrite
from azureml.acft.accelerator.utils.run_utils import add_run_properties

from azureml.acft.common_components.utils.error_handling.swallow_all_exceptions_decorator import (
    swallow_all_exceptions,
)


logger = get_logger_app("azureml.acft.contrib.hf.nlp.entry_point.finetune.register_model")


COMPONENT_NAME = "ACFT-Register_Model"
SUPPORTED_MODEL_ASSET_TYPES = [Model.Framework.CUSTOM, "PRESETS"]
# omitting underscores which is supported in model name for consistency
VALID_MODEL_NAME_PATTERN = r"^[a-zA-Z0-9-]+$"
NEGATIVE_MODEL_NAME_PATTERN = r"[^a-zA-Z0-9-]"
REGISTRATION_DETAILS_JSON_FILE = "model_registration_details.json"
PEFT_VERSION_KEY = "peft_version"
BASE_MODEL_KEY = "base_model"


def str2bool(arg):
    """Convert string to bool."""
    arg = arg.lower()
    if arg in ["true", '1']:
        return True
    elif arg in ["false", '0']:
        return False
    else:
        raise ValueError(f"Invalid argument {arg} to while converting string to boolean")


def parse_string_tags(input: str) -> Dict[str, str]:
    '''
    Return a dictionary by parsing the given string.

    Input expects no explicit single quote or double quotes from user.

    :param input: String to be parsed as dictionary.
    :return: A dictionary with key value pair defined from input string.
    '''
    if input == "None":
        return {}
    result = {}
    tags = input.replace(';', ',').split(',')
    for tag in tags:
        tag = tag.strip()
        if ':' in tag:
            key, value = tag.split(':', 1)
            result[key.strip()] = value.strip()
        else:
            result[tag] = tag
    return result


def parse_args():
    """Return arguments."""
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument("--model_path", type=str, help="Directory containing model files")
    parser.add_argument(
        "--convert_to_safetensors",
        type=str2bool,
        default="false",
        choices=[True, False],
        help="convert pytorch model to safetensors format"
    )
    parser.add_argument(
        "--task_name",
        type=str,
        help="Finetuning task name",
    )
    parser.add_argument(
        "--model_type",
        type=str,
        default="PRESETS",
        choices=SUPPORTED_MODEL_ASSET_TYPES,
        help="Type of model you want to register",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        help="Name to use for the registered model. If it already exists, the version will be auto incremented.",
    )
    parser.add_argument(
        "--model_asset_id",
        type=str,
        help="Asset id of model",
    )
    parser.add_argument(
        "--model_version",
        type=str,
        help="Model version in workspace/registry. If model with same version exists,version will be auto incremented",
        default=None,
    )
    parser.add_argument(
        "--registration_details_folder",
        type=Path,
        help="A folder which contains a JSON file into which model registration details will be written",
    )
    parser.add_argument(
        "--model_tag",
        type=parse_string_tags,
        default=dict({}),
        help="Optional tag for the model to be registered"
    )
    args = parser.parse_args()
    logger.info(f"Args received {args}")
    return args


def get_workspace_details() -> Workspace:
    """Fetch the workspace details from run context."""
    run = Run.get_context()
    if isinstance(run, _OfflineRun):
        return Workspace.from_config()
    return run.experiment.workspace


def is_model_available(ml_client, model_name, model_version):
    """Return true if model is available else false."""
    is_available = True
    try:
        ml_client.models.get(name=model_name, version=model_version)
    except Exception as e:
        logger.warning(f"Model with name - {model_name} and version - {model_version} is not available. Error: {e}")
        is_available = False
    return is_available


def get_model_name(model_asset_id: str) -> Optional[str]:
    """Construct the model name from the base model."""
    import uuid

    # model_asset_id: azureml://registries/<registry_name>/models/<model_name>/versions/<version>
    base_model_name = model_asset_id.split("/")[5]
    logger.info(f"Base model name: {base_model_name}")

    new_model_name = base_model_name + "-ft-" + str(uuid.uuid4())
    logger.info(f"Updated model name: {new_model_name}")

    return new_model_name


def get_base_model_id(model_asset_id: str) -> Optional[str]:
    """Fetch the base model id from the base model."""
    # base_model_id : azureml://registries/<registry_name>/models/<model_name>
    base_model_id = "/".join(model_asset_id.split('/')[:6])
    return base_model_id


def update_peft_adapter_config(model_path: str, model_asset_id: str):
    """Update the peft adapter_config.json with `peft_version` and `base_model`."""
    adapter_config_file = Path(model_path, PEFT_ADAPTER_CONFIG_FILE_NAME)
    update_config = {
        PEFT_VERSION_KEY: peft_version,
        BASE_MODEL_KEY: get_base_model_id(model_asset_id),
    }
    if adapter_config_file.is_file():
        update_json_file_and_overwrite(str(adapter_config_file), update_config)
        logger.info(f"Updated {PEFT_ADAPTER_CONFIG_FILE_NAME}.")
    else:
        logger.info(f"Could not find {PEFT_ADAPTER_CONFIG_FILE_NAME}.")


def convert_lora_weights_to_safetensors(model_path: str):
    """Read the bin files and convert them to safe tensors."""
    import os
    import torch
    from azureml.acft.contrib.hf.nlp.utils.io_utils import find_files_with_inc_excl_pattern
    from safetensors.torch import save_file

    bin_files = find_files_with_inc_excl_pattern(model_path, include_pat=".bin$")
    logger.info(f"Following bin files are identified: {bin_files}")
    for bin_file in bin_files:
        bin_file_sd = torch.load(bin_file, map_location=torch.device("cpu"))
        safe_tensor_file = bin_file.replace(".bin", ".safetensors")
        save_file(bin_file_sd, safe_tensor_file)
        logger.info(f"Created {safe_tensor_file}")
        os.remove(bin_file)
        logger.info(f"Deleted {bin_file}")


def copy_model_to_output(model_path: str, output_dir: str):
    """Copy the model from model path to output dir."""
    import shutil
    logger.info("Started copying the model weights to output directory")
    shutil.copytree(model_path, output_dir, dirs_exist_ok=True)
    logger.info("Completed copying the weights")


def get_properties(model_asset_id: str) -> Dict[str, str]:
    """Fetch the appropriate properties regarding the base model."""
    logger.info(f"Model Asset Id: {model_asset_id}")
    properties = {}

    # model_asset_id: azureml://registries/<registry_name>/models/<model_name>/versions/<version>
    # baseModelId : azureml://registries/<registry_name>/models/<model_name>
    # baseWeightsId : <model_name>
    properties["baseModelId"] = get_base_model_id(model_asset_id)
    properties["baseWeightsId"] = model_asset_id.split("/")[-3]

    # fixed properties
    additional_properties = {
        "baseModelWeightsVersion": 1.0,
        "hasDeltaWeights": "true",
        "maas-finetuning": "true",
    }
    properties.update(additional_properties)
    logger.info(f"Adding the following properties to the registered model: {properties}")

    return properties


def register_custom_model(
    workspace, model_path, model_name, model_type, model_description, tags, properties, registration_details_folder
):
    """Register the model in custom format."""
    # register the model using SDKV1
    model = Model.register(
        workspace=workspace,
        model_path=model_path,  # where the model was copied to in output
        model_name=model_name,
        model_framework=model_type,
        description=model_description,
        tags=tags,
        properties=properties
    )
    logger.info(f"Registering model {model.name} with version {model.version}.")
    logger.info(f"Model registered. AssetID : {model.id}")

    # save the model info
    model_info = {
        "id": model.id,
        "name": model.name,
        "version": model.version,
        "type": model.model_framework,
        "properties": model.properties,
        "tags": model.tags,
        "description": model.description,
    }
    json_object = json.dumps(model_info, indent=4)
    registration_file = registration_details_folder / REGISTRATION_DETAILS_JSON_FILE

    with open(registration_file, "w+") as outfile:
        outfile.write(json_object)
    logger.info("Saved model registration details in output json file.")


def register_model(args: Namespace):
    """Run main function."""
    model_name = args.model_name
    model_type = args.model_type
    registration_details_folder = args.registration_details_folder
    tags, properties, model_description = args.model_tag, {}, ""

    # set properties
    properties = get_properties(args.model_asset_id)

    # create workspace details
    ws = get_workspace_details()

    if not re.match(VALID_MODEL_NAME_PATTERN, model_name):
        # update model name to one supported for registration
        logger.info(f"Updating model name to match pattern `{VALID_MODEL_NAME_PATTERN}`")
        model_name = re.sub(NEGATIVE_MODEL_NAME_PATTERN, "-", model_name)
        logger.info(f"Updated model_name = {model_name}")

    st = time.time()
    if Model.Framework.CUSTOM == model_type:
        register_custom_model(
            workspace=ws,
            model_path=registration_details_folder,
            model_name=model_name,
            model_type=Model.Framework.CUSTOM,
            model_description=model_description,
            tags=tags,
            properties=properties,
            registration_details_folder=registration_details_folder
        )
    elif "PRESETS" == model_type:
        registermodel_entrypoint(
            model_name=model_name,
            registered_model_output=str(registration_details_folder),
            registered_model_version=None,
            properties=properties,
            tags=tags
        )

    time_to_register = time.time() - st
    logger.info(f"Time to register: {time_to_register} seconds")

    logger.info(f"Adding model name to root job properties")
    add_run_properties(
        properties_to_add={"registered_ft_model_name": model_name},
        add_to_root=True
    )

@swallow_all_exceptions(time_delay=60)
def main():
    """Main run function."""
    args = parse_args()

    set_logging_parameters(
        task_type=args.task_name,
        acft_custom_dimensions={
            LoggingLiterals.PROJECT_NAME: PROJECT_NAME,
            LoggingLiterals.PROJECT_VERSION_NUMBER: VERSION,
            LoggingLiterals.COMPONENT_NAME: COMPONENT_NAME
        },
        azureml_pkg_denylist_logging_patterns=[] if is_debug_logging_enabled() else LOGS_TO_BE_FILTERED_IN_APPINSIGHTS,
        log_level=logging.DEBUG if is_debug_logging_enabled() else logging.INFO,
    )

    # convert to safe tensors
    if args.convert_to_safetensors:
        convert_lora_weights_to_safetensors(args.model_path)

    # update adapter_config.json with `peft_version`
    update_peft_adapter_config(args.model_path, args.model_asset_id)

    # update model name
    if args.model_name is None:
        args.model_name = get_model_name(args.model_asset_id)

    # copy to output dir
    copy_model_to_output(args.model_path, args.registration_details_folder)

    # register model
    register_model(args)


# run script
if __name__ == "__main__":
    main()
