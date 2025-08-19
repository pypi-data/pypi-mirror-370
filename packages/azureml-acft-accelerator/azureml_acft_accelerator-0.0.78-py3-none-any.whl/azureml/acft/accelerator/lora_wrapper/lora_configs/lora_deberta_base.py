# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Lora params for deberta_base
"""

from collections import OrderedDict

LORA_PARAMS = OrderedDict(
    [
        ["lora_layer", "MergedLinear"],
        ["layers_to_modify", ["in_proj"]],
        ["transformer_block_name_prefix", "in_proj"],
    ]
)


class LORA_DEBERTA_BASE:
    """
    Class for defining Lora Params for bert_base_uncased
    """

    # TODO Warp the lora_r, alpha and dropout into a dataclass
    def __init__(self, lora_r, lora_alpha, lora_dropout, merge_weights):
        """
        initializing lora params
        """

        LORA_PARAMS["r"] = lora_r
        LORA_PARAMS["lora_alpha"] = lora_alpha
        LORA_PARAMS["lora_dropout"] = lora_dropout
        LORA_PARAMS["merge_weights"] = merge_weights
        LORA_PARAMS["fan_in_fan_out"] = False
        LORA_PARAMS["bias"] = False
        LORA_PARAMS["enable_lora"] = [True, False, True]

    def get_lora_parameters(self):
        """
        returns lora parameters
        """

        return LORA_PARAMS
