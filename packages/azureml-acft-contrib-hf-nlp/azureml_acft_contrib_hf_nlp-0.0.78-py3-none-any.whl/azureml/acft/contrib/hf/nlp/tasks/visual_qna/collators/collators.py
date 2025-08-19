# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict

import torch
from transformers import BatchFeature, PreTrainedTokenizerBase

from ..constants import TokenizedColumns


class LlamaVisualQnADataCollator:
    """Data collator for Visual QnA tasks using LLaMA models."""

    def __init__(self, tokenizer: PreTrainedTokenizerBase):
        self.tokenizer = tokenizer

    def pad_sequence(self, sequences, padding_side="right", padding_value=0):
        """
        Pad a list of sequences to the same length.
        sequences: list of tensors in [seq_len, *] shape
        """
        assert padding_side in ["right", "left"]
        max_size = sequences[0].size()
        trailing_dims = max_size[1:]
        max_len = max(len(seq) for seq in sequences)
        batch_size = len(sequences)
        output = sequences[0].new_full(
            (batch_size, max_len) + trailing_dims, padding_value
        )
        for i, seq in enumerate(sequences):
            length = seq.size(0)
            if padding_side == "right":
                output.data[i, :length] = seq
            else:
                output.data[i, -length:] = seq
        return output

    def cat_with_pad(self, tensors, dim, padding_value=0):
        """
        cat along dim, while pad to max for all other dims
        """
        ndim = tensors[0].dim()
        assert all(
            t.dim() == ndim for t in tensors[1:]
        ), "All tensors must have the same number of dimensions"

        out_size = [max(t.shape[i] for t in tensors) for i in range(ndim)]
        out_size[dim] = sum(t.shape[dim] for t in tensors)
        output = tensors[0].new_full(out_size, padding_value)

        index = 0
        for t in tensors:
            # Create a slice list where every dimension except dim is full slice
            slices = [slice(0, t.shape[d]) for d in range(ndim)]
            # Update only the concat dimension slice
            slices[dim] = slice(index, index + t.shape[dim])

            output[slices] = t
            index += t.shape[dim]

        return output

    def __call__(self, batch: Dict[str, Any]) -> Dict[str, torch.Tensor]:

        input_ids_list = []
        pixel_values_list = []

        for inputs in batch:
            input_ids_list.append(inputs[TokenizedColumns.INPUT_IDS][0])
            if (
                TokenizedColumns.PIXEL_VALUES in inputs
                and inputs[TokenizedColumns.PIXEL_VALUES] is not None
            ):
                pixel_values_list.append(inputs[TokenizedColumns.PIXEL_VALUES])

        input_ids = self.pad_sequence(
            input_ids_list, padding_side="right", padding_value=0
        )
        attention_mask = (input_ids != 0).long()
        # Generate labels: mask out padding tokens with -100
        labels = input_ids.clone()
        labels[labels == self.tokenizer.pad_token_id] = -100

        result = {
            TokenizedColumns.INPUT_IDS: input_ids,
            TokenizedColumns.LABELS: labels,
            TokenizedColumns.ATTENTION_MASK: attention_mask,
        }
        if pixel_values_list:
            pixel_values_tensor_list = []
            for i, pv_item in enumerate(pixel_values_list):
                current_pv = pv_item
                if not isinstance(current_pv, torch.Tensor):
                    current_pv = torch.tensor(current_pv, dtype=torch.bfloat16)
                elif current_pv.dtype != torch.bfloat16:
                    current_pv = current_pv.to(torch.bfloat16)
                pixel_values_tensor_list.append(current_pv)

            if (
                not pixel_values_tensor_list
            ):  # Should not happen if pixel_values_list is not empty
                result[TokenizedColumns.PIXEL_VALUES] = None
            else:
                result[TokenizedColumns.PIXEL_VALUES] = self.cat_with_pad(
                    pixel_values_tensor_list, dim=0
                )

        return BatchFeature(result)


class CollatorFactory:
    """Factory to get appropriate collator based on model type."""

    @staticmethod
    def get_collator(tokenizer: PreTrainedTokenizerBase):
        return LlamaVisualQnADataCollator(tokenizer)
