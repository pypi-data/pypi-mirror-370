# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
File Containing Functions for Lora Wrapper
"""

from typing import List, Tuple, Union, Optional

import traceback
from collections import OrderedDict

from . import lora_configs
from . import lora_layers as lora
from azureml.acft.common_components import get_logger_app
from ..constants import AzuremlConstants, HfModelTypes
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
from azureml.acft.common_components.utils.error_handling.error_definitions import ACFTUserError
from azureml._common._error_definition.azureml_error import AzureMLError  # type: ignore


logger = get_logger_app(__name__)

# TODO Move to file
# Store `model_type` as the key
LORA_CONFIG_MAP = OrderedDict(
    [
        [HfModelTypes.GPT2, "LoraGpt2"],
        [HfModelTypes.BERT, "LoraBert"],
        [HfModelTypes.ROBERTA, "LoraRoberta"],
        [HfModelTypes.DEBERTA, "LoraDeberta"],
        [HfModelTypes.DISTILBERT, "LoraDistilbert"],
        [HfModelTypes.T5, "LoraT5"],
        [HfModelTypes.BART, "LoraBart"],
        [HfModelTypes.MBART, "LoraMbart"],
        [HfModelTypes.CAMEMBERT, "LoraCamembert"],
        [HfModelTypes.GPT_NEOX, "LoraGptNeoX"],
        [HfModelTypes.LLAMA, "LoraLlama"],
        [HfModelTypes.FALCON, "LoraFalcon"],
        [HfModelTypes.REFINEDWEBMODEL, "LoraFalcon"],
    ]
)


class LoraWrapper:
    """
    LoRA Wrapper class used to integrarte lora in training
    """

    def __init__(
        self,
        hf_model_type: str,
        newly_initialized_params: Optional[List[str]] = None,
        lora_r: int = 8,
        lora_alpha: int = 128,
        lora_dropout: float = 0.0,
        merge_weights: bool = True,
        lora_weights_merged_with_base_model: bool = True,
    ):
        """
        hf_model_type - bert_base_uncased and bert_base_cased both belong to model_type bert
        newly_initialized_parameters - set of parameters that are newly initialized, i.e. in case of lora
            only the newly initialized parameters will be set to trainable
        lora_r - the dimension to which the weight matrix is down projected to
            In case of Linear layer, say the weight (W) dimension is m x n, the lora decomposes W to matrices B and A
            such that W = BA with B having dimensions m x lora_r and A having dimensions lora_r x n
        lora_alpha - scaling parameter based on which the lora weights are updated
        merge_weights
            - If set to true, calling the `eval` method will merge the lora layers to the base model weights
            - Based on this flag, the forward will either merge the weights or ignore them
            For linear layer, mathematically merging the weights back to W => W = W + BA, the B and A are called as
            lora_B and lora_A
        lora_weights_merged_with_base_model
            During the start of training or whenever the .train() method is called with
            lora_weights_merged_with_base_model and merge_weights are set to True, the weights and lora layers will get
            unmerged so that the training resumes from the checkpoints last saved model weights
            unmerging => W = W - BA
        """

        if hf_model_type not in LORA_CONFIG_MAP:
            raise ACFTValidationException._with_error(
            AzureMLError.create(
                ACFTUserError,
                pii_safe_message=(
                    f"Lora is not supported for {hf_model_type}. "
                    f"List of supported model_types with Lora: {list(LORA_CONFIG_MAP.keys())}"
                )
            )
        )

        # get lora parameters
        lora_config_obj = getattr(lora_configs, LORA_CONFIG_MAP[hf_model_type])(
            lora_r, lora_alpha, lora_dropout, merge_weights)
        self.lora_params = lora_config_obj.get_lora_parameters()
        self.lora_weights_merged_with_base_model = lora_weights_merged_with_base_model

        # remaining parameters for lora block
        self.lora_blocks_meta_data = lora_config_obj.get_lora_blocks_meta_data()

        # newly initialized parameters
        self.newly_initialized_params = (newly_initialized_params or []) + ["lora"]
        logger.info(f"Newly initialized params: {self.newly_initialized_params}")

    def identify_for_lora_block(self, block_name: str) -> Tuple[bool, Union[str, None]]:
        if_lora_block, lora_block = False, None
        for search_pattern in self.lora_blocks_meta_data:
            if search_pattern in block_name:
                if_lora_block = True
                lora_block = search_pattern
                break

        return if_lora_block, lora_block

    def update_attention_block_with_lora_layers(self, model):
        """
        Assumption
        ==========
        - attention module has query and value attributes
        - query and value blocks are replaced with lora.Linear block
        """
        updated_block_names = set()
        for name, _ in list(model.named_parameters()):
            if_lora_block, lora_block = self.identify_for_lora_block(name)
            if if_lora_block:
                layers_to_modify = self.lora_blocks_meta_data[lora_block]["layers_to_modify"]
                lora_layer = getattr(lora, self.lora_blocks_meta_data[lora_block]["lora_layer"])
                try:
                    block_name = ".".join(name.split(".")[:-2])
                    if block_name in updated_block_names:
                        continue
                    updated_block_names.add(block_name)
                    transformer_block = model.get_submodule(block_name)  # id remains the same
                    # logger.info(f"Working on transformer block: {transformer_block}")
                    for layer_to_modify in layers_to_modify:
                        curr_layer = getattr(transformer_block, layer_to_modify)
                        in_feat_dim, out_feat_dim = (
                            curr_layer.weight.shape[1],
                            curr_layer.weight.shape[0],
                        )
                        if self.lora_params.get("fan_in_fan_out", False):
                            in_feat_dim, out_feat_dim = (
                                out_feat_dim,
                                in_feat_dim,
                            )
                        # logger.info(
                        #     f"Curr layer: {curr_layer}, {in_feat_dim}, {out_feat_dim}"
                        # )
                        new_layer = lora_layer(in_feat_dim, out_feat_dim, **self.lora_params)
                        new_layer.merged = self.lora_weights_merged_with_base_model  # used for unmerging the weights
                        # logger.info(f"New layer: {new_layer}")
                        new_layer.weight.data = curr_layer.weight.data  # copying the pretrained weights
                        setattr(
                            transformer_block, layer_to_modify, new_layer
                        )  # replacing the curr layer with lora layer
                        logger.info(
                            f"Name: {name} | Block: {block_name} | Existing layer: {curr_layer} | New layer: {new_layer}"
                        )
                except Exception as exp:
                    logger.info(f"Failed to get block for {name}. Ignoring this block - {exp}")
                    logger.info(traceback.format_exc())

        return model

    def set_trainable_parameters(self, model):
        """
        Used only with lora modules fine-tuning
        - mark lora layers as trainable
        - mark the newly initailized parameters trainable
        """
        for name, param in model.named_parameters():
            # By default all the parameters are trainable
            for new_name in self.newly_initialized_params:
                if new_name in name:
                    param.requires_grad = True
                    break
                else:
                    param.requires_grad = False

        return model

    def merge_lora_layers(
      self, model, lora_layer_search_strings: List[str] = AzuremlConstants.LORA_LAYER_SEARCH_STRINGS):
        """
        Loosely speaking, each lora layer has a weight, lora_a, lora_b layer.
        This function merges the lora layers weights using the formula
            `weight.data += (lora_b @ lora_a) * scaling`
        This is implemented in the lora layers eval method. we will just invoke that

        NOTE We call the eval function only for the lora layers so that the other layers
        remain untouched
        """
        merged_module_strings = set()
        for name, _ in model.named_parameters():
            # example model parameter name - bert.encoder.layer.9.attention.self.key.weight
            sub_module_string = ".".join(name.split(".")[:-1])
            if sub_module_string in merged_module_strings:  # skipping the already processed module
                continue
            if any([name.endswith(search_str) for search_str in lora_layer_search_strings]):  # lora layer
                merged_module_strings.update([sub_module_string])
                submodule = model.get_submodule(sub_module_string)
                if isinstance(submodule, lora.LoRALayer):
                    submodule.eval()
                else:
                    logger.warning(
                        f"Found a submodule {sub_module_string} not of lora type."
                        "skipping the merge weights for the module"
                    )

        return model

    def get_lora_layers_state_dict(
      self, model, lora_layer_search_strings: List[str] = AzuremlConstants.LORA_LAYER_SEARCH_STRINGS):
        """
        This function identifies the lora layers and returns the state_dict of the same
        """
        lora_layers_state_dict = {}
        for name, param in model.named_parameters():
            if any([name.endswith(search_str) for search_str in lora_layer_search_strings]):  # lora layer
                lora_layers_state_dict[name] = param.detach()   # param.detach() won't work for CPU training

        return lora_layers_state_dict
