# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper utiities for image tiling."""

import ast
import re
from typing import Any, Optional, Tuple, cast

import torch

from azureml.acft.common_components import get_logger_app
from azureml.acft.common_components.image.runtime_common.common.exceptions import (
    AutoMLVisionValidationException)
from azureml.acft.common_components.image.runtime_common.common.tiling_dataset_element import Tile
from azureml.acft.common_components.image.runtime_common.object_detection.common.constants import \
    TilingParameters

logger = get_logger_app(__name__)


def parse_tile_grid_size_str(tile_grid_size_str: str) -> Tuple[int, int]:
    """ Parse tile_grid_size in one of the following string formats.
            1. "(3, 2)"
            2. "3x2"
            3. "3X2"

    :param tile_grid_size_str: String representation of tile_grid_size
    :type tile_grid_size_str: str
    :return: Parsed tile_grid_size
    :rtype: Tuple[int, int]
    """
    format_1 = "3x2"
    format_2 = "3X2"
    format_3 = "(3, 2)"
    invalid_str_error_msg = (
        f"Unable to parse tile_grid_size {tile_grid_size_str}. "
        f"Should be in the format {format_1}, or {format_2}, or {format_3}"
    )

    if 'x' in tile_grid_size_str or 'X' in tile_grid_size_str:
        # Parse tile_grid_size in format "3x2" or "3X2"
        # Split by spaces, 'x' or 'X' characters and remove empty strings from the split.
        tile_grid_size_separated = list(filter(None, re.split("[ xX]+", tile_grid_size_str.strip())))
        if len(tile_grid_size_separated) != 2:
            raise AutoMLVisionValidationException(f"{invalid_str_error_msg}", has_pii=False)
        try:
            tile_grid_size = (int(tile_grid_size_separated[0]), int(tile_grid_size_separated[1]))
        except ValueError:
            raise AutoMLVisionValidationException({invalid_str_error_msg}, has_pii=False)
    else:
        # Parse tile_grid_size in the format "(3, 2)"
        try:
            tile_grid_size = ast.literal_eval(tile_grid_size_str.strip())
        except SyntaxError:
            raise AutoMLVisionValidationException({invalid_str_error_msg}, has_pii=False)

    return tile_grid_size


def validate_tiling_settings(tile_grid_size: Optional[Tuple[int, int]], tile_overlap_ratio: Optional[float]) -> None:
    """ Validate tiling settings.

    :param tile_grid_size: Tuple indicating number of tiles along width and height dimensions.
    :type tile_grid_size: Tuple[int, int]
    :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension.
    :type tile_overlap_ratio: float
    """
    if tile_grid_size is None:
        return

    if isinstance(tile_grid_size, tuple) or isinstance(tile_grid_size, list):
        if len(tile_grid_size) != 2:
            raise AutoMLVisionValidationException(
                f"tile_grid_size is of size {len(tile_grid_size)}, should be of size 2. Cannot use tiling. "
                f"For more details, refer {TilingParameters.TILING_DOC_LINK}", has_pii=False)
    else:
        # Resolving TypeEror when tile_grid_size is neither tuple nor list
        raise AutoMLVisionValidationException(
            f"tile_grid_size value is {tile_grid_size}, but it should be of size 2. Cannot use tiling. "
            f"For more details, refer {TilingParameters.TILING_DOC_LINK}", has_pii=False)

    if not isinstance(tile_grid_size[0], int) or not isinstance(tile_grid_size[1], int):
        raise AutoMLVisionValidationException(
            f"tile_grid_size {tile_grid_size} has non-integer values. Cannot use tiling", has_pii=False)

    if tile_grid_size[0] <= 0 or tile_grid_size[1] <= 0:
        raise AutoMLVisionValidationException(
            f"Invalid tile_grid_size {tile_grid_size}. Values should be positive integers. Cannot use tiling",
            has_pii=False
        )

    if tile_grid_size[0] == 1 and tile_grid_size[1] == 1:
        raise AutoMLVisionValidationException(
            f"Invalid tile_grid_size {tile_grid_size}. At least one of dimensions should have value greater than 1."
            f"Cannot use tiling",
            has_pii=False
        )

    if not isinstance(tile_overlap_ratio, float):
        raise AutoMLVisionValidationException(
            f"Invalid tile_overlap_ratio {tile_overlap_ratio}. It should be a float value. "
            f"Cannot use tiling",
            has_pii=False
        )

    if tile_overlap_ratio < 0.0 or tile_overlap_ratio >= 1.0:
        raise AutoMLVisionValidationException(
            f"Invalid tile_overlap_ratio {tile_overlap_ratio}. Value should be >= 0 and < 1. Cannot use tiling.",
            has_pii=False
        )


def get_tiles(tile_grid_size: Tuple[int, int], tile_overlap_ratio: float, image_size: Tuple[int, int]) -> Any:
    """Get tiles when image is split using tile_grid_size.

    :param tile_grid_size: Grid size indicating total number of tiles the image is split into along each axis.
    :type tile_grid_size: Tuple[int, int]
    :param tile_overlap_ratio: Overlap ratio between adjacent tiles in each dimension.
    :type tile_overlap_ratio: float
    :param image_size: Tuple indicating width and height of the image.
    :type image_size: Tuple[int, int]
    :return: List of tiles.
    :rtype: List[Tile]
    """
    tile_width = image_size[0] / (tile_overlap_ratio + (1 - tile_overlap_ratio) * tile_grid_size[0])
    tile_height = image_size[1] / (tile_overlap_ratio + (1 - tile_overlap_ratio) * tile_grid_size[1])

    # Tiles start at 0.0 and in increments of (1- tile_overlap_ratio) * tile_width
    tile_top_x_list = torch.arange(0.0, image_size[0], (1 - tile_overlap_ratio) * tile_width,
                                   device="cpu")[:tile_grid_size[0]]
    tile_top_y_list = torch.arange(0.0, image_size[1], (1 - tile_overlap_ratio) * tile_height,
                                   device="cpu")[:tile_grid_size[1]]
    tile_top_list = torch.cartesian_prod(tile_top_x_list, tile_top_y_list)
    tile_bottom_list = tile_top_list.add(torch.tensor([tile_width, tile_height], device="cpu").view(1, 2))
    tiles = torch.cat((tile_top_list, tile_bottom_list), dim=1)
    # Round the pixel co-ordinates
    tiles.round_()

    return [Tile(cast(Tuple[float, float, float, float], tuple(tile.tolist()))) for tile in tiles]
