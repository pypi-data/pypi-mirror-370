import sys
import warnings
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from scipy.signal import find_peaks

sys.path.append("..")
from ultrasound_metrics.metrics.utils import (
    calculate_linear_interpolation,
    find_max_idx_within_expected_target_radius,
    get_subscript_idx_of_target_max_within_roi,
    reduce_image_to_1D_at_point,
    reduce_image_to_only_measurement_dimensions,
    reduce_max_idx_to_only_measurement_dimensions,
    reorder_measured_dims_into_original_shape,
    set_default_measurement_dims,
)

IMG_DIM = 4


def compute_sll(
    img: NDArray[np.floating],
    roi_indices: Optional[NDArray[np.integer]] = None,
    dims_to_measure: Optional[NDArray[np.integer]] = None,
    target_radius: Optional[int] = None,
    show_plot: bool = False,
) -> tuple[Optional[float], ...]:
    """Computes the side lobe level (SLL) of a point target.

    Parameters:
    img : np.ndarray
        The input image.
    roi_indices : np.ndarray
        Region of interest in the form of array indices.
    dims_to_measure : np.ndarray | None
        List of dimensions across which to measure the SLL.
        If `None`, then the default space dimensions of the bmode
        image are used (dimensions [1,2,3]). If any of these
        dimensions are singleton, then they are excluded from
        consideration.
    target_radius : int | None
        Expected radius of the target used to find max point around
        the max detected within the ROI. This is used in case the
        target is registered but the position of the max value is
        not located within the ROI. If `None`, then then no search
        for the max value outside the roi is performed.

    Returns:
    sll : tuple
        The side lobe level of the point target over all input and
        non-singleton dimensions. The side lobe level is calculated as
            sll = 10*log10((side lobe peak amplitude)/(main lobe peak amplitude))
    """
    while img.ndim < IMG_DIM:  # time, lateral, elevation, depth
        img = img[None, ...]  # singleton time if none provided
    if roi_indices is None:
        roi_indices = np.indices(img.shape).reshape(img.ndim, -1).T
    if dims_to_measure is None:
        dims_to_measure = set_default_measurement_dims(img.shape)

    img_max_idx = get_subscript_idx_of_target_max_within_roi(img, roi_indices)
    dim_reduced_img = reduce_image_to_only_measurement_dimensions(img, dims_to_measure, img_max_idx)
    if show_plot and dim_reduced_img.ndim > 1:
        fig, ax = plt.subplots()
        ax.imshow(np.log10(dim_reduced_img))
        ax.plot(img_max_idx[3], img_max_idx[1], "xr")
    dim_reduced_img_max_idx = reduce_max_idx_to_only_measurement_dimensions(
        np.asarray(img_max_idx, dtype=int), dims_to_measure
    )
    if target_radius is not None:
        dim_reduced_img_max_idx = find_max_idx_within_expected_target_radius(
            dim_reduced_img, dim_reduced_img_max_idx, target_radius
        )

    sll_of_measured_dims = measure_sll_of_target(dim_reduced_img, dim_reduced_img_max_idx, show_plot)
    sll = reorder_measured_dims_into_original_shape(sll_of_measured_dims, img.ndim, dims_to_measure)

    return tuple(sll)


def measure_sll_of_target(
    img: NDArray[np.floating], img_max_idx: tuple[int, ...], show_plot: bool
) -> NDArray[np.floating]:
    n_dim = img.ndim
    sll = np.zeros(n_dim, dtype=float)
    for dim in range(0, n_dim):
        img_line_in_dim_through_max = reduce_image_to_1D_at_point(img, img_max_idx, dim)
        # Getting the max val and arg max here rather than re-finding in case a higher
        # max val exists on the line
        max_idx_on_line = img_max_idx[dim]
        max_val_on_line = float(img[img_max_idx])
        sll_val = measure_sll(img_line_in_dim_through_max, max_idx_on_line, max_val_on_line)
        sll[dim] = sll_val
        if show_plot:
            fig, ax = plt.subplots()
            ax.plot(10 * np.log10(img_line_in_dim_through_max))
            img_max = 10 * np.log10(max_val_on_line)
            ax.axhline(img_max, ls="--", c="k")
            ax.axhline(sll_val + img_max, ls="--", c="k")
            ax.text(max_idx_on_line + 10, img_max * 0.95, f"SLL={round(sll_val, 2)!s}")
            ax.set_xlabel("pixel")
            ax.set_ylabel("dB")
    return sll


def measure_sll(im_line: NDArray[np.floating], max_idx: int, max_val: float, use_interp: bool = True) -> float:
    """Measures the side lobe level (SLL) of the input pixel array.
    The half-max point is detected and used as a starting index
    for detecting the next occurring peak in the line.  This way,
    sub-peaks within the main lobe will not be accidentally
    counted as the side lobe. The side lobe peak is measured
    on each side of the PSF and then the maximum one is used for
    computing the SLL.

    Parameters:
    im_line : np.ndarray
        The 1-D orthogonal line across the target
    max_idx : int
        The index of the maximum position in the ROI
    max_val : float
        The value of the maximum position in the ROI
    use_interp : bool
        Whether to use linear interpolation to obtain sub-pixel
        precision for detection of the half-max point

    Returns:
    sll : float
        The side lobe level is calculated as
            sll = 10*log10((side lobe peak amplitude)/(main lobe peak amplitude))
    """
    hm_of_side_1 = measure_half_width_half_max(im_line[max_idx::-1], max_val, use_interp)
    side_lobe_amplitude_1 = find_one_side_side_lobe_amplitude(im_line[(max_idx - int(round(hm_of_side_1))) :: -1])

    hm_of_side_2 = measure_half_width_half_max(im_line[max_idx:], max_val, use_interp)
    side_lobe_amplitude_2 = find_one_side_side_lobe_amplitude(im_line[(max_idx + int(round(hm_of_side_2))) :])

    sll = 10 * float(np.log10(max(side_lobe_amplitude_1, side_lobe_amplitude_2)) / im_line[max_idx])

    return sll


def measure_half_width_half_max(pixel_array: NDArray[np.floating], max_val: float, use_interp: bool) -> float:
    hwhm = 0.0
    half_max_value = 0.5 * max_val
    indices_greater_than_half_width = np.where(pixel_array < half_max_value)[0]
    if len(indices_greater_than_half_width) == 0:
        warnings.warn(
            "The half-max point was not found. \
                      The dimension with length {len(pixel_array)} may have been too small, \
                       or the target was too close to the edge of the image."
        )
        hwhm = float(len(pixel_array))
    else:
        hwhm_no_interp = int(indices_greater_than_half_width[0])
        a_idx = hwhm_no_interp
        a = float(pixel_array[a_idx])
        b_idx = a_idx - 1
        b = float(pixel_array[b_idx])
        hwhm = (
            calculate_linear_interpolation(a, b, a_idx, b_idx, half_max_value) if use_interp else float(hwhm_no_interp)
        )
    return hwhm


def find_one_side_side_lobe_amplitude(pixel_array: NDArray[np.floating]) -> float:
    peaks, _ = find_peaks(np.log10(pixel_array))
    if len(peaks) == 0:
        warnings.warn("No side-lobe peak detected!")
        return 1.0
    return float(pixel_array[peaks[0]])
