# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This file contains telemetry PII stripping formatter."""

from logging import LogRecord
from typing import Dict, Tuple, List, Optional
from azureml.automl.core.shared.exceptions import NON_PII_MESSAGE
from azureml.automl.core.shared.telemetry_formatter import AppInsightsPIIStrippingFormatter
from azureml.acft.common_components.utils.constants import (
    NonAzureMLLoggingLibsAllowedPatterns,
    LoggingLibsIdentifier,
)


class AppInsightsPIIStrippingAllMessagesFormatter(AppInsightsPIIStrippingFormatter):
    """Formatter that will prevent any PII debug/info/warning/exception from getting logged"""

    def __init__(
        self,
        *args,
        azureml_pkg_denylist_logging_patterns: Optional[List] = None,
        non_azureml_packages_to_disable_logs: Optional[List] = None,
        **kwargs
    ):
        """
        Initialize a new instance of AppInsightsPIIStrippingAllMessagesFormatter.

        :param azureml_pkg_denylist_logging_patterns: Substring patterns that would be used to identify the logs to
                                                        exclude from Azure ML package logs.
        :type azureml_pkg_denylist_logging_patterns: Optional[List]
        :param disable_non_azureml_package_logs: List of non-Azure ML package names to disable logs for.
        :type disable_non_azureml_package_logs: Optional[List]
        """
        super().__init__(*args, **kwargs)

        self.azureml_pkg_denylist_logging_patterns = azureml_pkg_denylist_logging_patterns or []
        self.non_azureml_packages_to_disable_logs = non_azureml_packages_to_disable_logs or []

        self.non_azureml_pkg_allowlist_logging_patterns = self._prepare_allowlist_patterns_for_non_azureml_packages()

    def _prepare_allowlist_patterns_for_non_azureml_packages(self) -> Dict[str, Tuple[str]]:
        """Prepare allowlist patterns for non-AzureML packages

        :return: Dict of allowlist patterns
        :rtype: Dict[str, Tuple[str]]
        """

        lib_to_allowlist_patterns = {}

        for lib, patterns in NonAzureMLLoggingLibsAllowedPatterns.NON_AZUREML_PKGS_IDENTIFIER_PATTERNS_MAPPING.items():
            if lib not in self.non_azureml_packages_to_disable_logs:
                lib_to_allowlist_patterns[lib] = patterns
        return lib_to_allowlist_patterns

    def format(self, record: LogRecord) -> str:
        """
        Modify the log record to strip log messages if they originate from a non-AzureML packages and not matches
        the allowed pattern to log in appinsights for corresponding non-AzureML package or if they originate from
        AzureML packages and not matches the denylist pattern to log in appinsights for AzureML package.

        :param record: Logging record.
        :return: Formatted record message.
        """
        message = record.getMessage().lower()
        is_azureml_package = record.name.startswith(LoggingLibsIdentifier.AZUREML)

        if (
            is_azureml_package
            and not any(pattern.lower() in message for pattern in self.azureml_pkg_denylist_logging_patterns)
        ) or any(
            (record.name.startswith(non_azureml_pkg) and any(pattern.lower() in message for pattern in patterns))
            for non_azureml_pkg, patterns in self.non_azureml_pkg_allowlist_logging_patterns.items()
        ):
            return super().format(record)

        record.message = NON_PII_MESSAGE
        record.msg = NON_PII_MESSAGE
        return super().format(record)
