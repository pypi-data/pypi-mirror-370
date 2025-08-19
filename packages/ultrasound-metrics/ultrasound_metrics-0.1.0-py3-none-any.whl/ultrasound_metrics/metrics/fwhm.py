import warnings
from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from scipy.optimize import curve_fit

IMG_DIM = 4


def compute_fwhm(
    img: NDArray[np.floating],
    roi_indices: Optional[NDArray[np.integer]] = None,
    dims_to_measure: Optional[NDArray[np.integer]] = None,
    target_radius: Optional[int] = None,
    bf_grid_spacing: Optional[NDArray[np.floating]] = None,
    img_save_filename: Optional[str] = None,
) -> tuple[Optional[float], ...]:
    """Computes the full-width half-max of a point target.

    Parameters:
    img : np.ndarray
        The input image.
    roi_indices : np.ndarray
        Region of interest in the form of array indices.
    dims_to_measure : np.ndarray | None
        List of dimensions across which to measure the FWHM.
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
    bf_grid_spacing : np.ndarray | None
        The beamforming grid spacing in shape and dimension
        ordering consistent with the img parameter. If `None`,
        then the FWHM is returned in units of pixels.

    Returns:
    fwhm : tuple
        The full-width half-max of the point target over all input and
        non-singleton dimensions.
    """
    while img.ndim < IMG_DIM:  # time, lateral, elevation, depth
        img = img[None, ...]  # singleton time if none provided
    if roi_indices is None:
        roi_indices = np.indices(img.shape).reshape(img.ndim, -1).T
    if dims_to_measure is None:
        dims_to_measure = set_default_measurement_dims(img.shape)
    if bf_grid_spacing is None:
        bf_grid_spacing = np.ones(img.ndim)

    img_max_idx = get_subscript_idx_of_target_max_within_roi(img, roi_indices)
    dim_reduced_img = reduce_image_to_only_measurement_dimensions(img, dims_to_measure)
    dim_reduced_img_max_idx = tuple(np.asarray(img_max_idx)[dims_to_measure].tolist())
    if target_radius is not None:
        dim_reduced_img_max_idx = find_max_idx_within_expected_target_radius(
            dim_reduced_img, dim_reduced_img_max_idx, target_radius
        )

    fwhm_of_measured_dims = measure_fwhm_of_target(dim_reduced_img, dim_reduced_img_max_idx)
    if img_save_filename is not None:
        plt.imshow(dim_reduced_img)
        plt.plot(
            [dim_reduced_img_max_idx[1], dim_reduced_img_max_idx[1]],
            [
                dim_reduced_img_max_idx[0] - fwhm_of_measured_dims[0] / 2,
                dim_reduced_img_max_idx[0] + fwhm_of_measured_dims[0] / 2,
            ],
            "r",
        )
        plt.plot(
            [
                dim_reduced_img_max_idx[1] - fwhm_of_measured_dims[1] / 2,
                dim_reduced_img_max_idx[1] + fwhm_of_measured_dims[1] / 2,
            ],
            [dim_reduced_img_max_idx[0], dim_reduced_img_max_idx[0]],
            "r",
        )
        # plt.savefig(img_save_filename)
        # plt.close()

    fwhm = reorder_measured_dims_into_original_shape(fwhm_of_measured_dims, img.ndim, dims_to_measure)
    fwhm = convert_fwhm_to_input_units(fwhm, bf_grid_spacing)

    return tuple(map(float, fwhm))


def set_default_measurement_dims(img_shape: tuple[int, ...]) -> NDArray[np.integer]:
    default_bf_image_space_dims = [1, 2, 3]
    non_singleton_dims_of_img = np.where(np.array(img_shape) > 1)[0]
    dims_to_measure = [d for d in default_bf_image_space_dims if d in non_singleton_dims_of_img]
    if len(dims_to_measure) == 0:
        raise ValueError(
            "No valid dimensions to measure. Assumed space dimensions are [1,2,3], but these are all singleton."
        )
    return np.asarray(dims_to_measure, dtype=int)


def get_subscript_idx_of_target_max_within_roi(
    img: NDArray[np.floating], roi_indices: NDArray[np.integer]
) -> tuple[int, ...]:
    roi_idxs = [tuple(idx) for idx in roi_indices]
    voxel_values = np.array([img[idx] for idx in roi_idxs])
    voxel_max_idx = np.argmax(voxel_values)
    idx_of_max_in_roi_indices = roi_idxs[voxel_max_idx]
    return idx_of_max_in_roi_indices


def reduce_image_to_only_measurement_dimensions(
    img: NDArray[np.floating], measurement_dimensions: NDArray[np.integer]
) -> NDArray[np.floating]:
    idx_for_dimension_removal_slicing = 0
    idxs_to_keep_of_each_dimension: list[Union[int, slice]] = [idx_for_dimension_removal_slicing] * img.ndim
    for dimension_to_keep in measurement_dimensions:
        idxs_to_keep_of_each_dimension[dimension_to_keep] = slice(None)
    img_with_measurement_dimensions_only = img[tuple(idxs_to_keep_of_each_dimension)]
    return img_with_measurement_dimensions_only


def find_max_idx_within_expected_target_radius(
    img: NDArray[np.floating], img_max_idx: tuple[int, ...], radius: int
) -> tuple[int, ...]:
    img_subscript_indices = np.indices(img.shape)
    mask_center = np.array(img_max_idx)
    for _ in range(0, img.ndim):
        mask_center = mask_center[..., None]  # convert shape for subtraction with matrix

    img_mask = np.sqrt(np.sum((img_subscript_indices - mask_center) ** 2, axis=0)) <= radius
    masked_img = img * img_mask
    max_idx_array = np.unravel_index(np.argmax(masked_img), img.shape)
    # Convert numpy indices to regular Python integers for type compatibility
    max_idx = tuple(int(i) for i in max_idx_array)
    return max_idx


def measure_fwhm_of_target(img: NDArray[np.floating], img_max_idx: tuple[int, ...]) -> NDArray[np.floating]:
    n_dim = img.ndim
    fwhm: NDArray[np.floating] = np.empty(n_dim, dtype=float)
    fwhm[:] = np.nan
    # Old approach: find linear-interpolated point in 1-D
    for dim in range(0, n_dim):
        img_line_in_dim_through_max = reduce_image_to_1D_at_point(img, img_max_idx, dim)
        # Getting the max val and arg max here rather than re-finding in case a higher
        # max val exists on the line
        max_idx_on_line = img_max_idx[dim]
        max_val_on_line = img[img_max_idx]
        fwhm[dim] = measure_sub_pixel_fwhm(img_line_in_dim_through_max, max_idx_on_line, max_val_on_line)
    # plt.imshow(img)
    # plt.plot([img_max_idx[1],img_max_idx[1]],[img_max_idx[0]-fwhm[0]/2,img_max_idx[0]+fwhm[0]/2],'r')
    # plt.plot([img_max_idx[1]-fwhm[1]/2,img_max_idx[1]+fwhm[1]/2],[img_max_idx[0],img_max_idx[0]],'r')

    # Fit 2-D Gaussian and measure FWHM from fit
    fwhm = calculate_fwhm_from_2D_gaussian_fit(img, img_max_idx, fwhm)
    return fwhm


def reduce_image_to_1D_at_point(
    img: NDArray[np.floating], point: tuple[int, ...], keep_dim: int
) -> NDArray[np.floating]:
    n_dim = img.ndim
    img_slice: list[Union[int, slice]] = [slice(None)] * n_dim
    for dim in range(0, n_dim):
        if dim != keep_dim:
            img_slice[dim] = point[dim]
    return img[tuple(img_slice)]


def measure_sub_pixel_fwhm(
    im_line: NDArray[np.floating], max_idx: int, max_val: float, use_interp: bool = True
) -> float:
    """Measures the sub-pixel FWHM using linear interpolation

    Parameters:
    im_line : np.ndarray
        The 1-D orthogonal line across the target
    max_idx : int
        The index of the maximum position in the ROI
    max_val : float
        The value of the maximum position in the ROI
    use_interp : bool
        Whether to use linear interpolation to obtain sub-pixel
        precision

    Returns:
    fwhm : float
        The sub-pixel FWHM
    """
    im_line = np.squeeze(im_line)
    max_val_squeezed = float(np.squeeze(max_val))

    hm_of_first_side = measure_half_width_half_max(im_line[max_idx::-1], max_val_squeezed, use_interp)
    hm_of_second_side = measure_half_width_half_max(im_line[max_idx:], max_val_squeezed, use_interp)

    return hm_of_first_side + hm_of_second_side


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


def calculate_linear_interpolation(a: float, b: float, a_idx: int, b_idx: int, interp_val: float) -> float:
    return a_idx + (b - interp_val) * (b_idx - a_idx) / (b - a)


def calculate_fwhm_from_2D_gaussian_fit(
    img: NDArray[np.floating], img_max_idx: tuple[int, ...], fwhm: NDArray[np.floating]
) -> NDArray[np.floating]:
    if img.ndim != 2:
        raise ValueError("The provided image must be 2-D for 2-D Gaussian fitting.")
    x_var_idx = 3
    y_var_idx = 4
    img_cropped, img_cropped_max_idx = crop_image_around_max(img, img_max_idx, fwhm)
    var_estimate = calculate_var_from_fwhm(fwhm)

    theta = 0.0
    offset = 0.0
    initial_guess = (
        float(img_cropped[img_cropped_max_idx]),
        float(img_cropped_max_idx[0]),
        float(img_cropped_max_idx[1]),
        float(var_estimate[0]),
        float(var_estimate[1]),
        theta,
        offset,
    )
    try:
        fitted_gaussian_params = fit_2d_gaussian(img_cropped, initial_guess)
        estimated_var = fitted_gaussian_params[[x_var_idx, y_var_idx]]
    except Exception:
        estimated_var = var_estimate

    fwhm = calculate_fwhm_from_var(estimated_var)
    return fwhm


def crop_image_around_max(
    img: NDArray[np.floating], img_max_idx: tuple[int, ...], fwhm: NDArray[np.floating]
) -> tuple[NDArray[np.floating], tuple[int, int]]:
    # Cropping range of 4*FWHM (measured by pixel evaluation)
    fwhm_ints = np.array([int(val) if val is not None else 0 for val in fwhm]) * 2

    x_crop_start = max(img_max_idx[0] - fwhm_ints[0], 0)
    x_crop_stop = min(img_max_idx[0] + fwhm_ints[0] + 1, img.shape[0])
    y_crop_start = max(img_max_idx[1] - fwhm_ints[1], 0)
    y_crop_stop = min(img_max_idx[1] + fwhm_ints[1] + 1, img.shape[1])

    img_cropped = img[x_crop_start:x_crop_stop, y_crop_start:y_crop_stop].copy()
    img_cropped /= np.max(img_cropped)
    max_idx_array = np.unravel_index(np.argmax(img_cropped), img_cropped.shape)
    img_cropped_max_idx = (int(max_idx_array[0]), int(max_idx_array[1]))

    return img_cropped, img_cropped_max_idx


def calculate_var_from_fwhm(fwhm: NDArray[np.floating]) -> NDArray[np.floating]:
    """Calculate FWHM from variance."""
    return fwhm / float(2 * np.sqrt(2 * np.log(2)))


def fit_2d_gaussian(img: NDArray[np.floating], initial_guess: tuple[float, ...]) -> NDArray[np.floating]:
    """Fit a 2D Gaussian to the image and return the parameters."""
    fig, ax = plt.subplots()
    ax.imshow(img)
    # initial_guess = (10, 50, 50, 10, 15, 0, 2)
    x = np.linspace(0, img.shape[1], img.shape[1])
    y = np.linspace(0, img.shape[0], img.shape[0])
    x, y = np.meshgrid(x, y)
    print("initial guess ", initial_guess)
    popt: NDArray[np.floating]
    popt, _ = curve_fit(  # type: ignore[call-overload]
        gaussian_2d,
        (x, y),
        img.ravel(),
        p0=list(initial_guess),
        method="trf",
        bounds=(
            [0.0, 0.0, 0.0, 0.0, 0.0, -np.inf, -np.inf],
            [
                2.0,
                float(img.shape[0]),
                float(img.shape[1]),
                2.0 * float(initial_guess[3]),
                2.0 * float(initial_guess[4]),
                np.inf,
                np.inf,
            ],
        ),
        maxfev=5000,
    )
    print("fitted result ", popt)
    # Reconstruct the fitted Gaussian
    fit = gaussian_2d((x, y), *popt)
    fig2, ax2 = plt.subplots()
    ax2.imshow(fit.reshape(img.shape[0], img.shape[1]))

    return popt


def gaussian_2d(
    xy: tuple[NDArray[np.floating], NDArray[np.floating]],
    amplitude: float,
    xo: float,
    yo: float,
    sigma_x: float,
    sigma_y: float,
    theta: float,
    offset: float,
) -> NDArray[np.floating]:
    """2D Gaussian function."""
    x, y = xy
    # Ensure x and y are float64
    x = x.astype(np.float64)
    y = y.astype(np.float64)

    # Calculate the Gaussian
    exponent = -((x - xo) ** 2 / (2 * sigma_x**2) + (y - yo) ** 2 / (2 * sigma_y**2))
    g = amplitude * np.exp(exponent)

    return g.ravel()


def calculate_fwhm_from_var(var: NDArray[np.floating]) -> NDArray[np.floating]:
    """Calculate FWHM from variance."""
    return var * float(2 * np.sqrt(2 * np.log(2)))


def reorder_measured_dims_into_original_shape(
    fwhm_of_measured_dims: NDArray[np.floating], n_dim_of_input_image: int, measurement_dimensions: NDArray[np.integer]
) -> NDArray[np.floating]:
    """Reorder the measured FWHM values into the original shape."""
    fwhm_of_input_img_shape = np.empty(n_dim_of_input_image, dtype=float)
    fwhm_of_input_img_shape[:] = np.nan
    for index, dim in enumerate(measurement_dimensions):
        val = fwhm_of_measured_dims[index]
        fwhm_of_input_img_shape[dim] = float(val) if not np.isnan(val) else None
    return fwhm_of_input_img_shape


def convert_fwhm_to_input_units(
    fwhm: NDArray[np.floating], bf_grid_spacing: NDArray[np.floating]
) -> NDArray[np.floating]:
    """Convert FWHM from pixels to physical units."""
    return fwhm * bf_grid_spacing
