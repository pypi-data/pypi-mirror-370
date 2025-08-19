# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Lora params for llama"""

from .lora_base import BaseLora, LoraBlockConstants, LoraLayerConstants
from typing import Dict, Any


class LoraLlama(BaseLora):
    """
    Class for defining Lora Params for gpt2
    """

    # TODO Warp the lora_r, alpha and dropout into a dataclass
    def __init__(self, lora_r, lora_alpha, lora_dropout, merge_weights):
        """initializing lora params"""

        super().__init__(lora_r, lora_alpha, lora_dropout, merge_weights)

    def get_lora_blocks_meta_data(self) -> Dict[str, Any]:
        """lora block meta data"""
        return {
            "self_attn": {
                LoraBlockConstants.LayersToModify: ["q_proj", "v_proj"],
                LoraBlockConstants.LoraLayer: "Linear"
            },
        }
