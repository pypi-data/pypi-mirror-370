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
NER
"""

from argparse import Namespace
from typing import List

from ...constants.constants import Tasks
from ...base_runner import BaseRunner
from .preprocess.base import NerPreprocessArgs, NerDataset
from .preprocess.preprocess_for_inference import NerPreprocessForInfer

from transformers.hf_argparser import HfArgumentParser

from azureml.acft.common_components import get_logger_app


logger = get_logger_app(__name__)


class NerRunner(BaseRunner):

    def run_preprocess_for_finetune(self, component_args: Namespace, unknown_args: List[str]) -> None:

        from .preprocess.preprocess_for_finetune import NerPreprocessForFinetune

        load_config_kwargs = getattr(component_args, "finetune_config", {}).get("load_config_kwargs", {})
        self.check_model_task_compatibility(
            model_name_or_path=component_args.model_name_or_path,
            task_name=Tasks.NAMED_ENTITY_RECOGNITION,
            **load_config_kwargs,
        )

        preprocess_arg_parser = HfArgumentParser([NerPreprocessArgs])
        output_args = preprocess_arg_parser.parse_args_into_dataclasses(unknown_args, return_remaining_strings=True)
        preprocess_args: NerPreprocessArgs = output_args[0]

        logger.info(f"unused args - {output_args[1]}")

        preprocess_obj = NerPreprocessForFinetune(component_args, preprocess_args)
        preprocess_obj.preprocess()

    def run_preprocess_for_infer(self, *args, **kwargs) -> None:
        data = [x.split() for x in kwargs["data"]]
        model_name_or_path = kwargs["tokenizer_path"]
        component_args = Namespace(**{"model_name_or_path": model_name_or_path})
        preprocess_arg_parser = HfArgumentParser([NerPreprocessArgs])
        preprocess_args: NerPreprocessArgs = preprocess_arg_parser.parse_args_into_dataclasses([])[0]
        preprocess_args.tag_key = None
        # preprocess_args.label_column = None
        preprocess_obj = NerPreprocessForInfer(component_args, preprocess_args)
        test_data = {preprocess_args.token_key: data}
        encoded_data = preprocess_obj.preprocess(test_data)
        return encoded_data

    def run_finetune(self, component_plus_preprocess_args: Namespace) -> None:

        from .finetune.finetune import NerFinetune

        finetune_obj = NerFinetune(vars(component_plus_preprocess_args), NerDataset)
        finetune_obj.finetune()

    def run_modelselector(self, *args, **kwargs) -> None:

        from ...utils.model_selector_utils import model_selector

        model_selector(kwargs)
