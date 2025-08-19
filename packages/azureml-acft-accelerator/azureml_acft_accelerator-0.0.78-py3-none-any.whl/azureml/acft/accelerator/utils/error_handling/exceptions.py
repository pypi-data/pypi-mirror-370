# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Exceptions thrown by GLLM component
"""

from azureml._common._error_response._error_response_constants import ErrorCodes  # type: ignore
from azureml._common.exceptions import AzureMLException  # type: ignore


class LLMException(AzureMLException):
    """
    Base exception related to FineTuning Large Language Models service.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message, **kwargs):
        """
        Initialize a new instance of LLMException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """

        super(LLMException, self).__init__(exception_message, **kwargs)

    @property
    def error_code(self):
        """
        returns error code for azureml_error
        """

        return self._azureml_error.error_definition.code


class ValidationException(LLMException):
    """
    Exceptions related to validation errors.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message, **kwargs):
        """
        Initialize a new instance of ValidationException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """

        super(ValidationException, self).__init__(exception_message, **kwargs)


class ArgumentException(LLMException):
    """
    Exception related to arguments.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message, **kwargs):
        """
        Initialize a new instance of ArgumentException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """

        super(ArgumentException, self).__init__(exception_message, **kwargs)


class DataException(ValidationException):
    """
    Exception related to data validations.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message, **kwargs):
        """
        Initialize a new instance of DataException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """

        super(DataException, self).__init__(exception_message, **kwargs)


class ServiceException(LLMException):
    """
    Exception related to LLM service.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message, **kwargs):
        """
        Initialize a new instance of ServiceException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """

        super(ServiceException, self).__init__(exception_message, **kwargs)


class ResourceException(LLMException):
    """
    Exception related to Azure resources.

    :param exception_message: A message describing the error.
    :type exception_message: str
    """

    def __init__(self, exception_message, **kwargs):
        """
        Initialize a new instance of ResourceException.

        :param exception_message: A message describing the error.
        :type exception_message: str
        """

        super(ResourceException, self).__init__(exception_message, **kwargs)
