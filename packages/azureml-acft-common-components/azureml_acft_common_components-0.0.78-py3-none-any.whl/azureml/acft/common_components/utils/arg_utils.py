# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utility functions parsing arguments"""

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.common_components.utils.error_handling.exceptions import ACFTValidationException
from azureml.acft.common_components.utils.error_handling.error_definitions import ArgumentInvalid


def str2bool(arg, arg_name=""):
    """Convert string to boolean.

    :param arg: String to be converted to boolean.
    :type arg: str
    :param arg_name: Name of the argument.
    :type arg_name: str

    :return: Boolean value.
    :rtype: bool
    """
    arg = arg.lower()
    if arg in ["true", "1"]:
        return True
    elif arg in ["false", "0"]:
        return False
    else:
        raise ACFTValidationException._with_error(
            AzureMLError.create(ArgumentInvalid, argument_name=arg_name, expected_type="bool")
        )
