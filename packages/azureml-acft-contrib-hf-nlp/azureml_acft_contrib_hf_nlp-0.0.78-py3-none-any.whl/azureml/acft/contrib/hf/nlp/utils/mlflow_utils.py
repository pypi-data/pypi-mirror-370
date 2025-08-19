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
mlflow utilities
"""
import json
from typing import List, Union, Optional, Tuple
import shutil
import yaml
from pathlib import Path
from mlflow.models import Model

from ..constants.constants import MLFlowHFFlavourConstants, MLFLOW_FLAVORS
from .common_utils import deep_update
from .io_utils import find_files_with_inc_excl_pattern

from peft import PeftModel

from transformers import TrainerCallback, TrainingArguments, TrainerState, TrainerControl
from transformers import PreTrainedModel, PreTrainedTokenizerBase
from transformers import pipeline
from transformers.utils import (
    WEIGHTS_INDEX_NAME,
    SAFE_WEIGHTS_INDEX_NAME,
    WEIGHTS_NAME,
    SAFE_WEIGHTS_NAME
)
from transformers.integrations.deepspeed import is_deepspeed_zero3_enabled

from torch_ort import ORTModule

from azureml._common._error_definition.azureml_error import AzureMLError

from azureml.acft.common_components.utils.error_handling.exceptions import ACFTSystemException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTSystemError
from azureml.acft.common_components import get_logger_app

from azureml.acft.accelerator.utils.license_utils import download_license_file
from azureml.acft.accelerator.utils.code_utils import get_model_custom_code_files, copy_code_files

import azureml.evaluate.mlflow as hf_mlflow
import mlflow


logger = get_logger_app(__name__)


def replace_mlflow_weights_with_pytorch_weights_zero3(pytorch_model_save_path: str, mlflow_model_save_path: str):
    """The mlflow.save saves the dummy model weights when deepspeed stage3 optimization is enabled. This is because
    in evaluation model is saved using ModelClass.save_pretrained to save the model. The save_pretrained method
    fetches the state dictionary using model.state_dict which is dummy when stage3 is enabled.To circumvent this
    behavior, we are copying the PyTorch model weights to MlFlow folder.

    :param pytorch_model_save_path: Folder where the PyTorch weights are saved. The weights saved in this
        folder are final weights and the model should be able to load using AutoModelFor<TaskName>.from_pretrained(...)
    :type: str
    :param mlflow_model_save_path: Output folder where the MlFlow weights are saved. The weights in this folder gets
    updated
    :type: str
    """
    dst_folder = Path(mlflow_model_save_path, "data", "model")

    # Copy the PyTorch artifacts -> mlflow
    index_file = Path(pytorch_model_save_path, WEIGHTS_INDEX_NAME)
    safe_index_file = Path(pytorch_model_save_path, SAFE_WEIGHTS_INDEX_NAME)
    weights_file = Path(pytorch_model_save_path, WEIGHTS_NAME)
    safe_weights_file = Path(pytorch_model_save_path, SAFE_WEIGHTS_NAME)

    # Clean the directory for already created dummy files
    # Identify all the model artifacts files
    dummy_model_artifacts_file_paths = find_files_with_inc_excl_pattern(
        str(dst_folder),
        include_pat=".bin$|.safetensors$|" + f"{str(safe_index_file)}|{str(index_file)}"
    )
    logger.info("Removing the dummy files created with mlflow.save")
    for file_name in dummy_model_artifacts_file_paths:
        logger.info(f"Removing {file_name}")
        Path(file_name).unlink()

    if index_file.exists() or safe_index_file.exists():
        logger.info("Copying the index file + shards to MlFlow model folder")
        # copy the sharded files to mlflow model artifacts
        load_index_file = index_file if index_file.exists() else safe_index_file
        with open(load_index_file, "r", encoding="utf-8") as f:
            index = json.load(f)
        shard_files = [str(Path(pytorch_model_save_path, x)) for x in list(set(index["weight_map"].values()))]
        shard_files.append(str(load_index_file))    # already has pytorch_model_save_path as prefix
        for shard_file in shard_files:
            logger.info(f"Copy started for {shard_file}")
            shutil.copy(shard_file, str(dst_folder))
    elif weights_file.exists() or safe_weights_file.exists():
        # copy the file to mlflow model artifacts
        existing_weights_file = weights_file if weights_file.exists() else safe_weights_file
        logger.info(f"Copy started for {existing_weights_file}")
        shutil.copy(str(existing_weights_file), str(dst_folder))
    else:
        raise ACFTSystemException._with_error(
            AzureMLError.create(
                ACFTSystemError,
                pii_safe_message=("Unable to replace dummy MlFlow weights with PyTorch weights with DS-Zero3 optimizer")
            )
        )


class SaveMLflowModelCallback(TrainerCallback):
    """
    A [`TrainerCallback`] that sends the logs to [AzureML](https://pypi.org/project/azureml-sdk/).
    """

    def __init__(
        self,
        mlflow_model_save_path: Union[str, Path],
        pytorch_model_save_path: Optional[Union[str, Path]],
        mlflow_infer_params_file_path: Union[str, Path],
        mlflow_task_type: str,
        model_name: str,
        model_name_or_path: Optional[str] = None,
        class_names: Optional[List[str]] = None,
        metadata: str = None,
        **kwargs
    ) -> None:
        """
        init azureml_run which is azureml Run object
        """
        self.mlflow_model_save_path = mlflow_model_save_path

        # Use pytorch save folder to load the model. This is set in case of LoRA where the base model is wrapped to add
        # lora weights
        self.pytorch_model_save_path = pytorch_model_save_path
        if self.pytorch_model_save_path is not None:
            logger.info(
                f"Will use pytorch folder - {pytorch_model_save_path} while saving the mlflow model")

        self.mlflow_infer_params_file_path = mlflow_infer_params_file_path
        self.mlflow_task_type = mlflow_task_type
        self.class_names = class_names
        self.model_name = model_name
        self.model_name_or_path = model_name_or_path
        self.mlflow_hf_args = kwargs.get("mlflow_hf_args", {})
        self.mlflow_ft_conf = kwargs.get("mlflow_ft_conf", {})
        self.mlflow_hftransformers_misc_conf = self.mlflow_ft_conf.get("mlflow_hftransformers_misc_conf", {})
        self.mlflow_model_signature = self.mlflow_ft_conf.get("mlflow_model_signature", None)
        self.mlflow_save_model_kwargs = self.mlflow_ft_conf.get("mlflow_save_model_kwargs", {})
        self.metadata = metadata
        self.mlflow_flavor = self.mlflow_ft_conf.get("mlflow_flavor", None)

    def load_model_tokenizer(self, **kwargs) -> Tuple[PreTrainedModel, PreTrainedTokenizerBase]:

        model, tokenizer = kwargs["model"], kwargs["tokenizer"]

        reload_model = True
        if self.pytorch_model_save_path is None:
            reload_model = False
        elif is_deepspeed_zero3_enabled() and isinstance(model, PeftModel):
            # do not try to load peft model again if it is deepspeed stage-3
            reload_model = False

        if reload_model:

            base_model_cls = model.__class__
            if isinstance(model, PeftModel):
                base_model_cls = model.base_model.model.__class__
            logger.info(f"Base model class to load the model before mlflow model save: {base_model_cls}")

            model = base_model_cls.from_pretrained(
                self.pytorch_model_save_path,
                low_cpu_mem_usage=True,
                torch_dtype="auto"
            )
            tokenizer = tokenizer.__class__.from_pretrained(self.pytorch_model_save_path)

        return model, tokenizer

    def on_train_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs):
        """
        Event called at the end of training.
        Save MLflow model at the end of training

        Model and Tokenizer information is part of kwargs
        """

        # saving the mlflow on world process 0
        if state.is_world_process_zero:

            model, tokenizer = self.load_model_tokenizer(**kwargs)

            # tokenization parameters for inference
            # task related parameters
            with open(self.mlflow_infer_params_file_path, 'r') as fp:
                mlflow_inference_params = json.load(fp)

            misc_conf = {
                MLFlowHFFlavourConstants.TASK_TYPE: self.mlflow_task_type,
                MLFlowHFFlavourConstants.TRAIN_LABEL_LIST: self.class_names,
                **mlflow_inference_params,
            }

            # if a huggingface_id was passed, save it to MLModel file, otherwise not
            if self.model_name != MLFlowHFFlavourConstants.DEFAULT_MODEL_NAME:
                misc_conf.update({MLFlowHFFlavourConstants.HUGGINGFACE_ID: self.model_name})

            # auto classes need to be passed in misc_conf if custom code files are present in the model folder
            if hasattr(model.config, "auto_map"):
                misc_conf.update(self.mlflow_hf_args)
                logger.info(f"Updated misc conf with Auto classes - {misc_conf}")

            logger.info(f"Adding additional misc to MLModel - {self.mlflow_hftransformers_misc_conf}")
            misc_conf = deep_update(misc_conf, self.mlflow_hftransformers_misc_conf)

            # files_list = prepare_mlflow_preprocess()
            # model_artifact_path = "llm_multiclass_model"
            # conda_env = {
            #     'channels': ['conda-forge'],
            #     'dependencies': [
            #         'python=3.8.8',
            #         'pip',
            #         {'pip': [
            #         'mlflow',
            #         'torch==1.12.0',
            #         'transformers==4.6.0',
            #     ]}
            #     ],
            #     'name': 'mlflow-env'
            # }
            if isinstance(model, PreTrainedModel):
                acft_model = model
            elif isinstance(model, ORTModule) and hasattr(model, "module"):
                acft_model = model.module
            elif is_deepspeed_zero3_enabled() and isinstance(model, PeftModel) and hasattr(model, "base_model"):
                # save dummy model in-case of peft deepspeed stage-3 model
                acft_model = model.base_model
            else:
                raise ACFTSystemException._with_error(
                    AzureMLError.create(ACFTSystemError, pii_safe_message=(
                        f"Got unexpected model - {model}"
                    ))
                )

            # Check if any code files are present in the model folder
            py_code_files = get_model_custom_code_files(self.model_name_or_path, model)

            # Save Model depending on flavor
            if self.mlflow_flavor == MLFLOW_FLAVORS.TRANSFORMERS:
                self.save_oss_flavor_mlflow_model(model=acft_model, tokenizer=tokenizer, py_code_files=py_code_files)
            else:
                # save hftransformers or hftransformers model
                self.save_hftransformers_mlflow_model(model=acft_model, tokenizer=tokenizer, misc_conf=misc_conf, py_code_files=py_code_files)

            # save LICENSE file to MlFlow model
            if self.model_name_or_path:
                license_file_path = Path(self.model_name_or_path, MLFlowHFFlavourConstants.LICENSE_FILE)
                if license_file_path.is_file():
                    shutil.copy(str(license_file_path), self.mlflow_model_save_path)
                    logger.info("LICENSE file is copied to mlflow model folder")
                else:
                    download_license_file(self.model_name, str(self.mlflow_model_save_path))

            # setting mlflow model signature for inference
            if self.mlflow_model_signature is not None:
                logger.info(f"Adding mlflow model signature - {self.mlflow_model_signature}")
                mlflow_model_file = Path(self.mlflow_model_save_path, MLFlowHFFlavourConstants.MISC_CONFIG_FILE)
                if mlflow_model_file.is_file():
                    mlflow_model_data = {}
                    with open(str(mlflow_model_file), "r") as fp:
                        yaml_data = yaml.safe_load(fp)
                        mlflow_model_data.update(yaml_data)
                        mlflow_model_data["signature"] = self.mlflow_model_signature

                    with open(str(mlflow_model_file), "w") as fp:
                        yaml.dump(mlflow_model_data, fp)
                        logger.info(f"Updated mlflow model file with 'signature': {self.mlflow_model_signature}")
                else:
                    logger.info("No MLmodel file to update signature")
            else:
                logger.info("No signature will be added to mlflow model")

            logger.info("Saved as mlflow model at {}".format(self.mlflow_model_save_path))


    def save_oss_flavor_mlflow_model(self, model, tokenizer, py_code_files):
        """
        Saves the finetuned model with transformers mlflow flavor
        """
        logger.info(f"Trying Saving Finetuned Model with FLAVOR : {self.mlflow_flavor}")
        model_pipeline = pipeline(task=self.mlflow_task_type, model=model, tokenizer=tokenizer, config=model.config)
        mlflow.transformers.save_model(
            transformers_model=model_pipeline,
            path=self.mlflow_model_save_path,
            code_paths=py_code_files,
            conda_env=str(Path(str(self.model_name_or_path), MLFlowHFFlavourConstants.CONDA_YAML_FILE)),
            metadata=self.metadata,
            **self.mlflow_save_model_kwargs,
        )
        logger.info(f"Saved Finetuned Model with FLAVOR : {self.mlflow_flavor}")
        copy_code_files(
            py_code_files,
            [str(Path(self.mlflow_model_save_path, dir)) for dir in ['model', Path("components", "tokenizer")]]
        )


    def save_hftransformers_mlflow_model(self, model, tokenizer, misc_conf, py_code_files):
        """
        Saves the finetuned model with hftransformers/hftransfomersv2 mlflow flavor
        """
        logger.info(f"Trying Saving Finetuned Model with FLAVOR : {self.mlflow_flavor}")
        # passing metadata through mlflow.models.Model api will dump the metadata
        # inline with the pyfunc at the parent level of the MLmodel yaml
        mlflow_model = Model(metadata=self.metadata)
        hf_mlflow.hftransformers.save_model(
            model,
            self.mlflow_model_save_path,
            tokenizer,
            model.config,
            misc_conf,
            code_paths=py_code_files,
            mlflow_model=mlflow_model,
            **self.mlflow_save_model_kwargs,
        )
        logger.info(f"Saved Finetuned Model with FLAVOR : {self.mlflow_flavor}")

        # code_paths=files_list, artifact_path=model_artifact_path, conda_env=conda_env,)
        # restructure_mlflow_acft_code(self.mlflow_model_save_path)

        # copying the py files to mlflow destination
        # copy dynamic python files to config, model and tokenizer
        copy_code_files(
            py_code_files,
            [str(Path(self.mlflow_model_save_path, 'data', dir)) for dir in ['config', 'model', 'tokenizer']]
        )
