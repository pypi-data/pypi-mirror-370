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
File for factory method for all NLP HF tasks
This file is called by component scripts files to fetch the corresponding task runners
"""

from .constants.constants import Tasks
from .base_runner import BaseRunner


def get_task_runner(task_name: str):
    """
    returns hf task related runner
    """
    if task_name == Tasks.NAMED_ENTITY_RECOGNITION:
        from .tasks.ner.runner import NerRunner
        return NerRunner

    if task_name == Tasks.SINGLE_LABEL_CLASSIFICATION:
        from .tasks.single_label.runner import SingleLabelRunner
        return SingleLabelRunner

    if task_name == Tasks.MULTI_LABEL_CLASSIFICATION:
        from .tasks.multi_label.runner import MultiLabelRunner
        return MultiLabelRunner

    if task_name == Tasks.SUMMARIZATION:
        from .tasks.summarization.runner import SummarizationRunner
        return SummarizationRunner

    if task_name == Tasks.TRANSLATION:
        from .tasks.translation.runner import TranslationRunner
        return TranslationRunner

    if task_name == Tasks.QUESTION_ANSWERING:
        from .tasks.qna.runner import QnARunner
        return QnARunner

    if task_name == Tasks.TEXT_GENERATION:
        from .tasks.text_generation.runner import TextGenerationRunner
        return TextGenerationRunner

    if task_name == Tasks.NLP_NER:
        from .tasks.nlp_ner.runner import NLPNerRunner
        return NLPNerRunner

    if task_name == Tasks.NLP_MULTICLASS:
        from .tasks.nlp_multiclass.runner import NLPMulticlassRunner
        return NLPMulticlassRunner

    if task_name == Tasks.NLP_MULTILABEL:
        from .tasks.nlp_multilabel.runner import NLPMultilabelRunner
        return NLPMultilabelRunner

    if task_name == Tasks.CHAT_COMPLETION:
        from .tasks.chat_completion.runner import ChatCompletionRunner
        return ChatCompletionRunner

    if task_name == Tasks.VISUAL_QUESTION_ANSWERING:
        from .tasks.visual_qna.runner import VisualQnARunner
        return VisualQnARunner

    raise NotImplementedError(f"HF runner for the task {task_name} is not supported")
