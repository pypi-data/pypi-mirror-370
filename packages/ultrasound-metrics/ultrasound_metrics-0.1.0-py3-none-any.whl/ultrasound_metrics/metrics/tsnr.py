"""Temporal Signal-to-Noise Ratio (tSNR) for ultrasound speckle.

This module provides functions for computing the temporal SNR of ultrasound speckle
over multiple acquisitions, which is useful for quantifying decorrelation, evaluating
probe motion, and checking image stability in repeated scans.

This method is closely related to the repeated-measurements and adjacent-frame SNR
estimates used in noise.py, but retains per-pixel granularity rather than aggregating
into a single value.
"""

import warnings

from array_api_compat import array_namespace
from beartype import beartype as typechecker
from jaxtyping import jaxtyped

from ultrasound_metrics._utils.array_api import ArrayAPIObj


@jaxtyped(typechecker=typechecker)
def tsnr(
    data: ArrayAPIObj,
    *,
    output_db: bool = False,
) -> ArrayAPIObj:
    """
    Compute the temporal Signal-to-Noise Ratio (tSNR) of ultrasound speckle.

    This function evaluates the stability of signal over time at each
    spatial location (pixel or voxel) using signal decomposition.

    tSNR(x, y, z) = signal_power(x, y, z) / noise_power(x, y, z)
    where:
    - signal_power is the power of the temporal mean (stable component)
    - noise_power is the power of temporal variations (unstable component)

    Parameters
    ----------
    data : array
        Input data with shape (x, [y,], z, t) or (x, t) where:
        - x, y, z are spatial dimensions (y is optional for 2D data)
        - t is the time dimension (repeated acquisitions/frames)
        - For ROI analysis, spatial dimensions can be flattened to (x, t)
        - Can be real or complex floating-point data
    output_db : bool, optional
        If True, return tSNR in decibels: 10 * log10(signal_power / noise_power)
        If False, return tSNR in linear scale: signal_power / noise_power
        Default is False.

    Returns
    -------
    tsnr : array
        Temporal SNR values with shape (x, [y,], z).
        Each pixel/voxel contains the tSNR value for that spatial location.

    Raises
    ------
    ValueError
        If data has fewer than 2 dimensions or if time dimension has fewer than 2 points.

    Warns
    -----
    UserWarning
        If noise power is zero for some pixels (would cause division by zero).

    Notes
    -----
    - For 2D data, input shape should be (x, z, t)
    - For 3D data, input shape should be (x, y, z, t)
    - For ROI analysis, flattened spatial data can use shape (x, t)
    - The time dimension (t) must have at least 2 points to compute temporal mean
    - Zero noise power will cause a warning and return +inf for those pixels
    - Complex data is handled by computing the magnitude (absolute value) before processing
    - Uses signal decomposition: signal = temporal_mean, noise = data - signal

    """
    xp = array_namespace(data)

    # Validate input dimensions
    if data.ndim < 2:
        raise ValueError(f"Data must have at least 2 dimensions (spatial + time), got {data.ndim}")

    # Check time dimension (last dimension)
    time_dim = data.shape[-1]
    if time_dim < 2:
        raise ValueError(f"Time dimension must have at least 2 points to compute temporal mean, got {time_dim}")

    # Decompose the raw signal into "signal" and "noise"
    # Signal is the temporal mean (stable component), noise is everything else (temporal variations)
    signal = xp.mean(data, axis=-1, keepdims=True)
    noise = data - signal

    # Compute signal power and noise power
    signal_power = xp.mean(xp.abs(signal) ** 2, axis=-1)
    noise_power = xp.mean(xp.abs(noise) ** 2, axis=-1)

    # Check for zero noise power and warn if found
    if xp.any(noise_power == 0):
        warnings.warn(
            "Noise power is zero for some pixels. This would cause division by zero. "
            "Returning +inf for those pixels. Check if your data has sufficient temporal variation.",
            UserWarning,
        )

    # Handle division by zero by returning +inf for zero noise power
    with xp.errstate(divide="ignore", invalid="ignore"):
        tsnr = xp.where(noise_power == 0, xp.inf, signal_power / noise_power)

    # Convert to dB if requested
    if output_db:
        tsnr = 10 * xp.log10(tsnr)

    return tsnr
