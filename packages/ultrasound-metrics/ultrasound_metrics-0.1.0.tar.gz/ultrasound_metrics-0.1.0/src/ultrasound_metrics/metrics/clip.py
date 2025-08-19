"""Measure signal-clipping in ultrasound pulse-echo data (RF or I/Q).

Uses time-domain amplitude thresholding.
"""

from enum import Enum
from typing import Any, Optional, Union

import equinox as eqx
import jax
import jax.numpy as jnp
from beartype import beartype as typechecker
from jaxtyping import Array, Bool, Num, Real, jaxtyped

# Helper type for scalar values: jaxtyping
Scalar = Union[float, int]


class ClipDetectMethod(str, Enum):
    """Enum for different clipping metrics."""

    THRESHOLD = "threshold"
    MAX_AMPLITUDE = "max_amplitude"


@jaxtyped(typechecker=typechecker)
def clip_ratio(
    data: Num[Array, " *batch sample"],
    method: Union[ClipDetectMethod, str] = ClipDetectMethod.THRESHOLD,
    **kwargs: Any,
) -> float:
    """Measure the ratio of clipped samples in the data.

    Supports multiple methods for clipping detection.

    Args:
        data: data array of shape (..., n_samples)
        method: Method to use for clipping detection.
        **kwargs: Additional keyword arguments for the clipping detection method.

    Returns:
        Ratio of clipped samples in the data.
    """
    if method == ClipDetectMethod.THRESHOLD:
        return float(is_clipped_threshold(data, **kwargs).mean())
    elif method == ClipDetectMethod.MAX_AMPLITUDE:
        return float(is_clipped_max_amplitude(data, **kwargs).mean())
    else:
        raise ValueError(f"Invalid clip detection method: {method}")


@jaxtyped(typechecker=typechecker)
@eqx.filter_jit
def is_clipped_threshold(
    data: Num[Array, " *batch sample"],
    *,
    max_threshold: float,
    min_threshold: Optional[float] = None,
) -> Bool[Array, " *batch sample"]:
    """Detect clipped samples in the data by comparing to a threshold.

    Args:
        data: data array of shape (..., n_samples)
        max_threshold: maximum allowed amplitude
        min_threshold: minimum allowed amplitude. If None, symmetric threshold is assumed.

    Returns:
        Boolean mask with shape=data.shape indicating which samples were clipped
    """
    if jnp.iscomplexobj(data):
        # Use magnitude for complex data to detect clipping
        return jnp.abs(data) >= max_threshold

    if min_threshold is None:
        min_threshold = -max_threshold
    return (data < min_threshold) | (data > max_threshold)


@eqx.filter_jit
@jaxtyped(typechecker=typechecker)
def _is_clipped_max_amplitude_core(
    data_to_check: Real[Array, " sample"],
    *,
    low_factor: Optional[float],
    high_factor: Optional[float],
    min_contiguous: int,
) -> Bool[Array, " sample"]:
    """Core computation for clip detection on a single channel.

    Args:
        data_to_check: data array of shape (sample,)
        low_factor: low threshold factor
        high_factor: high threshold factor
        min_contiguous: minimum number of contiguous samples outside the range to consider
            that the signal was clipped.
    """
    # Calculate the min/max range of the data
    min_val = jnp.min(data_to_check)
    max_val = jnp.max(data_to_check)
    data_range = max_val - min_val

    # Create mask for potential clips
    # Start with an array of False values
    potential_clips = jnp.zeros_like(data_to_check, dtype=bool)

    # Check low threshold if it's active
    if low_factor is not None:
        # 0 magnitude is not clipping for complex-magnitude data
        low_threshold = min_val + (low_factor * data_range)
        potential_clips = potential_clips | (data_to_check <= low_threshold)

    # Check high threshold if it's active
    if high_factor is not None:
        high_threshold = max_val - (high_factor * data_range)
        potential_clips = potential_clips | (data_to_check >= high_threshold)

    # If min_contiguous is 1, we assume any potential clips are real clips
    has_contiguous_clip = jnp.array(min_contiguous <= 1)

    # Check for contiguous clipped samples using convolution
    if min_contiguous > 1:
        # Create a kernel of ones with length min_contiguous
        kernel = jnp.ones(min_contiguous)
        # Convolve with the potential_clips
        conv_result = jnp.convolve(potential_clips, kernel, mode="same")
        # If any window sum equals min_contiguous, we have a contiguous segment of clipped samples
        has_contiguous_clip = jnp.any(conv_result >= min_contiguous)

    # Return the potential clips mask if contiguous clipping exists, otherwise zeros
    return jnp.where(has_contiguous_clip, potential_clips, jnp.zeros_like(potential_clips))


@jaxtyped(typechecker=typechecker)
def is_clipped_max_amplitude(
    data: Num[Array, " *batch sample"],
    *,
    range_factor: Union[Scalar, tuple[Optional[Scalar], Optional[Scalar]]] = 0.01,
    min_contiguous: int = 1,
) -> Bool[Array, " *batch sample"]:
    """Detect clipped samples in the data by checking for contiguous segments outside the normal range.

    Implementation note: allows for a different threshold for each time-series in the batch.

    Args:
        data: data array of shape (..., n_samples)
        range_factor: How far inside the data's min/max range to consider as clipping:
            - float: symmetric factor for real data (e.g., 0.01 means within ±1% of the data range)
                For complex data, this is the factor for the magnitude range.
            - tuple: (lower, upper) factors for asymmetric thresholds
            - None for either value in the tuple to disable clipping detection on that side
            Use range_factor when clipping is soft, or when there is some preprocessing
                (such as filtering or lossy compression) that softens hard-clipping.
        min_contiguous: minimum number of contiguous samples outside the range to consider
            that the signal was clipped.
            This is for guessing whether the signal was clipped, rather than just
                that the actual signal amplitude has some range.

    Returns:
        Boolean mask with shape=data.shape indicating which samples were clipped
    """
    if min_contiguous < 1:
        raise ValueError("min_contiguous must be at least 1 for clip detection")

    is_real = bool(jnp.isrealobj(data))

    # Convert and check range_factor argument
    if isinstance(range_factor, (int, float)):
        if is_real:
            # Symmetric range_factor
            range_factor = (float(range_factor), float(range_factor))
        else:
            # For complex data, we take the magnitude, so the min-value (0) is not clipping
            range_factor = (None, float(range_factor))
    else:
        assert isinstance(range_factor, tuple)
        # Convert to float types while preserving None
        range_factor = (
            float(range_factor[0]) if range_factor[0] is not None else None,
            float(range_factor[1]) if range_factor[1] is not None else None,
        )
    assert isinstance(range_factor, tuple)
    assert len(range_factor) == 2

    low_factor, high_factor = range_factor
    if (low_factor is None) and (high_factor is None):
        raise ValueError("At least one side of range_factor must not be None detect clips")
    # Validate range factors that are not None
    if (low_factor is not None) and (low_factor < 0):
        raise ValueError("low_factor must be non-negative")
    if (high_factor is not None) and (high_factor < 0):
        raise ValueError("high_factor must be non-negative")

    # For complex data, we take the magnitude, assuming that clipping happens before
    # conversion from real -> complex (RF -> IQ).
    data_to_check: Real[Array, " *batch sample"] = data if is_real else jnp.abs(data)

    # Prepare data for processing
    original_shape = data.shape

    # Reshape to make this easier for vmap
    reshaped_data: Real[Array, " batch_all sample"] = jax.lax.collapse(
        data_to_check, start_dimension=0, stop_dimension=-1
    )
    # Handle each batch independently
    batch_result = jax.vmap(
        lambda x: _is_clipped_max_amplitude_core(
            data_to_check=x,
            low_factor=low_factor,
            high_factor=high_factor,
            min_contiguous=min_contiguous,
        )
    )(reshaped_data)

    # Reshape back to original dimensions
    return batch_result.reshape(original_shape)
