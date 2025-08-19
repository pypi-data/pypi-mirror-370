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

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.error_handling.error_definitions import (
    ACFTUserError,
)
from azureml.acft.common_components.utils.error_handling.exceptions import (
    ACFTDataException,
)
from datasets import Dataset
from PIL import Image
from transformers import AutoProcessor

from ....constants.constants import MLFlowHFFlavourTasks
from ....utils.data_utils import AzuremlDataset
from ....utils.validation_utils import AzuremlValidatorMixin
from ..constants import InputJsonColumns, PreprocessingParams, TokenizedColumns

ANSWER_SUFFIX = "<|end|><|endoftext|>"
_IGNORE_INDEX = -100


logger = get_logger_app(__name__)


@dataclass
class VisualQnAPreprocessArgs:
    model_name_or_path: str = field(
        metadata={"help": "Model name or path for AutoProcessor."}
    )
    train_file_path: str = field(metadata={"help": "Path to training JSONL file."})
    images_folder: str = field(metadata={"help": "Path to images folder."})
    output_dir: str = field(
        metadata={"help": "Output directory for preprocessed data."}
    )
    validation_file_path: Optional[str] = field(
        default=None, metadata={"help": "Path to validation JSONL file."}
    )
    test_file_path: Optional[str] = field(
        default=None, metadata={"help": "Path to test JSONL file."}
    )
    mlflow_task_type: str = field(
        default=MLFlowHFFlavourTasks.VISUAL_QUESTION_ANSWERING
    )
    max_seq_length: int = field(
        default=-1, metadata={"help": "Maximum sequence length for tokenization."}
    )

    label_column: str = field(
        default="Answer", metadata={"help": "Column name to use as label."}
    )

    instruction: str = field(
        default="Respond with ONLY a single letter (A, B, C, or D) corresponding to the correct answer. Do not provide explanations, reasoning, or any additional text.",
        metadata={"help": "Instruction to provide to the model during preprocessing."},
    )

    batch_size: int = field(
        default=1, metadata={"help": "Batch size for preprocessing."}
    )

    pad_to_max_length: bool = field(
        default=True, metadata={"help": "Pad sequences to max length."}
    )


class PreprocessedDataset:
    VALID_FORMAT = ".jsonl"

    def __init__(self, path: Path):
        self.path = path
        self.dataset = None
        self.__load()

    def __validate_path(self):
        if not self.path.exists():
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError, pii_safe_message=(f"Invalid Path {self.path}.")
                )
            )
        if self.path.suffix != self.VALID_FORMAT:
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=(f"Invalid format {self.path.suffix}."),
                )
            )

    def __load(self):
        self.__validate_path()
        self.dataset = Dataset.from_json(str(self.path))
        self.dataset.set_format(type="torch", columns=self.dataset.column_names)


class VisualQnADataset(AzuremlDataset, AzuremlValidatorMixin):

    def __init__(
        self,
        path: Path,
        images_folder: Path,
        required_columns: List[str],
        required_column_dtypes: List[str],
        processor: AutoProcessor,
        dataset_args: Dict[str, Any],
        slice: str = "train",
        label_column: str = InputJsonColumns.ANSWER,
        label_column_optional: bool = False,
        model_name_or_path: str = None,
    ) -> None:
        self.path = path
        self.images_folder = images_folder
        self.processor = processor
        self.dataset_args = dataset_args
        self.slice = slice
        self.label_column = label_column
        self.label_column_optional = label_column_optional
        self.required_columns = required_columns
        self.required_column_dtypes = required_column_dtypes
        self.batch_size = self.dataset_args[PreprocessingParams.BATCH_SIZE]
        self.dataset = None
        self.model_name_or_path = model_name_or_path
        self.__load_dataset()
        super(AzuremlDataset, self).__init__(
            required_columns=required_columns,
            required_column_dtypes=required_column_dtypes,
        )
        self.encode_dataset()

    def __load_dataset(self):
        self.dataset = Dataset.from_json(str(self.path))
        self.validate()

    def __load_image(self, image_path: str) -> Image.Image:
        full_path = self.images_folder / image_path
        return Image.open(full_path).convert("RGB")

    def __tokenize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        image = self.__load_image(data[InputJsonColumns.IMAGE_PATH])
        question = data[InputJsonColumns.QUESTION]
        choices = []
        for key in data:
            if key.startswith(InputJsonColumns.CHOICE):
                choices.append(data[key])

        # Sort choices by their letter to maintain order (A, B, C, D...)
        choices.sort(key=lambda x: x.strip()[0] if x.strip() else "")

        answer = data[InputJsonColumns.ANSWER]
        if not answer:
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=(f"Answer cannot be empty."),
                )
            )
        
        return self.__tokenize_llama(image, question, choices, answer)

    def __tokenize_llama(self, image, question, choices, answer):
        """Llama-specific tokenization for multimodal input"""
        # Process the image first to get vision tensors

        # Format the conversation with image first, then text
        conversation = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "width": image.width,
                            "height": image.height,
                        },
                    },
                    {
                        "type": "text",
                        "text": question + "\n" + "\n".join(choices),
                    },
                ],
            }
        ]

        instruction = self.dataset_args.get(PreprocessingParams.INSTRUCTION, "")
        if instruction:
            conversation[0]["content"].append({"type": "text", "text": instruction})
        prompt_str = self.processor.tokenizer.apply_chat_template(
            conversation, tokenize=False, add_generation_prompt=False
        )
        proc_out = self.processor(text=prompt_str, images=[image], return_tensors="pt")
        input_ids = proc_out[TokenizedColumns.INPUT_IDS]  # includes <|patch|> tokens
        pixel_values = proc_out[TokenizedColumns.PIXEL_VALUES]

        # 4. append answer tokens and create labels
        answer_tokens = self.processor.tokenizer(answer, return_tensors="pt").input_ids
        input_ids = torch.cat([input_ids, answer_tokens], dim=1)

        labels = torch.full_like(input_ids, _IGNORE_INDEX)
        labels[:, -answer_tokens.shape[1] :] = answer_tokens

        max_len = int(self.dataset_args[PreprocessingParams.MAX_TRAINING_LENGTH])
        if 0 < max_len < input_ids.size(1):
            input_ids = input_ids[:, :max_len]
            labels = labels[:, :max_len]

        if not isinstance(pixel_values, torch.Tensor):
            pixel_values = torch.tensor(pixel_values)

        if pixel_values.dtype == torch.bfloat16:
            pixel_values = pixel_values.to(torch.float32)

        return {
            TokenizedColumns.INPUT_IDS: input_ids,
            TokenizedColumns.LABELS: labels,
            TokenizedColumns.ATTENTION_MASK: torch.ones_like(input_ids),
            TokenizedColumns.PIXEL_VALUES: pixel_values,
        }

    def encode_dataset(self):
        self.dataset = self.dataset.map(
            self.__tokenize,
            batched=False,
            remove_columns=self.dataset.column_names,
        )

    def validate(self) -> None:
        sample_record = self.dataset[0]
        logger.info(f"Sample record: {sample_record}")
        choice_keys = [
            key for key in sample_record if key.startswith(InputJsonColumns.CHOICE)
        ]
        logger.info(f"Choice keys: {choice_keys}")
        if len(choice_keys) < 2:
            raise ACFTDataException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=(f"Each record must have at least two choices (e.g., 'Choice A', 'Choice B')."),
                )
            )

    def to_parquet(self, path: Path) -> None:
        self.dataset.to_parquet(str(path), batch_size=self.batch_size)
