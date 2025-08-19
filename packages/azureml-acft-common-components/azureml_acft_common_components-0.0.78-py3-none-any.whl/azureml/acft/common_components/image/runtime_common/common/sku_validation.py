# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper Utils for sku validation."""

import pynvml
import torch

from azureml.acft.common_components import get_logger_app
from .exceptions import AutoMLVisionValidationException
from . import distributed_utils

MEGABYTE = 1024.0 * 1024.0
# Set MIN_GPU_MEM to be between 11321.8750MB (the max observed gpu mem consumption)
# and 11,441.1875MB (NC6 GPU mem size got by pynvml).
MIN_GPU_MEM = 11400 * MEGABYTE

logger = get_logger_app(__name__)


def validate_gpu_sku(device: str, min_gpu_mem: float = MIN_GPU_MEM) -> None:
    """Validate gpu sku requirements.

    :param device: Target device
    :type device: Pytorch device or str
    :param min_gpu_mem: the min value of the gpu mem.
    :type min_gpu_mem: int
    """

    if device == 'cpu' or not torch.cuda.is_available() or not distributed_utils.master_process():
        return
    min_free_gpu_memory = max(0, min_gpu_mem - 400 * MEGABYTE)
    # Keeping a buffer of 400 MB for the OS. Checking if atleast
    # 11000 MB is availble.
    pynvml.nvmlInit()
    try:
        is_valid = True
        per_device_infos = []
        device_count = pynvml.nvmlDeviceGetCount()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            if mem_info.total < min_gpu_mem:
                is_valid = False
                per_device_infos.append(
                    "{}: mem_info_total:({} MB) is smaller than min_gpu_mem:({} MB)".format(
                        pynvml.nvmlDeviceGetName(handle),
                        mem_info.total / MEGABYTE,
                        min_gpu_mem / MEGABYTE
                    )
                )
            elif mem_info.free < min_free_gpu_memory:
                is_valid = False
                per_device_infos.append(
                    "{}: Available mem_info_free:({} MB) is smaller than min_free_gpu_mem:({} MB) required."
                    "Please free some GPU RAM before submitting the run".format(
                        pynvml.nvmlDeviceGetName(handle),
                        mem_info.free / MEGABYTE,
                        min_free_gpu_memory / MEGABYTE
                    )
                )
        if is_valid:
            logger.info("GPU memory validated to be above the minimum threshold of {} MB."
                        .format(min_gpu_mem / MEGABYTE))
        else:
            error = "Failed to validate gpu sku requirements. {}".format("; ".join(per_device_infos))
            logger.error(error)
            raise AutoMLVisionValidationException(error, has_pii=False)
    except pynvml.NVMLError as error:
        logger.info("Exception while validating gpu sku requirements. {}".format(error))
    finally:
        pynvml.nvmlShutdown()
