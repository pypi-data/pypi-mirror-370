# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
This file defines torch utilities.
"""

from typing import Union

from .constants import UNKNOWN_VALUE


def get_node_gpu_count() -> Union[int, str]:
    """Calculate the GPU count of a given compute."""
    try:
        import torch
        return torch.cuda.device_count()
    except Exception:
        return UNKNOWN_VALUE
