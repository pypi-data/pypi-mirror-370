from typing import Optional, Union

import numpy as np
from numpy.typing import NDArray


def set_default_measurement_dims(img_shape: tuple[int, ...]) -> NDArray[np.integer]:
    default_bf_image_space_dims = [1, 2, 3]
    non_singleton_dims_of_img = np.where(np.array(img_shape) > 1)[0]
    dims_to_measure = [d for d in default_bf_image_space_dims if d in non_singleton_dims_of_img]
    if len(dims_to_measure) == 0:
        raise ValueError(
            "No valid dimensions to measure.  Assumed space dimensions are [1,2,3], but these are all singleton."
        )
    return np.array(dims_to_measure)


def get_subscript_idx_of_target_max_within_roi(
    img: NDArray[np.floating], roi_indices: NDArray[np.integer]
) -> tuple[int, ...]:
    roi_idxs = [tuple(idx) for idx in roi_indices]
    voxel_values = np.array([img[idx] for idx in roi_idxs])
    voxel_max_idx = np.argmax(voxel_values)
    idx_of_max_in_roi_indices = roi_idxs[voxel_max_idx]
    return idx_of_max_in_roi_indices


def reduce_image_to_only_measurement_dimensions(
    img: NDArray[np.floating], measurement_dimensions: NDArray[np.integer], img_max_idx: tuple[int, ...]
) -> NDArray[np.floating]:
    idxs_to_keep_of_each_dimension: list[Union[int, slice]] = list(img_max_idx)
    for dimension_to_keep in measurement_dimensions:
        idxs_to_keep_of_each_dimension[dimension_to_keep] = slice(None)
    img_with_measurement_dimensions_only = img[tuple(idxs_to_keep_of_each_dimension)]
    return img_with_measurement_dimensions_only


def reduce_max_idx_to_only_measurement_dimensions(
    img_max_idx: NDArray[np.integer], dims_to_measure: NDArray[np.integer]
) -> tuple[int, ...]:
    indices = np.array(img_max_idx)[dims_to_measure]
    # Convert each element to an integer before creating the tuple
    return tuple(int(i) for i in indices)


def find_max_idx_within_expected_target_radius(
    img: NDArray[np.floating], img_max_idx: tuple[int, ...], radius: int
) -> tuple[int, ...]:
    img_subscript_indices = np.indices(img.shape)
    mask_center = np.array(img_max_idx)
    for _ in range(0, img.ndim):
        mask_center = mask_center[..., None]  # convert shape for subtraction with matrix

    img_mask = np.sqrt(np.sum((img_subscript_indices - mask_center) ** 2, axis=0)) <= radius
    masked_img = img * img_mask
    max_idx = np.unravel_index(np.argmax(masked_img), img.shape)
    return tuple(int(i) for i in max_idx)


def reduce_image_to_1D_at_point(
    img: NDArray[np.floating], point: tuple[int, ...], keep_dim: int
) -> NDArray[np.floating]:
    n_dim = img.ndim
    img_slice: list[Union[int, slice]] = [slice(None)] * n_dim
    for dim in range(0, n_dim):
        if dim != keep_dim:
            img_slice[dim] = point[dim]
    return img[tuple(img_slice)]


def calculate_linear_interpolation(a: float, b: float, a_idx: int, b_idx: int, interp_val: float) -> float:
    return a_idx + (b - interp_val) * (b_idx - a_idx) / (b - a)


def reorder_measured_dims_into_original_shape(
    sll_of_measured_dims: NDArray[np.floating], n_dim_of_input_image: int, measurement_dimensions: NDArray[np.integer]
) -> list[Optional[float]]:
    sll_of_input_img_shape: list[Optional[float]] = [None] * n_dim_of_input_image
    for index, dim in enumerate(measurement_dimensions):
        val = sll_of_measured_dims[index]
        sll_of_input_img_shape[dim] = float(val) if val is not None else None
    return sll_of_input_img_shape
