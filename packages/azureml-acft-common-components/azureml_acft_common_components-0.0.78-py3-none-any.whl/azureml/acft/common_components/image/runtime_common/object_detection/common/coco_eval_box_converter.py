# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Conversion to format for COCO-style evaluation."""

import itertools

from typing import Any, Dict, List

from azureml.acft.common_components.image.runtime_common.object_detection.eval.utils import \
    prepare_bounding_boxes_for_eval
from azureml.acft.common_components.image.runtime_common.object_detection.common import boundingbox


class COCOEvalBoxConverter:
    """
    Helper that converts from object detection model predictions to
    boxes for COCO-style evaluation.
    """

    def __init__(self, index_map: List[str]):
        """Initialize converter with empty list of predictions.

        :param index_map: Map from numerical indices to class names
        :type index_map: List of strings
        """

        # Copy the index map.
        self._index_map = index_map

        # Initialize predictions to empty list.
        self._all_predictions_with_info : List[Dict[str, Any]] = []

    def add_predictions(self, predictions_with_info_per_image: List[Dict[str, Any]]):
        """Accumulate the predictions for a set of images.

        :param predictions_with_info_per_image: Predictions for a typically small set of images, eg a batch
        :type predictions_with_info_per_image: list of dicts with height, width, boxes, labels, scores and masks
        """

        self._all_predictions_with_info.extend(predictions_with_info_per_image)

    def get_boxes(self) -> List[Dict[str, Any]]:
        """Get boxes in COCO-style evaluation format.

        :return: Detections in format that can be consumed by cocotools/vocmap
        :rtype: list of dicts
        """

        # Initialize list of ImageBoxes objects for images.
        bounding_boxes = []

        # Go through all the predictions and make an ImageBoxes object for each.
        for predictions_with_info in self._all_predictions_with_info:
            image_boxes = boundingbox.ImageBoxes(predictions_with_info["filename"], self._index_map)
            image_boxes.add_boxes(
                predictions_with_info["boxes"], predictions_with_info["labels"], predictions_with_info["scores"],
                predictions_with_info.get("masks", None)
            )
            bounding_boxes.append(image_boxes)

        # Convert from ImageBoxes to format that can be consumed by cocotools/vocmap.
        eval_bounding_boxes : List[Dict[str, Any]] = prepare_bounding_boxes_for_eval(bounding_boxes)
        return eval_bounding_boxes

    @classmethod
    def aggregate_boxes(cls, eval_bounding_boxes: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Aggregate evaluation bounding boxes from multiple threads.

        :return: Detections in format that can be consumed by cocotools/vocmap
        :rtype: list of dicts
        """

        return list(itertools.chain.from_iterable(eval_bounding_boxes))
