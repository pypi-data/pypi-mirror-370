# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This file defines the decorators used in the package
"""
import sys
import time
from functools import wraps
from typing import Any, Callable
import os

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml._common.exceptions import AzureMLException
from azureml.automl.core._run import run_lifecycle_utilities
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import NON_PII_MESSAGE
from azureml.core.run import Run  # type: ignore
from azureml.exceptions import ServiceException as AzureMLServiceException

from azureml.acft.common_components.utils.logging_utils import get_logger_app, SystemSettings
from .error_definitions import (
    ACFTInternalError,
    InsufficientGPUMemory,
    InsufficientSHMMemory,
    InsufficientGPUMemoryAutoFindBatchSize,
    LossScaleAtMinimum,
    FP16TrainingNotSupportedForModel,
    CudaErrorInvalidDeviceOrdinal
)
from .exceptions import ACFTSystemException
from ..torch_utils import get_node_gpu_count
from ..run_utils import calculate_per_node_process_count


logger = get_logger_app(__name__)


CUDA_OUT_OF_MEMORY_ERROR = "CUDA out of memory"
SHARED_MEMORY_ERROR = "shared memory"
AUTO_FIND_BATCH_SIZE_MEMORY_ERROR = "No executable batch size found, reached zero"
LOSS_SCALE_AT_MINIMUM = "Current loss scale already at minimum - cannot decrease scale anymore"
CUDA_ERROR = "CUDA error:"
CUDA_ERROR_INVALID_DEVICE_ORDINAL = "CUDA error: invalid device ordinal"
CUDNN_ERROR = "cuDNN error:"
CUDA_ERROR_EXCEPTION_MESSAGE = "Potential temporary hardware failure - please resubmit the run. If that does not " \
                               "solve the problem, please file a support ticket for further investigation."
MMDETECTION_FP16_TRAINING_NOT_SUPPORTED_ERROR_1 = "expected scalar type Half but found Float"
MMDETECTION_FP16_TRAINING_NOT_SUPPORTED_ERROR_2 = "got Half for the destination and Float for the source"
MMDETECTION_FP16_TRAINING_NOT_SUPPORTED_ERROR_3 = "not implemented for 'Half'"


def swallow_all_exceptions(fail_run: bool = True, time_delay: int = 0) -> Callable[..., Any]:
    """This decorates a function to handle uncaught exceptions and fail the run with System Error.

    :param fail_run: if True, fail the run. If False, just log the exception and raise it further.
        Note: This is useful when an exception is raised from a child process, because the exception details might not
        reach the parent process, so it's safer to log the contents directly in the child process.
    :type fail_run: bool
    :param time_delay: time delay in seconds to allow log server to process the logs in async queue.
    :type time_delay: int, default 0
    """

    def wrap(func):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            remove_pii = not _is_pii_stripping_enabled()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                str_e = str(e)

                if isinstance(e, (AzureMLException, AzureMLServiceException)):
                    interpreted_exception = e
                elif CUDA_OUT_OF_MEMORY_ERROR in str_e:
                    azureml_error = AzureMLError.create(InsufficientGPUMemory)
                    raise AzureMLException._with_error(azureml_error)
                elif AUTO_FIND_BATCH_SIZE_MEMORY_ERROR in str_e:
                    azureml_error = AzureMLError.create(InsufficientGPUMemoryAutoFindBatchSize, error=e)
                    raise AzureMLException._with_error(azureml_error)
                elif CUDA_ERROR_INVALID_DEVICE_ORDINAL in str_e:
                    azureml_error = AzureMLError.create(
                        CudaErrorInvalidDeviceOrdinal,
                        number_of_gpu_to_use_finetuning=calculate_per_node_process_count(),
                        maximum_number_of_gpu_to_use_finetuning=get_node_gpu_count()
                    )
                    raise AzureMLException._with_error(azureml_error)
                elif LOSS_SCALE_AT_MINIMUM in str_e:
                    azureml_error = AzureMLError.create(LossScaleAtMinimum, error=e)
                    raise AzureMLException._with_error(azureml_error)
                elif SHARED_MEMORY_ERROR in str_e:
                    azureml_error = AzureMLError.create(InsufficientSHMMemory)
                    raise AzureMLException._with_error(azureml_error)
                elif (
                    MMDETECTION_FP16_TRAINING_NOT_SUPPORTED_ERROR_1 in str_e
                    or MMDETECTION_FP16_TRAINING_NOT_SUPPORTED_ERROR_2 in str_e
                    or MMDETECTION_FP16_TRAINING_NOT_SUPPORTED_ERROR_3 in str_e
                ):
                    azureml_error = AzureMLError.create(FP16TrainingNotSupportedForModel, error=e)
                    raise AzureMLException._with_error(azureml_error)
                else:
                    # This is an unknown exception - try to log as much non PII info in telemetry
                    # in case logging is not yet initialized or not working
                    error_details = str_e

                    # If CUDA related error, direct user to file a ticket.
                    if (CUDA_ERROR in str_e) or (CUDNN_ERROR in str_e):
                        error_details = (
                            CUDA_ERROR_EXCEPTION_MESSAGE
                        )

                    error_msg_without_pii = logging_utilities._get_pii_free_message(e) if remove_pii else str(e)
                    traceback_obj = e.__traceback__ if hasattr(e, "__traceback__") else None or sys.exc_info()[2]
                    traceback_msg_without_pii = logging_utilities._CustomStackSummary.get_traceback_message(
                        traceback_obj,
                        remove_pii
                    )

                    interpreted_exception = ACFTSystemException._with_error(
                        AzureMLError.create(
                            ACFTInternalError,
                            error_details=error_details,
                            traceback=traceback_msg_without_pii,
                            pii_safe_message=error_msg_without_pii,
                            **kwargs
                        ),
                        inner_exception=e,
                    ).with_traceback(traceback_obj)

                run = Run.get_context()

                # The logging_utilities package's _get_pii_free_message function only handles the AutoMLException.
                # This is workaround used to handle the ACFTException by defining new local function.
                old_get_pii_free_message = logging_utilities._get_pii_free_message
                logging_utilities._get_pii_free_message = _get_pii_free_acft_message
                if fail_run:
                    run_lifecycle_utilities.fail_run(run, interpreted_exception, is_aml_compute=True)
                else:
                    logging_utilities.log_traceback(interpreted_exception, logger)
                logging_utilities._get_pii_free_message = old_get_pii_free_message
                raise
            finally:
                if time_delay > 0:
                    time.sleep(time_delay)

        return wrapper

    return wrap


def _get_pii_free_acft_message(exception: BaseException) -> str:
    """Get pii free message for ACFT exceptions.
    :param exception: Exception object
    :type exception: BaseException
    :return: PII free message
    :rtype: str
    """
    get_pii_free_exception_msg_format = getattr(exception, "get_pii_free_exception_msg_format", None)
    if get_pii_free_exception_msg_format and callable(get_pii_free_exception_msg_format) and \
       getattr(exception, "_azureml_error", None):
        return get_pii_free_exception_msg_format()
    else:
        return NON_PII_MESSAGE


def _is_pii_stripping_enabled() -> bool:
    """Check if PII stripping is enabled.
    :return: True if PII stripping is enabled, False otherwise
    :rtype: bool
    """
    return os.getenv(SystemSettings.LOG_LEVEL_DEBUG, 'False').lower() != 'true'
