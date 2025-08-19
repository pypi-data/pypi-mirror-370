# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Errors for the package."""
from azureml._common._error_definition.user_error import (
    ArgumentInvalid,
    Memory,
    NotFound,
    NotSupported,
    UserError,
    ArgumentBlankOrEmpty,
    InvalidData
)
from azureml._common._error_definition.system_error import SystemError
from azureml._common._error_definition.utils.error_decorator import error_decorator
from azureml._common._error_definition.system_error import ClientError
from .error_strings import ACFTErrorStrings


class ACFTUserError(UserError):
    """
    Generic User Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return ACFTErrorStrings.GENERIC_ERROR


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

        return ACFTErrorStrings.TASK_NOT_SUPPORTED


@error_decorator(use_parent_error_code=True)
class ModelFamilyNotSupported(NotSupported):
    """
    Model Family Not Supported Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return ACFTErrorStrings.MODEL_FAMILY_NOT_SUPPORTED


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

        return ACFTErrorStrings.INVALID_DATASET


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

        return ACFTErrorStrings.MODEL_INCOMPATIBLE_WITH_TASK


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

        return ACFTErrorStrings.TOKENIZER_NOT_SUPPORTED


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

        return ACFTErrorStrings.MODEL_NOT_SUPPORTED


class ValidationError(UserError):
    """
    Validation Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return ACFTErrorStrings.VALIDATION_ERROR


@error_decorator(use_parent_error_code=True)
class InvalidMlflowModelFormat(ValidationError):
    """
    Invalid mlflow model format
    """
    @property
    def message_format(self) -> str:
        """
        Message Format
        """
        return ACFTErrorStrings.INVALID_MLFLOW_MODEL_FORMAT


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

        return ACFTErrorStrings.RESOURCE_NOT_FOUND


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

        return ACFTErrorStrings.INVALID_CHECKPOINT_DIRECTORY


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

        return ACFTErrorStrings.PATH_NOT_FOUND


@error_decorator(use_parent_error_code=True)
class InsufficientSHMMemory(Memory):
    """
    Insufficient shared memory error
    """
    @property
    def message_format(self) -> str:
        """
        Message Format
        """
        return ACFTErrorStrings.INSUFFICIENT_SHM_MEMORY


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
        return ACFTErrorStrings.INSUFFICIENT_GPU_MEMORY


class ACFTInternalError(ClientError):
    """Top level unknown system error."""

    @property
    def message_format(self) -> str:
        """Non-formatted error message"""
        return ACFTErrorStrings.INTERNAL_ERROR


@error_decorator(use_parent_error_code=True)
class MLClientNotCreated(ACFTInternalError):
    """
    ML Client Not Created Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return ACFTErrorStrings.ML_CLIENT_NOT_CREATED


@error_decorator(use_parent_error_code=True)
class DeploymentFailed(ACFTInternalError):
    """
    Deployment Failed Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return ACFTErrorStrings.DEPLOYMENT_FAILED


@error_decorator(use_parent_error_code=True)
class PredictionFailed(ACFTInternalError):
    """
    Prediction Failed Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return ACFTErrorStrings.PREDICTION_FAILED


@error_decorator(use_parent_error_code=True)
class InvalidLabel(InvalidData):
    """
    Invalid Label Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return ACFTErrorStrings.INVALID_LABEL


@error_decorator(use_parent_error_code=True)
class ModelInputEmpty(ArgumentBlankOrEmpty):
    """
    Model input not provided
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return ACFTErrorStrings.ARGUMENT_BLANK_OR_EMPTY


class ACFTSystemError(SystemError):
    """
    ACFT system error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return ACFTErrorStrings.GENERIC_ERROR


class LossScaleAtMinimum(UserError):
    """
    Deepspeed Loss scale at minimum error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """
        return ACFTErrorStrings.LOSS_SCALE_AT_MINIMUM


class SKUNotSupported(NotSupported):
    """
    SKU Not Supported Error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """

        return ACFTErrorStrings.SKU_NOT_SUPPORTED


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
        return ACFTErrorStrings.INSUFFICIENT_GPU_MEMORY_AUTO_FIND_BATCH_SIZE


class FP16TrainingNotSupportedForModel(NotSupported):
    """
    FP16 training not supported for specified model error
    """

    @property
    def message_format(self) -> str:
        """
        Message Format
        """
        return ACFTErrorStrings.FP16_TRAINING_NOT_SUPPORTED_FOR_MODEL


class CudaErrorInvalidDeviceOrdinal(NotSupported):
    """Error definition for invalid device ordinal."""

    @property
    def message_format(self) -> str:
        """
        Message Format
        """
        return ACFTErrorStrings.INVALID_PARAM_NUMBER_OF_GPU_TO_USE_FINETUNING
