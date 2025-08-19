# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------

"""
This file defines the util functions used for logging.
It also filters unwanted logs from dependent packages like transformers
"""

import logging
import transformers
import datasets

try:
    from deepspeed.utils import logger as deepspeed_logger
except ImportError:
    deepspeed_logger = None

try:
    from optimum.utils import logging as optimum_logging
except ImportError:
    optimum_logging = None

import uuid

from . import run_utils
from .config import Config
from azureml.telemetry import get_telemetry_log_handler
from azureml.automl.core.shared.telemetry_formatter import (
    AppInsightsPIIStrippingFormatter
)
from applicationinsights.channel.contracts import MessageData
from applicationinsights.channel import TelemetryContext

# Logs with following string in them will not be sent to appinsights
LOGS_TO_BE_FILTERED_APPINSIGHTS = [
    "Dataset columns after pruning",
    "loading configuration file",
    "Model config",
    "loading file",
    "Namespace(",
    "output type to python objects for",
    "Class Names:",
    "Class names : ",
    "Metrics calculator:",
    "The following columns in the training set",
    # validation filter strings
    "Dataset Columns: ",
    "Data formating",
    "dtype mismatch for feature",
    "Removing label_column"
    "Removed columns:"
    "Component Args:"
    "Using client id:"
]

# Logs with following string in them will not be sent to stream
LOGS_TO_BE_FILTERED_STREAM = [
    "Training completed. Do not forget to share your model on",
]


def _get_custom_dimension():
    """
    gets custom dimensions like subscition_id, workspace name, region, etc. used by the logger
    :return dictionary containing the custom dimensions
    """

    custom_dim = {
        "sub_id": run_utils._get_sub_id(),
        "ws_name": run_utils._get_ws_name(),
        "region": run_utils._get_region(),
        "run_id": run_utils._get_run_id(),
        "compute_target_name": run_utils._get_compute(),
        "compute_target_type": run_utils._get_compute_vm_size(),
    }
    return custom_dim


class GllmHandler(logging.StreamHandler):
    """
    GLLM Handler class extended from logging.StreamHandler, used as handler for the logger
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emits logs to stream after adding custom dimensions
        """

        # Do not log statements to be filtered. Does this check delay logging and hence delay the component itself?!
        if record.getMessage() is not None:
            record_message = record.getMessage().lower()
            # Loop through all the preset strings and check if the current log contains any one of those strings
            if any([filter_str.lower() in record_message for filter_str in LOGS_TO_BE_FILTERED_STREAM]):
                return

        new_properties = getattr(record, "properties", {})
        new_properties.update({"log_id": str(uuid.uuid4())})
        custom_dimensions = _get_custom_dimension()
        cust_dim_copy = custom_dimensions.copy()
        cust_dim_copy.update(new_properties)
        setattr(record, "properties", cust_dim_copy)
        msg = self.format(record)
        if record.levelname == "ERROR" and "AzureMLException" not in record.getMessage():
            setattr(
                record,
                "exception_tb_obj",
                "non-azureml exception raised so scrubbing",
            )
        stream = self.stream
        stream.write(msg)


def _appinsights_filter_processor(data: MessageData, context: TelemetryContext) -> bool:
    """
    A process that will be added to TelemetryClient that will prevent any PII debug/info/warning from getting logged
    """

    # Do not log statements to be filtered
    if data.message is not None:
        data_message = data.message.lower()
        # Loop through all the preset strings and check if the current log contains any one of those strings
        if any([filter_str.lower() in data_message for filter_str in LOGS_TO_BE_FILTERED_APPINSIGHTS]):
            return False

    return True


def get_logger_app(
    logging_level: str = "DEBUG",
    custom_dimensions: dict = None,
    name: str = Config.LOGGER_NAME,
):
    """
    Creates handlers and define formatter for emitting logs to AppInsights
    Also adds handlers to HF logs
    :returns logger which emits logs to stdOut and appInsights with PII Scrubbing
    """

    numeric_log_level = getattr(logging, logging_level.upper(), None)
    if not isinstance(numeric_log_level, int):
        raise ValueError("Invalid log level: %s" % logging_level)

    logger = logging.getLogger(name)

    # don't log twice i.e. root logger
    logger.propagate = False

    logger.setLevel(numeric_log_level)

    handler_names = [handler.get_name() for handler in logger.handlers]

    run_id = run_utils._get_run_id()
    app_name = Config.FINETUNE_APP_NAME

    if Config.AMLFT_HANDLER_NAME not in handler_names:
        # create Gllm handler and set formatter
        format_str = (
            "%(asctime)s [{}] [{}] [%(module)s] %(funcName)s "
            "%(lineno)s: %(levelname)-8s [%(process)d] %(message)s \n"
        )
        formatter = logging.Formatter(format_str.format(app_name, run_id))
        stream_handler = GllmHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(numeric_log_level)
        stream_handler.set_name(Config.AMLFT_HANDLER_NAME)
        logger.addHandler(stream_handler)

    if Config.APP_INSIGHT_HANDLER_NAME not in handler_names:
        # create AppInsight handler and set formatter
        appinsights_handler = get_telemetry_log_handler(
            instrumentation_key=Config.INSTRUMENTATION_KEY_AML_OLD,
            component_name="automl",
        )
        formatter = AppInsightsPIIStrippingFormatter(
            fmt=(
                "%(asctime)s [{}] [{}] [%(module)s] %(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d]"
                " %(message)s \n".format(app_name, run_id)
            )
        )
        appinsights_handler.setFormatter(formatter)
        appinsights_handler.setLevel(numeric_log_level)
        appinsights_handler.set_name(Config.APP_INSIGHT_HANDLER_NAME)
        appinsights_handler._synchronous_client.add_telemetry_processor(_appinsights_filter_processor)
        appinsights_handler._default_client.add_telemetry_processor(_appinsights_filter_processor)
        logger.addHandler(appinsights_handler)

        # Remove any previously added handlers
        transformers.logging.disable_default_handler()

        if Config.HF_LOGS_TO_APP_INSIGHT:
            # Config transformers logger
            transformers.logging.set_verbosity_debug()
            transformers.logging.add_handler(appinsights_handler)
            transformers.logging.add_handler(stream_handler)
            # Config datasets logger
            datasets.logging.get_logger().setLevel(numeric_log_level)
            datasets.logging.get_logger().addHandler(appinsights_handler)
            datasets.logging.get_logger().addHandler(stream_handler)

            # Config deepspeed logger
            if deepspeed_logger is not None:
                deepspeed_logger.setLevel(numeric_log_level)
                deepspeed_logger.addHandler(appinsights_handler)
                deepspeed_logger.addHandler(stream_handler)

            # Config optimum logger
            if optimum_logging is not None:
                optimum_logging.disable_default_handler()
                optimum_logging.set_verbosity_info()
                optimum_logging.add_handler(appinsights_handler)
                optimum_logging.add_handler(stream_handler)

    return logger
