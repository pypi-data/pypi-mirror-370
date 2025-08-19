# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exceptions for the acft package."""
import json
from typing import Any, Optional

from azureml._common._error_definition import AzureMLError
from azureml._common._error_response._error_response_constants import ErrorCodes
from azureml._common.exceptions import AzureMLException
from azureml.exceptions import UserErrorException


class ACFTException(AzureMLException):
    """Base class for all ACFT exceptions."""

    def _exception_msg_format(
            self, error_name: str, message: str, error_response: Optional[str], log_safe: bool = True
    ) -> str:
        """format the exception message.
        :param error_name: name of the error
        :type error_name: str
        :param message: message to be displayed
        :type message: str
        :param error_response: error response
        :type error_response: str Optional
        :param log_safe: if True, print the inner exception type for a log safe message
        :type log_safe: bool
        :return: formatted exception message
        :rtype: str
        """
        inner_exception_message = None
        if self._inner_exception:
            if log_safe:
                # Only print the inner exception type for a log safe message
                inner_exception_message = self._inner_exception.__class__.__name__
            else:
                inner_exception_message = "{}: {}".format(
                    self._inner_exception.__class__.__name__, str(self._inner_exception)
                )
        return "{}:\n\tMessage: {}\n\tInnerException: {}\n\tErrorResponse \n{}".format(
            error_name, message, inner_exception_message, error_response
        )

    def get_pii_free_exception_msg_format(self) -> str:
        """Get PII free exception message format.

        :return: PII free exception message format
        """
        # Update exception message to be PII free
        # Update inner exception to log exception type only
        # Update Error Response to contain PII free message
        pii_free_msg = self._azureml_error.log_safe_message_format()
        error_dict = json.loads(
            self._serialize_json(
                filter_fields=[AzureMLError.Keys.MESSAGE_FORMAT, AzureMLError.Keys.MESSAGE_PARAMETERS]
            )
        )
        error_dict["error"]["message"] = pii_free_msg
        return self._exception_msg_format(self.__class__.__name__, pii_free_msg, json.dumps(error_dict, indent=4))


# User Exception
class ACFTUserException(UserErrorException, ACFTException):
    """Exception for user errors caught during ACFT model training."""


class ACFTValidationException(ACFTUserException):
    """Exception for any errors caught when validating inputs."""

    _error_code = ErrorCodes.VALIDATION_ERROR


class ACFTDataException(ACFTValidationException):
    """Exception related to data validations."""

    _error_code = ErrorCodes.INVALIDDATA_ERROR

    def __init__(self, message: str = "", **kwargs: Any) -> None:
        """Init function that accepts message argument.

        In the case of torch.utils.data.DataLoader with num_workers > 0, any exceptions raised in
        worker processes is reraised using this function
        https://github.com/pytorch/pytorch/blob/v2.1.0/torch/_utils.py#L674.
        If an exception raised in worker process has "message" in its properties,
        this function expects the __init__ method
        to have message argument. Adding it here as we raise ACFTDataException and it has "message" parameter.
        Please note that this behavior in torch can be changed in future versions
        and this __init__ method needs to be updated accordingly.
        """
        if "exception_message" in kwargs:
            message = kwargs.pop("exception_message")
        super().__init__(exception_message=message, **kwargs)


# System Exception
class ACFTSystemException(ACFTException):
    """Exception for internal errors that happen within the SDK."""

    _error_code = ErrorCodes.SYSTEM_ERROR


class ACFTTrainingException(ACFTSystemException):
    """Exception for issues that arise during model training."""


class ACFTResourceException(ACFTSystemException):
    """Exception related to Azure resources."""


class ACFTServiceException(ACFTSystemException):
    """Exception related to Azure services."""
