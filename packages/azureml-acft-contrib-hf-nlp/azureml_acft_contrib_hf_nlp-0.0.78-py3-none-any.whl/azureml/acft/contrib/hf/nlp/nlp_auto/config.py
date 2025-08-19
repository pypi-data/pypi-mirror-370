# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
File containing HF config related functions
"""


# https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

import os
from typing import Optional, Union
import copy
from ..constants.constants import HfModelTypes

from azureml.acft.common_components import get_logger_app

from transformers import AutoConfig, PretrainedConfig


logger = get_logger_app(__name__)


class AzuremlAutoConfig(AutoConfig):

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> PretrainedConfig:

        apply_adjust = kwargs.pop("apply_adjust", True)
        kwargs_log = copy.deepcopy(kwargs)
        id2label = kwargs_log.pop("id2label", None)
        label2id = kwargs_log.pop("label2id", None)
        logger.info(f"id2label {id2label}")
        logger.info(f"label2id {label2id}")
        logger.info(f"Initializing config with {kwargs_log}")
        config = super(AzuremlAutoConfig, cls).from_pretrained(
            hf_model_name_or_path,
            **kwargs,
        )

        return AzuremlAutoConfig.post_init(config) if apply_adjust else config

    @staticmethod
    def post_init(config: PretrainedConfig) -> PretrainedConfig:

        model_type = AzuremlAutoConfig.get_model_type(config)
        if model_type == HfModelTypes.GPT2:
            config.pad_token_id = config.eos_token_id
            logger.info(f"Setting the config pad token id to {config.pad_token_id}")

        # forcefully supressing the model output tensors
        # hidden_states
        #   Tuple of `torch.FloatTensor` (one for the output of the embeddings, if the model has an embedding layer, +
        #   one for the output of each layer) of shape `(batch_size, sequence_length, hidden_size)`
        config.output_hidden_states = False

        # attentions
        #   Tuple of `torch.FloatTensor` (one for each layer) of shape `(batch_size, num_heads, sequence_length,
        #   sequence_length)`.
        config.output_attentions = False

        # past_key_values
        #   Tuple of `tuple(torch.FloatTensor)` of length `config.n_layers`, with each tuple having 2 tensors of shape
        #   `(batch_size, num_heads, sequence_length, embed_size_per_head)`)
        if hasattr(config, 'use_cache'):
            config.use_cache = False

        return config

    @staticmethod
    def get_model_type(
        config: Optional[PretrainedConfig] = None,
        hf_model_name_or_path: Optional[Union[str, os.PathLike]] = None,
        **kwargs,
    ) -> str:

        # PreTrainedConfig has an attribute model_type
        if config is not None:
            return getattr(config, "model_type")
        elif hf_model_name_or_path is not None:
            config = super(AzuremlAutoConfig, AzuremlAutoConfig).from_pretrained(hf_model_name_or_path, **kwargs)
            return getattr(config, "model_type")
        else:
            raise ValueError("Pretrained config or model_name_or_path should be present")
