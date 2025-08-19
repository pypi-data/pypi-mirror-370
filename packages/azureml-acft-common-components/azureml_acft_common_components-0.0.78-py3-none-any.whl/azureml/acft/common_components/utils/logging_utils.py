# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This file defines the util functions used for logging
"""
from typing import Any, Dict, Optional, cast, List
import logging
import os
import sys

from dataclasses import dataclass, asdict

from azureml.acft.common_components.utils.constants import AzuremlRunType
from azureml.acft.common_components.utils.telemetry_pii_stripping_formatter import (
    AppInsightsPIIStrippingAllMessagesFormatter,
)
from azureml.automl.core.shared import log_server
from azureml.automl.core.shared.logging_fields import camel_to_snake_case
from azureml.core import Run
from azureml.core.run import _OfflineRun

from azureml.automl.core.shared.telemetry_formatter import AppInsightsPIIStrippingFormatter
from azureml.telemetry import get_diagnostics_collection_info, INSTRUMENTATION_KEY
from azureml.telemetry.contracts import RequiredFieldKeys, StandardFieldKeys
from azureml.telemetry.logging_handler import AppInsightsLoggingHandler


TELEMETRY_AZUREML_ACFT_COMPONENT_KEY = "azureml.acft"
UNKNOWN_VALUE = "UNKNOWN"


class LoggingLiterals:
    """Literals that help logging and correlating different training runs."""

    PROJECT_NAME = "project_name"
    PROJECT_VERSION_NUMBER = "project_version_number"
    TASK_TYPE = "task_type"
    LOG_FOLDER = "log_folder"
    LOG_FILENAME = "log_filename"
    RANK = "rank"
    PROPERTIES = "properties"
    STDOUT = "stdout"
    APP_NAME = "app_name"
    COMPONENT_NAME = "component_name"


class SystemSettings:
    """System settings."""

    LOG_FILENAME = "azureml_acft.log"
    LOG_FOLDER = "logs"
    DEFAULT_APP_NAME = "acft"
    DEFAULT_COMPUTE_TARGETS = "AmlCompute"
    DEFAULT_CLIENT_TYPE = "sdk"
    LOG_LEVEL_DEBUG = "log_level_debug"


@dataclass
class AzuremlAcftSettings:
    """AzureAcftSettings class to configure logging."""

    task_type: str
    subscription_id: str
    region: str
    parent_run_id: str
    run_id: str
    child_run_id: str
    app_name: str = SystemSettings.DEFAULT_APP_NAME
    azureml_acft_common_components_version: str = UNKNOWN_VALUE
    azureml_acft_accelerator_version: str = UNKNOWN_VALUE
    compute_target: str = SystemSettings.DEFAULT_COMPUTE_TARGETS
    client_type: str = SystemSettings.DEFAULT_CLIENT_TYPE


class ProcessRankLoggingFilter(logging.Filter):
    """Filter to add process rank information to log records."""

    def filter(self, record: Any) -> bool:
        """Add process rank information to the log record if running in distributed mode.
        No op otherwise.
        The information is added to the properties attribute as this attribute is merged into
        custom dimensions by log_server and is reported to AppInsights.
        (See LogRecordStreamHandler.handle_log_record in azureml.automl.core.shared.log_server)

        :param record: log record
        :type record: logging.LogRecord
        :return: Flag to indicate if this specific record has to be logged.
        :rtype: bool
        """
        try:
            from torch import distributed as dist
        except ImportError:
            return True
        if dist.is_available() and dist.is_initialized():
            process_rank_property = {LoggingLiterals.RANK: cast(int, dist.get_rank())}
            if hasattr(record, LoggingLiterals.PROPERTIES):
                record.properties.update(process_rank_property)
            else:
                record.properties = process_rank_property
        return True


def get_logger_app(name: str) -> logging.Logger:
    """Get a logger object with the specified name. This function adds a ProcessRankLoggingFilter to the returned
    logger so that logs output will have rank information.

    :param name: name of the logger
    :type name: str
    :return: logger object.
    :rtype: logging.Logger
    """
    name_logger = logging.getLogger(name)
    name_logger.addFilter(ProcessRankLoggingFilter())
    return name_logger


def is_debug_logging_enabled() -> bool:
    """Check if debug logging is enabled.

    :return: True if debug logging is enabled, False otherwise.
    :rtype: bool
    """
    return os.getenv(SystemSettings.LOG_LEVEL_DEBUG, 'False').lower() == 'true'


def set_logging_parameters(
    task_type: str,
    output_dir: Optional[str] = None,
    output_file: Optional[str] = None,
    acft_custom_dimensions: Optional[Dict] = None,
    hf_logs_to_app_insight: Optional[bool] = True,
    azureml_pkg_denylist_logging_patterns: Optional[List] = None,
    non_azureml_packages_to_disable_logs: Optional[List] = None,
    log_level: int = logging.DEBUG,
) -> None:
    """Sets the logging parameters so that we can track all the training runs from
    a given project.

    :param task_type: task type
    :type task_type: str
    :param output_dir: output directory of log file
    :type output_dir: Optional[str]
    :param output_file: name of the file for logging
    :type output_file: Optional[str]
    :param acft_custom_dimensions: custom information to add in log messages
    :type acft_custom_dimensions: Optional[Dict]
    :param hf_logs_to_app_insight: add app insight handler to HF trainer logger, if true
    :type hf_logs_to_app_insight: Optional[bool]
    :param azureml_pkg_denylist_logging_patterns: Substrings patterns that would be used to identify the logs to
                                                exclude from Azure ML package logs.
    :type azureml_pkg_denylist_logging_patterns: Optional[List]
    :param disable_non_azureml_package_logs: List of non-Azure ML package names to disable logs for.
    :type disable_non_azureml_package_logs: Optional[List]
    """

    output_dir = output_dir or SystemSettings.LOG_FOLDER
    logging_file = output_file or SystemSettings.LOG_FILENAME

    azureml_run = Run.get_context()
    _set_default_custom_dimensions_and_handlers(task_type, output_dir, logging_file, azureml_run, log_level)

    _set_acft_custom_dimensions(acft_custom_dimensions)

    _set_formatter_to_handlers(
        log_server.handlers,
        azureml_run.id,
        hf_logs_to_app_insight,
        azureml_pkg_denylist_logging_patterns,
        non_azureml_packages_to_disable_logs,
    )
    if hf_logs_to_app_insight:
        _add_app_insights_handler_to_hf_logger(log_server.handlers)


def _set_formatter_to_handlers(
    handlers: Dict[str, logging.Handler],
    run_id: str,
    hf_logs_to_app_insight: bool,
    azureml_pkg_denylist_logging_patterns: Optional[List] = None,
    non_azureml_packages_to_disable_logs: Optional[List] = None,
) -> None:
    """Set formatter to the handlers
    :param handlers: handlers added in logger
    :type handlers: Dict[str, logging.Handler]
    :param run_id: run id
    :type run_id: str
    :param hf_logs_to_app_insight: flag to indicate whether to add app insights handler to HuggingFace logger. If
    true, then add AppInsightsPIIStrippingAllMessagesFormatter which strip PII information from all logs messages (
    info, warning, error, exceptions) else use AppInsightsPIIStrippingFormatter which strips exception messages.
    :type hf_logs_to_app_insight: bool
    :param azureml_pkg_denylist_logging_patterns: Substring patterns that would be used to identify the logs to exclude
                                               from Azure ML package logs.
    :type azureml_pkg_denylist_logging_patterns: Optional[List]
    :param disable_non_azureml_package_logs: List of non-Azure ML package names to disable logs for.
    :type disable_non_azureml_package_logs: Optional[List]
    """

    fmt = (
        "%(asctime)s.%(msecs)03d - {} - {} - %(levelname)s - %(process)d - %(name)s.%(funcName)s:%(lineno)d - %("
        "message)s".format(SystemSettings.DEFAULT_APP_NAME, run_id)
    )
    datefmt = "%Y-%m-%d %H:%M:%S"
    for key, handler in handlers.items():
        if isinstance(handler, AppInsightsLoggingHandler) and not is_debug_logging_enabled():
            if hf_logs_to_app_insight:
                formatter = AppInsightsPIIStrippingAllMessagesFormatter(
                    fmt=fmt,
                    datefmt=datefmt,
                    azureml_pkg_denylist_logging_patterns=azureml_pkg_denylist_logging_patterns,
                    non_azureml_packages_to_disable_logs=non_azureml_packages_to_disable_logs,
                )
            else:
                formatter = AppInsightsPIIStrippingFormatter(fmt=fmt, datefmt=datefmt)
        else:
            formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

        handler.setFormatter(formatter)


def _set_acft_custom_dimensions(acft_custom_dimensions: Dict) -> None:
    """Add acft custom dimensions to the log server's custom dimensions.
    :param acft_custom_dimensions: custom dimensions related to the acft project
    :type acft_custom_dimensions: Dict
    """
    if acft_custom_dimensions and LoggingLiterals.PROJECT_NAME in acft_custom_dimensions:
        project_name = acft_custom_dimensions[LoggingLiterals.PROJECT_NAME]
        log_server.update_custom_dimensions({LoggingLiterals.PROJECT_NAME: project_name})

    if acft_custom_dimensions and LoggingLiterals.PROJECT_VERSION_NUMBER in acft_custom_dimensions:
        project_version_number = acft_custom_dimensions[LoggingLiterals.PROJECT_VERSION_NUMBER]
        log_server.update_custom_dimensions({LoggingLiterals.PROJECT_VERSION_NUMBER: project_version_number})

    if acft_custom_dimensions and LoggingLiterals.COMPONENT_NAME in acft_custom_dimensions:
        component_name = acft_custom_dimensions[LoggingLiterals.COMPONENT_NAME]
        log_server.update_custom_dimensions({LoggingLiterals.COMPONENT_NAME: component_name})


def _get_azureml_acft_common_components_version() -> str:
    """Get version of azureml.acft.common_components package"""
    try:
        from azureml.acft import common_components

        return common_components.VERSION
    except Exception:
        return UNKNOWN_VALUE


def _get_azureml_acft_accelerator_version() -> str:
    """Get version of azureml.acft.accelerator package"""
    try:
        from azureml.acft import accelerator

        return accelerator.VERSION
    except Exception:
        return UNKNOWN_VALUE


def _get_root_pipeline_run(azureml_run: Run):
    """
    Get root pipeline run. Root pipeline run is the pipeline/step run which is at the root in the run hierarchy
    or is child of a non-pipeline/step run (for example, when pipeline run is child of HyperDrive run).

    :param azureml_run: Current run.
    :type azureml_run: azureml.core.Run
    :return: Root pipeline run if exists else None.
    :rtype: azureml.core.Run
    """
    parent_run = azureml_run.parent
    child_run = None
    while parent_run is not None and (
        parent_run.type == AzuremlRunType.PIPELINE_RUN or parent_run.type == AzuremlRunType.STEP_RUN
    ):
        child_run = parent_run
        parent_run = parent_run.parent
    return child_run


def _set_default_custom_dimensions_and_handlers(
    task_type: str, output_dir: str, logging_file: str, azureml_run: Run, log_level: int = logging.DEBUG
) -> None:
    """Add current run custom dimensions information and handlers (file, stream and app insights) to log server

    :param task_type: task type
    :type task_type: str
    :param output_dir: output directory of log file
    :type output_dir: str
    :param logging_file: name of the file for logging
    :type logging_file: str
    """
    if not isinstance(azureml_run, _OfflineRun):
        subscription_id = azureml_run.experiment.workspace.subscription_id
        region = azureml_run.experiment.workspace.location
        root_pipeline_run = _get_root_pipeline_run(azureml_run=azureml_run)
        parent_run_id = root_pipeline_run.id if root_pipeline_run is not None else None
    else:
        subscription_id = "not_available_offline"
        region = "not_available_offline"
        parent_run_id = "not_available_offline"
    child_run_id = azureml_run.id

    # Build the acft settings expected by the logger
    acft_settings = AzuremlAcftSettings(
        task_type=task_type,
        subscription_id=subscription_id,
        region=region,
        parent_run_id=parent_run_id,
        run_id=child_run_id,
        child_run_id=child_run_id,
        azureml_acft_common_components_version=_get_azureml_acft_common_components_version(),
        azureml_acft_accelerator_version=_get_azureml_acft_accelerator_version(),
    )
    log_server.update_custom_dimensions(asdict(acft_settings))

    component_name_literal = camel_to_snake_case(RequiredFieldKeys.COMPONENT_NAME_KEY)
    algorithm_type_literal = camel_to_snake_case(StandardFieldKeys.ALGORITHM_TYPE_KEY)
    subscription_id_literal = camel_to_snake_case(RequiredFieldKeys.SUBSCRIPTION_ID_KEY)

    log_server.update_custom_dimensions(
        {
            component_name_literal: TELEMETRY_AZUREML_ACFT_COMPONENT_KEY,
            algorithm_type_literal: task_type,
            subscription_id_literal: subscription_id,
        }
    )

    os.makedirs(output_dir, exist_ok=True)
    # :func set_log_file - adds a file handler to handlers global variable
    log_server.set_log_file(os.path.join(output_dir, logging_file))
    # Setting the log level for the file handler
    if "file" in log_server.handlers and isinstance(log_server.handlers["file"], logging.FileHandler):
        log_server.handlers["file"].setLevel(log_level)
    _add_stream_handler(log_level)
    send_telemetry, level = get_diagnostics_collection_info(component_name=TELEMETRY_AZUREML_ACFT_COMPONENT_KEY)
    if send_telemetry:
        log_server.enable_telemetry(INSTRUMENTATION_KEY, component_name=TELEMETRY_AZUREML_ACFT_COMPONENT_KEY)
    log_server.set_verbosity(level)


def _add_stream_handler(log_level: int = logging.DEBUG) -> None:
    """Add console handler i.e., stream handler"""

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(log_level)
    log_server.add_handler(LoggingLiterals.STDOUT, stdout_handler)


def _add_app_insights_handler_to_hf_logger(handlers: Dict) -> None:
    """Set the app insight handler to all hf logger

    :param handlers: The dictionary of handlers attached to log server
    :type handlers: Dict
    """
    try:
        import transformers

        transformers.logging.disable_default_handler()
    except ImportError:
        transformers = None

    try:
        import datasets
    except ImportError:
        datasets = None

    try:
        from deepspeed.utils import logger as deepspeed_logger
    except ImportError:
        deepspeed_logger = None

    try:
        from optimum.utils import logging as optimum_logging
    except ImportError:
        optimum_logging = None

    for key, handler in handlers.items():
        if transformers:
            transformers.logging.set_verbosity_debug()
            transformers.logging.add_handler(handler)

        if datasets:
            datasets.logging.get_logger().setLevel(handler.level)
            datasets.logging.get_logger().addHandler(handler)

        if deepspeed_logger:
            deepspeed_logger.setLevel(handler.level)
            deepspeed_logger.addHandler(handler)

        if optimum_logging:
            optimum_logging.set_verbosity_info()
            optimum_logging.add_handler(handler)
