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
NLP NER
"""

from argparse import Namespace
from typing import List

from ...constants.constants import Tasks
from ...base_runner import BaseRunner
from .preprocess.base import NLPNerPreprocessArgs, NLPNerDataset

from transformers.hf_argparser import HfArgumentParser


class NLPNerRunner(BaseRunner):

    def run_preprocess_for_finetune(self, component_args: Namespace, unknown_args: List[str]) -> None:

        from .preprocess.preprocess_for_finetune import NLPNerPreprocessForFinetune

        self.check_model_task_compatibility(
            model_name_or_path=component_args.model_name_or_path, task_name=Tasks.NAMED_ENTITY_RECOGNITION
        )
        
        preprocess_arg_parser = HfArgumentParser([NLPNerPreprocessArgs])
        preprocess_args: NLPNerPreprocessArgs = preprocess_arg_parser.parse_args_into_dataclasses(unknown_args)[0]

        preprocess_obj = NLPNerPreprocessForFinetune(component_args, preprocess_args)
        preprocess_obj.preprocess()

    def run_modelselector(self, *args, **kwargs) -> None:

        from ...utils.model_selector_utils import model_selector

        model_selector(kwargs)

    def run_finetune(self, component_plus_preprocess_args: Namespace) -> None:

        from ..ner.finetune.finetune import NerFinetune

        finetune_obj = NerFinetune(vars(component_plus_preprocess_args), NLPNerDataset)
        finetune_obj.finetune()

    def run_preprocess_for_infer(self, *args, **kwargs) -> None:
        raise NotImplementedError
