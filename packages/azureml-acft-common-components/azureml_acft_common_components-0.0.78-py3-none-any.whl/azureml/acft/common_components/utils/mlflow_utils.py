# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
This file defines the util functions related to mlflow
"""

from azureml.acft.common_components.utils.constants import MlflowMetaConstants


def update_acft_metadata(
    finetuning_task: str,
    metadata: dict={},
    is_finetuned_model: bool=True,
    base_model_asset_id: str=None,
) -> dict:
    """ update metadata to be dumped in MlFlow MlModel File/checkpoints

    :param metadata: dict of meta info to be updated with
    :type metadata: dict
    :param finetuning_task: finetunting task type
    :type finetuning_task: str
    :param is_finetuned_model: whether the model is finetuned one or base model
    :type is_finetuned_model: bool
    :param base_model_asset_id: asset id of the input model
    :type base_model_asset_id: str

    :return: metadata
    :rtype: dict
    """

    metadata.update({
        MlflowMetaConstants.IS_FINETUNED_MODEL : is_finetuned_model,
        MlflowMetaConstants.IS_ACFT_MODEL : True,
        MlflowMetaConstants.FINETUNING_TASK: finetuning_task,
    })
    if base_model_asset_id:
        metadata[MlflowMetaConstants.BASE_MODEL_ASSET_ID] = base_model_asset_id

    return metadata
