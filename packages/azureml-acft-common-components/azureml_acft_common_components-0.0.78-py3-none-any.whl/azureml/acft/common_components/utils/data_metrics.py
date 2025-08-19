# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utility functions to calculate preprocessing metrics."""

import numpy as np
from typing import List, Optional
from dataclasses import dataclass

from datasets.load import Dataset

from .logging_utils import get_logger_app
from .error_handling.exceptions import ACFTSystemException
from .error_handling.error_definitions import ACFTSystemError

from azureml._common._error_definition.azureml_error import AzureMLError


logger = get_logger_app(__name__)


@dataclass(frozen=True)
class TokenDistribution:
    """Dataclass to store token distribution."""
    cumulative_tokens: int
    min_token_length: int
    max_token_length: int
    mean_token_length: float
    median_token_length: np.floating
    percentile_90_token_length: np.floating
    percentile_10_token_length: np.floating

    @classmethod
    def from_list(cls, list_tokens: List[int]):
        """Calculate the token distribution.

        The distribution calculation is copied from https://cookbook.openai.com/examples/chat_finetuning_data_prep.
        """
        if list_tokens is None:
            logger.warning("Token distribution cannot be calculated as no input is passed.")
            return None
        if not isinstance(list_tokens, list):
            logger.warning(
                "Token distribution cannot be calculated due to dtype mismatch. "
                f"Expected input type: list. Found - {type(list_tokens)}"
            )
            return None
        np_array_tokens = np.array(list_tokens)
        if not issubclass(np_array_tokens.dtype.type, (np.integer, np.floating)):
            logger.warning(
                "Token distribution cannot be calculated due to dtype mismatch. "
                f"Expected input type: list[int]. Found - list[{np_array_tokens.dtype}]"
            )
            return None

        return TokenDistribution(
            cumulative_tokens=np_array_tokens.sum(),
            min_token_length=np_array_tokens.min(),
            max_token_length=np_array_tokens.max(),
            mean_token_length=np_array_tokens.mean(),
            median_token_length=np.median(np_array_tokens),
            percentile_90_token_length=np.quantile(np_array_tokens, 0.9),
            percentile_10_token_length=np.quantile(np_array_tokens, 0.1)
        )

    def __repr__(self) -> str:
        """String representation."""
        return str(self.__dict__)


def calculate_token_distribution(
    tokenized_dataset: Dataset, column_to_use: str = "input_ids", ignore_token_id: int = -100
) -> Optional[TokenDistribution]:
    """Calculate the token distribution for the tokenized dataset.

    :param tokenized_dataset - dataset after converting text to tokens
    :type Dataset
    :param column_to_use - column name to use for getting the token distribution.
    :type string
    :param ignore_token_id - This token id will be ignored while calculating the token length for each example.
    :type int
    :param Returns the token distribution
    :rtype Optional[TokenDistribution]
    """
    if column_to_use not in tokenized_dataset.column_names:
        raise ACFTSystemException._with_error(
            AzureMLError.create(
                ACFTSystemError,
                pii_safe_message=(
                    f"{column_to_use} not present in the tokenized dataset. "
                    f"Possible columns are: {tokenized_dataset.column_names}"
                )
            )
        )

    def _calculate_len_post_filter(single_example: List[int]) -> int:
        """Filter the example for :param `ignore_token_id` and calculate the token length."""
        return len(list(filter(lambda x: x != ignore_token_id, single_example)))

    return TokenDistribution.from_list(list(map(_calculate_len_post_filter, tokenized_dataset[column_to_use])))
