# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Data Augmentations for object detection."""

import random
from typing import Optional, Tuple

from PIL.Image import Image
import torch
import torchvision.transforms.functional as functional
from torch import Tensor

from azureml.acft.common_components import get_logger_app

logger = get_logger_app(__name__)


def hflip(image: Image, boxes: Tensor, masks: Optional[Tensor] = None) \
        -> Tuple[Image, Tensor, Optional[Tensor]]:
    """
    Flip image horizontally.

    :param image: image
    :type image: Image
    :param boxes: bounding boxes in (x_min, y_min, x_max, y_max) (n_objects, 4)
    :type boxes: Tensor
    :param masks: NxHxW pixel array masks for the object
    :type masks: Optional[Tensor]
    :return: flipped image, updated bounding boxes, flipped masks (or none, if no mask provided)
    :rtype: Tuple[Image, Tensor, Optional[Tensor]]
    """
    new_image = functional.hflip(image)

    new_boxes = boxes
    if len(boxes) > 0:
        new_boxes[:, [0, 2]] = image.width - boxes[:, [2, 0]]

    new_masks = masks.flip(-1) if masks is not None else None

    return new_image, new_boxes, new_masks


def expand(image: Image,
           boxes: Tensor,
           masks: Optional[Tensor] = None) -> Tuple[Image, Tensor, Optional[Tensor]]:
    """
    Expand image and fill the surrounding space with the mean of ImageNet.
    This is intended to detect smaller objects.

    :param image: image
    :type image: Image
    :param boxes: bounding boxes in (x_min, y_min, x_max, y_max) (n_objects, 4)
    :type boxes: Tensor
    :param masks: NxHxW pixel array masks for the object
    :type masks: Optional[Tensor]
    :return: expanded image, new boxes, expanded mask (or none, if no mask provided)
    :rtype: Tuple[Image, Tensor, Optional[Tensor]]
    """
    imagenet_mean = [0.485, 0.456, 0.406]

    tensor_image = functional.to_tensor(image)
    depth, height, width = tensor_image.size()

    ratio = random.uniform(1, 2)
    new_height = int(height * ratio)
    new_width = int(width * ratio)
    top = random.randint(0, new_height - height)
    left = random.randint(0, new_width - width)

    # place a image in a larger mean image
    new_image = torch.ones((3, new_height, new_width), dtype=torch.float)
    new_image[:, :, :] *= torch.FloatTensor(imagenet_mean).unsqueeze(1).unsqueeze(2)
    new_image[:, top:top + height, left:left + width] = tensor_image

    new_boxes = boxes
    if len(boxes) > 0:
        new_boxes[:, :2] += torch.FloatTensor([left, top])
        new_boxes[:, 2:] += torch.FloatTensor([left, top])

    # if there are masks, align them with the image
    new_masks = None
    if masks is not None:
        new_masks = torch.zeros((masks.shape[0], new_height, new_width), dtype=torch.float)
        new_masks[:, top:top + height, left:left + width] = masks

    new_image = functional.to_pil_image(new_image)

    return new_image, new_boxes, new_masks


def random_crop_around_bbox(image: Image, boxes: Tensor, masks: Optional[Tensor] = None) \
        -> Tuple[Image, Tensor, Optional[Tensor]]:
    """
    Randomly crop image but include all the bounding boxes.

    :param image: image
    :type image: Image
    :param boxes: bounding boxes in (x_min, y_min, x_max, y_max) (n_objects, 4)
    :type boxes: Tensor
    :param masks: NxHxW pixel array masks for the object
    :type masks: Optional[Tensor]
    :return: expanded image, new boxes, augmented masks (or none, if no mask provided)
    :rtype: Tuple[Image, Tensor, Optional[Tensor]]
    """
    tensor_image = functional.to_tensor(image)
    depth, height, width = tensor_image.size()

    if len(boxes) > 0:
        # Get coordinates of the smallest rectangle covering all objects in image.
        x_min = int(torch.min(boxes[:, 0]))
        y_min = int(torch.min(boxes[:, 1]))
        x_max = int(torch.max(boxes[:, 2]))
        y_max = int(torch.max(boxes[:, 3]))
    else:
        # If no objects in image, then set limits so the crop sampling code for images with objects still works.
        x_min = width
        y_min = height
        x_max = 0
        y_max = 0

    # bypass in case of out of bounds bbox coordinates
    if x_min < 0 or y_min < 0 or x_max > width or y_max > height:
        logger.warning("Due to out of bounds bbox coordinates, no random_crop_around_bbox will be applied")
        return image, boxes, masks

    max_trials = 50
    for _ in range(max_trials):
        # Randomly choose a cropping rectangle that covers all objects in the image.
        left = random.randint(0, x_min)
        right = random.randint(x_max, width)
        top = random.randint(0, y_min)
        bottom = random.randint(y_max, height)

        # Patch coordinates for the case when there are no objects in the image. Since the only constraint on `left`
        # and `right` is that they be in the [0, width], their values may be in the wrong order.
        left, right = sorted([left, right])
        top, bottom = sorted([top, bottom])

        new_w = right - left
        new_h = bottom - top

        # retry if image size is too small or aspect_ratio is way off
        aspect_ratio = new_h / (new_w + 1e-9)
        if new_h * new_w < height * width * 0.6 or not 0.5 < aspect_ratio < 2:
            continue

        crop = torch.FloatTensor([left, top, right, bottom])

        # crop image
        new_image = tensor_image[:, top:bottom, left:right]

        # adjust bbox
        new_boxes = boxes
        if len(boxes) > 0:
            new_boxes[:, :2] -= crop[:2]
            new_boxes[:, 2:] -= crop[:2]

        # crop masks, if they exist
        new_masks = masks[:, top:bottom, left:right] if masks is not None else None

        new_image = functional.to_pil_image(new_image)

        return new_image, new_boxes, new_masks

    return image, boxes, masks


def spatial_level_transforms(image: Image,
                             boxes: Tensor,
                             prob: float,
                             masks: Optional[Tensor] = None) -> Tuple[Image, Tensor, Optional[Tensor]]:
    """
    Apply various spatial change of both an input image and bounding boxes in an random order.
    Support expand, hflip and random_crop_around_bbox.

    :param image: image
    :type image: Image
    :param boxes: bounding boxes in (x_min, y_min, x_max, y_max) (n_objects, 4)
    :type boxes: Tensor
    :param prob: target probability of applying each of data augmentations
    :type prob: float
    :param masks: NxHxW pixel array masks for the object
    :type masks: Optional[Tensor]
    :return: augmented image, boxes, augmented masks (or none, if no mask provided)
    :rtype: Tuple[Image, Tensor, Optional[Tensor]]
    """
    new_image = image
    new_boxes = boxes
    new_masks = masks

    if random.random() < prob:
        if random.random() < prob:
            new_image, new_boxes, new_masks = random_crop_around_bbox(new_image, new_boxes, new_masks)
        else:
            new_image, new_boxes, new_masks = expand(new_image, new_boxes, new_masks)

    if random.random() < prob:
        new_image, new_boxes, new_masks = hflip(new_image, new_boxes, new_masks)

    return new_image, new_boxes, new_masks


def transform(image, boxes, is_train, apply_automl_train_augmentations, prob, post_transform=None, masks=None):
    """
    Apply data augmentations for Object Detection.

    :param image: image
    :type image: PIL Image
    :param boxes: bounding boxes in (x_min, y_min, x_max, y_max)
    :type boxes: tensor (n_objects, 4)
    :param is_train: which mode (training, inferencing) is the network in?
    :type is_train: bool
    :param apply_automl_train_augmentations: Should automl_augmentations be applied
    :type apply_automl_train_augmentations: bool
    :param prob: target probability of applying each of data augmentations
    :type prob: float
    :param post_transform: transform function to apply after augmentations
    :type post_transform: function that gets 3 parameters (is_train, image tensor, boxes tensor)
                          and returns a tuple with new image, boxes, height, width
    :param masks: (optional) pixel array masks for the object
    :type masks: NxHxW Tensor
    :return: augmented image, boxes, areas, image height, image width, augmented masks
    :rtype: PIL image, tensor, list, int, int, tensor (or none, if no mask provided)
    """
    new_image = image
    new_boxes = boxes
    new_masks = masks

    if is_train and apply_automl_train_augmentations:
        new_image, new_boxes, new_masks = spatial_level_transforms(new_image, new_boxes, prob, new_masks)

    new_height = new_image.height
    new_width = new_image.width
    new_image = functional.to_tensor(new_image)

    if post_transform is not None:
        new_image, new_boxes, new_height, new_width, new_masks = post_transform(
            is_train, new_image, new_boxes, new_masks)

    # update the areas of bbox for mAP calculation for each object group based on the size of objects
    if len(boxes) > 0:
        new_areas = ((new_boxes[:, 2] - new_boxes[:, 0]) * (new_boxes[:, 3] - new_boxes[:, 1])).tolist()
    else:
        new_areas = []

    return new_image, new_boxes, new_areas, new_height, new_width, new_masks
