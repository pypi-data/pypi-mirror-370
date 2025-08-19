# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper Utils for distributed mode."""
import logging
import json
import os
import pickle
import sys
import torch
from torch import Tensor
import torch.distributed as dist
from typing import Any, Callable, Dict, List, cast, Tuple, Union, Optional

from azureml.automl.core._logging import log_server
from azureml.core import Run

from .constants import DistributedLiterals, DistributedParameters
from .exceptions import AutoMLVisionSystemException, AutoMLVisionValidationException, AutoMLVisionRuntimeUserException


def dist_available_and_initialized() -> bool:
    """ Check if distributed mode is available and is initialized.

    :return: distributed mode or not.
    :rtype: bool
    """
    return cast(bool, dist.is_available() and dist.is_initialized())


def get_world_size() -> int:
    """ Get the world size when running in distributed mode.
    Returns 1 if not in distributed mode.

    :return: world_size
    :rtype: int
    """
    if dist_available_and_initialized():
        return cast(int, dist.get_world_size())
    return 1


def get_rank() -> int:
    """Get the rank of the current process when running in distributed mode.
    Returns 0 if not in distributed mode.

    :return: rank
    :rtype: int
    """
    if dist_available_and_initialized():
        return cast(int, dist.get_rank())
    return 0


def master_process() -> bool:
    """ Return if the current process is the master process.
    If in distributed mode, return true for process with rank 0.
    Else, return True.

    :return: If the current process is the master process.
    :rtype: bool
    """
    return get_rank() == 0


def all_gather(data: Any) -> List[Any]:
    """Run distributed all_gather on pickle-able objects.

    Note (Important!!!):
        Make sure that "data" entirely resides in cpu memory. There are deadlocks otherwise.

        - Say Process P0 uses cuda:0 and P1 uses cuda:1. In this function, the data is pickled and converted
          to a tensor on current gpu before calling dist.all_gather(). Data from P0 (say D0) has device cuda:0 and
          data from P1 (say D1) has device cuda:1.
        - During the dist.all_gather() call, data is moved to the target gpu on which it is requested.
          After dist.all_gather() call, P0 gets [D0, D1] in tensor_list and both of them have device "cuda:0".
          P1 gets [D0, D1] in tensor_list and both of them have device "cuda:1".
        - When some values in data are on gpu, the dist.all_gather() does not move those values to the target gpu.
          This results in memory on a gpu being accessed by two processes, which results in deadlocks and stuck runs.

    Note: This code has been copied from PyTorch example code here:
    https://github.com/pytorch/vision/blob/master/references/detection/utils.py#L75

    :param data: data that has be to be gathered on all processes.
    :type data: any
    :return: List of data objects from all processes.
    :rtype: List
    """
    world_size = get_world_size()
    if world_size == 1:
        return [data]

    device = 'cuda'

    # serialized to a Tensor
    buffer = pickle.dumps(data)
    storage = torch.ByteStorage.from_buffer(buffer)
    tensor = torch.ByteTensor(storage).to(device)

    # obtain Tensor size of each rank
    local_size = torch.tensor([tensor.numel()], device=device)
    size_list = [torch.tensor([0], device=device) for _ in range(world_size)]
    dist.all_gather(size_list, local_size)
    size_list_int = [int(size.item()) for size in size_list]
    max_size = max(size_list_int)

    # receiving Tensor from all ranks
    # we pad the tensor because torch all_gather does not support
    # gathering tensors of different shapes
    tensor_list = []
    for _ in size_list_int:
        tensor_list.append(torch.empty((max_size,), dtype=torch.uint8, device=device))
    if local_size != max_size:
        padding = torch.empty(size=(max_size - local_size,), dtype=torch.uint8, device=device)
        tensor = torch.cat((tensor, padding), dim=0)
    dist.all_gather(tensor_list, tensor)

    data_list = []
    for size, tensor in zip(size_list_int, tensor_list):
        buffer = tensor.cpu().numpy().tobytes()[:size]
        data_list.append(pickle.loads(buffer))

    return data_list


def all_gather_uneven_tensors(input_tensor: Tensor) -> List[Tensor]:
    """Run distributed all_gather on tensors with size only differing in first dimension.

    Assumptions:
        - The tensor should be on the current gpu device.
        - The tensors being gathered from all processes
            - should have same number of dimensions and
            - should have same size in all dimensions other than dimension 0

    :param input_tensor: tensor that has to be gathered on all processes.
    :type input_tensor: torch.Tensor
    :return: List of tensors gathered from all processes.
    :rtype: List[torch.Tensor]
    """
    world_size = get_world_size()
    if world_size == 1:
        return [input_tensor]

    # obtain tensor size of each rank
    local_size = torch.tensor(input_tensor.size(), dtype=torch.long, device="cuda")
    size_list = [torch.zeros(input_tensor.ndim, dtype=torch.long, device="cuda") for _ in range(world_size)]
    dist.all_gather(size_list, local_size)

    # Verify that tensor sizes are equal in dimensions other than 0.
    rank = get_rank()
    for index, size in enumerate(size_list):
        if not torch.all(torch.eq(local_size[1:], size[1:])):
            raise AutoMLVisionSystemException(
                f"Tensor from process {rank} is of size {local_size} and "
                f"tensor from process {index} is of size {size}. "
                f"Cannot gather tensors having different sizes in dimensions other than 0.", has_pii=False)

    max_size, _ = torch.max(torch.stack(size_list), dim=0)

    # receiving tensor from all ranks
    # we pad the tensor because torch all_gather does not support
    # gathering tensors of different shapes
    tensor_list = [torch.empty(max_size.tolist(), dtype=input_tensor.dtype, device="cuda") for _ in range(world_size)]
    if local_size[0] != max_size[0]:
        # Padding the tensor along first dimension with zeros
        padding_size = local_size.clone().detach()
        padding_size[0] = max_size[0] - local_size[0]
        padding = torch.empty(padding_size.tolist(), dtype=input_tensor.dtype, device="cuda")
        input_tensor = torch.cat((input_tensor, padding), dim=0)
    dist.all_gather(tensor_list, input_tensor)

    output_list = []
    for index, (size, tensor) in enumerate(zip(size_list, tensor_list)):
        tensor = tensor[:size[0], ...]
        output_list.append(tensor)

    return output_list


def reduce_dict(input_dict: Dict[Any, Tensor], average: bool = True) -> Dict[Any, Tensor]:
    """Reduce a dictionary of tensors from all processes and return a dictionary with
    same keys as input_dict and reduced values.

    To be used with similar tensors from all processes with the below restrictions.
        1) Restrictions on input_dict within a process
            - Tensors for all the keys should already be on the current gpu device.
            - Tensors for all the keys in input_dict should have same size. This is because tensors for all keys
              are stacked using torch.stack before calling dist.all_reduce() and
              stack only works with tensors of same size.
        2) Restrictions on input_dict across processes.
            - input_dict on all processes should have same set of keys.
            - Tensors should have same size across processes i.e. tensors from process 1 should have
              same size as tensors from process 2 and so on.

    Note: The tensors in return dict will not have grad_fn as the below code is executed in torch.no_grad block.

    Note: This code has been copied from PyTorch example code here:
    https://github.com/pytorch/vision/blob/master/references/detection/utils.py#L118

    :param input_dict: Dictionary of tensors to be reduced.
    :type input_dict: Dict
    :param average: Whether to do average or sum for reduce.
    :type average: Boolean
    :return: Dictionary with same keys as data and reduced tensors as values.
    :rtype data: Dict
    """
    world_size = get_world_size()
    if world_size < 2:
        return input_dict

    with torch.no_grad():
        keys = []
        values = []
        # sort the keys so that they are consistent across processes.
        for key in sorted(input_dict.keys()):
            keys.append(key)
            values.append(input_dict[key])
        # Combine the tensors into a single tensor.
        tensor_values = torch.stack(values, dim=0)
        dist.all_reduce(tensor_values)
        if average:
            tensor_values /= world_size

        result = dict(zip(keys, tensor_values))
    return result


def update_settings_for_distributed_training(settings: Dict[str, Any], world_size: int, node_count: int) -> None:
    """ Update the settings and environment variables required for distributed training
    before launching worker processes.

    :param settings: Dictionary with all training and model settings
    :type settings: dict
    :param world_size: Distributed world size
    :type world_size: int
    :param node_count: Node count
    :type node_count: int
    """
    master_addr, master_port = _get_master_addr_and_port(settings, node_count)

    settings.update({
        DistributedLiterals.WORLD_SIZE: world_size,
        DistributedLiterals.MASTER_ADDR: master_addr,
        DistributedLiterals.MASTER_PORT: master_port,
        log_server.TELEMETRY_ENV_NAME: os.environ.get(log_server.TELEMETRY_ENV_NAME),
        log_server.LOGFILE_ENV_NAME: os.environ.get(log_server.LOGFILE_ENV_NAME),
        log_server.VERBOSITY_ENV_NAME: os.environ.get(log_server.VERBOSITY_ENV_NAME),
        "custom_dimensions": json.dumps(log_server.custom_dimensions)
    })


def _get_master_addr_and_port(settings: Dict[str, Any], node_count: int) -> Tuple[str, str]:
    """Get the master address and port.

    :param settings: Dictionary with all training and model settings
    :type settings: dict
    :param node_count: Node count
    :type node_count: int
    :return: Tuple consisting of master address then port
    :rtype: Tuple[str, str]
    """
    if node_count == 1:
        return settings[DistributedLiterals.MASTER_ADDR], settings[DistributedLiterals.MASTER_PORT]

    # Pull the MASTER_ADDR and MASTER_PORT from environment variables. In multi-node training, these
    # environment varaibles should be populated by AML Infra.
    master_addr = os.getenv(DistributedLiterals.MASTER_ADDR)
    master_port = os.getenv(DistributedLiterals.MASTER_PORT)
    if master_addr is None:
        raise AutoMLVisionSystemException(
            f"{DistributedLiterals.MASTER_ADDR} environment variable is not set for multi-node training.")
    if master_port is None:
        raise AutoMLVisionSystemException(
            f"{DistributedLiterals.MASTER_PORT} environment variable is not set for multi-node training.")
    return master_addr, master_port


def _enable_distributed_logging(settings: Dict[str, Any]) -> None:
    """Enable logging when operating in a distributed environment.

    :param settings: Dictionary with all settings
    :type settings: dict
    """
    log_server.enable_telemetry(settings.get(log_server.TELEMETRY_ENV_NAME))
    try:
        log_server.set_verbosity(int(os.environ.get(log_server.VERBOSITY_ENV_NAME, str(logging.INFO))))
    except Exception:
        pass

    log_server.update_custom_dimensions(json.loads(settings["custom_dimensions"]))

    # Add console handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(pid)d - %(name)s.%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    stdout_handler.setFormatter(formatter)
    log_server.add_handler('stdout', stdout_handler)


def _set_distributed_logging_rank(rank: int) -> None:
    """Set the rank for distributed logging.
    :param rank: The global rank of the current process.
    :type rank: int
    """
    parent_log_path = os.path.split(os.environ.get(log_server.LOGFILE_ENV_NAME, 'debug.log'))
    log_filename_split = os.path.splitext(parent_log_path[1])
    child_log_path = os.path.join(
        parent_log_path[0], "{}-{}{}".format(log_filename_split[0], rank, log_filename_split[1]))
    log_server.set_log_file(child_log_path)


def setup_distributed_training(local_rank: int, settings: Dict[str, Any], logger: logging.Logger) -> None:
    """ Setup distributed training for a worker process.
    :param local_rank: The local rank of the process within the node.
    :type local_rank: int
    :type rank: int
    :param settings: Dictionary with all training and model settings
    :type settings: dict
    :param logger: Logger to use for log messages
    :type logger: logging.Logger
    """
    # Enable distributed logging.
    # It's important that enabling logging executes as early as possible. Otherwise, if an exception
    # is raised before logging is enabled, the exception will not be logged properly.
    _enable_distributed_logging(settings)
    rank = _calculate_rank(local_rank)
    _set_distributed_logging_rank(rank)

    world_size = settings.get(DistributedLiterals.WORLD_SIZE, None)
    if world_size is None:
        msg = f"{DistributedLiterals.WORLD_SIZE} parameter is missing from settings in distributed mode."
        logger.error(f"{msg}")
        raise AutoMLVisionSystemException(msg, has_pii=False)

    # init process group
    logger.info(f"Setting up process group for worker {rank}")
    os.environ[DistributedLiterals.MASTER_ADDR] = settings[DistributedLiterals.MASTER_ADDR]
    os.environ[DistributedLiterals.MASTER_PORT] = settings[DistributedLiterals.MASTER_PORT]
    torch.cuda.set_device(local_rank)
    try:
        dist.init_process_group(backend=DistributedParameters.DEFAULT_BACKEND,
                                rank=rank, world_size=world_size)
    except Exception as e:
        user_error = False
        suspected_cause = ""
        if isinstance(e, RuntimeError):
            multiple_jobs_error_message = " Please make sure there are no other AutoML jobs running on the same" \
                " compute. If you are using a compute instance, please make sure that the" \
                " max_concurrent_iterations/max_concurrent_trials parameter is set to 1."
            if "Timed out" in repr(e):
                user_error = True
                suspected_cause = "There are other processes/jobs using the gpus in the compute.{}".format(
                    multiple_jobs_error_message
                )
            elif "Address already in use" in repr(e):
                user_error = True
                suspected_cause = "The address/port used for distributed communication is already in use.{}".format(
                    multiple_jobs_error_message
                )

        msg = "Encountered {} exception while setting up process group for worker process: {}.{}".format(
            e.__class__.__name__, rank,
            " Suspected cause: {}".format(suspected_cause) if suspected_cause else ""
        )

        logger.error(msg)
        if user_error:
            raise AutoMLVisionRuntimeUserException(msg, inner_exception=e, has_pii=False)
        else:
            raise AutoMLVisionSystemException(msg, inner_exception=e, has_pii=False)


def launch_single_or_distributed_training(
        settings: Dict[str, Any],
        train_worker_fn: Union[Callable[[int, Dict[str, Any], Optional[str]], None],
                               Callable[[int, Dict[str, Any], Optional[str], bool], None]],
        additional_train_worker_fn_args: Union[Tuple[Optional[str]], Tuple[Optional[str], bool]],
        logger: logging.Logger, azureml_run: Run) -> None:
    """ Launch single or multi-gpu training based on `distributed` setting and available device count.

    :param settings: Dictionary with all training and model settings.
    :type settings: Dict
    :param train_worker_fn: Entrypoint function for the worker process in multi-gpu training. In single-gpu case,
        entrypoint function in called in the same process that calls the current function.
    :type: train_worker_fn: Callable
    :param additional_train_worker_fn_args: Arguments passed to train_worker_fn in addition to rank and settings.
    :type additional_train_worker_fn_args: Tuple
    :param logger: Logger to use for log messages
    :type logger: logging.Logger
    :param azureml_run: The run object
    :type azureml_run: Run
    """
    distributed = settings[DistributedLiterals.DISTRIBUTED]
    device_count = _get_device_count()
    node_count = _get_node_count()
    world_size = node_count * device_count if device_count > 0 else node_count
    logger.info(f"device_count: {device_count}, node_count: {node_count}")

    if node_count > 1:
        _validate_multinode_run(distributed, device_count, azureml_run)

    if distributed and world_size > 1:
        logger.info(f"Starting distributed training with world_size: {world_size}.")
        update_settings_for_distributed_training(settings, world_size, node_count)
        # Launch process(es) for distributed training
        torch.multiprocessing.spawn(train_worker_fn, args=(settings, *additional_train_worker_fn_args),
                                    nprocs=device_count, join=True)
    else:
        if distributed:
            logger.warning(f"Distributed flag is {distributed}, but is not supported as the world_size is 1. "
                           f"Training using a single process and settings the flag to False")
            settings[DistributedLiterals.DISTRIBUTED] = False
        train_worker_fn(0, settings, *additional_train_worker_fn_args)


def _get_device_count() -> int:
    """Get the device count (the number of CUDA-enabled GPUs available).
    :return: Device count.
    :rtype: int
    """
    return cast(int, torch.cuda.device_count()) if torch.cuda.is_available() else 0


def _calculate_rank(local_rank: int) -> int:
    """Calculate the global rank when running in distributed mode.
    :param local_rank: The local rank of the process within the node.
    :type local_rank: int
    :return: The global rank of the current process.
    :rtype: int
    """
    return local_rank + _get_node_rank() * _get_device_count()


def _get_node_count() -> int:
    """Get the node count (the number of VMs in the current AML job).
    :return: Node count.
    :rtype: int
    """
    return int(os.environ.get(DistributedLiterals.NODE_COUNT, 1))


def _get_node_rank() -> int:
    """Get the rank of the current node.
    :return: Node rank.
    :rtype: int
    """
    return int(os.environ.get(DistributedLiterals.NODE_RANK, 0))


def _is_infiniband_enabled() -> bool:
    """Return whether InfiniBand is enabled.
    :return: Whether InfiniBand is enabled.
    :rtype: bool
    """
    return os.environ.get(DistributedLiterals.NCCL_IB_DISABLE) == '0'


def _validate_multinode_run(distributed: bool, device_count: int, azureml_run: Run) -> None:
    """Validate multi-node run.
    :param distributed: The value of distribtued setting flag (i.e. whether distributed runs are enabled).
    :type distributed: bool
    :param device_count: The device count (i.e. number of CUDA-enabled GPUs on the machine).
    :type device_count: int
    :param azureml_run: The run object
    :type azureml_run: Run
    """
    # Error if CPU training
    if device_count == 0:
        raise AutoMLVisionValidationException(
            "Multi-node training is only supported on machines with one or more GPUs.")

    # Error if distributed flag disabled
    if not distributed:
        raise AutoMLVisionValidationException("Distributed flag must be enabled for multi-node training.")

    # Warn if InfiniBand is disabled
    if not _is_infiniband_enabled():
        from azureml.acft.common_components.image.runtime_common.common import utils
        utils.post_warning(
            azureml_run,
            "InfiniBand is not available on the compute cluster. Multi-node training may be slow. "
            "Please enable InfiniBand by ensuring that the VMs in the compute cluster have the "
            "hardware required for InfiniBand.")
