# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from mlflow.exceptions import MlflowException
from azureml._common._error_response._error_response_constants import ErrorCodes


class AzureMLMLFlowException(MlflowException):
    """Base Model Evaluation Exception."""

    _error_code = ErrorCodes.SYSTEM_ERROR

    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)


class AzureMLMLFlowUserException(MlflowException):
    """User Exception."""

    _error_code = ErrorCodes.USER_ERROR

    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)


class AzureMLMLFlowInvalidModelException(AzureMLMLFlowUserException):
    """Invalid Model Exception."""


class AzureMLMLFlowValueException(AzureMLMLFlowUserException):
    """Value Exception."""


class AzureMLMLFlowTypeException(AzureMLMLFlowUserException):
    """Type Exception."""
