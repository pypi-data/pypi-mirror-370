# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import shutil
from pathlib import Path
from typing import Optional, List

import torch

import peft
from peft import get_peft_model, LoraConfig, prepare_model_for_kbit_training

from transformers.modeling_utils import PreTrainedModel

from azureml.acft.common_components import get_logger_app

from ..constants import AzuremlConstants
from ..utils.model_utils import print_model_summary


logger = get_logger_app(__name__)


class PeftLoraWrapper:

    def __init__(
        self,
        model: PreTrainedModel,
        model_name_or_path: str,
        peft_task_type: str,
        newly_initialized_layers: Optional[List[str]] = None,
        lora_r: int = 8,
        lora_alpha: int = 128,
        lora_dropout: float = 0.0,
        finetune_in_8bit: bool = False,
        finetune_in_4bit: bool = False,
        target_modules: Optional[List[str]] = None,
        target_parameters: Optional[List[str]] = None,
    ) -> None:
        """
        :param model: HuggingFace PreTrainedModel
        :type model: PreTrainedModel
        :param model_name_or_path: ModelName or path to the model folder from which the model is loaded.
            This is useful to save the model in case of 4bit / 8bit training
        :type model_name_or_path: str
        :param peft_task_type: The task type based on which the peft auto class is selected.
            For example, if the finetune needs to be done for SequenceClassification, the
            peft_task_type is SEQ_CLS
        :type peft_task_type: str
        :param newly_initialized_layers: model layers that are newly initialized or nor present in the model
            checkpoint. The new layers will be made trainable in case of LoRA finetune
        :type newly_initialized_layers: Optional[List[str]]
        :param lora_r: The rank of the lower dimension to which the Linear Layer weights are projected to.
            Let's say the linear layer weight matrix, W, has dimension m x n, the lora decomposes W to matrices B and A
            such that W = BA with B having dimensions m x lora_r and A having dimensions lora_r x n
        :type lora_r: int
        :param lora_alpha: scaling parameter based on which the lora weights are updated
        :type lora_alpha: int
        :param lora_dropout: lora drop out parameter
        :type lora_dropout: float
        :param finetune_in_8bit: A boolean value if set to true enables QLoRA(8bit) finetune
        :type finetune_in_8bit: bool
        :param finetune_in_4bit: A boolean value if set to true enables QLoRA(4bit) finetune
        :type finetune_in_4bit: bool
        :param target_modules: "List of module names or regex expression of the module names to replace with Lora."
            "For example, ['q', 'v'] or '.*decoder.*(SelfAttention|EncDecAttention).*(q|v)$' ". For few model families,
            this information is already a part of mapping TRANSFORMERS_MODELS_TO_LORA_TARGET_MODULES_MAPPING in the pkg
        :type target_modules: Optional[List[str]]
        :param target_parameters: List of expert-specific layers (MOE)
        :type target_parameters: Optional[List[str]]
        """
        self.model = model
        self.model_name_or_path = model_name_or_path
        self.lora_config = self._get_lora_config(
            lora_r=lora_r, lora_alpha=lora_alpha, lora_dropout=lora_dropout,
            newly_initialized_layers=newly_initialized_layers,
            peft_task_type=peft_task_type, target_modules=target_modules,
            target_parameters=target_parameters,
        )
        self.finetune_in_kbit = finetune_in_8bit or finetune_in_4bit
        self.finetune_in_4bit = finetune_in_4bit
        self.newly_initialized_layers = newly_initialized_layers

        self.__post_init__()

    def __post_init__(self):

        # base model save path
        if self.finetune_in_kbit:
            self.base_model_save_path = AzuremlConstants.BASE_WEIGHTS_FOLDER

    def _is_zero_local_rank_process(self):
        # XXX This is a redundant function already part of torch.dist and HF Trainer. Will remove in the future

        return os.environ["LOCAL_RANK"] == '0'

    def _get_local_rank(self):
        # XXX This is a redundant function already part of torch.dist and HF Trainer. Will remove in the future

        return os.environ["LOCAL_RANK"]

    def _get_lora_config(
        self,
        lora_r: int,
        lora_alpha: int,
        lora_dropout: float,
        peft_task_type: str,
        newly_initialized_layers: Optional[List[str]] = None,
        target_modules: Optional[List[str]] = None,
        target_parameters: Optional[List[str]] = None,
        
    ) -> LoraConfig:
        """Construct the peft config based on the lora parameters and new initialized layers.

        :param lora_r: The rank of the lower dimension to which the Linear Layer weights are projected to.
            Let's say the linear layer weight matrix, W, has dimension m x n, the lora decomposes W to matrices B and A
            such that W = BA with B having dimensions m x lora_r and A having dimensions lora_r x n
        :type lora_r: int
        :param lora_alpha: scaling parameter based on which the lora weights are updated
        :type lora_alpha: int
        :param lora_dropout: lora drop out parameter
        :type lora_dropout: float
        :param peft_task_type: The task type based on which the peft auto class is selected.
            For example, if the finetune needs to be done for SequenceClassification, the
            peft_task_type is SEQ_CLS
        :type peft_task_type: str
        :param newly_initialized_layers: model layers that are newly initialized or nor present in the model
            checkpoint. The new layers will be made trainable in case of LoRA finetune
        :type newly_initialized_layers: Optional[List[str]]
        :param target_modules: "List of module names or regex expression of the module names to replace with Lora."
            "For example, ['q', 'v'] or '.*decoder.*(SelfAttention|EncDecAttention).*(q|v)$' ". For few model families,
            this information is already a part of mapping TRANSFORMERS_MODELS_TO_LORA_TARGET_MODULES_MAPPING in the pkg
        :type target_modules: Optional[List[str]]
        :param target_parameters: List of expert-specific layers (MOE)
        :type target_parameters: Optional[List[str]]
        :return: lora config
        :rtype: peft.LoraConfig

        NOTE Use target_modules if the lora target modules are not specified in the map
        TRANSFORMERS_MODELS_TO_LORA_TARGET_MODULES_MAPPING
        """

        # calculate new initialized modules from new initialized layers
        new_initialized_modules = None
        if newly_initialized_layers is not None:
            new_initialized_modules = list(
                set(
                    [".".join(layer.split(".")[:-1]) for layer in newly_initialized_layers]
                )
            )
        logger.info(f"Newly initialized modules: {new_initialized_modules}")

        if target_modules is None:
            logger.info("Target modules are not set. Please check if the trainable layers are as expected")
        # TODO Check if peft task type can be auto computed
        lora_config = LoraConfig(
            task_type=peft_task_type,
            inference_mode=False,
            r=lora_r,
            lora_alpha=lora_alpha,
            lora_dropout=lora_dropout,
            modules_to_save=new_initialized_modules,
            target_modules=target_modules,
            target_parameters=target_parameters,
        )
        logger.info(f"PEFT lora config: {lora_config}")

        return lora_config

    def peft_model_init(self):
        """Add the lora weights and initialize the model"""
        if self.finetune_in_kbit:
            if self._is_zero_local_rank_process():
                logger.info(f'Saving the base model in rank: {self._get_local_rank()}')
                # Read the :func `_save_base_model` description to understand why base model is getting saved
                self._save_base_model()

            logger.info(f"Preparing the model for {4 if self.finetune_in_4bit else 8}bit training")
            self.model = prepare_model_for_kbit_training(self.model, use_gradient_checkpointing=False)

        self.model = get_peft_model(self.model, self.lora_config)

    def _save_base_model(self):
        """
        Save a copy of the base model. This is needed while merging the weights for quantized finetuning. 8bit / 4bit.

        The base model could differ from the actual loaded model because of the head that gets attached to the base
        model. For example, the base model in case of SequenceClassification adds 2 classes in the head by default
        while the actual model could contain more than 2 classes. This difference will lead to errors while loading
        the adapter weights before merging the model.

        If there are no differences b/w the pretrained model and the actual loaded model as mentioned in the
        :param self.newly_initialized_layers, we won't save the base model
        """

        if self.finetune_in_kbit and self.newly_initialized_layers:

            # NOTE This snippet of code might be helpful in the immediate release. Otherwise, will delete it in next PR
            # if not self.finetune_in_4bit:  # 8bit finetune
            #     logger.info(
            #         f"Saving the initial base model weights to "
            #         f"{self.base_model_save_path}. This is useful while merging the weights post finetuning."
            #     )
            #     quantization_config = getattr(self.model.config, "quantization_config", None)
            #     if quantization_config is not None:
            #         delattr(self.model.config, "quantization_config")
            #     self.model.save_pretrained(self.base_model_save_path)
            #     self.model.__dict__["name_or_path"] = self.base_model_save_path
            #     if quantization_config is not None:
            #         setattr(self.model.config, "quantization_config", quantization_config)

            if Path(self.model_name_or_path).is_dir:  # 4bit or 8bit finetune
                logger.info(
                    f"Copying the initial base model weights from {self.model_name_or_path} to "
                    f"{self.base_model_save_path}. This is useful while merging the weights post finetuning."
                )
                shutil.copytree(self.model_name_or_path, self.base_model_save_path, dirs_exist_ok=True)

                # saving the custom config
                logger.info("Saving the custom config")
                quantization_config = getattr(self.model.config, "quantization_config", None)
                pre_quantization_dtype = getattr(self.model.config, "_pre_quantization_dtype", None)
                if quantization_config is not None:
                    # The :attr quantization_config is set when loading the model in 4bit / 8bit
                    # But since merging is not supported for 4bit / 8bit, we don't load the model
                    # with quantization config
                    delattr(self.model.config, "quantization_config")
                    # Additionally delete `_pre_quantization_dtype`
                    # The value is a `torch.dtype` and is not a json serializable object
                    # which causes issues when trying to save model.config
                    if hasattr(self.model.config, "_pre_quantization_dtype"):
                        delattr(self.model.config, "_pre_quantization_dtype")
                self.model.config.save_pretrained(self.base_model_save_path)
                self.model.__dict__["name_or_path"] = self.base_model_save_path
                if quantization_config is not None:
                    setattr(self.model.config, "quantization_config", quantization_config)
                    # Setting back `_pre_quantization_dtype` as it is used in model forward for 
                    # autocasting in FlashAttention2 implementation.
                    if pre_quantization_dtype is not None:
                        setattr(self.model.config, "_pre_quantization_dtype", pre_quantization_dtype)

            else:
                raise ValueError("Cannot save the base model!")

        else:
            logger.info("Base model saving is not required!")

    def peft_model_merge(self):

        if self.finetune_in_kbit:
            # save the adapter weights
            logger.info(f"Saving the adapter weights to {AzuremlConstants.LORA_BASE_FOLDER}")
            self.model.save_pretrained(AzuremlConstants.LORA_BASE_FOLDER)  # only the lora weights will be saved

            auto_cls = getattr(peft, f"Auto{self.model.__class__.__name__}")
            logger.info(f"Identified auto cls: {auto_cls}")
            self.model = auto_cls.from_pretrained(
                AzuremlConstants.LORA_BASE_FOLDER,
                low_cpu_mem_usage=True,
                torch_dtype=torch.float32,
            )  # loads both base weights and lora weights

        # Merge LoRA weights with base model weights
        logger.info("merging the lora weights with base model weights")
        self.model = self.model.merge_and_unload()
