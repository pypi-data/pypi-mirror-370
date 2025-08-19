# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Common callbacks for all vetricals."""

from dataclasses import asdict
from transformers.trainer_callback import TrainerCallback, TrainerControl, TrainerState
from transformers.trainer import TrainingArguments, get_last_checkpoint

from .checkpoint_utils import save_extra_files_to_checkpoint


class SaveExtraFilesToCheckpoints(TrainerCallback):
    """save extrafiles to checkpoint folder for image/multimodal verticals."""

    def __init__(self, metadata: str,
                 model_selector_output: str,
                 optimization_args: dict,
                 io_args: dict) -> None:
        """
        :param metadata: dict containg the meta information
        :type metadata: dict
        :param model_selector_output: path of the input model
        :type model_selector_output: str
        :param optimization_args: dict of optimization args
        :type optimization_args: dict
        :param io_args: dict of io args
        :type io_args: dict

        :return: None
        :rtype: None
        """
        super().__init__()
        self.io_args = asdict(io_args)
        self.optimization_args = asdict(optimization_args)
        self.metadata = metadata
        self.model_selector_output = model_selector_output

    def on_save(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs) -> None:
        """Callback called after saving each checkpoint.
        :param args: training arguments
        :type args: TrainingArguments (transformers.TrainingArguments)
        :param state: trainer state
        :type state: TrainerState (transformers.TrainerState)
        :param control: trainer control
        :type control: TrainerControl (transformers.TrainerControl)
        :param kwargs: keyword arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """
        last_checkpoint_folder = get_last_checkpoint(args.output_dir)
        if args.should_save:  # save only on rank-0
            save_extra_files_to_checkpoint(last_checkpoint_folder, self.metadata, self.model_selector_output,
                                           self.optimization_args, self.io_args, save_checkpoint_done_file=True)

    def on_train_end(self, args: TrainingArguments, state: TrainerState, control: TrainerControl, **kwargs) -> None:
        """Callback called at the end of training.
        :param args: training arguments
        :type args: TrainingArguments (transformers.TrainingArguments)
        :param state: trainer state
        :type state: TrainerState (transformers.TrainerState)
        :param control: trainer control
        :type control: TrainerControl (transformers.TrainerControl)
        :param kwargs: keyword arguments
        :type kwargs: dict

        :return: None
        :rtype: None
        """

        if args.should_save:  # save only on rank-0
            save_extra_files_to_checkpoint(self.io_args["pytorch_model_folder"], self.metadata,
                                           self.model_selector_output, self.optimization_args, self.io_args)
