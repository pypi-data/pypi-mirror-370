# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utility functions related to checkpoints."""

import os
import json
import shutil
from pathlib import Path

from azureml.acft.common_components.model_selector.constants import ModelSelectorDefaults, ModelSelectorConstants


def save_extra_files_to_checkpoint(checkpoint_dir: str, metadata: str, model_selector_output: str,
                                   optimization_args: dict, io_args: dict,
                                   save_checkpoint_done_file: bool = False):
    """
    Save extra files like model_metadata.json and others to checkpoint directory.
    """
    # FIXME: remove cyclic dependency due to azureml-acft-accelerator import
    from azureml.acft.accelerator.constants import SaveFileConstants

    model_name = optimization_args.get(ModelSelectorConstants.MODEL_NAME)
    input_model_path = os.path.join(model_selector_output, ModelSelectorDefaults.MLFLOW_MODEL_DIRECTORY)
    if not os.path.isdir(input_model_path):
        input_model_path = os.path.join(model_selector_output, model_name)
    input_model_defaults_path = os.path.join(input_model_path, ModelSelectorDefaults.MODEL_DEFAULTS_PATH)

    op_metadata_path = os.path.join(checkpoint_dir, ModelSelectorDefaults.MODEL_METADATA_PATH)
    with open(op_metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    op_modeldefaults_path = os.path.join(checkpoint_dir, ModelSelectorDefaults.MODEL_DEFAULTS_PATH)
    if os.path.isfile(input_model_defaults_path):
        shutil.copy(input_model_defaults_path, op_modeldefaults_path)

    optimization_args_save_path = os.path.join(checkpoint_dir, SaveFileConstants.OPTIMIZATION_ARGS_SAVE_PATH)
    with open(optimization_args_save_path, 'w') as fp:
        json.dump(optimization_args, fp, indent=2)

    io_args_save_path = os.path.join(checkpoint_dir, SaveFileConstants.IO_ARGS_SAVE_PATH)
    with open(io_args_save_path, 'w') as fp:
        json.dump(io_args, fp, indent=2)

    if save_checkpoint_done_file:
        # checkpoint_done.txt will be saved at the end after all checkpoint related files, like global_step*,
        # trainer_state.json, etc., have been saved. If it exists in a checkpoint folder, the checkpoint can
        # be considered valid.
        checkpoint_done_path = os.path.join(checkpoint_dir, SaveFileConstants.CHECKPOINT_DONE_PATH)
        Path(checkpoint_done_path).touch()


def check_and_update_resume_from_checkpoint(component_args_dict: dict, logger):
    """
    Check if there are checkpoint files in the pytorch_model_folder and update the resume_from_checkpoint flag.
    """
    if component_args_dict.get("resume_from_checkpoint"):
        checkpoint_files = []
        if os.path.exists(component_args_dict.get("pytorch_model_folder", "")):
            checkpoint_files = \
                [f for f in os.listdir(component_args_dict["pytorch_model_folder"]) if f.startswith("checkpoint")]
            if not checkpoint_files:
                component_args_dict["resume_from_checkpoint"] = False
                logger.info("No checkpoint files found in output folder. \
        Setting resume_from_checkpoint to False.")
        else:
            component_args_dict["resume_from_checkpoint"] = False
            logger.info("No pytorch_model_folder found. Setting resume_from_checkpoint to False.")
