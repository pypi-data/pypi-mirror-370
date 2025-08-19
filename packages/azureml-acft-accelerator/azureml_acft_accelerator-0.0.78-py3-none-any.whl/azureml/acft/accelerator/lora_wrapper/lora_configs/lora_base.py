# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABC
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class LoraLayerConstants:
    R = "r"
    Alpha = "lora_alpha"
    DropOut = "lora_dropout"
    MergeWeights = "merge_weights"
    FanInFanOut = "fan_in_fan_out"
    EnableLora = "enable_lora"


@dataclass
class LoraBlockConstants:
    LayersToModify = "layers_to_modify"
    LoraLayer = "lora_layer"


class BaseLora(ABC):
    def __init__(self, lora_r, lora_alpha, lora_dropout, merge_weights):
        """initializing lora params"""
        self.lora_params = {}
        self.lora_params[LoraLayerConstants.R] = lora_r
        self.lora_params[LoraLayerConstants.Alpha] = lora_alpha
        self.lora_params[LoraLayerConstants.DropOut] = lora_dropout
        self.lora_params[LoraLayerConstants.MergeWeights] = merge_weights
        self.lora_params[LoraLayerConstants.FanInFanOut] = False

    def get_lora_parameters(self) -> Dict[str, Any]:
        """Get the lora paramters such as r, alpha, dropout etc"""
        return self.lora_params

    def get_lora_blocks_meta_data(self) -> Dict[str, Any]:
        """Define the mapping of transformer block to lora layer"""
        pass
