# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""File for adding all the constants"""

from dataclasses import dataclass


UNKNOWN_VALUE = "UNKNOWN"


class AzuremlRunType:
    """A class to represent azureml run types."""

    PIPELINE_RUN = "azureml.PipelineRun"
    STEP_RUN = "azureml.StepRun"


class AzuremlSKUType:
    """A class to represent azureml sku types."""

    STANDARD_NC24s_V3 = "Standard_NC24s_v3"


@dataclass(frozen=True)
class LoggingLibsIdentifier:
    """
    A class to represent logging libs.
    """

    AZUREML = "azureml."
    TRANSFORMER = "transformers."
    DATASETS = "datasets."
    OPTIMUM = "optimim."
    DEEPSPEED = "deepspeed."


@dataclass(frozen=True)
class NonAzureMLLoggingLibsAllowedPatterns:

    """
    A class to represent allowed logging patterns for non azureml logging libs.
    """

    ALLOWED_PATTERN_TO_LOG_IN_APPINSIGHTS_FOR_TRANSFORMERS_LIBS = [
        "Image processor",
        "PyTorch: setting up devices",
        "ModuleWithLoss Wrapper",
        "cuda_amp half precision backend",
        "Running Evaluation",
        "Num examples =",
        "Num Epochs =",
        "Batch size =",
        "Gradient Accumulation steps =",
        "Total optimization steps =",
        "Instantaneous batch size per device =",
        "Total train batch size (w. parallel, distributed & accumulation) =",
        "Number of trainable parameters =",
        "safetensors installation",
    ]

    ALLOWED_PATTERN_TO_LOG_IN_APPINSIGHTS_FOR_DATASETS_LIBS = [
        "Generating train split",
        "Using custom data configuration",
        "Checksum Computation",
        "Unable to verify splits sizes",
    ]

    ALLOWED_PATTERN_TO_LOG_IN_APPINSIGHTS_FOR_OPTIMUM_LIBS = [
        "Wrap ORTModule for ONNX Runtime training",
        "Running training",
        "Num examples =",
        "Num Epochs =",
        "Batch size =",
        "Gradient Accumulation steps =",
        "Total optimization steps =",
        "Instantaneous batch size per device =",
        "Total train batch size (w. parallel, distributed & accumulation) =",
        "Number of trainable parameters =",
        "Evaluating with PyTorch backend",
        "Training completed.",
    ]

    ALLOWED_PATTERN_TO_LOG_IN_APPINSIGHTS_FOR_DEEPSPEED_LIBS = [
        "Initializing TorchBackend in DeepSpeed",
        "OVERFLOW!",
        "DeepSpeed info",
        "DeepSpeed Basic Optimizer =",
        "DeepSpeed using configured LR scheduler =",
    ]

    NON_AZUREML_PKGS_IDENTIFIER_PATTERNS_MAPPING = {
        LoggingLibsIdentifier.TRANSFORMER: ALLOWED_PATTERN_TO_LOG_IN_APPINSIGHTS_FOR_TRANSFORMERS_LIBS,
        LoggingLibsIdentifier.DATASETS: ALLOWED_PATTERN_TO_LOG_IN_APPINSIGHTS_FOR_DATASETS_LIBS,
        LoggingLibsIdentifier.OPTIMUM: ALLOWED_PATTERN_TO_LOG_IN_APPINSIGHTS_FOR_OPTIMUM_LIBS,
        LoggingLibsIdentifier.DEEPSPEED: ALLOWED_PATTERN_TO_LOG_IN_APPINSIGHTS_FOR_DEEPSPEED_LIBS,
    }


class MlflowMetaConstants:
    """ mlflow consants"""
    IS_FINETUNED_MODEL = "is_finetuned_model"
    IS_ACFT_MODEL = "is_acft_model"
    BASE_MODEL_NAME = "base_model_name"
    BASE_MODEL_ASSET_ID = "base_model_asset_id"
    FINETUNING_TASK = "finetuning_task"
    BASE_MODEL_TASK = "base_model_task"


class TransformerConstants:
    """Transformer contants."""
    ROOT_CACHE_FOLDER = "/tmp"
    HF_MODULES_CACHE = "HF_MODULES_CACHE"
