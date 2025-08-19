# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Lora params for deberta family models"""

from .lora_base import BaseLora, LoraBlockConstants, LoraLayerConstants
from typing import Dict, Any


class LoraDeberta(BaseLora):
    """Class for defining Lora Params for deberta models"""

    # TODO Warp the lora_r, alpha and dropout into a dataclass
    def __init__(self, lora_r, lora_alpha, lora_dropout, merge_weights):
        """initializing lora params"""
        super().__init__(lora_r, lora_alpha, lora_dropout, merge_weights)

    def get_lora_parameters(self) -> Dict[str, Any]:
        lora_parameters = super().get_lora_parameters()
        lora_parameters[LoraLayerConstants.EnableLora] = [True, False, True]

        return lora_parameters

    def get_lora_blocks_meta_data(self) -> Dict[str, Any]:
        """lora block meta data"""
        return {
            "in_proj": {
                LoraBlockConstants.LayersToModify: ["in_proj"],
                LoraBlockConstants.LoraLayer: "MergedLinear"
            },
        }
