# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Common utilities for object detection and object detection yolo."""
import json
import os
import numpy as np
import time
import torch

import azureml.automl.core.shared.constants as shared_constants

from collections import namedtuple
from torchvision import transforms
from typing import Any, Dict, Union

from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.image.runtime_common.common import utils
from azureml.acft.common_components.image.runtime_common.common.artifacts_utils import \
    _download_model_from_artifacts
from azureml.acft.common_components.image.runtime_common.common.constants import ArtifactLiterals, \
    MetricsLiterals, SettingsLiterals, TrainingLiterals as CommonTrainingLiterals

from azureml.acft.common_components.image.runtime_common.common.dataset_helper import AmlDatasetHelper
from azureml.acft.common_components.image.runtime_common.object_detection.common.constants import \
    PredictionLiterals, ValidationMetricType, MaskImageExportLiterals, MaskImageExportParameters, TilingLiterals, \
    MaskToolsLiterals
from azureml.acft.common_components.image.runtime_common.object_detection.eval.incremental_voc_evaluator import \
    IncrementalVocEvaluator

from azureml.acft.common_components.image.runtime_common.object_detection.models.base_model_wrapper import \
    BaseObjectDetectionModelWrapper
from azureml.acft.common_components.image.runtime_common.object_detection_yolo.models.yolo_wrapper import \
    YoloV5Wrapper
from .masktools import _extract_settings_and_convert_mask_to_polygon, convert_polygon_to_rle_masks,\
    decode_rle_masks_as_binary_mask, encode_mask_as_rle
from ..data.datasets import AmlDatasetObjectDetection
from ..data.dataset_wrappers import CommonObjectDetectionDatasetWrapper, DatasetProcessingType
from ..eval import cocotools
from ..models import detection
from ...common.average_meter import AverageMeter
from ...common.exceptions import AutoMLVisionSystemException
from ...common.system_meter import SystemMeter

logger = get_logger_app(__name__)


def _load_model_wrapper(torch_model_file, device, model_settings) \
        -> Union[BaseObjectDetectionModelWrapper, YoloV5Wrapper]:
    checkpoint = torch.load(torch_model_file, map_location=device)
    model_state = checkpoint['model_state']
    model_name = checkpoint['model_name']
    number_of_classes = checkpoint['number_of_classes']
    specs = checkpoint['specs']
    settings = specs['model_settings']
    settings.update(specs['inference_settings'])
    # make sure we overwrite those matching model settings with the user provided ones (if any)
    settings.update(model_settings)

    model_wrapper = detection.setup_model(model_name=model_name,
                                          model_state=model_state,
                                          number_of_classes=number_of_classes,
                                          specs=specs['model_specs'],
                                          classes=specs['classes'],
                                          device=device,
                                          settings=settings)

    return model_wrapper


def _fetch_model_from_artifacts(run_id, device, experiment_name=None, model_settings={}):
    _download_model_from_artifacts(run_id=run_id, experiment_name=experiment_name)

    return _load_model_wrapper(shared_constants.PT_MODEL_FILENAME, device, model_settings)


def _get_box_dims(image_shape, box):
    box_keys = ['topX', 'topY', 'bottomX', 'bottomY']
    height, width = image_shape[0], image_shape[1]

    box_dims = dict(zip(box_keys, [coordinate.item() for coordinate in box]))

    box_dims['topX'] = box_dims['topX'] * 1.0 / width
    box_dims['bottomX'] = box_dims['bottomX'] * 1.0 / width
    box_dims['topY'] = box_dims['topY'] * 1.0 / height
    box_dims['bottomY'] = box_dims['bottomY'] * 1.0 / height

    return box_dims


def _get_bounding_boxes(label, image_shape, classes, masktool_settings=None):
    bounding_boxes = []

    if 'masks' not in label:
        masks = [None] * len(label['boxes'])
    else:
        masks = label['masks']

    for box, label_index, score, mask in zip(label['boxes'], label['labels'], label['scores'], masks):
        box_dims = _get_box_dims(image_shape, box)

        box_record = {PredictionLiterals.BOX: box_dims,
                      PredictionLiterals.LABEL: classes[label_index],
                      PredictionLiterals.SCORE: score.item()}

        if mask is not None:
            # TODO: clean up the duplicates (here and the below from _write_dataset_file_line).
            #  Currently, we generate polygon twice which can be once.
            mask = _extract_settings_and_convert_mask_to_polygon(mask, masktool_settings)
            box_record[PredictionLiterals.POLYGON] = mask

        bounding_boxes.append(box_record)

    return bounding_boxes


def _write_prediction_file_line(fw, filename, label, image_shape, classes, masktool_settings=None):
    bounding_boxes = _get_bounding_boxes(label, image_shape, classes, masktool_settings)

    annotation = {PredictionLiterals.FILENAME: filename,
                  PredictionLiterals.BOXES: bounding_boxes}

    fw.write('{}\n'.format(json.dumps(annotation)))


def _write_dataset_file_line(fw, filename, label, image_shape, classes, masktool_settings=None):
    labels = []
    scores = []

    if 'masks' not in label:
        masks = [None] * len(label['boxes'])
    else:
        masks = label['masks']

    for box, label_index, score, mask in zip(label['boxes'], label['labels'], label['scores'], masks):
        label_record = _get_box_dims(image_shape, box)
        label_record[PredictionLiterals.LABEL] = classes[label_index]

        if mask is not None:
            mask = _extract_settings_and_convert_mask_to_polygon(mask, masktool_settings)
            label_record[PredictionLiterals.POLYGON] = mask

        labels.append(label_record)
        scores.append(score.item())

    AmlDatasetHelper.write_dataset_file_line(fw, filename, scores, labels)


def _create_mask_filename(filename_root, index, class_label, confidence_score, image_type):
    return (f"{filename_root}_{index}_label_{class_label}_conf_"
            f"{str(confidence_score).replace('.','')[:4]}.{image_type.lower()}")


def _write_masks_as_images(label, classes, output_dir, settings=None):

    if settings is None:
        settings = {}

    filename = label["filename"]

    filename_root = os.path.basename(filename).split(".")[0]
    converter = transforms.ToPILImage()

    export_image_type = settings.get(
        MaskImageExportLiterals.IMAGE_TYPE, MaskImageExportParameters.DEFAULT_IMAGE_TYPE)

    output_dir = os.path.join(output_dir, 'masks')

    if 'masks' in label:
        for i, (mask, label, score) in enumerate(zip(label['masks'], label['labels'], label['scores'])):
            binary_mask = decode_rle_masks_as_binary_mask([mask]) * 255
            pil_mask = converter(binary_mask)
            class_label = classes[label.item()]
            output_filename = _create_mask_filename(
                filename_root, i, class_label, score.item(), export_image_type)
            os.makedirs(os.path.join(output_dir, filename_root, class_label), exist_ok=True)
            pil_mask.save(os.path.join(output_dir, filename_root, class_label, output_filename))


def _get_boxes_masks_classes_scores_from_prediction_dict(width, height, label_to_index_map, prediction_dict):
    """Helper function to extract boxes, masks, classes and scores from a prediction dict."""

    # Initialize the boxes, masks, labels and scores.
    boxes, rle_masks, labels, scores = [], None, [], []

    # Go through all predicted objects.
    for object_ in prediction_dict[PredictionLiterals.BOXES]:
        # Convert the box from normalized coordinates to pixel coordinates and append it to the list.
        box = object_["box"]
        box_coordinates = [box["topX"] * width, box["topY"] * height, box["bottomX"] * width, box["bottomY"] * height]
        boxes.append(box_coordinates)

        # Check if there are contour polygon(s) for the object.
        if PredictionLiterals.POLYGON in object_:
            # Convert polygon(s) to mask.
            polygon = object_[PredictionLiterals.POLYGON]
            for segment in polygon:
                segment[::2] = [x * width for x in segment[::2]]
                segment[1::2] = [y * height for y in segment[1::2]]
            box_rle_masks = convert_polygon_to_rle_masks(polygon, height, width)
            box_binary_mask = decode_rle_masks_as_binary_mask(box_rle_masks)
            box_rle_mask = encode_mask_as_rle(torch.as_tensor(box_binary_mask, dtype=torch.uint8))

            # Append mask to existing list, initializing it if necessary.
            if rle_masks is None:
                rle_masks = []
            rle_masks.append(box_rle_mask)

        # Get the label index and append it to the existing list.
        labels.append(label_to_index_map(object_[PredictionLiterals.LABEL]))

        # Get the score and append it to the existing list.
        scores.append(object_[PredictionLiterals.SCORE])

    return boxes, rle_masks, labels, scores


def _evaluate_predictions_incrementally(
    predictions_file_name: str, dataset: AmlDatasetObjectDetection, incremental_evaluator: IncrementalVocEvaluator
):
    logger.info("Start evaluating predictions incrementally.")

    # Open the predictions file.
    with open(predictions_file_name, "rt") as f:
        # Go through predictions line by line (each line contains all the predictions for an image).
        for prediction_line_index, prediction_line in enumerate(f):
            # Parse the JSON string for the predictions for the current image.
            prediction_dict = json.loads(prediction_line)

            # Get the name of the image file for the current predictions and check that it exists in the dataset.
            filename = dataset._dataset_helper.get_image_full_path(prediction_line_index)
            assert prediction_dict[PredictionLiterals.FILENAME] in filename

            # Get the current image and the the supervision information associated with it.
            image, label, image_info = dataset.get_image_label_info_for_image_url(filename)
            if image is None:
                logger.info(f"Skip invalid image {image}.")
                continue

            # Convert the boxes, masks and classes to format suitable to processing in the incremental evaluator.
            gt_objects = {
                "boxes": label["boxes"].detach().cpu().numpy(),
                "masks": [
                    encode_mask_as_rle(mask.detach().cpu()) for mask in label["masks"]
                ] if label.get("masks") is not None else None,
                "classes": label["labels"].detach().cpu().numpy(),
                "scores": None
            }

            # Get the boxes, masks, classes and scores for the current predictions and convert them to format suitable
            # to processing in the incremental evaluator.
            boxes, rle_masks, classes, scores = _get_boxes_masks_classes_scores_from_prediction_dict(
                image_info["original_width"], image_info["original_height"], dataset.label_to_index_map,
                prediction_dict
            )
            predicted_objects = {
                "boxes": np.array(boxes), "masks": rle_masks, "classes": np.array(classes), "scores": np.array(scores)
            }

            # Make batch containing only the current image and send to incremental evaluator.
            incremental_evaluator.evaluate_batch([gt_objects], [predicted_objects], [image_info])

    logger.info(f"End evaluating {prediction_line_index + 1} predictions incrementally.")


def _update_with_voc_metrics(current_metrics, cumulative_per_label_metrics, voc_metrics, is_train=False):
    """
    Update the current metrics and the cumulative metrics according to the VOC metrics dictionary.
    """

    MetricInformation = namedtuple("MetricInformation", ["type", "is_base", "updates_current"])
    METRIC_INFORMATION_BY_NAME = {
        MetricsLiterals.PRECISION: MetricInformation("scalar", is_base=True, updates_current=True),
        MetricsLiterals.RECALL: MetricInformation("scalar", is_base=True, updates_current=True),
        MetricsLiterals.AVERAGE_PRECISION: MetricInformation("scalar", is_base=True, updates_current=False),
        MetricsLiterals.PER_LABEL_METRICS: MetricInformation("per_label", is_base=False, updates_current=True),
        MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS: MetricInformation(
            "image_level", is_base=False, updates_current=True
        ),
        MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD: MetricInformation(
            "per_score_threshold", is_base=False, updates_current=True
        )
    }

    def _alter_name(name):
        return name + ("_train" if is_train else "")

    def _round(x, value_type):
        if value_type == "scalar":
            if isinstance(x, torch.Tensor):
                x = x.item()
            return round(x, 5)

        if value_type == "per_label":
            return {
                label_index: {
                    metric_name: _round(metrics[metric_name], "scalar")
                    for metric_name, metric_information in METRIC_INFORMATION_BY_NAME.items()
                    if metric_information.is_base
                }
                for label_index, metrics in x.items()
            }

        if value_type == "image_level":
            return {
                metric_name: _round(metric_value, "scalar")
                for metric_name, metric_value in x.items()
            }

        if value_type == "per_score_threshold":
            return {
                _round(score_threshold, "scalar"): [
                    [_round(column, "scalar") for column in row] for row in confusion_matrix
                ]
                for score_threshold, confusion_matrix in x.items()
            }

    # Set the current metrics: precision, recall, per label, image level and confusion matrix metrics.
    for metric_name, metric_information in METRIC_INFORMATION_BY_NAME.items():
        if metric_information.updates_current and (metric_name in voc_metrics):
            altered_metric_name = _alter_name(metric_name)
            metric_value = voc_metrics[metric_name]
            current_metrics[altered_metric_name] = _round(metric_value, metric_information.type)

    # Update the cumulative per-label metrics. Use label index instead of label name due to pii.
    for label_index, metrics in current_metrics[_alter_name(MetricsLiterals.PER_LABEL_METRICS)].items():
        # If entry does not exist, initialize to empty dictionary.
        if label_index not in cumulative_per_label_metrics:
            cumulative_per_label_metrics[label_index] = {}

        # Go through base metrics: precision, recall and average precision.
        for metric_name, metric_information in METRIC_INFORMATION_BY_NAME.items():
            if metric_information.is_base:
                # If entry does not exist, initialize to empty list.
                if metric_name not in cumulative_per_label_metrics[label_index]:
                    cumulative_per_label_metrics[label_index][metric_name] = []

                # Accumulate current metric value.
                cumulative_per_label_metrics[label_index][metric_name].append(metrics[metric_name])


def compute_metrics(eval_bounding_boxes, val_metric_type,
                    val_coco_index, incremental_voc_evaluator,
                    computed_metrics, cumulative_per_label_metrics,
                    coco_metric_time, voc_metric_time,
                    primary_metric, is_train=False) -> float:
    """Compute metrics from validation bounding boxes.

    :param eval_bounding_boxes: Bounding boxes list
    :type eval_bounding_boxes: List
    :param val_metric_type: Validation metric evaluation type.
    :type val_metric_type: ValidationMetricType.
    :param val_coco_index: Cocoindex created from validation data
    :type val_coco_index: Pycocotool Cocoindex object
    :param incremental_voc_evaluator: Evaluator for object detection that has seen all labels and predictions
    :type incremental_voc_evaluator: IncrementalVocEvaluator
    :param computed_metrics: Dictionary to store all metrics
    :type computed_metrics: Dict
    :param cumulative_per_label_metrics: Dictionary to store per label metrics across epochs
    :type cumulative_per_label_metrics: Dict
    :param coco_metric_time: Meter to record COCO-style metrics computation time
    :type coco_metric_time: AverageMeter
    :param voc_metric_time: Meter to record VOC-style metrics computation time
    :type voc_metric_time: AverageMeter
    :param primary_metric: Metric that is evaluated and logged by AzureML run object.
    :type primary_metric: str
    :param is_train: is this data for training
    :type is_train: bool
    :return: mAP score
    :rtype: float
    """

    if val_metric_type in ValidationMetricType.ALL_COCO and val_coco_index is None:
        raise AutoMLVisionSystemException(f"val_metric_type is {val_metric_type}. But, val_coco_index is None. "
                                          f"Cannot compute metrics.", has_pii=False)

    if (val_metric_type in ValidationMetricType.ALL_VOC) and (incremental_voc_evaluator is None):
        raise AutoMLVisionSystemException("val_metric_type is {val_metric_type} but incremental_voc_evaluator is None"
                                          ". Cannot compute metrics.", has_pii=False)

    map_score = 0.0

    task = "bbox"
    if eval_bounding_boxes and "segmentation" in eval_bounding_boxes[0]:
        task = "segm"

    if val_metric_type in ValidationMetricType.ALL_COCO:
        coco_metric_start = time.time()
        coco_score = cocotools.score_from_index(val_coco_index, eval_bounding_boxes, task)
        coco_metric_time.update(time.time() - coco_metric_start)
        logger.info(f"Coco Time {coco_metric_time.value:.4f} ({coco_metric_time.avg:.4f})")

        computed_metrics[MetricsLiterals.COCO_METRICS] = cocotools.convert_coco_metrics(coco_score)
        map_score = coco_score[1]  # mAP at IoU 0.5

    if val_metric_type in ValidationMetricType.ALL_VOC:
        # Compute aggregated metrics and report time.
        voc_metric_start = time.time()
        metrics = incremental_voc_evaluator.compute_metrics()
        voc_metric_time.update(time.time() - voc_metric_start)
        logger.info(
            f"Voc Time (aggregation) {voc_metric_time.value:.4f} ({voc_metric_time.avg:.4f})"
        )

        # Update the current metrics and the cumulative metrics.
        _update_with_voc_metrics(computed_metrics, cumulative_per_label_metrics, metrics, is_train=is_train)
        map_score = metrics[MetricsLiterals.MEAN_AVERAGE_PRECISION]

    computed_metrics[primary_metric + "{train}".format(train="_train" if is_train else "")] = round(map_score, 5)
    return map_score


def _evaluate_and_log(score_run, incremental_voc_evaluator):
    computed_metrics: Dict[str, Any] = {}
    per_label_metrics: Dict[str, Any] = {}

    compute_metrics([], val_metric_type=ValidationMetricType.VOC,
                    val_coco_index=None, incremental_voc_evaluator=incremental_voc_evaluator,
                    computed_metrics=computed_metrics, cumulative_per_label_metrics=per_label_metrics,
                    coco_metric_time=AverageMeter(), voc_metric_time=AverageMeter(),
                    primary_metric=MetricsLiterals.MEAN_AVERAGE_PRECISION)

    utils.log_all_metrics(computed_metrics, azureml_run=score_run, add_to_logger=True)
    properties_to_add = {
        MetricsLiterals.MEAN_AVERAGE_PRECISION: computed_metrics[MetricsLiterals.MEAN_AVERAGE_PRECISION],
        MetricsLiterals.PRECISION: computed_metrics[MetricsLiterals.PRECISION],
        MetricsLiterals.RECALL: computed_metrics[MetricsLiterals.RECALL],
    }
    score_run.add_properties(properties_to_add)


def _validate_score_run(
    task_is_detection, input_dataset, use_bg_label, iou_threshold, output_file, score_run
):
    logger.info("Begin validating scoring run")
    if input_dataset is None:
        logger.warning("No input dataset specified, skipping validation.")
        return

    system_meter = SystemMeter(log_static_sys_info=True)
    system_meter.log_system_stats()

    logger.info("Initializing validation dataset.")
    try:
        # Note for Yolo: use of AmlDatasetObjectDetection here instead of AmlDatasetObjectDetectionYolo means the
        # ground truth boxes are not padded and there is no need to call unpad_bbox() as is done in train.py.
        # TODO: move image padding inside the dataset and eliminate unpadding of predictions.
        validation_dataset: AmlDatasetObjectDetection = AmlDatasetObjectDetection(dataset=input_dataset,
                                                                                  is_train=False,
                                                                                  ignore_data_errors=True,
                                                                                  use_bg_label=use_bg_label,
                                                                                  masks_required=not task_is_detection)
        validation_dataset_wrapper = CommonObjectDetectionDatasetWrapper(
            dataset=validation_dataset, dataset_processing_type=DatasetProcessingType.IMAGES)
    except KeyError:
        logger.warning("Dataset does not contain ground truth, skipping validation.")
        return
    logger.info("End initializing validation dataset.")

    # Initialize the incremental evaluator.
    incremental_evaluator = IncrementalVocEvaluator(
        task_is_detection, len(validation_dataset_wrapper.dataset.classes), iou_threshold
    )

    # Evaluate the model's predictions, storing partial evaluation results in the incremental evaluator.
    _evaluate_predictions_incrementally(output_file, validation_dataset, incremental_evaluator)

    # Aggregate evaluation results and log them in the run.
    _evaluate_and_log(score_run, incremental_evaluator)


def score_validation_data(run, model_settings, settings, device, val_dataset, score_with_model):
    """ Runs validations on the best model to give predictions output

    :param run: azureml run object
    :type run: azureml.core.Run
    :param model_settings: dictionary containing model settings
    :type model_settings: dict
    :param settings: dictionary containing settings
    :type settings: dict
    :param device: device to use for inferencing
    :type device: str
    :param val_dataset: The validation dataset
    :type val_dataset: AbstractDataset
    :param score_with_model: method to be called for scoring
    :type score_with_model: Callable
    """
    logger.info("Beginning validation for the best model")

    ignore_data_errors = settings.get(SettingsLiterals.IGNORE_DATA_ERRORS, True)

    # Get image_list_file with path
    root_dir = settings.get(SettingsLiterals.IMAGE_FOLDER, None)
    val_labels_file = settings.get(SettingsLiterals.VALIDATION_LABELS_FILE, None)
    if val_labels_file is not None:
        val_labels_file = os.path.join(settings[SettingsLiterals.LABELS_FILE_ROOT], val_labels_file)
        root_dir = os.path.join(settings[SettingsLiterals.DATA_FOLDER], root_dir)

    if val_labels_file is None and val_dataset is None:
        logger.warning("No validation dataset or validation file was given, skipping scoring run.")
        return

    # Get target path
    target_path = settings.get(SettingsLiterals.OUTPUT_DATASET_TARGET_PATH, None)
    if target_path is None:
        target_path = AmlDatasetHelper.get_default_target_path()

    batch_size = settings[CommonTrainingLiterals.VALIDATION_BATCH_SIZE]
    output_file = settings.get(SettingsLiterals.VALIDATION_OUTPUT_FILE, None)
    num_workers = settings[SettingsLiterals.NUM_WORKERS]
    validate_scoring = settings[SettingsLiterals.VALIDATE_SCORING]
    log_scoring_file_info = settings.get(SettingsLiterals.LOG_SCORING_FILE_INFO, False)

    model = _fetch_model_from_artifacts(run_id=run.id, device=device,
                                        model_settings=model_settings)

    logger.info(f"start scoring for validation data: batch_size: {batch_size}")

    score_with_model(model, run, target_path=target_path,
                     output_file=output_file, root_dir=root_dir,
                     image_list_file=val_labels_file, batch_size=batch_size,
                     ignore_data_errors=ignore_data_errors,
                     input_dataset=val_dataset,
                     num_workers=num_workers,
                     device=device,
                     validate_score=validate_scoring,
                     log_output_file_info=log_scoring_file_info,
                     download_image_files=False)


def write_per_label_metrics_file(output_dir, per_label_metrics, val_index_map):
    """ Write per_label_metrics to a json file in the output directory.

    :param output_dir: Output directory
    :type output_dir: str
    :param per_label_metrics: Per label metrics accumulated over all the epochs
    :type per_label_metrics: dict
    :param val_index_map: Map from numerical indices to class names
    :type val_index_map: List of strings
    """
    # Replace label indices with label names.
    per_label_metrics_with_names = {val_index_map[label_index]: value
                                    for label_index, value in per_label_metrics.items()}

    per_label_metrics_file_path = os.path.join(output_dir, ArtifactLiterals.PER_LABEL_METRICS_FILE_NAME)

    with open(per_label_metrics_file_path, 'w') as f:
        json.dump(per_label_metrics_with_names, f)


def get_inference_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Get inference settings from settings dictionary

    :param settings: Settings
    :type settings: dict
    :return: Settings for inference.
    :rtype: dict
    """
    inference_settings_keys = [TilingLiterals.TILE_GRID_SIZE, TilingLiterals.TILE_OVERLAP_RATIO,
                               TilingLiterals.TILE_PREDICTIONS_NMS_THRESH]

    # for other settings like masktools in score_script.py
    mask_settings_keys = [MaskToolsLiterals.MASK_PIXEL_SCORE_THRESHOLD,
                          MaskToolsLiterals.MAX_NUMBER_OF_POLYGON_POINTS,
                          MaskImageExportLiterals.EXPORT_AS_IMAGE,
                          MaskImageExportLiterals.IMAGE_TYPE]

    inference_settings_keys += mask_settings_keys

    inference_settings: Dict[str, Any] = {}
    for key in inference_settings_keys:
        if key in settings:
            inference_settings[key] = settings[key]
    return inference_settings
