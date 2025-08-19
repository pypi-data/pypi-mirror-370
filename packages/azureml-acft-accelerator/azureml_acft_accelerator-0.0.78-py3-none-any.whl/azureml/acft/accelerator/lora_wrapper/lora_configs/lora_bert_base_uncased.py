# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Lora params for bert_base_uncased
"""

from collections import OrderedDict

LORA_PARAMS = OrderedDict(
    [
        ["lora_layer", "Linear"],
        ["layers_to_modify", ["query", "value"]],
        ["transformer_block_name_prefix", "attention.self"],
    ]
)


class LORA_BERT_BASE_UNCASED:
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

    def get_lora_parameters(self):
        """
        returns lora parameters
        """

        return LORA_PARAMS
