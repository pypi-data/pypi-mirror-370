# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This file contains definitions of custom error classes used for emitting cutom error messages
"""

from azureml._common._error_definition import error_decorator  # type: ignore
from azureml._common._error_definition.system_error import ClientError  # type: ignore
from azureml._common._error_definition.user_error import (  # type: ignore
    ArgumentBlankOrEmpty,
    ArgumentInvalid,
    ArgumentMismatch,
    ArgumentOutOfRange,
    Authentication,
    BadArgument,
    BadData,
    Conflict,
    ConnectionFailure,
    EmptyData,
    InvalidDimension,
    MalformedArgument,
    Memory,
    MissingData,
    NotFound,
    NotReady,
    NotSupported,
    UserError,
)

from .error_strings import LLMErrorStrings


class LLMInternalError(ClientError):
    """
    Internal LLM Generic Error
    """

    @property
    def message_format(self) -> str:
        """
        Message format
        """

        return LLMErrorStrings.LLM_GENERIC_ERROR

class SKUNotSupported(NotSupported):
    """
    SKU Not Supported Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.SKU_NOT_SUPPORTED

@error_decorator(use_parent_error_code=True)
class TaskNotSupported(NotSupported):
    """
    Task Not Supported Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.TASK_NOT_SUPPORTED


@error_decorator(use_parent_error_code=True)
class InvalidDataset(NotSupported):
    """
    Task Not Supported Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.INVALID_DATASET


@error_decorator(use_parent_error_code=True)
class ModelIncompatibleWithTask(NotSupported):
    """
    Task Not Supported Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.MODEL_INCOMPATIBLE_WITH_TASK


@error_decorator(use_parent_error_code=True)
class TokenizerNotSupported(NotSupported):
    """
    Tokenizer Not Supported Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.TOKENIZER_NOT_SUPPORTED


@error_decorator(use_parent_error_code=True)
class ModelNotSupported(NotSupported):
    """
    Module Not Supported Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.MODEL_NOT_SUPPORTED


class ValidationError(UserError):
    """
    Validation Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.VALIDATION_ERROR


@error_decorator(use_parent_error_code=True)
class ResourceNotFound(NotFound):
    """
    Resource Not Found Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.RESOURCE_NOT_FOUND


@error_decorator(use_parent_error_code=True)
class InvalidCheckpointDirectory(ArgumentInvalid):
    """
    Invalid Checkpoint Directory Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.INVALID_CHECKPOINT_DIRECTORY


@error_decorator(use_parent_error_code=True)
class PathNotFound(ArgumentInvalid):
    """
    Path not found Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.PATH_NOT_FOUND


@error_decorator(use_parent_error_code=True)
class MLClientNotCreated(LLMInternalError):
    """
    ML Client Not Created Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.ML_CLIENT_NOT_CREATED


@error_decorator(use_parent_error_code=True)
class DeploymentFailed(LLMInternalError):
    """
    Deployment Failed Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.DEPLOYMENT_FAILED


@error_decorator(use_parent_error_code=True)
class PredictionFailed(LLMInternalError):
    """
    Prediction Failed Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.PREDICTION_FAILED


@error_decorator(use_parent_error_code=True)
class InvalidLabel(LLMInternalError):
    """
    Invalid Label Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return LLMErrorStrings.INVALID_LABEL


@error_decorator(
    use_parent_error_code=True, details_uri="https://docs.microsoft.com/en-us/azure/virtual-machines/sizes-gpu"
)
class InsufficientGPUMemory(Memory):
    """
    Insufficient GPU memory error
    """
    @property
    def message_format(self) -> str:
        """
        Message Format
        """
        return LLMErrorStrings.INSUFFICIENT_GPU_MEMORY


@error_decorator(
    use_parent_error_code=True, details_uri="https://docs.microsoft.com/en-us/azure/virtual-machines/sizes-gpu"
)
class InsufficientGPUMemoryAutoFindBatchSize(Memory):
    """
    Insufficient GPU memory error
    """
    @property
    def message_format(self) -> str:
        """
        Message Format
        """
        return LLMErrorStrings.INSUFFICIENT_GPU_MEMORY_AUTO_FIND_BATCH_SIZE


class LossScaleAtMinimum(UserError):
    """
    Deepspeed Loss scale at minimum error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """
        return LLMErrorStrings.LOSS_SCALE_AT_MINIMUM
