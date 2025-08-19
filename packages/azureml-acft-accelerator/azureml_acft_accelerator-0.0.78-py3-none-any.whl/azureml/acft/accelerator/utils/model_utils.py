# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This file contains utility functions for model
"""

from typing import Union, Tuple, Optional, List

import torch.nn as nn

from transformers import PreTrainedModel

from ..lora_wrapper.lora_wrapper import LoraWrapper
from ..constants import _AzuremlOptimizationArgs, AzuremlConstants

from azureml._common._error_definition.azureml_error import AzureMLError

from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.utils.error_handling.swallow_all_exceptions_decorator import (
    swallow_all_exceptions
)


logger = get_logger_app(__name__)


def add_lora_layers_to_model(
    model: Union[nn.Module, PreTrainedModel],
    unmerge_weights: bool,
    optimizer_args: _AzuremlOptimizationArgs,
    new_initialized_layers: Optional[List[str]] = None,
) -> Tuple[Union[nn.Module, PreTrainedModel], Optional[LoraWrapper]]:
    """
    :param model
        Base model of any framework HuggingFace, MMAction
    :param unmerge_weights
        Unmerges the base weights and lora layers to resume training from last train state. In case of continual finetune,
        the base weights are subtracted from lora weights to arrive at the last train state
    :param optimizer_args
        LoRA args
    :param new_initialized_layers
        List of newly initialized layers. During finetune with lora, ONLY lora layers and newly initialized layers are
        trained and `gradient_update` for rest of the layers is set to False
    """
    lora_wrapper_obj = LoraWrapper(
        hf_model_type=optimizer_args.model_type,
        newly_initialized_params=new_initialized_layers,
        lora_r=optimizer_args.lora_r,
        lora_alpha=optimizer_args.lora_alpha,
        lora_dropout=optimizer_args.lora_dropout,
        lora_weights_merged_with_base_model=unmerge_weights,
    )
    model = lora_wrapper_obj.update_attention_block_with_lora_layers(model)
    model = lora_wrapper_obj.set_trainable_parameters(model)

    return model, lora_wrapper_obj


@swallow_all_exceptions(time_delay=60)
def print_model_summary(model, print_params=False):
    """
    prints the model summary
    """
    model_param_train_info = []
    total_params, trainable_params = 0, 0
    prefix_for_grad, prefix_for_no_grad = "+" * 10, " " * 10
    for name, param in model.named_parameters():
        if print_params:
            total_params += param.numel()
            if param.requires_grad:
                trainable_params += param.numel()
                model_param_train_info.append(f"{prefix_for_grad} {param.device} {param.dtype} {name}")
            else:
                model_param_train_info.append(f"{prefix_for_no_grad} {param.device} {param.dtype} {name}")
        else:
            model_param_train_info.append(name)

    model_param_train_info_str = "\n".join(model_param_train_info)
    logger.info(model_param_train_info_str)
    if print_params:
        logger.info(f"Total model parameters: {total_params}")
        logger.info(f"Total trainable parameters: {trainable_params}")


@swallow_all_exceptions(time_delay=60)
def print_model_weights_top_n_layers(model, n=-1):
    """
    Prints model weights for top n layers.
    If n == -1 prints all layer weights
    """
    layer_count = 0
    check_layer = True
    if n == -1: check_layer = False
    for name, param in model.named_parameters():
        logger.info(name)
        logger.info(param.data)
        layer_count += 1
        if check_layer and layer_count >= n:
            break
