# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Lora params for falcon"""

from .lora_base import BaseLora, LoraBlockConstants, LoraLayerConstants
from typing import Dict, Any


class LoraFalcon(BaseLora):
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
            "self_attention": {
                LoraBlockConstants.LayersToModify: ["query_key_value"],
                LoraBlockConstants.LoraLayer: "Linear"
            },
        }
