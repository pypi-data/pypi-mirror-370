# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2020 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------

"""This file defines the util functions used for downloading license file."""

import os
from pathlib import Path
from shutil import copyfile
import shutil
from typing import List

from .logging_utils import get_logger_app

logger = get_logger_app(__name__)

HF_REPO_LICENSE_FILE_NAME = "LICENSE"


def download_license_file_from_hf_repo(model_id: str, destination_paths: List[str]) -> bool:
    """
    Download the LICENSE file of Hugging Face models from the model repo.
    :param model_id: The model id of the model's license to download.
    :type model_id: str
    :param destination_paths: List of path to download the license file to.
    :type destination_paths: List[str]
    :return: True if the license file is downloaded successfully, False otherwise.
    :rtype: bool
    """
    from huggingface_hub import hf_hub_download
    try:
        license_file = hf_hub_download(
            repo_id=model_id,
            filename=HF_REPO_LICENSE_FILE_NAME,
        )
        for destination_path in destination_paths:
            copyfile(license_file, str(Path(destination_path, HF_REPO_LICENSE_FILE_NAME)))
        return True
    except Exception:
        return False


def save_license_file(model_name_or_path, license_file_name, destination_paths: List[str]) -> bool:
    """
    Save the license file to the model directory.
    :param model_name_or_path: The model name (hf id) or path.
    :type model_name_or_path: str
    :param license_file_name: The name of the license file.
    :type license_file_name: str
    :param destination_paths: The path to save the license file to.
    :type destination_paths: List[str]
    :return: True if the license file is saved successfully, False otherwise.
    :rtype: bool
    """
    is_success = False
    destination_paths = [path for path in destination_paths if os.path.exists(path) and os.path.isdir(path)]

    if model_name_or_path:
        license_file_path = os.path.join(model_name_or_path, license_file_name)
        if os.path.exists(license_file_path) and os.path.isfile(license_file_path):
            for destination_path in destination_paths:
                shutil.copy(license_file_path, destination_path)
            is_success = True
        else:
            is_success = download_license_file_from_hf_repo(model_name_or_path, destination_paths)
    if is_success:
        logger.info(f"LICENSE file is copied to {','.join(destination_paths)}")
    else:
        logger.warning(
            f"Unable to fetch LICENSE file for {model_name_or_path}. "
            f"It is the responsibility of the user to set LICENSE file for the model in {','.join(destination_paths)}."
        )
    return is_success
