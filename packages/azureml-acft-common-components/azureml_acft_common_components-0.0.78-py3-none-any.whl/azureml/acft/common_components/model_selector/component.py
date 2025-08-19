# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""For model selector component."""

import json
import os
import shutil
import random
import time
import yaml
from pathlib import Path
from typing import Dict, Iterator, Union, Callable, List
from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.acft.common_components.utils.error_handling.error_definitions import (
    ModelInputEmpty, ACFTSystemError, ACFTUserError)
from azureml.acft.common_components.utils.error_handling.exceptions import (
    ACFTValidationException,
    ACFTSystemException,
)
from azureml.acft.common_components.utils.logging_utils import get_logger_app
from azureml.acft.common_components.utils.constants import MlflowMetaConstants
from .constants import (
    ModelRepositoryURLs,
    ModelSelectorConstants,
    ModelSelectorDefaults,
    ModelSelectorAPIConstants,
    ModelFamily,
    RunDetailsConstants
)
from ..utils.hf_hub_utils import check_if_model_present_in_hf_hub
from ..utils.license_utils import save_license_file
from azureml.core.run import Run
import requests
from azureml.dataprep.rslex import Copier, PyIfDestinationExists, PyLocationInfo
from azureml.dataprep.api._rslex_executor import ensure_rslex_environment

logger = get_logger_app(__name__)


class ModelSelector:
    """Model selector class to select the model and store the arguments to json file."""
    def __init__(
        self,
        pytorch_model: str = None,
        mlflow_model: str = None,
        model_name: str = None,
        output_dir: str = None,
        model_family: str = None,
        download_from_source: bool = False,
        unsupported_model_list: List[str] = [],
        component_type: str = None,
        **kwargs,
    ) -> None:
        """Default implementation for model selector. Override the functions for custom implementation.

        :param pytorch_model: asset path of pytorch model, defaults to None
        :type pytorch_model: str, optional
        :param mlflow_model: asset path of mlflow model, defaults to None
        :type mlflow_model: str, optional
        :param model_name: model name from the framework (i.e., HF), defaults to None
        :type model_name: str, optional
        :param output_dir: path to store arguments and model, defaults to None
        :type output_dir: str, optional
        :param model_family: model family, defaults to None
        :type model_family: str, optional
        :param unsupported_model_list: list of blocked models used to validate model name, defaults to None
        :type unsupported_model_list: List[str], optional
        :param component_type: Object created from which component, defaults to None
        :type component_type: str, optional
        """
        self.pytorch_model = pytorch_model
        self.mlflow_model = mlflow_model
        self.output_dir = output_dir
        self.model_name = model_name
        self.keyword_arguments = kwargs
        self.model_family = model_family
        self.download_from_source = download_from_source
        self.unsupported_model_list = unsupported_model_list
        self.base_model_asset_id = None
        self.metadata = {}
        self.model_through_input_port = self.pytorch_model or self.mlflow_model
        self.component_type = component_type
        if self.model_through_input_port:
            is_mlflow_model = self.mlflow_model is not None
            self.base_model_asset_id = self.get_model_asset_id(is_mlflow_model=is_mlflow_model)
            logger.info(f"asset id of input model: {self.base_model_asset_id}")

    def _download_pytorch_model_from_registry(self) -> None:
        """Download pytorch model from AzureML registry"""
        model_path = os.path.join(
            self.output_dir, ModelSelectorDefaults.PYTORCH_MODEL_DIRECTORY
        )
        ModelSelector._copy_directories(self.pytorch_model, model_path)
        logger.info(
            f"Downloaded pytorch model from {self.pytorch_model} to {model_path}."
        )

    def _download_mlflow_model_from_registry(self) -> None:
        """Download mlflow model from AzureML registry"""
        model_path = os.path.join(
            self.output_dir, ModelSelectorDefaults.MLFLOW_MODEL_DIRECTORY
        )
        self.convert_mlflow_model_to_pytorch_model(self.mlflow_model, Path(model_path))
        logger.info(
            f"Downloaded mlflow model from {self.mlflow_model} to {model_path}."
        )

    def _fetch_metadata(self) -> None:
        """ fetch metadata from i/p model. """
        if self.mlflow_model:
            model_path = os.path.join(
                self.output_dir, ModelSelectorDefaults.MLFLOW_MODEL_DIRECTORY
            )
            mlmodel_path = os.path.join(model_path, ModelSelectorConstants.MLMODEL)
            try:
                with open(mlmodel_path, "r") as f:
                    yaml_dict = yaml.safe_load(f)
                self.metadata = yaml_dict.get("metadata", {})
                logger.info(f"Fetched metadata from {ModelSelectorConstants.MLMODEL}: {self.metadata}")
            except Exception as e:
                logger.warning(
                    f"Failed while fetching metadata from {ModelSelectorConstants.MLMODEL}"
                    f"with err: {str(e)}"
                )
        elif self.pytorch_model:
            model_path = os.path.join(
                self.output_dir, ModelSelectorDefaults.PYTORCH_MODEL_DIRECTORY
            )
            model_metadata_file = os.path.join(model_path,
                                               ModelSelectorDefaults.MODEL_METADATA_PATH)
            if os.path.isfile(model_metadata_file):
                with open(model_metadata_file, "r") as f:
                    self.metadata = json.load(f)
                    logger.info(f"Fetched metadata from {model_metadata_file} file: {self.metadata}")
            else:
                logger.warning("unable to fetch metadata from the model provided through the"
                               f"input port since {ModelSelectorDefaults.MODEL_METADATA_PATH} is not found")

        if not self.model_name:
            if MlflowMetaConstants.BASE_MODEL_NAME in self.metadata:
                self.model_name = self.metadata.get(MlflowMetaConstants.BASE_MODEL_NAME)
            else:
                self.model_name = self.metadata.get(ModelSelectorConstants.MODEL_NAME, None)

        if ModelSelectorConstants.BASE_MODEL_ASSET_ID not in self.metadata and self.base_model_asset_id:
            self.metadata.update({ModelSelectorConstants.BASE_MODEL_ASSET_ID : self.base_model_asset_id})
        if self.model_name and MlflowMetaConstants.BASE_MODEL_NAME not in self.metadata:
            self.metadata.update({MlflowMetaConstants.BASE_MODEL_NAME : self.model_name})

        return

    def _prepare_and_logs_arguments(self) -> None:
        """Update the keyword arguments (if present) with required key-val items and
        Store the model selector arguments to json file.
        """
        arguments = {
            ModelSelectorConstants.MLFLOW_MODEL_PATH: self.mlflow_model,
            ModelSelectorConstants.PYTORCH_MODEL_PATH: self.pytorch_model,
            ModelSelectorConstants.MODEL_NAME: self.model_name,
            ModelSelectorConstants.MODEL_METADATA: self.metadata
        }

        if self.keyword_arguments:
            self.keyword_arguments.update(arguments)
        else:
            self.keyword_arguments = arguments

        os.makedirs(self.output_dir, exist_ok=True)
        model_selector_args_save_path = os.path.join(
            self.output_dir, ModelSelectorDefaults.MODEL_SELECTOR_ARGS_SAVE_PATH
        )
        logger.info(
            f"Saving the model selector args to {model_selector_args_save_path}"
        )
        with open(model_selector_args_save_path, "w") as output_file:
            json.dump(self.keyword_arguments, output_file, indent=2)

    @staticmethod
    def _copy_directories(asset_path: str, destination: str) -> None:
        """Recursively copy asset to destination

        :param asset_path: asset path of Azure ML
        :type asset_path: str
        :param destination: destination path
        :type destination: str
        """
        os.makedirs(destination, exist_ok=True)
        shutil.copytree(asset_path, destination, dirs_exist_ok=True)

    @staticmethod
    def flatten_and_copy_directories(src_dir, dest_dir):
        """Recursively copy from source to destination

        :param src_dir: source directory path
        :type asset_path: str
        :param dest_dir: destination path
        :type dest_dir: str
        """
        for subdir in os.listdir(src_dir):
            subdir_or_file = os.path.join(src_dir, subdir)
            if os.path.isdir(subdir_or_file):
                ModelSelector.flatten_and_copy_directories(subdir_or_file, dest_dir)
            else:
                shutil.copy2(subdir_or_file, dest_dir)

    @staticmethod
    def _copy_directories_using_MLmodel_yaml(src_dir: str, dest_dir: str) -> None:
        """Copy mlflow model directories using MLmodel.yaml file.

        It finds the path key in MLmodel and copies entire folder structure in dest_dir
        :param src_dir: source directory path
        :type asset_path: str
        :param dest_dir: destination path
        :type dest_dir: str
        :raises ACFTValidationException: if path key not found in MLmodel.yaml
        """
        mlmodel_file_path = os.path.join(src_dir, ModelSelectorConstants.MLMODEL)

        def _find_key(json_input: Dict, key: str) -> Iterator[str]:
            if isinstance(json_input, dict):
                for k, v in json_input.items():
                    if k == key:
                        yield v
                    if isinstance(v, (dict, list)):
                        yield from _find_key(v, key)
            elif isinstance(json_input, list):
                for item in json_input:
                    yield from _find_key(item, key)

        with open(mlmodel_file_path, "r") as file:
            data = yaml.safe_load(file)
            model_path = list(_find_key(data, "path"))

            if len(model_path) == 0:
                raise ACFTValidationException._with_error(
                    AzureMLError.create(ACFTUserError, pii_safe_message=f"Model path not found in {mlmodel_file_path}")
                )

        for path in model_path:
            ModelSelector._copy_directories(asset_path=os.path.join(src_dir, path), destination=dest_dir)

        # copy mlmodel file to fetch metadata later
        shutil.copy2(mlmodel_file_path, dest_dir)

    def convert_mlflow_model_to_pytorch_model(self, mlflow_model_path: Union[str, Path], download_dir: Path) -> None:
        """
        Download the mlflow model assets(model, config and proprocessor.json file)
        in the download directory to have similar directory structure as the pytorch model.

        :param mlflow_model_path: Path of the mlflow model
        :type mlflow_model_path: Union[str, Path]
        :param download_dir: Destination directory to download the model
        :type download_dir: Path
        """

        os.makedirs(download_dir, exist_ok=True)
        # mlflow models should contains MLmodel file
        if not os.path.isfile(os.path.join(mlflow_model_path, ModelSelectorConstants.MLMODEL)):
            error_string = f"{ModelSelectorConstants.MLMODEL} missing in the input mlflow model"
            raise ACFTValidationException._with_error(
                AzureMLError.create(ACFTUserError, pii_safe_message=error_string)
            )
        try:
            if self.component_type == ModelSelectorConstants.DIFFUSERS:
                # Diffusers model consist of multiple directories having different models.
                # Copy the entire directory structure to download directory without flattening.
                ModelSelector._copy_directories_using_MLmodel_yaml(src_dir=mlflow_model_path, dest_dir=download_dir)
            else:
                # flatten and copy to download dir
                ModelSelector.flatten_and_copy_directories(src_dir=mlflow_model_path, dest_dir=download_dir)

            # copy license file
            save_license_file(
                model_name_or_path=mlflow_model_path,
                license_file_name=ModelSelectorDefaults.LICENSE_FILE_NAME,
                destination_paths=[str(download_dir)],
            )
        except Exception as e:
            shutil.rmtree(download_dir, ignore_errors=True)
            raise ACFTValidationException._with_error(
                AzureMLError.create(ACFTUserError, pii_safe_message=str(e))
            )

    def _call_api_with_retries(self, request_method: Callable[..., requests.Response],
                               uri: str, **kwargs: dict) -> requests.Response:
        """
        Submit a REST API request to the given uri using the given request method. Retries failed requests
        and either fails with error reporting or returns the request reponse.

        :param request_method: request method to call
        :type request_method: Callable[..., requests.Response]
        :param uri: REST API uri
        :type uri: str
        :param **kwargs: keyword args to pass to request method
        :type **kwargs: dict
        """

        for i in range(ModelSelectorAPIConstants.API_RETRY_COUNT - 1):
            try:
                return request_method(uri, **kwargs)
            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Encountered {e.__class__.__name__} error while calling REST API "
                    f"Retries left: {ModelSelectorAPIConstants.API_RETRY_COUNT - i - 1}. Error details: {e}"
                )

                wait_time = ((2 ** i) * ModelSelectorAPIConstants.BACKOFF_IN_SECONDS + random.uniform(0, 1))
                logger.info(f"Waiting {wait_time:.2f} seconds before attempting call to {uri} again.")
                time.sleep(wait_time)

        # Attempt to load the call REST API one more time. Warn and advise to run again in case of new failure.
        logger.warning("Attempting to call REST API one last time. If this fails, please submit a new run.")
        try:
            return request_method(uri, **kwargs)
        except requests.exceptions.RequestException as e:
            error_string = (
                f"Encountered {e.__class__.__name__} error while calling REST API "
                f"Failed with exception {e}"
            )
            raise ACFTSystemException._with_error(
                AzureMLError.create(ACFTSystemError, pii_safe_message=error_string)
            )

    def _get_model_info_from_registry(self) -> requests.Response:
        """
        Retrieve model metadata from registry using REST API call.
        :return API call response
        :type requests.Response
        """
        if self.service_endpoint is None:
            logger.info(f"{ModelSelectorAPIConstants.SERVICE_ENDPOINT} environment variable is not set")
            return
        if not self.base_model_asset_id:
            self.base_model_asset_id = ModelSelectorAPIConstants.MODEL_ASSET_ID.format(
                ModelSelectorDefaults.MODEL_REGISTRY, self.registry_model_name)
        registry_uri = ModelSelectorAPIConstants.REGISTRY_URI.format(self.service_endpoint, self.base_model_asset_id)

        # make API call to get model info from registry
        logger.info(f"Calling REST API to get model metadata for {self.registry_model_name} from registry")
        request_args = {"headers" : self.auth_header}
        return self._call_api_with_retries(requests.get, registry_uri, **request_args)

    def _get_blobstore_sas_credential(self, model_info: dict) -> requests.Response:
        """
        Retrieve SaS credential for blob url specified in model_info using REST API call.
        :param model_info: model metadata including blob url
        :type model_info: dict
        :return API call response
        :type requests.Response
        """
        model_url = model_info[ModelSelectorAPIConstants.URL]
        self.base_model_asset_id = model_info[ModelSelectorAPIConstants.ASSET_ID]

        # get SaS credential because we cannot access blob store with AML Run Token
        sas_uri = ModelSelectorAPIConstants.SAS_URI.format(self.service_endpoint)
        blob_reference_sas_request_dto = {
            ModelSelectorAPIConstants.BLOB_REF_ASSET_ID: self.base_model_asset_id,
            ModelSelectorAPIConstants.BLOB_REF_BLOB_URI: model_url
        }

        # make API call to get SaS credential from registry
        logger.info("Calling REST API to get SaS credential for model artifacts blob")
        request_args = {"json" : blob_reference_sas_request_dto, "headers" : self.auth_header}
        return self._call_api_with_retries(requests.post, sas_uri, **request_args)

    def _download_blobstore_model_artifacts(self, sas_info: dict) -> os.PathLike:
        """
        Download model artifacts from blobstore with SaS credential.
        :param sas_info: SaS credential
        :type model_info: dict
        :return model_download_path: path that model artifacts are downloaded to
        :type os.Path
        """
        model_download_path = os.path.join(self.output_dir, ModelSelectorConstants.REGISTRY_DOWNLOAD_DIR)
        os.makedirs(model_download_path, exist_ok=True)
        download_location = PyLocationInfo('Local', model_download_path, {})
        if_exists = PyIfDestinationExists.MERGE_WITH_OVERWRITE
        credential = sas_info[ModelSelectorAPIConstants.BLOB_REF][ModelSelectorAPIConstants.CREDENTIAL]
        wasbs_uri = credential[ModelSelectorAPIConstants.WASBS_URI]
        try:
            logger.info("Downloading model artifacts from blobstore")
            ensure_rslex_environment()
            Copier.copy_uri(download_location, wasbs_uri, if_exists, "")
        except Exception as e:
            error_string = (
                f"Unable to download model artifacts from blobstore."
                f"Failed with exception {e}"
            )
            raise ACFTSystemException._with_error(
                AzureMLError.create(ACFTSystemError, pii_safe_message=error_string)
            )

        logger.info(f"Model {self.registry_model_name} is downloaded to folder {model_download_path}")
        return model_download_path

    def _model_name_download_from_registry(self) -> bool:
        """
        Search for model name in ModelSelectorDefaults.MODEL_REGISTRY.
        Download model and set model asset path (self.pytorch_model or self.mlflow_model)
        if the model is successfully downloaded from the registry.

        :return: True if model is downloaded from registry, False otherwise
        :rtype: bool
        """

        # convert HF id to registry model name
        self.registry_model_name = self.model_name.replace("/", "-")
        self._add_mmd_model_prefix()
        logger.info(f"Searching for model {self.registry_model_name} in registry")

        # get AML run token and service endpoint
        context = Run.get_context()
        self.auth_header = context.experiment.workspace._auth_object.get_authentication_header()
        self.service_endpoint = os.getenv(ModelSelectorAPIConstants.SERVICE_ENDPOINT)

        model_info_response = self._get_model_info_from_registry()

        # if the model was found, get sas credential and download model artifacts
        if model_info_response.status_code == 200:
            logger_str = f"Model {self.registry_model_name} was found in registry "\
                         f"{ModelSelectorDefaults.MODEL_REGISTRY}"
            logger.info(logger_str)
            model_info = model_info_response.json()
            logger.info(f"model_info: {model_info}")

            # get SaS credential for accessing blobstore
            sas_info_response = self._get_blobstore_sas_credential(model_info)
            if sas_info_response.status_code != 200:
                error_string = "Unable to retrieve SaS token for model download from registry"
                raise ACFTSystemException._with_error(
                    AzureMLError.create(ACFTSystemError, pii_safe_message=error_string)
                )
            sas_info = sas_info_response.json()
            logger.info("SaS token retrieved to download model")

            # download model artifacts from blobstore using sas credential
            model_download_path = self._download_blobstore_model_artifacts(sas_info)

            # set the asset path for the downloaded model, replace model_name with registry_model_name
            model_format = model_info[ModelSelectorAPIConstants.MODEL_FORMAT]
            if model_format == ModelSelectorAPIConstants.CUSTOM_MODEL:
                self.pytorch_model = Path(model_download_path, ModelSelectorConstants.PYTORCH_MODEL_ROOT)
                self.model_name = self.registry_model_name
                self._remove_mmd_model_prefix()

            elif model_format == ModelSelectorAPIConstants.MLFLOW_MODEL:
                self.mlflow_model = Path(model_download_path, ModelSelectorConstants.MLFLOW_MODEL_ROOT)
                self.model_name = self.registry_model_name
                self._remove_mmd_model_prefix()
            else:
                logger.warning(f'Model {self.registry_model_name} is not \
                            of type {ModelSelectorAPIConstants.CUSTOM_MODEL} or \
                            {ModelSelectorAPIConstants.MLFLOW_MODEL}')
            return True
        else:
            logger.warning(f'Model {self.model_name} was not found in registry '
                           f'{ModelSelectorDefaults.MODEL_REGISTRY}. Received response with status code'
                           f' {model_info_response.status_code} and error message: {model_info_response.content}')
            return False

    def _add_mmd_model_prefix(self) -> None:
        """ Add mmd-3x prefix to model name for MMDetection Models if not present.
        """
        if self.model_family == ModelFamily.MMDETECTION_IMAGE:
            # MMD 3.x models are prefix with mmd-3x in the model registry
            if self.registry_model_name.startswith(ModelSelectorDefaults.MMD_MODELS_PREFIX):
                msg = f"Model {self.registry_model_name} is already prefixed with "\
                      f"{ModelSelectorDefaults.MMD_MODELS_PREFIX}"
                logger.info(msg)
            else:
                self.registry_model_name = f"{ModelSelectorDefaults.MMD_MODELS_PREFIX}{self.registry_model_name}"

    def _remove_mmd_model_prefix(self) -> None:
        """Remove mmd-3x prefix from model name if present."""
        if self.model_name.startswith(ModelSelectorDefaults.MMD_MODELS_PREFIX):
            msg = (
                f"Model {self.model_name} is prefixed with {ModelSelectorDefaults.MMD_MODELS_PREFIX}"
                f" Removing prefix."
            )
            logger.info(msg)
            self.model_name = self.model_name[len(ModelSelectorDefaults.MMD_MODELS_PREFIX) :]

    def _validate_hf_model_name(self) -> None:
        """Validate if model name is present in hugging face model repository.
        :raises ACFTValidationException: if model name is not present in hugging face model repository
        """
        model_info_list = check_if_model_present_in_hf_hub(self.model_name)
        if len(model_info_list) == 0:
            raise ACFTValidationException._with_error(
                AzureMLError.create(
                    ACFTUserError,
                    pii_safe_message=f"Model name {self.model_name} is not present in hugging face model repository. "
                                     f"Please check {ModelRepositoryURLs.HF_TRANSFORMER_IMAGE_CLASSIFIFCATION} for "
                                     f"valid model name."
                )
            )

    def _validate_if_model_supported(self) -> None:
        """Validate if model is supported by ACFT.
        :raises ACFTValidationException: if model is not supported by ACFT
        """
        error_message = f"{self.model_name} is not supported. " \
                        f"Please select different model from AzureML Model catalog "
        if self.model_family == ModelFamily.HUGGING_FACE_IMAGE:
            error_message += f"or check {ModelRepositoryURLs.HF_TRANSFORMER_IMAGE_CLASSIFIFCATION}"
        elif self.model_family == ModelFamily.MMDETECTION_IMAGE:
            error_message += f"or check {ModelRepositoryURLs.MMDETECTION}"
        elif self.model_family == ModelFamily.MMTRACKING_VIDEO:
            error_message += f"or check {ModelRepositoryURLs.MMTRACKING}"
        if self.model_name in self.unsupported_model_list:
            raise ACFTValidationException._with_error(
                AzureMLError.create(ACFTUserError, pii_safe_message=error_message)
            )

    def get_model_asset_id(self, is_mlflow_model: bool) -> str:
        """Read the model asset id from the run context.

        :param is_mlflow_model: whether the model is provided through mlflow i/p port
        :type is_mlflow_model: bool

        :return asset id of the i/p model
        :rtype str
        """
        try:
            run_ctx = Run.get_context()
            if isinstance(run_ctx, Run):
                run_details = run_ctx.get_details()
                model_path = RunDetailsConstants.MLFLOW_MODEL if is_mlflow_model else RunDetailsConstants.PYTORCH_MODEL
                return run_details[RunDetailsConstants.RUN_DEFINITION][
                    RunDetailsConstants.INPUT_ASSETS][model_path][
                    RunDetailsConstants.ASSET][RunDetailsConstants.ASSET_ID]
            else:
                logger.info("Found offline run")
                return ModelSelectorConstants.ASSET_ID_NOT_FOUND
        except Exception as e:
            logger.warning(f"Could not fetch the model asset id: {e}")
            return ModelSelectorConstants.ASSET_ID_NOT_FOUND

    def run_workflow(self) -> None:
        """If model asset path is provided then it will download the model. Pytorch model will take preference
        over mlflow model. If model name is provided then, it will download the model from the registry. If the
        model is not found in the registry, it will download model from framework hub.
        It's responsibility of downstream component (e.g., finetune) to load the model.

        :raises ArgumentException._with_error: Raise exception if model ports or model name is not provided.
        """

        # If model_name is provided and asset paths are not specified, download the model from the registry.
        # If the model is found in the registry, the asset path will be set for the next if/elif block
        if ((self.model_name is not None) and (self.pytorch_model is None) and (self.mlflow_model is None)):

            if not self.download_from_source:
                model_found_in_registry = self._model_name_download_from_registry()
            else:
                model_found_in_registry = False
                # remove mmd prefix from model name if present when downloading from source
                self._remove_mmd_model_prefix()
                logger.info("Retrieving model from source instead of registry.")

            # If model is not found in the registry, validate model_name before downloading from framework hub
            if not model_found_in_registry:
                self.base_model_asset_id = None
                self._validate_if_model_supported()

                if self.model_family == ModelFamily.HUGGING_FACE_IMAGE:
                    self._validate_hf_model_name()

        if self.pytorch_model is not None:
            self._download_pytorch_model_from_registry()
            self.pytorch_model = ModelSelectorDefaults.PYTORCH_MODEL_DIRECTORY
            self.mlflow_model = None
        elif self.mlflow_model is not None:
            self._download_mlflow_model_from_registry()
            self.mlflow_model = ModelSelectorDefaults.MLFLOW_MODEL_DIRECTORY
        elif self.model_name is None:
            raise ACFTValidationException._with_error(
                AzureMLError.create(
                    ModelInputEmpty, argument_name="Model ports and model_name"
                )
            )
        self._fetch_metadata()

        self._prepare_and_logs_arguments()
