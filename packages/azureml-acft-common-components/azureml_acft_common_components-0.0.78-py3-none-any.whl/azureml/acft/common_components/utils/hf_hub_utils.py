# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utility functions for hugging face hub."""

from typing import List

from .logging_utils import get_logger_app

logger = get_logger_app(__name__)


def check_if_model_present_in_hf_hub(model_name: str) -> List:
    """Check if model name is present in the Hugging Face model repository.
    :param model_name: Model name to be validated.
    :type model_name: str
    :return: List of model info objects.
    :rtype: List
    """
    try:
        from huggingface_hub import HfApi

        api = HfApi()
        model_info_list = api.list_models(search=model_name)
        model_info_list = [model_info for model_info in model_info_list if model_info.modelId == model_name]
        return model_info_list
    except ImportError:
        logger.warning("Please install huggingface_hub to use validate_hf_model_name function.")
