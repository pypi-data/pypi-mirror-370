"""Array API helper functions.

Not part of the public API.
"""

import warnings
from typing import Any, Optional, Union

import numpy as np
from array_api_compat import (
    array_namespace,
    is_jax_array,
    is_numpy_array,
    is_torch_array,
)
from array_api_extra import isclose
from beartype import beartype as typechecker
from jaxtyping import Num, jaxtyped

# Helper type annotations
Real = Union[float, int]
# Note: When the Array API standard includes an Array Protocol, this should be updated
# https://github.com/data-apis/array-api/pull/589/
ArrayAPIObj = Any


@jaxtyped(typechecker=typechecker)
def histogram(
    x: Num[ArrayAPIObj, "*x_dims"],
    bins: Union[int, Num[ArrayAPIObj, "..."]],
    range: Optional[tuple[Real, Real]] = None,  # noqa: A002
    weights: Optional[Num[ArrayAPIObj, "*x_dims"]] = None,
    density: bool = False,
) -> tuple[ArrayAPIObj, ArrayAPIObj]:
    """Compute the histogram of a set of data.

    This function implements histogram functionality in a way that is compatible
    with multiple array backends.

    Parameters
    ----------
    x : array
        Input data. The histogram is computed over the flattened array.
    bins : int or array
        If `bins` is an int, it defines the number of equal-width bins in the
        given range. If `bins` is an array, it defines the monotonically increasing
        array of bin edges, including the rightmost edge, allowing for non-uniform bin
        widths.
    range : (float, float), optional
        The lower and upper range of the bins. If not provided, range is simply
        (x.min(), x.max()). Values outside the range are ignored.
    weights : array, optional
        An array of weights, of the same shape as `x`. Each value in `x` only
        contributes its associated weight towards the bin count.
    density : bool, optional
        If False, the result will contain the number of samples in each bin.
        If True, the result is the value of the probability density function at
        the bin, normalized such that the integral over the range is 1.

    Returns
    -------
    hist : array
        The values of the histogram. See `density` for a description of the
        possible semantics.
    bin_edges : array
        The edges of the bins. Length of `hist` plus 1 (nbins + 1).

    Notes
    -----
    This implementation attempts to remain compatible with the Array API standard
    while providing histogram functionality similar to numpy.histogram. When the
    Array API standard includes a histogram function, this implementation will be
    updated to use it.
    """
    # Get the array namespace to determine which array library we're using
    xp = array_namespace(x)

    # Error checking
    if (weights is not None) and (x.shape != weights.shape):
        raise ValueError("x and weights must have the same shape")

    # Try to use library-specific implementations when available for best performance
    if is_numpy_array(x):
        return np.histogram(x, bins=bins, range=range, weights=weights, density=density)

    elif is_jax_array(x):
        import jax.numpy as jnp

        return jnp.histogram(x, bins=bins, range=range, weights=weights, density=density)

    elif is_torch_array(x):
        import torch

        if weights is not None:
            weights = weights.flatten()

        # PyTorch has a argument-name helper that will complain
        # if we pass in range=None, so we need to handle that case separately
        kwargs = {}
        if range is not None:
            kwargs["range"] = range
        hist_result = torch.histogram(x.flatten(), bins=bins, weight=weights, density=density, **kwargs)  # type: ignore[arg-type]
        return hist_result.hist, hist_result.bin_edges

    else:
        array_lib_name = xp.__name__
        warnings.warn(f"histogram not implemented for {array_lib_name}. Casting to numpy for calculation.")
        x = np.asarray(x)
        hist_np, bin_edges_np = np.histogram(x, bins=bins, range=range, weights=weights, density=density)
        return xp.asarray(hist_np), xp.asarray(bin_edges_np)


@jaxtyped(typechecker=typechecker)
def nanmean(x: ArrayAPIObj, axis: Optional[int] = None, keepdims: bool = False) -> ArrayAPIObj:
    xp = array_namespace(x)
    is_nan = xp.isnan(x)
    x_no_nan = xp.where(is_nan, 0, x)
    count = xp.sum(~is_nan, axis=axis, keepdims=keepdims)
    total = xp.sum(x_no_nan, axis=axis, keepdims=keepdims)
    # Avoid division by zero: set denominator to 1 where count==0 (will fix result below)
    safe_count = xp.where(count == 0, 1, count)
    mean = total / safe_count
    # Set result to NaN where count==0
    mean = xp.where(count == 0, float("nan"), mean)
    return mean


def assert_array_equal(
    actual: ArrayAPIObj,
    expected: ArrayAPIObj,
    *,
    rtol: float = 1e-7,
    atol: float = 0.0,
    check_dtype: bool = True,
    err_msg: str = "",
) -> None:
    """Assert that two arrays are equal within tolerance (array-api compatible).

    This function provides array-api compatible array comparison for testing,
    avoiding the need to use private SciPy modules like xp_assert_equal.

    Parameters:
        actual: The actual array result
        expected: The expected array result
        rtol: Relative tolerance
        atol: Absolute tolerance
        check_dtype: Whether to check that dtypes match
        err_msg: Custom error message

    Raises:
        AssertionError: If arrays are not equal within tolerance
    """
    # Get array namespace from actual array
    xp = array_namespace(actual, expected)

    # Check shapes match
    if actual.shape != expected.shape:
        raise AssertionError(
            f"Arrays have different shapes. {err_msg}\nActual shape: {actual.shape}\nExpected shape: {expected.shape}"
        )

    # Check dtypes if requested
    if check_dtype and actual.dtype != expected.dtype:
        raise AssertionError(
            f"Arrays have different dtypes. {err_msg}\nActual dtype: {actual.dtype}\nExpected dtype: {expected.dtype}"
        )

    # Check values using array-api compatible methods
    # Use array_api_extra.isclose for tolerance checking (handles both real and complex arrays)
    # For dtype compatibility when check_dtype=False, convert to compatible dtypes
    actual_compare = actual
    expected_compare = expected

    if not check_dtype and actual.dtype != expected.dtype:
        # Convert to compatible dtypes for comparison
        # Convert both to the more general dtype (typically float)
        if xp.isdtype(actual.dtype, "integral") and xp.isdtype(expected.dtype, "integral"):
            # Both integers, keep as integers
            pass
        elif xp.isdtype(actual.dtype, "real floating") or xp.isdtype(expected.dtype, "real floating"):
            # At least one is float, convert both to float
            target_dtype = xp.float64 if hasattr(xp, "float64") else xp.float32
            actual_compare = xp.asarray(actual, dtype=target_dtype)
            expected_compare = xp.asarray(expected, dtype=target_dtype)
        elif xp.isdtype(actual.dtype, "complex floating") or xp.isdtype(expected.dtype, "complex floating"):
            # At least one is complex, convert both to complex
            target_dtype = xp.complex128 if hasattr(xp, "complex128") else xp.complex64
            actual_compare = xp.asarray(actual, dtype=target_dtype)
            expected_compare = xp.asarray(expected, dtype=target_dtype)

    close_elements = isclose(actual_compare, expected_compare, rtol=rtol, atol=atol, xp=xp)
    all_close = xp.all(close_elements)

    if not all_close:
        # Create a helpful error message
        max_diff = float(xp.max(xp.abs(actual - expected)))
        mean_diff = float(xp.mean(xp.abs(actual - expected)))

        raise AssertionError(
            f"Arrays are not equal within tolerance. {err_msg}\n"
            f"Max difference: {max_diff}\n"
            f"Mean difference: {mean_diff}\n"
            f"Tolerance: rtol={rtol}, atol={atol}"
        )


@jaxtyped(typechecker=typechecker)
def convolve2d(
    image: Num[ArrayAPIObj, "height width"], kernel: Num[ArrayAPIObj, "kernel_height kernel_width"]
) -> ArrayAPIObj:
    """Apply 2D convolution using backend-specific implementations.

    This function provides 2D convolution functionality that is compatible
    with multiple array backends, using optimized implementations when available.

    Parameters
    ----------
    image : array_like, shape (height, width)
        Input image to convolve
    kernel : array_like, shape (kernel_height, kernel_width)
        Convolution kernel

    Returns
    -------
    result : array_like, shape (height, width)
        Convolved image with same shape as input

    Notes
    -----
    This implementation attempts to use backend-specific optimized convolution
    functions when available (scipy for numpy, JAX signal for JAX arrays,
    torch.nn.functional for PyTorch). For other backends, it falls back to
    a manual implementation using Array API operations.
    """
    xp = array_namespace(image)

    if is_numpy_array(image):
        from scipy import ndimage

        # Use scipy's convolve for better performance and 'same' mode
        return ndimage.convolve(image, kernel, mode="constant", cval=0.0)

    elif is_jax_array(image):
        import jax.scipy.signal as jax_signal

        return jax_signal.convolve2d(image, kernel, mode="same")

    elif is_torch_array(image):
        import torch.nn.functional as F

        # PyTorch conv2d expects (batch, channels, height, width) format
        # Add batch and channel dimensions
        image_4d = image.unsqueeze(0).unsqueeze(0)  # Shape: (1, 1, H, W)
        kernel_4d = kernel.unsqueeze(0).unsqueeze(0)  # Shape: (1, 1, 3, 3)

        # Apply convolution with padding to maintain same size
        padding = kernel.shape[-1] // 2  # For 3x3 kernel, padding=1
        result = F.conv2d(image_4d, kernel_4d, padding=padding)

        # Remove batch and channel dimensions
        return result.squeeze(0).squeeze(0)

    else:
        # Fallback to manual implementation for other backends
        array_lib_name = xp.__name__
        warnings.warn(
            f"Convolution not optimized for {array_lib_name}. Using fallback implementation which may be slower."
        )
        return _manual_convolve2d(image, kernel)


def _manual_convolve2d(image: ArrayAPIObj, kernel: ArrayAPIObj) -> ArrayAPIObj:
    """Manual 2D convolution implementation using Array API operations.

    This provides a fallback convolution implementation that works with any
    Array API compatible library, though it may be slower than optimized
    backend-specific versions.

    Parameters
    ----------
    image : array_like
        Input image
    kernel : array_like
        Convolution kernel

    Returns
    -------
    result : array_like
        Convolved image with same shape as input
    """
    xp = array_namespace(image, kernel)

    # Get dimensions
    img_h, img_w = image.shape
    ker_h, ker_w = kernel.shape

    # Calculate padding to maintain same output size
    pad_h = ker_h // 2
    pad_w = ker_w // 2

    # Pad the image with zeros
    padded_image = xp.zeros((img_h + 2 * pad_h, img_w + 2 * pad_w), dtype=image.dtype)
    padded_image[pad_h : pad_h + img_h, pad_w : pad_w + img_w] = image

    # Initialize output
    output = xp.zeros_like(image)

    # Perform convolution
    for i in range(img_h):
        for j in range(img_w):
            # Extract patch from padded image
            patch = padded_image[i : i + ker_h, j : j + ker_w]
            # Compute dot product with kernel
            output[i, j] = xp.sum(patch * kernel)

    return output
