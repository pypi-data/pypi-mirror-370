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

from argparse import Namespace
from dataclasses import fields
from typing import List

from azureml.acft.common_components import get_logger_app
from transformers.hf_argparser import HfArgumentParser

from ...base_runner import BaseRunner
from .finetune.finetune import VisualQnAFinetune
from .preprocess.base import VisualQnAPreprocessArgs
from .preprocess.preprocess_for_finetune import VisualQnAPreprocessForFinetune

logger = get_logger_app(__name__)


class VisualQnARunner(BaseRunner):
    """Runner class for Visual Question Answering task."""

    def run_preprocess_for_finetune(
        self, component_args: Namespace, unknown_args: List[str]
    ) -> None:
        """Run preprocessing for finetuning."""
        logger.info("Starting preprocessing for Visual QnA finetuning.")

        logger.warning(
            "Skipping model chat compatibility check as `Visual QnA` is not a recognized "
            "task in huggingface."
        )
        logger.info(f"Unknown args: {unknown_args}")
        parsed_unknown_args = {}
        i = 0
        while i < len(unknown_args):
            if unknown_args[i].startswith("--"):
                key = unknown_args[i][2:]  # Remove '--' prefix
                if i + 1 < len(unknown_args) and not unknown_args[i + 1].startswith(
                    "--"
                ):
                    value = unknown_args[i + 1]
                    i += 2
                else:
                    value = "True"  # Flag without value
                    i += 1
                parsed_unknown_args[key] = value
            else:
                i += 1

        logger.info(f"Parsed unknown args: {parsed_unknown_args}")

        args_dict = vars(component_args)
        logger.info(f"Available component args: {args_dict}")
        combined_args = {**args_dict, **parsed_unknown_args}
        logger.info(f"Combined args: {combined_args}")
        dataclass_fields = set(f.name for f in fields(VisualQnAPreprocessArgs))
        logger.info(f"Valid dataclass fields: {dataclass_fields}")
        filtered_args = {}
        unused_args = {}
        for k, v in combined_args.items():
            if k in dataclass_fields:
                filtered_args[k] = v
            else:
                unused_args[k] = v

        logger.info(f"Filtered args for preprocessing: {filtered_args}")
        logger.info(f"Unused args: {unused_args}")

        preprocess_arg_parser = HfArgumentParser([VisualQnAPreprocessArgs])
        preprocess_args = preprocess_arg_parser.parse_dict(filtered_args)[0]
        preprocess_obj = VisualQnAPreprocessForFinetune(preprocess_args, unused_args)
        preprocess_obj.preprocess()

    def run_finetune(self, component_args: Namespace) -> None:
        """Run finetuning."""
        logger.info("Starting finetuning for Visual QnA.")
        finetune_params = vars(component_args)
        finetune = VisualQnAFinetune(finetune_params)
        finetune.finetune()

    def run_modelselector(self, *args, **kwargs) -> None:
        """Model selection logic."""
        from ...utils.model_selector_utils import model_selector

        model_selector(kwargs)

    def run_preprocess_for_infer(self, *args, **kwargs) -> None:
        pass
