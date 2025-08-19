# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Constants for model selector component."""

from dataclasses import dataclass


class ModelSelectorConstants:
    """String constants for model selector component."""

    PYTORCH_MODEL_PATH = "pytorch_model_path"
    MLFLOW_MODEL_PATH = "mlflow_model_path"
    MODEL_NAME = "model_name"
    MLFLOW_MODEL_DATA_PATH = "data"
    LICENSE_PATH = "license_path"
    MLFLOW_MODEL_ROOT = "mlflow_model_folder"
    PYTORCH_MODEL_ROOT = "pytorch_model_folder"
    REGISTRY_DOWNLOAD_DIR = "registry_model_download"
    FINETUNING_TASKS = "finetuning_tasks"
    MODEL_METAFILE_PATH = "model_metafile_path"
    MODEL_DEFAULTS_PATH = "model_defaults_path"
    BASE_MODEL_ASSET_ID = "base_model_asset_id"
    BASE_MODEL_TASK = "base_model_task"
    ASSET_ID_NOT_FOUND = "ASSET_ID_NOT_FOUND"
    MODEL_NAME_NOT_FOUND = "MODEL_NAME_NOT_FOUND"
    MODEL_METADATA = "model_metadata"
    MLMODEL = "MLmodel"
    DIFFUSERS = "diffusers"


class ModelSelectorAPIConstants:
    """String constants for API calls in model selector component"""

    REGISTRY_URI = "{}/modelregistry/v1.0/registry/models?assetIdOrReference={}"
    SERVICE_ENDPOINT = "AZUREML_SERVICE_ENDPOINT"
    MODEL_ASSET_ID = "azureml://registries/{}/models/{}/labels/latest"
    SAS_URI = "{}/assetstore/v1.0/dataReference/getBlobReferenceSAS"
    CUSTOM_MODEL = "CUSTOM"
    MLFLOW_MODEL = "MLFLOW"
    URL = "url"
    MODEL_FORMAT = "modelFormat"
    ASSET_ID = "assetId"
    BLOB_REF = "blobReferenceForConsumption"
    CREDENTIAL = "credential"
    WASBS_URI = "wasbsUri"
    BLOB_REF_ASSET_ID = "AssetId"
    BLOB_REF_BLOB_URI = "BlobUri"
    API_RETRY_COUNT = 5
    BACKOFF_IN_SECONDS = 1
    KVTAGS = "kvTags"
    TASK = "task"


@dataclass
class ModelSelectorDefaults:
    """Data class for model selector defaults."""

    MODEL_SELECTOR_ARGS_SAVE_PATH = "model_selector_args.json"
    MLFLOW_MODEL_DIRECTORY = "model"
    PYTORCH_MODEL_DIRECTORY = "model"
    MODEL_METADATA_PATH = "model_metadata.json"
    MODEL_DEFAULTS_PATH = "model_defaults.json"
    # Mandetory name for HF trainer.
    MODEL_CHECKPOINT_FILE_NAME = "pytorch_model.bin"
    # License file for HF
    LICENSE_FILE_NAME = "LICENSE"
    MODEL_REGISTRY = "azureml"
    MMD_MODELS_PREFIX = "mmd-3x-"
    FAST_RCNN_MODEL_PREFIX = "fast-rcnn"


class RunDetailsConstants:
    """ Run details constants"""

    MLFLOW_MODEL = "mlflow_model"
    PYTORCH_MODEL = "pytorch_model"
    RUN_DEFINITION = "runDefinition"
    INPUT_ASSETS = "inputAssets"
    ASSET = "asset"
    ASSET_ID = "assetId"
    NODE_COUNT = "nodeCount"
    PROCESS_COUNT = "processCount"
    PYTORCH_DISTRIBUTION = "pyTorch"


@dataclass
class ModelFamily:
    """A class to represent model family constants."""

    HUGGING_FACE_IMAGE = "HuggingFaceImage"
    MMDETECTION_IMAGE = "MmDetectionImage"
    MMTRACKING_VIDEO = "MmTrackingVideo"


@dataclass
class ModelRepositoryURLs:
    """A class to represent model repository URLs."""

    MMDETECTION = "https://github.com/open-mmlab/mmdetection/tree/v3.1.0/configs"
    HF_TRANSFORMER_IMAGE_CLASSIFIFCATION = (
        "https://huggingface.co/models?pipeline_tag=image-classification&library=transformers"
    )
    MMTRACKING = "https://github.com/open-mmlab/mmtracking/tree/v0.14.0/configs/mot"
