# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Error strings for custom errors"""
from azureml.acft.common_components.utils.constants import AzuremlSKUType


class ACFTErrorStrings:
    """Error strings for ACFT errors"""

    INTERNAL_ERROR = (
        "Encountered an internal ACFT error. Error Message/Code: {error_details}. Traceback: "
        "{traceback:log_safe}. Additional information: {pii_safe_message:log_safe}."
    )
    GENERIC_ERROR = "{pii_safe_message:log_safe}"
    TASK_NOT_SUPPORTED = (
        "Given Task [{TaskName:log_safe}] is not supported, Please check name or supply different task"
    )
    MODEL_NOT_SUPPORTED = (
        "Given Model [{ModelName:log_safe}] is not supported, Please check name or provide different model"
    )
    MODEL_FAMILY_NOT_SUPPORTED = (
        "[{model_family:log_safe}] is not supported, Supported model families: [{supported_model_families:log_safe}]"
    )
    MODEL_INCOMPATIBLE_WITH_TASK = (
        "The selected Model [{ModelName:log_safe}] doesn't support the current Task [{TaskName:log_safe}], "
        "Please select a different model"
    )
    TOKENIZER_NOT_SUPPORTED = (
        "The selected Tokenizer [{Tokenizer:log_safe}] doesn't support the current Task [{TaskName:log_safe}], "
        "Please select a different tokenizer or tokenizer type"
    )
    SKU_NOT_SUPPORTED = (
        "The selected compute does not meet minimum compute requirements, "
        f"Please use {AzuremlSKUType.STANDARD_NC24s_V3} SKU."
    )
    VALIDATION_ERROR = "Error while validating parameters [{error:log_safe}]"
    RESOURCE_NOT_FOUND = "Resource [{ResourceName:log_safe}] not found"
    INVALID_CHECKPOINT_DIRECTORY = "Provide a valid checkpoint directory. Got [{dir:log_safe}]"
    PATH_NOT_FOUND = "Path [{path:log_safe}] was not found"
    ML_CLIENT_NOT_CREATED = (
        "Failed to create ML Client. This is likely because you didn't create a managed identity and assign it to "
        "your compute cluster."
    )
    DEPLOYMENT_FAILED = "Failed to create deployment with error [{error:log_safe}]"
    PREDICTION_FAILED = "Prediction Failed with error [{error:log_safe}]"
    INVALID_LABEL = "Label {label} is not found in training/validation data"
    INVALID_DATASET = "Only one label found in training and validation data combined"
    INSUFFICIENT_SHM_MEMORY = (
        "There is not enough shared memory on the machine to do the operation. "
        "Please try running the experiment with a smaller batch size."
    )
    INSUFFICIENT_GPU_MEMORY = (
        "There is not enough GPU memory on the machine to do the operation. "
        "Please try:\n"
        "1. Running the experiment on a VM with higher GPU memory.\n"
        "2. Decreasing the `per_device_train_batch_size`.\n"
        "3. Enabling LoRA or Deepspeed or ORT or any combinations of these.\n"
        "4. Setting the `pad_to_max_length` to false for Language tasks.\n"
        "5. Decreasing the `image_size` for Image tasks.\n"
        "6. Decreasing the `lora_r` if `apply_lora` is set to true.\n"
    )
    INVALID_MLFLOW_MODEL_FORMAT = (
        "Please make sure that the mlflow model has the following directories: \n [{directories:log_safe}] "
    )
    ARGUMENT_BLANK_OR_EMPTY = "An empty value for argument [{argument_name:log_safe}] is provided."
    INSUFFICIENT_GPU_MEMORY_AUTO_FIND_BATCH_SIZE = (
        "Auto find batch size couldn't find the right batch size to do the operation. Encountered error [{error}]. "
        "You could try:\n"
        "1. Running the experiment on Standard_NC24s_v3 SKU.\n"
        "2. Enabling LoRA.\n"
        "3. Enabling deepspeed optimization\n"
        "4. Enabling deepspeed and ORT optimization.\n"
    )
    LOSS_SCALE_AT_MINIMUM = (
        "Encountered an error while training with Deepspeed [{error}]"
        "Try with fp32 precision or provide a different Deepspeed config"
    )
    FP16_TRAINING_NOT_SUPPORTED_FOR_MODEL = (
        "An error occurred while attempting to train with fp16 precision for the specified model [{error}]. "
        "Please consider using fp32 precision or selecting a different model."
    )
    INVALID_PARAM_NUMBER_OF_GPU_TO_USE_FINETUNING = (
        "The selected value for number_of_gpu_to_use_finetuning [{number_of_gpu_to_use_finetuning:log_safe}] is "
        "higher than gpus present in the node [{maximum_number_of_gpu_to_use_finetuning:log_safe}]. Please fix "
        "the value and try again."
    )
