# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
This file defines transformer related utilities. Call this file before calling transformer modules.
"""

import os
from pathlib import Path

from .constants import TransformerConstants


# This is set to avoid cache invalidation problem when accessing remote code b/w multiple processes.
os.environ[TransformerConstants.HF_MODULES_CACHE] = str(
    Path(
        TransformerConstants.ROOT_CACHE_FOLDER,
        TransformerConstants.HF_MODULES_CACHE + f'.{os.environ.get("RANK", "main")}'
    )
)
