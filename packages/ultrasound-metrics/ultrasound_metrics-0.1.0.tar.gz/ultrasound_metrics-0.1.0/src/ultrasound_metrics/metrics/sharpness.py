"""Image sharpness metrics, such as Tenengrad."""

from types import ModuleType
from typing import Optional

from array_api_compat import array_namespace
from beartype import beartype as typechecker
from jaxtyping import Bool, Num, jaxtyped

from .._utils.array_api import ArrayAPIObj, convolve2d


@jaxtyped(typechecker=typechecker)
def tenengrad(
    image: Num[ArrayAPIObj, "height width"],
    roi: Optional[Bool[ArrayAPIObj, "height width"]] = None,
    sobel_kernel: Optional[Num[ArrayAPIObj, "kernel_height kernel_width"]] = None,
    reduce_sum: bool = True,
    normalize: bool = False,
) -> ArrayAPIObj:
    """Compute the Tenengrad sharpness metric of an image.

    Tenengrad sharpness [1][2] is a robust and accurate measure for focusing quality
    that performs well in digital photography. The metric applies a lateral
    Sobel filter to detect edges primarily in the horizontal direction, then
    sums the magnitude of the filtered response within a region of interest.

    This implementation is particularly suitable for ultrasound images where
    the lateral focusing quality is of primary interest.

    Parameters
    ----------
    image : array_like, shape (height, width)
        Input image for sharpness calculation. Should be a 2D array.
    roi : array_like, shape (height, width), optional
        Binary mask defining the region of interest. If provided, only pixels
        where roi is True (or non-zero) will contribute to the sharpness metric.
        If None, the entire image is used. Can be boolean or numeric array.
    sobel_kernel : array_like, shape (kernel_height, kernel_width), optional
        Custom convolution kernel to use for edge detection. If None, uses the
        default lateral Sobel filter optimized for ultrasound applications [3]:
        ```
        [ 1  0 -1]
        [ 2  0 -2]
        [ 1  0 -1]
        ```
        Custom kernels should be 2D arrays with odd dimensions.
    reduce_sum : bool, optional
        If True (default), returns the summed Tenengrad value as a scalar.
        If False, returns the magnitude image after Sobel filtering for visualization.
    normalize : bool, optional
        If True and reduce_sum=True, returns the mean instead of sum to normalize by ROI size.
        This makes the metric independent of ROI area. Default is False.

    Returns
    -------
    result : scalar or array_like
        If reduce_sum=True: The Tenengrad sharpness value (scalar). Higher values indicate
        sharper images. If normalize=True, returns mean instead of sum.
        If reduce_sum=False: The magnitude image after Sobel filtering (same shape as input).

    Notes
    -----
    The Tenengrad metric is computed as:

    F = Σ |G(r)|

    where G(r) is the result of convolving the image with the lateral Sobel
    filter, and the sum is taken over all pixels r in the region of interest.

    For ultrasound applications, it's recommended to exclude near-field
    artifacts by using an ROI that begins at approximately 10mm depth.

    References
    ----------
    .. [1] Groen, F. C., Young, I. T., & Ligthart, G. (1985). A comparison of
           different focus functions for use in autofocus algorithms.
           Cytometry, 6(2), 81-91.
    .. [2] Mir, R. N., et al. (2014). An extensive study of focus measures for
           digital photography. In Proc. Int. Conf. Comput. Sci. Inf. Technol.
    .. [3] Vr˚alstad, A.E. et al. (2024). Coherence Based Sound Speed Aberration
           Correction — with clinical validation in fetal ultrasound. arXiv:2411.16551
    """
    # Get the array namespace
    xp: ModuleType = array_namespace(image, roi, sobel_kernel)

    # Validate input
    if image.ndim != 2:
        raise ValueError(f"Image must be 2D, got {image.ndim}D")

    # Use provided kernel or create default lateral Sobel filter
    if sobel_kernel is None:
        # Define the lateral Sobel filter kernel
        # This detects edges primarily in the horizontal direction
        sobel_kernel = xp.asarray([
            [1.0, 0.0, -1.0],
            [2.0, 0.0, -2.0],
            [1.0, 0.0, -1.0],
        ])
    else:
        # Validate custom kernel
        if sobel_kernel.ndim != 2:
            raise ValueError(f"Sobel kernel must be 2D, got {sobel_kernel.ndim}D")

        kernel_h, kernel_w = sobel_kernel.shape
        if kernel_h % 2 == 0 or kernel_w % 2 == 0:
            raise ValueError(f"Sobel kernel dimensions must be odd, got {kernel_h}x{kernel_w}")

    # Apply convolution using backend-specific implementations
    filtered_image = convolve2d(image, sobel_kernel)

    # Take absolute value (magnitude)
    magnitude = xp.abs(filtered_image)

    if roi is not None:
        magnitude = magnitude[roi]  # This gives us a 1D array of just ROI pixels

    if not reduce_sum:
        return magnitude

    # Compute scalar metric
    if normalize:
        sharpness = xp.mean(magnitude)
    else:
        sharpness = xp.sum(magnitude)

    return sharpness
