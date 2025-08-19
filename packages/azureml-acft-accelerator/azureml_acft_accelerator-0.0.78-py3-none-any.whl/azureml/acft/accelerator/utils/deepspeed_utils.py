# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This file contains utilty functions for Deepspeed Training
"""

from inspect import getmodule
from typing import List

from transformers.modeling_utils import PreTrainedModel

from deepspeed.utils import set_z3_leaf_modules

from azureml.acft.common_components import get_logger_app


logger = get_logger_app(__name__)


def set_z3_leaf_modules_for_moe_models(model: PreTrainedModel, list_of_moe_layers: List[str]):
    """Sets a flag within a module in `model` to instruct ZeRO3 to stop setting hooks recursively
       when it encounters a module class listed in `list_of_moe_layers`.
       This is particularly useful in the context of Mixture of Experts (MoE) models.
       In MoE models, the computation order of experts varies across forward passes.
       This variability can disrupt ZeRO3's functionality, as ZeRO3 relies on tracking the
       computation order of modules to prefetch parameters efficiently.
       By designating a module as a 'leaf' node, ZeRO3 will prefetch parameters for all child modules
       upon entering the module.
       source - https://github.com/microsoft/DeepSpeed/pull/4966
    """
    if list_of_moe_layers is None or len(list_of_moe_layers) == 0:
        logger.info("No MoE layers are passed for setting `_z3_leaf=True`.")
        return
    logger.info(f"Setting leaf modules for MoE model - {model.__class__}.")
    leaf_modules_of_moe_models = []
    modeling_module = getmodule(model)
    logger.info(f"Modeling module - {modeling_module}")
    # convert strings to respective module classes
    for module in list_of_moe_layers:
        leaf_modules_of_moe_models.append(getattr(modeling_module, module))
    # set z3 leaf modules
    set_z3_leaf_modules(model, leaf_modules_of_moe_models)
    logger.info(f"Setting `_z3_leaf=True` for MoE layers - {leaf_modules_of_moe_models}")
