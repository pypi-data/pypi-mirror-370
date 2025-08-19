# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
File containing HF model related functions
"""
import os
from pathlib import Path

from typing import List, Tuple

import torch

from transformers.models.auto.modeling_auto import (
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification,
    AutoModelForSeq2SeqLM,
    AutoModelForQuestionAnswering,
    AutoModelForCausalLM,
)
from transformers.utils import CONFIG_NAME
from transformers.modeling_utils import PreTrainedModel

from transformers import BitsAndBytesConfig

from azureml.acft.common_components import get_logger_app

from .config import AzuremlAutoConfig

from transformers import Llama4ForConditionalGeneration
LLAMA_4 = 'llama4'
GPT_OSS = 'gpt_oss'

logger = get_logger_app(__name__)


class AzuremlAutoModelBase():
    @classmethod
    def get_model_path(cls, hf_model_name_or_path, resume_from_checkpoint):
        model_path = hf_model_name_or_path
        if resume_from_checkpoint:
            if Path(resume_from_checkpoint, CONFIG_NAME).exists():
                logger.info(f"Found config.json present under resume_from_checkpoint. Will assume resume_from_checkpoint contains full model weights.")
                model_path = resume_from_checkpoint
            else:
                logger.info("No config.json present under resume_from_checkpoint. Will assume lora+peft case where resume_from_checkpoint contains just lora weights (adapter_model.bin).")
        return model_path
    
    @classmethod
    def update_task_specific_params_to_config(cls, task_specific_key, model):
        task_specific_params = model.config.task_specific_params
        if task_specific_params is not None and task_specific_key in task_specific_params:
            model.config.update(task_specific_params.get(task_specific_key))
            if model.can_generate():
                model.generation_config.update(**task_specific_params.get(task_specific_key))


# not using Inheritance for Azureml class as while loading auto classes for `trust_remote_code=True` the
# huggingface classes checks for the parent class name and they must be pre-defined Auto classes of transformers
# library not any other unknown custom classes
class AzuremlAutoModelForSequenceClassification(AzuremlAutoModelBase):

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> Tuple[PreTrainedModel, str, List[str]]:
        """Apply model specific hacks before calling the Base tokenizer"""

        # Initialize the config
        problem_type = kwargs.pop("problem_type", None)
        num_labels = kwargs.pop("num_labels", None)
        label2id = kwargs.pop("label2id", None)
        id2label = kwargs.pop("id2label", None)
        load_config_kwargs = kwargs.pop("load_config_kwargs", {})
        ignore_mismatched_sizes = kwargs.pop("ignore_mismatched_sizes", False)
        load_in_8bit = kwargs.pop("load_in_8bit", False)
        load_in_4bit = kwargs.pop("load_in_4bit", False)
        if load_in_8bit or load_in_4bit:
            # Setting device_map to None or {"": torch.cuda.current_device()} is trying to load
            # the model in GPU 0 always. To avoid that and load the model in all GPUs, :env
            # variable LOCAL_RANK is passed explicitly
            kwargs["device_map"] = {"": int(os.environ["LOCAL_RANK"])}
            logger.info(f'Setting the device map to use the current device GPU: {kwargs["device_map"]}')

        resume_from_checkpoint = kwargs.pop("resume_from_checkpoint", None)
        model_path = cls.get_model_path(hf_model_name_or_path, resume_from_checkpoint)
        logger.info(f"Loading config and model from: {model_path}")
        config = AzuremlAutoConfig.from_pretrained(
            model_path,
            problem_type=problem_type,
            num_labels=num_labels,
            id2label=id2label,
            label2id=label2id,
            output_attentions=False,
            output_hidden_states=False,
            **load_config_kwargs,
        )
        bnb_config = None
        if load_in_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )

        # Initialize the model
        model_type = AzuremlAutoConfig.get_model_type(config, **load_config_kwargs)
        model, model_loading_metadata = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            config=config,
            quantization_config=bnb_config,
            ignore_mismatched_sizes=ignore_mismatched_sizes,
            output_loading_info=True,
            **kwargs,
        )
        return model, model_type, model_loading_metadata["missing_keys"]


# not using Inheritance for Azureml class as while loading auto classes for `trust_remote_code=True` the 
# huggingface classes checks for the parent class name and they must be pre-defined Auto classes of transformers 
# library not any other unknown custom classes
class AzuremlAutoModelForTokenClassification(AzuremlAutoModelBase):

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> Tuple[PreTrainedModel, str, List[str]]:
        """Apply model specific hacks before calling the Base tokenizer"""

        # Initialize the config
        problem_type = kwargs.pop("problem_type", None)
        num_labels = kwargs.pop("num_labels", None)
        label2id = kwargs.pop("label2id", None)
        id2label = kwargs.pop("id2label", None)
        load_config_kwargs = kwargs.pop("load_config_kwargs", {})
        ignore_mismatched_sizes = kwargs.pop("ignore_mismatched_sizes", False)
        load_in_8bit = kwargs.pop("load_in_8bit", False)
        load_in_4bit = kwargs.pop("load_in_4bit", False)
        if load_in_8bit or load_in_4bit:
            # Setting device_map to None or {"": torch.cuda.current_device()} is trying to load
            # the model in GPU 0 always. To avoid that and load the model in all GPUs, :env
            # variable LOCAL_RANK is passed explicitly
            kwargs["device_map"] = {"": int(os.environ["LOCAL_RANK"])}
            logger.info(f'Setting the device map to use the current device GPU: {kwargs["device_map"]}')
        bnb_config = None
        if load_in_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=(
                    torch.bfloat16
                    if torch.cuda.is_bf16_supported() else
                    torch.float16
                ),
            )

        resume_from_checkpoint = kwargs.pop("resume_from_checkpoint", None)
        model_path = cls.get_model_path(hf_model_name_or_path, resume_from_checkpoint)
        logger.info(f"Loading config and model from: {model_path}")
        config = AzuremlAutoConfig.from_pretrained(
            model_path,
            problem_type=problem_type,
            num_labels=num_labels,
            id2label=id2label,
            label2id=label2id,
            output_attentions=False,
            output_hidden_states=False,
            **load_config_kwargs,
        )

        # Initialize the model
        model_type = AzuremlAutoConfig.get_model_type(config, **load_config_kwargs)
        model, model_loading_metadata = AutoModelForTokenClassification.from_pretrained(
            model_path,
            config=config,
            quantization_config=bnb_config,
            ignore_mismatched_sizes=ignore_mismatched_sizes,
            output_loading_info=True,
            **kwargs,
        )
        return model, model_type, model_loading_metadata["missing_keys"]


# not using Inheritance for Azureml class as while loading auto classes for `trust_remote_code=True` the 
# huggingface classes checks for the parent class name and they must be pre-defined Auto classes of transformers 
# library not any other unknown custom classes
class AzuremlAutoModelForSummarization(AzuremlAutoModelBase):

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> Tuple[PreTrainedModel, str, List[str]]:
        """Apply model specific hacks before calling the Base tokenizer"""

        # Initialize the config
        problem_type = kwargs.pop("problem_type", None)
        label2id = kwargs.pop("label2id", None)
        id2label = kwargs.pop("id2label", None)
        # not None for t5 models
        tok_prefix = kwargs.pop("tok_prefix", None)
        load_config_kwargs = kwargs.pop("load_config_kwargs", {})
        ignore_mismatched_sizes = kwargs.pop("ignore_mismatched_sizes", False)
        load_in_8bit = kwargs.pop("load_in_8bit", False)
        load_in_4bit = kwargs.pop("load_in_4bit", False)
        if load_in_8bit or load_in_4bit:
            # Setting device_map to None or {"": torch.cuda.current_device()} is trying to load
            # the model in GPU 0 always. To avoid that and load the model in all GPUs, :env
            # variable LOCAL_RANK is passed explicitly
            kwargs["device_map"] = {"": int(os.environ["LOCAL_RANK"])}
            logger.info(f'Setting the device map to use the current device GPU: {kwargs["device_map"]}')

        bnb_config = None
        if load_in_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )

        config_params = {
            "problem_type": problem_type,
            "id2label": id2label,
            "label2id": label2id,
            "output_attentions": False,
            "output_hidden_states": False,
            **load_config_kwargs,
        }

        if tok_prefix is not None:
            config_params["prefix"] = tok_prefix

        resume_from_checkpoint = kwargs.pop("resume_from_checkpoint", None)
        model_path = cls.get_model_path(hf_model_name_or_path, resume_from_checkpoint)
        logger.info(f"Loading config and model from: {model_path}")
        config = AzuremlAutoConfig.from_pretrained(model_path, **config_params)

        # Initialize the model
        model_type = AzuremlAutoConfig.get_model_type(config, **load_config_kwargs)
        model, model_loading_metadata = AutoModelForSeq2SeqLM.from_pretrained(
            model_path,
            config=config,
            quantization_config=bnb_config,
            ignore_mismatched_sizes=ignore_mismatched_sizes,
            output_loading_info=True,
            **kwargs,
        )

        # Update config and generation_config with task specific parameters
        task_specific_key = "summarization"
        cls.update_task_specific_params_to_config(task_specific_key, model)

        return model, model_type, model_loading_metadata["missing_keys"]


# not using Inheritance for Azureml class as while loading auto classes for `trust_remote_code=True` the 
# huggingface classes checks for the parent class name and they must be pre-defined Auto classes of transformers 
# library not any other unknown custom classes
class AzuremlAutoModelForTranslation(AzuremlAutoModelBase):

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> Tuple[PreTrainedModel, str, List[str]]:
        """Apply model specific hacks before calling the Base tokenizer"""

        # Initialize the config
        problem_type = kwargs.pop("problem_type", None)
        label2id = kwargs.pop("label2id", None)
        id2label = kwargs.pop("id2label", None)
        source_lang = kwargs.pop("source_lang", None)
        target_lang = kwargs.pop("target_lang", None)
        # not None for t5 models
        tok_prefix = kwargs.pop("tok_prefix", None)
        # not None for Mbart models
        decoder_start_token_id = kwargs.pop("decoder_start_token_id", None)
        load_config_kwargs = kwargs.pop("load_config_kwargs", {})
        ignore_mismatched_sizes = kwargs.pop("ignore_mismatched_sizes", False)
        load_in_8bit = kwargs.pop("load_in_8bit", False)
        load_in_4bit = kwargs.pop("load_in_4bit", False)
        if load_in_8bit or load_in_4bit:
            # Setting device_map to None or {"": torch.cuda.current_device()} is trying to load
            # the model in GPU 0 always. To avoid that and load the model in all GPUs, :env
            # variable LOCAL_RANK is passed explicitly
            kwargs["device_map"] = {"": int(os.environ["LOCAL_RANK"])}
            logger.info(f'Setting the device map to use the current device GPU: {kwargs["device_map"]}')

        bnb_config = None
        if load_in_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )

        config_params = {
            "problem_type": problem_type,
            "id2label": id2label,
            "label2id": label2id,
            "output_attentions": False,
            "output_hidden_states": False,
            **load_config_kwargs,
        }

        if tok_prefix is not None:
            config_params["prefix"] = tok_prefix
        if decoder_start_token_id is not None:
            config_params["decoder_start_token_id"] = decoder_start_token_id

        resume_from_checkpoint = kwargs.pop("resume_from_checkpoint", None)
        model_path = cls.get_model_path(hf_model_name_or_path, resume_from_checkpoint)
        logger.info(f"Loading config and model from: {model_path}")
        config = AzuremlAutoConfig.from_pretrained(model_path, **config_params)

        # Initialize the model
        model_type = AzuremlAutoConfig.get_model_type(config, **load_config_kwargs)
        model, model_loading_metadata = AutoModelForSeq2SeqLM.from_pretrained(
            model_path,
            config=config,
            quantization_config=bnb_config,
            ignore_mismatched_sizes=ignore_mismatched_sizes,
            output_loading_info=True,
            **kwargs,
        )

        # Update config and generation_config with task specific parameters
        task_specific_key = f"translation_{source_lang}_to_{target_lang}"
        cls.update_task_specific_params_to_config(task_specific_key, model)
        
        return model, model_type, model_loading_metadata["missing_keys"]


# not using Inheritance for Azureml class as while loading auto classes for `trust_remote_code=True` the 
# huggingface classes checks for the parent class name and they must be pre-defined Auto classes of transformers 
# library not any other unknown custom classes
class AzuremlAutoModelForQnA(AzuremlAutoModelBase):

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> Tuple[PreTrainedModel, str, List[str]]:
        """Apply model specific hacks before calling the Base tokenizer"""

        # Initialize the config
        problem_type = kwargs.pop("problem_type", None)
        # Extractive QnA predicts the start and end logits => number of labels to be 2
        # The class names is hardcoded here to allow finetuning models that were trained with classes != 2
        # Refer to this issue for more information https://github.com/huggingface/transformers/issues/22601
        num_labels = 2
        load_config_kwargs = kwargs.pop("load_config_kwargs", {})
        ignore_mismatched_sizes = kwargs.pop("ignore_mismatched_sizes", False)
        load_in_8bit = kwargs.pop("load_in_8bit", False)
        load_in_4bit = kwargs.pop("load_in_4bit", False)
        if load_in_8bit or load_in_4bit:
            # Setting device_map to None or {"": torch.cuda.current_device()} is trying to load
            # the model in GPU 0 always. To avoid that and load the model in all GPUs, :env
            # variable LOCAL_RANK is passed explicitly
            kwargs["device_map"] = {"": int(os.environ["LOCAL_RANK"])}
            logger.info(f'Setting the device map to use the current device GPU: {kwargs["device_map"]}')
        bnb_config = None
        if load_in_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )

        resume_from_checkpoint = kwargs.pop("resume_from_checkpoint", None)
        model_path = cls.get_model_path(hf_model_name_or_path, resume_from_checkpoint)
        logger.info(f"Loading config and model from: {model_path}")
        config = AzuremlAutoConfig.from_pretrained(
            model_path,
            problem_type=problem_type,
            num_labels=num_labels,
            output_attentions=False,
            output_hidden_states=False,
            **load_config_kwargs,
        )

        # Initialize the model
        model_type = AzuremlAutoConfig.get_model_type(config, **load_config_kwargs)
        model, model_loading_metadata = AutoModelForQuestionAnswering.from_pretrained(
            model_path,
            config=config,
            ignore_mismatched_sizes=ignore_mismatched_sizes,
            quantization_config=bnb_config,
            output_loading_info=True,
            **kwargs,
        )
        return model, model_type, model_loading_metadata["missing_keys"]


# not using Inheritance for Azureml class as while loading auto classes for `trust_remote_code=True` the 
# huggingface classes checks for the parent class name and they must be pre-defined Auto classes of transformers 
# library not any other unknown custom classes
class AzuremlAutoModelForCausalLM(AzuremlAutoModelBase):

    @classmethod
    def from_pretrained(cls, hf_model_name_or_path: str, **kwargs) -> Tuple[PreTrainedModel, str, List[str]]:
        """Apply model specific hacks before calling the Base tokenizer"""

        # Initialize the config
        problem_type = kwargs.pop("problem_type", None)
        load_config_kwargs = kwargs.pop("load_config_kwargs", {})
        ignore_mismatched_sizes = kwargs.pop("ignore_mismatched_sizes", False)
        load_in_8bit = kwargs.pop("load_in_8bit", False)
        load_in_4bit = kwargs.pop("load_in_4bit", False)
        # use_flash_attention_2 support is deprecated in latest transformers
        if "use_flash_attention_2" in kwargs:
            del kwargs["use_flash_attention_2"]
        # Initialize the model
        resume_from_checkpoint = kwargs.pop("resume_from_checkpoint", None)
        model_path = cls.get_model_path(hf_model_name_or_path, resume_from_checkpoint)
        logger.info(f"Loading config and model from: {model_path}")
        config = AzuremlAutoConfig.from_pretrained(
            model_path,
            problem_type=problem_type,
            output_attentions=False,
            output_hidden_states=False,
            **load_config_kwargs,
        )
        model_type = AzuremlAutoConfig.get_model_type(config, **load_config_kwargs)

        if load_in_8bit or load_in_4bit:
            # Setting device_map to None or {"": torch.cuda.current_device()} is trying to load
            # the model in GPU 0 always. To avoid that and load the model in all GPUs, :env
            # variable LOCAL_RANK is passed explicitly
            kwargs["device_map"] = {"": int(os.environ["LOCAL_RANK"])}
            logger.info(f'Setting the device map to use the current device GPU: {kwargs["device_map"]}')
        bnb_config = None
        if load_in_4bit:
            if (config.model_type == GPT_OSS):
                from transformers import Mxfp4Config
                logger.info("Using Mxfp4Config for GPT-OSS model in 4-bit mode")
                bnb_config = Mxfp4Config(dequantize=True)
                kwargs["attn_implementation"] = "eager"

            else:
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_compute_dtype=(
                        torch.bfloat16
                        if torch.cuda.is_bf16_supported() else
                        torch.float16
                    ),
                )


        if (config.model_type == LLAMA_4):
            auto_class = Llama4ForConditionalGeneration
        else:
            auto_class = AutoModelForCausalLM

        model, model_loading_metadata = auto_class.from_pretrained(
            model_path,
            config=config,
            quantization_config=bnb_config,
            ignore_mismatched_sizes=ignore_mismatched_sizes,
            output_loading_info=True,
            **kwargs,
        )
        return model, model_type, model_loading_metadata["missing_keys"]
