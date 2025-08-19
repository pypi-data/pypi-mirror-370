# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Config file used for logging
"""


class Config:
    """
    config class
    """

    MAX_RETRIES = 3
    FINETUNE_APP_NAME = "Generic FT"
    PREPROCESS_APP_NAME = "preprocess"
    MODEL_SELECTOR_APP_NAME = "model_selector"
    VERBOSITY_LEVEL = "DEBUG"
    APP_INSIGHT_HANDLER_NAME = "AppInsightsHandler"
    AMLFT_HANDLER_NAME = "AmlFtHandlerName"
    LOGGER_NAME = "generic_finetune_component"
    HF_LOGS_TO_APP_INSIGHT = True
    INSTRUMENTATION_KEY_AML = "7b709447-0334-471a-9648-30349a41b45c"
    INSTRUMENTATION_KEY_AML_OLD = "71b954a8-6b7d-43f5-986c-3d3a6605d803"
    OFFLINE_RUN_MESSAGE = "This is an offline run"
