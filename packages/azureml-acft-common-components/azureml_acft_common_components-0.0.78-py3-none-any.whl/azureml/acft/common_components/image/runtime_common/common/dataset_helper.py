# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Common helper class for reading labeled Aml Datasets."""

import json
import os
import shutil
import tempfile
import time
import uuid
from typing import Any, List, cast
from urllib.parse import unquote
from azureml.data.abstract_dataset import AbstractDataset

import pandas

import azureml.dataprep as dprep

from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.image.runtime_common.common.exceptions import AutoMLVisionDataException, \
    AutoMLVisionRuntimeUserException
from azureml.core import Dataset as AmlDataset, Datastore, Run, Workspace
from azureml.data import dataset_error_handling, DataType
from azureml.data.dataset_factory import FileDatasetFactory
from azureml.dataprep import ExecutionError, ValidationError
from azureml.dataprep.api.engineapi.typedefinitions import FieldType
from azureml.dataprep.api.functions import get_portable_path
from azureml.exceptions import UserErrorException, AzureMLException

logger = get_logger_app(__name__)


class AmlDatasetHelper:
    """Helper for AzureML dataset."""
    LABEL_COLUMN_PROPERTY = '_Label_Column:Label_'
    DEFAULT_LABEL_COLUMN_NAME = 'label'
    DEFAULT_LABEL_CONFIDENCE_COLUMN_NAME = 'label_confidence'
    COLUMN_PROPERTY = 'Column'
    IMAGE_COLUMN_PROPERTY = '_Image_Column:Image_'
    DEFAULT_IMAGE_COLUMN_NAME = 'image_url'
    PORTABLE_PATH_COLUMN_NAME = 'PortablePath'
    DATASTORE_PREFIX = 'AmlDatastore://'
    OUTPUT_DATASET_PREFIX = "output_"
    STREAM_INFO_HANDLER_PROPERTY = 'handler'
    DATASTORE_HANDLER_NAME = 'AmlDatastore'

    def __init__(self, dataset: AbstractDataset, ignore_data_errors: bool = False,
                 image_column_name: str = DEFAULT_IMAGE_COLUMN_NAME,
                 download_files: bool = True):
        """Constructor - This reads the dataset and downloads the images that it contains.

        :param dataset: dataset
        :type dataset: AbstractDataset
        :param ignore_data_errors: Setting this ignores and files in the dataset that fail to download.
        :type ignore_data_errors: bool
        :param image_column_name: The column name for the image file.
        :type image_column_name: str
        :param download_files: Flag to download files or not.
        :type download_files: bool
        """

        self._data_dir = AmlDatasetHelper.get_data_dir()

        self.image_column_name = AmlDatasetHelper.get_image_column_name(dataset, image_column_name)
        self.label_column_name = AmlDatasetHelper.get_label_column_name(dataset,
                                                                        AmlDatasetHelper.DEFAULT_LABEL_COLUMN_NAME)

        if download_files:
            AmlDatasetHelper.download_image_files(dataset, self.image_column_name)

        dflow = dataset._dataflow.add_column(get_portable_path(dprep.col(self.image_column_name)),
                                             AmlDatasetHelper.PORTABLE_PATH_COLUMN_NAME, self.image_column_name)
        self.images_df = dflow.to_pandas_dataframe(extended_types=True)

        if download_files and ignore_data_errors:
            missing_file_indices = []
            for index in self.images_df.index:
                full_path = self.get_image_full_path(index)
                if not os.path.exists(full_path):
                    missing_file_indices.append(index)
                    msg = 'File not found. Since ignore_data_errors is True, this file will be ignored'
                    logger.warning(msg)
            self.images_df.drop(missing_file_indices, inplace=True)
            self.images_df.reset_index(inplace=True, drop=True)

    def get_image_full_path(self, index: int) -> str:
        """Return the full local path for an image.

        :param index: index
        :type index: int
        :return: Full path for the local image file
        :rtype: str
        """
        return AmlDatasetHelper.get_full_path(index, self.images_df, self._data_dir)

    def get_file_name_list(self) -> List[str]:
        """Return a list of the relative file names for the images.

        :return: List of the relative file names for the images
        :rtype: list(str)
        """
        return cast(List[str], self.images_df[AmlDatasetHelper.PORTABLE_PATH_COLUMN_NAME].tolist())

    @staticmethod
    def get_full_path(index: int, images_df: pandas.DataFrame, data_dir: str) -> str:
        """Return the full local path for an image.

        :param index: index
        :type index: int
        :param images_df: DataFrame containing images.
        :type images_df: Pandas DataFrame
        :param data_dir: data folder
        :type data_dir: str
        :return: Full path for the local image file
        :rtype: str
        """
        image_rel_path = images_df[AmlDatasetHelper.PORTABLE_PATH_COLUMN_NAME][index]
        # the image_rel_path can sometimes be an exception from dataprep
        if type(image_rel_path) is not str:
            logger.warning(f"The relative path of the image is of type {type(image_rel_path)}, "
                           f"expecting a string. Will ignore the image.")
            image_rel_path = "_invalid_"
        return cast(str, data_dir + '/' + image_rel_path)

    @staticmethod
    def write_dataset_file_line(fw: Any, image_file_name: str, confidence: List[float], label: List[str]) -> None:
        """Write a line to the dataset file.

        :param fw: The file to write to.
        :type fw: file
        :param image_file_name: The image file name with path within the datastore.
        :type image_file_name: str
        :param confidence: Label confidence values between 0.0 and 1.0
        :type confidence: List[float]
        :param label: The label names.
        :type label: List[str]
        """
        # unquote to convert the replace(%3A and %2F ...) in the url
        image_full_path = AmlDatasetHelper.DATASTORE_PREFIX + unquote(image_file_name)

        fw.write(
            json.dumps(
                {
                    AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME: image_full_path,
                    AmlDatasetHelper.DEFAULT_LABEL_CONFIDENCE_COLUMN_NAME: confidence,
                    AmlDatasetHelper.DEFAULT_LABEL_COLUMN_NAME: label
                }
            )
        )
        fw.write('\n')

    @staticmethod
    def create(run: Run, datastore: Datastore, labeled_dataset_file: str, target_path: str,
               dataset_id_property_name: str = 'labeled_dataset_id') -> None:
        """Create a labeled dataset file.

        :param run: AzureML Run to write the dataset id to..
        :type run: Run
        :param datastore: The AML datastore to store the Dataset file.
        :type datastore: Datastore
        :param labeled_dataset_file: The name of the Labeled Dataset file.
        :type labeled_dataset_file: str
        :param target_path: The path for the Labeled Dataset file in Datastore
        :type target_path: str
        :param dataset_id_property_name: The name of the dataset id property
        :type dataset_id_property_name: str
        """
        _, labeled_dataset_file_basename = os.path.split(labeled_dataset_file)
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(labeled_dataset_file, tmpdir)
            try:
                FileDatasetFactory.upload_directory(tmpdir, (datastore, target_path), overwrite=True)
            except dataset_error_handling.DatasetValidationError as e:
                # Dataset client fails to capture auth errors so we must catch the subsequent
                # validation error. Bug #1542254.
                msg = f"Encountered exception while uploading {labeled_dataset_file_basename} " \
                      f"file to default datastore. This can happen when there are insufficient permission for " \
                      f"accessing the datastore. Please check the logs for more details."
                raise AutoMLVisionRuntimeUserException(f"{msg}", inner_exception=e, has_pii=False)
        labeled_dataset_path = target_path + '/' + labeled_dataset_file_basename
        dataset = AmlDataset.Tabular.from_json_lines_files(
            path=(datastore, labeled_dataset_path),
            set_column_types={AmlDatasetHelper.DEFAULT_IMAGE_COLUMN_NAME: DataType.to_stream(datastore.workspace)})
        dataset_name = AmlDatasetHelper.OUTPUT_DATASET_PREFIX + run.id
        dataset = dataset.register(
            workspace=run.experiment.workspace, name=dataset_name, create_new_version=True)
        run.add_properties({dataset_id_property_name: dataset.id})

    @staticmethod
    def get_default_target_path() -> str:
        """Get the default target path in datastore to be used for Labeled Dataset files.

            :return: The default target path
            :rtype: str
            """
        return 'automl/datasets/' + str(uuid.uuid4())

    @staticmethod
    def get_data_dir() -> str:
        """Get the data directory to download the image files to.

        :return: Data directory path
        :type: str
        """
        return tempfile.gettempdir()

    @staticmethod
    def _get_column_name(ds: AmlDataset,
                         parent_column_property: str,
                         default_value: str) -> str:
        if parent_column_property in ds._properties:
            image_property = ds._properties[parent_column_property]
            if AmlDatasetHelper.COLUMN_PROPERTY in image_property:
                return cast(str, image_property[AmlDatasetHelper.COLUMN_PROPERTY])
            lower_column_property = AmlDatasetHelper.COLUMN_PROPERTY.lower()
            if lower_column_property in image_property:
                return cast(str, image_property[lower_column_property])
        return default_value

    @staticmethod
    def get_image_column_name(ds: AmlDataset, default_image_column_name: str) -> str:
        """Get the image column name by inspecting AmlDataset properties.
        Return default_image_column_name if not found in properties.

        :param ds: Aml Dataset object
        :type ds: TabularDataset (Labeled) or FileDataset
        :param default_image_column_name: default value to return
        :type default_image_column_name: str
        :return: Image column name
        :rtype: str
        """
        return AmlDatasetHelper._get_column_name(ds,
                                                 AmlDatasetHelper.IMAGE_COLUMN_PROPERTY,
                                                 default_image_column_name)

    @staticmethod
    def get_label_column_name(ds: AmlDataset, default_label_column_name: str) -> str:
        """Get the label column name by inspecting AmlDataset properties.
        Return default_label_column_name if not found in properties.

        :param ds: Aml Dataset object
        :type ds: TabularDataset (Labeled) or FileDataset
        :param default_label_column_name: default value to return
        :type default_label_column_name: str
        :return: Label column name
        :rtype: str
        """
        return AmlDatasetHelper._get_column_name(ds,
                                                 AmlDatasetHelper.LABEL_COLUMN_PROPERTY,
                                                 default_label_column_name)

    @staticmethod
    def is_labeled_dataset(ds: AmlDataset) -> bool:
        """Check if the dataset is a labeled dataset. In the current approach, we rely on the presence of
        certain properties to check for labeled dataset.

        :param ds: Aml Dataset object
        :type ds: TabularDataset or TabularDataset (Labeled)
        :return: Labeled dataset or not
        :rtype: bool
        """
        return AmlDatasetHelper.IMAGE_COLUMN_PROPERTY in ds._properties

    @staticmethod
    def download_image_files(ds: AmlDataset, image_column_name: str) -> None:
        """Helper method to download dataset files.

        :param ds: Aml Dataset object
        :type ds: TabularDataset (Labeled) or FileDataset
        :param image_column_name: The column name for the image file.
        :type image_column_name: str
        """
        AmlDatasetHelper._validate_image_column(ds, image_column_name)
        logger.info("Start downloading image files")
        start_time = time.perf_counter()
        data_dir = AmlDatasetHelper.get_data_dir()
        try:
            if AmlDatasetHelper.is_labeled_dataset(ds):
                ds._dataflow.write_streams(image_column_name, dprep.LocalFileOutput(data_dir)).run_local()
            else:  # TabularDataset
                ds.download(image_column_name, data_dir, overwrite=True)
        except (ExecutionError, UserErrorException, AzureMLException) as e:
            # AzureMLException is a temporary catch all until dprep refines the errors into UserErrorException
            raise AutoMLVisionDataException(
                f"Could not download dataset files. "
                f"Please check the logs for more details. Error Code: {e}")

        logger.info(f"Downloading image files took {time.perf_counter() - start_time:.2f} seconds")

    @staticmethod
    def mount_image_file_datastores(ds: AmlDataset, image_column_name: str, workspace: Workspace) -> None:
        """Mount datastores containing image files.

        :param ds: Aml Dataset object
        :type ds: azureml.core.Dataset
        :param image_column_name: The column name for the image file.
        :type image_column_name: str
        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        """
        # Convert the AML dataset to pandas.
        try:
            # (Why we're calling to_pandas_dataframe twice but with different arguments:
            # The first call (using on_error="fail") raises an exception if there's an error in the Dataset.
            # We can't use on_error="fail" together with extended_types=True because if extended_types=True is
            # part of the call, the on_error="fail" parameter is ignored. The extended_types=True parameter
            # is helpful because the resulting DataFrame contains structured information about the Datastore
            # and handler protocol (used below).)
            ds._dataflow.to_pandas_dataframe(on_error="fail")
            df = ds._dataflow.to_pandas_dataframe(extended_types=True)
        except (ExecutionError, UserErrorException, ValidationError) as e:
            raise AutoMLVisionDataException(
                f"Could not convert the dataset to a pandas data frame. "
                f"Please check the logs for more details. Error Code: {e}")
        AmlDatasetHelper._validate_image_column(ds, image_column_name)
        # Find all datastores referenced by the dataset.
        datastore_names = set()
        for image_stream_info in df[image_column_name]:
            pod = image_stream_info.to_pod()
            handler = pod.get(AmlDatasetHelper.STREAM_INFO_HANDLER_PROPERTY)
            if handler != AmlDatasetHelper.DATASTORE_HANDLER_NAME:
                raise AutoMLVisionDataException(
                    "Streaming images is only supported if all image files are contained in an AML datastore. "
                    f"Reading directly from the {handler} protocol is not supported at this time.")
            datastore_name = pod["arguments"]["datastoreName"]
            datastore_names.add(datastore_name)

        # Mount all datastores.
        for datastore_name in datastore_names:
            AmlDatasetHelper.mount_datastore(datastore_name, workspace)

    # A dictionary of datastore names to datastore mount contexts (for mounted datastores).
    datastores_to_mount_contexts = {}

    @classmethod
    def mount_datastore(cls, datastore_name: str, workspace: Workspace) -> None:
        """Mount a datastore to local disk.

        :param datastore_name: Datastore name.
        :type datastore_name: str
        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        """
        # Only mount a datastore if it has not been mounted already.
        if datastore_name in cls.datastores_to_mount_contexts:
            return

        try:
            logger.info("Begin datastore mount.")
            datastore = Datastore.get(workspace, datastore_name)
            dataset = AmlDataset.File.from_files((datastore, "/"))
            mount_context = dataset.mount(mount_point=os.path.join(AmlDatasetHelper.get_data_dir(), datastore_name))
            mount_context.start()
            logger.info("Datastore successfully mounted.")

            # Store the mounted context for the datastore.
            # This serves a couple purposes:
            # - This allows us to keep track of all datastores that have been mounted. Mounting a datastore twice
            #   to the same directory results in an exception.
            # - The mount context is not used again anywhere explicitly, but it must be kept around in memory.
            #   Otherwise, if a reference to the context is not kept, the context is garbage collected, and the mount
            #   stops working.
            cls.datastores_to_mount_contexts[datastore_name] = mount_context
        except UserErrorException as e:
            raise AutoMLVisionDataException(
                f"Could not mount datastore. "
                f"Please check the logs for more details. Error Code: {e}"
            )

    @staticmethod
    def _validate_image_column(ds: AmlDataset, image_column_name: str) -> None:
        """Helper method to validate if image column is present in dataset, and it's type is STREAM.

        :param ds: Aml Dataset object
        :type ds: TabularDataset (Labeled) or FileDataset
        :param image_column_name: The column name for the image file.
        :type image_column_name: str
        """
        try:
            dtypes = ds._dataflow.dtypes
        except (ExecutionError, ValidationError) as e:
            raise AutoMLVisionDataException(
                f"Could not validate dataset column types (could be a permission error). "
                f"Please check the logs for more details. Error Code: {e}")

        if image_column_name not in dtypes:
            raise AutoMLVisionDataException(f"Image URL column '{image_column_name}' is not present in the dataset.")

        image_column_dtype = dtypes.get(image_column_name)
        if image_column_dtype != FieldType.STREAM:
            raise AutoMLVisionDataException(
                f"The data type of image URL column '{image_column_name}' is {image_column_dtype.name}, "
                f"but it should be {FieldType.STREAM.name}.")
