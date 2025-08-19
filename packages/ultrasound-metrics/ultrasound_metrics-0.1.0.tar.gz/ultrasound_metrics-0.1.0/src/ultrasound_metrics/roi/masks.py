"""Mask creation functions for ROI selection in ultrasound images.

This module provides functions for creating boolean masks of various shapes
(circles, rectangles, squares) that can be used for region-of-interest selection
in ultrasound image analysis.

TODO: Add elliptical mask support for more precise ROI shapes (integrate with build_mask).
"""

from typing import Any, Union

from array_api_compat import array_namespace


def create_circular_mask(position: tuple[float, float], radius: float, x_axis: Any, z_axis: Any, xp: Any = None) -> Any:
    """Create a boolean mask for a circle centered at position with given radius.


    Parameters
    ----------
    position : tuple[float, float]
        (x, z) coordinates of the circle center.
    radius : float
        Radius of the circle.
    x_axis : array
        1D array of lateral coordinates (x).
    z_axis : array
        1D array of axial coordinates (z).
    xp : array namespace, optional
        Array API namespace. If None, inferred from x_axis.


    Returns
    -------
    mask : array
        Boolean mask: True inside circle, False elsewhere.
    """
    if xp is None:
        xp = array_namespace(x_axis)
    # Ensure x_axis and z_axis are arrays
    x_axis = xp.asarray(x_axis)
    z_axis = xp.asarray(z_axis)
    # Create meshgrid using the array API meshgrid function
    xx, zz = xp.meshgrid(x_axis, z_axis, indexing="xy")
    dist = xp.sqrt((xx - position[0]) ** 2 + (zz - position[1]) ** 2)
    mask = dist <= radius
    return mask


def create_rectangular_mask(
    top_left: tuple[float, float], dimension: tuple[float, float], x_axis: Any, z_axis: Any, xp: Any = None
) -> Any:
    """Create a boolean mask for a rectangle with top-left corner and dimensions.


    Parameters
    ----------
    top_left : tuple[float, float]
        (x, z) coordinates of the rectangle's top-left corner.
    dimension : tuple[float, float]
        (width, height) of the rectangle.
    x_axis : array
        1D array of lateral coordinates (x).
    z_axis : array
        1D array of axial coordinates (z).
    xp : array namespace, optional
        Array API namespace. If None, inferred from x_axis.


    Returns
    -------
    mask : array
        Boolean mask: True inside rectangle, False elsewhere.
    """
    if xp is None:
        xp = array_namespace(x_axis)
    x_axis = xp.asarray(x_axis)
    z_axis = xp.asarray(z_axis)
    xx, zz = xp.meshgrid(x_axis, z_axis, indexing="xy")
    x0, z0 = top_left
    width, height = dimension
    mask = (xx >= x0) & (xx <= x0 + width) & (zz >= z0) & (zz <= z0 + height)
    return mask


def build_mask(
    position: tuple[float, float],
    dimension: Union[float, tuple[float, float]],
    x_axis: Any,
    z_axis: Any,
    shape: str = "circle",
) -> Any:
    """
    Build a mask for ROI selection in a 2D grid.


    This is the main function for creating ROI masks of various shapes.
    It provides a unified interface for creating circular, rectangular, and square masks.


    Parameters
    ----------
    position : tuple[float, float]
        (x, z) position of the mask center (for circle/square) or top-left (for rectangle).
    dimension : float or tuple[float, float]
        Size of the shape. For circle/square: radius/width. For rectangle: (width, height).
    x_axis : array
        1D array of lateral coordinates (x).
    z_axis : array
        1D array of axial coordinates (z).
    shape : str, default="circle"
        Shape of the mask: 'circle', 'rectangle', or 'square'.


    Returns
    -------
    mask : array
        Boolean mask: True inside ROI, False elsewhere.


    Raises
    ------
    AttributeError
        If shape is not one of the supported shapes.
    ValueError
        If dimension format is invalid for the specified shape.


    Examples
    --------
    >>> import numpy as np
    >>> from ultrasound_metrics.roi import build_mask
    >>>
    >>> # Create coordinate arrays
    >>> x = np.linspace(-10, 10, 100)
    >>> z = np.linspace(0, 20, 100)
    >>>
    >>> # Create circular mask with radius 5 at center (0, 10)
    >>> mask = build_mask((0, 10), 5, x, z, shape="circle")
    >>>
    >>> # Create rectangular mask 8x6 at center (0, 10)
    >>> mask = build_mask((0, 10), (8, 6), x, z, shape="rectangle")
    """
    xp = array_namespace(x_axis)
    if shape not in ["circle", "rectangle", "square"]:
        raise AttributeError(f"Unknown shape for mask: {shape}")

    if shape in ["circle", "square"]:
        if isinstance(dimension, (float, int)):
            dimension = (dimension, dimension)
        elif isinstance(dimension, tuple) and len(dimension) == 2:
            pass
        else:
            raise ValueError(f"Invalid dimension for shape {shape}")
        if shape == "circle":
            mask = create_circular_mask(position, dimension[0], x_axis, z_axis, xp=xp)
        else:  # square
            # For square, position is center, so convert to top-left
            top_left = (position[0] - dimension[0] / 2, position[1] - dimension[1] / 2)
            mask = create_rectangular_mask(top_left, dimension, x_axis, z_axis, xp=xp)
    elif shape == "rectangle":
        if not (isinstance(dimension, tuple) and len(dimension) == 2):
            raise ValueError("Rectangle requires dimension=(width, height)")
        # For rectangle, position is center, so convert to top-left
        top_left = (position[0] - dimension[0] / 2, position[1] - dimension[1] / 2)
        mask = create_rectangular_mask(top_left, dimension, x_axis, z_axis, xp=xp)
    else:
        raise ValueError(f"Unknown shape for mask: {shape}")
    return mask
