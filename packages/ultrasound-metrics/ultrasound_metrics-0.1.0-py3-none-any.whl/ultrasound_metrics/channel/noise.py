"""Estimate the signal-to-noise ratio (SNR) of an ultrasound transducer system.

This module provides methods to calculate SNR using repeated pulse-echo
measurements of a phantom or tissue.

Motivation
----------
We would like to understand the power/SNR tradeoffs, e.g.:

* How much does AFE power improve SNR?
* How much does combining channels via summation improve SNR?
* How much do increasing chip-repeats improve SNR?

First, we need to measure SNR.


Implemented Methods
------------------

Repeated Measurements Variance
    Best for a static phantom:

    * Acquire multiple identical frames (same configuration)
    * Calculate the mean signal across frames (this represents the true signal)
    * Calculate the standard deviation across frames (this represents noise)
    * SNR = mean signal / standard deviation of noise

Signal Differences in Adjacent Frames
    Since tissue moves slowly and we acquire ultrafast ultrasound:

    * Calculate frame-to-frame differences
    * Assuming the tissue moves much slower than the frame rate,
        frame-to-frame differences primarily represent transmit and receive-channel noise
    * Compare mean signal amplitude to this difference (noise) to estimate SNR

Alternative Methods (Not Implemented)
------------------------------------

Transmit-Off Noise Measurements
    One of the most direct methods:

    * Collect data with the transmitter turned off (tx-off)
        This is all noise, so it's easy to calculate SNR.
    * Downside: noise may be nonlinear or signal-dependent, so this
        would not capture the practical SNR.

Spectral Analysis
    Assumes that the signal is narrowband and that the noise is flat.
    This is not true for our data, so we don't implement this.

Differences from B-Mode SNR
---------------------------

In ultrasound or image analysis, we often calculate SNR in the B-mode image.
For example, checking the strength of a reflector in the image.

You might take a spatial region analysis approach, e.g.:

    * Select regions devoid of signal (e.g. water) to calculate noise power
    * If a reflector is present, you can also calculate signal power

This is a great way to calculate image-related SNR. However, it does not
directly characterize the electronic noise, e.g. thermal or quantization noise.
Scatterer SNR probably belongs in a different submodule of this same repository.

"""

from enum import Enum

import equinox as eqx
import jax
import jax.numpy as jnp
from beartype import beartype as typechecker
from jaxtyping import Array, Float, Num, jaxtyped


class NoiseEstimationMethod(str, Enum):
    REPEATED_MEASUREMENTS = "repeated_measurements"
    ADJACENT_FRAMES = "adjacent_frames"


@jaxtyped(typechecker=typechecker)
@eqx.filter_jit
def noise_repeated_measurements(
    data: Num[Array, " repetition *samples"],
) -> tuple[Float[Array, ""], Float[Array, ""], Float[Array, ""]]:
    """Calculate noise from repeated measurements of a static phantom.

    Assumes the average signal is representative of the true signal.
    Then, the noise is the standard deviation of the signal across loops.

    Note: aggregates over samples dimension.

    Args:
        data: transducer data, (e.g. complex I/Q) data with shape (repetition, space, time)
            where `repetition` represents repeated acquisitions

    Returns:
        tuple (snr_db, signal_power, noise_power), where
            snr_db: signal-to-noise power-ratio in decibels (10*log10(signal_power/noise_power))
            signal_power: signal power
            noise_power: noise power
    """
    # Calculate signal power (magnitude squared of mean signal)
    signal_mean = data.mean(axis=0)
    signal_power_per_repetition = (jnp.abs(signal_mean) ** 2).sum()

    # Calculate noise variance in complex domain
    # Variance of complex random variable = Var(I) + Var(Q)
    noise_power_per_repetition = (jnp.var(data, axis=0)).sum()

    # Calculate SNR
    snr = signal_power_per_repetition / noise_power_per_repetition

    # Convert to decibels (power ratio, so 10*log10)
    snr_db = 10 * jnp.log10(snr)

    return snr_db, signal_power_per_repetition, noise_power_per_repetition


@jaxtyped(typechecker=typechecker)
@eqx.filter_jit
def noise_adjacent_frames(
    data: Num[Array, "repetition ..."],
) -> tuple[Float[Array, ""], Float[Array, ""], Float[Array, ""]]:
    """Calculate SNR using differences between adjacent frames.

    Assumes tissue moves slowly, so frame-to-frame differences primarily represent noise.

    Args:
        data: Complex I/Q data with shape (repetition, space, time)

    Returns:
        tuple (snr_db, signal_power, noise_power), where
            snr_db: signal-to-noise power-ratio in decibels (10*log10(signal_power/noise_power))
            signal_power: signal power
            noise_power: noise power
    """
    # i.e. we assume that we can average out the noise across 2 adjacent frames
    signal = (data[:-1] + data[1:]) / 2

    # Assume noise is difference from the rolling mean
    noise = jnp.diff(data, axis=0) / 2

    # Calculate signal power (magnitude squared)
    signal_power = jnp.abs(signal) ** 2
    signal_power = signal_power.sum()

    # Calculate noise power (magnitude squared)
    noise_power = jnp.abs(noise) ** 2
    noise_power = noise_power.sum()

    # Calculate SNR
    snr = signal_power / noise_power

    # Convert to decibels
    snr_db = 10 * jnp.log10(snr)

    return snr_db, signal_power, noise_power


def channel_noise(
    data: Num[Array, "repetition ..."], method: NoiseEstimationMethod
) -> tuple[Float[Array, ""], Float[Array, ""], Float[Array, ""]]:
    """Noise estimation method, helper function to select the appropriate method.

    Args:
        data: Complex I/Q data with shape (repetition, space, time)
        method: Noise estimation method

    Returns:
        tuple (snr_db, signal_power, noise_power)
    """
    result: tuple[Float[Array, ""], Float[Array, ""], Float[Array, ""]]
    if method == NoiseEstimationMethod.REPEATED_MEASUREMENTS:
        result = noise_repeated_measurements(data)
        return result
    elif method == NoiseEstimationMethod.ADJACENT_FRAMES:
        result = noise_adjacent_frames(data)
        return result
    else:
        raise ValueError(f"Invalid noise estimation method: {method}")


if __name__ == "__main__":
    import time

    # Example usage
    print("Example usage of noise_repeated_measurements")
    key = jax.random.PRNGKey(0)

    # Create example data: 10 loops, 64 channels, 100 time points
    # Signal component (same across loops but with different amplitude per channel/time)
    signal = jax.random.normal(key, (1, 64, 100)) + 1j * jax.random.normal(key, (1, 64, 100))

    # Add noise component (different for each loop)
    noise_scale = 0.1
    noise = noise_scale * (jax.random.normal(key, (10, 64, 100)) + 1j * jax.random.normal(key, (10, 64, 100)))

    # Combine signal and noise
    data = signal + noise

    # First call will compile
    for method in NoiseEstimationMethod:
        start = time.time()
        snr_db, signal_power, noise_power = channel_noise(data, method)
        end = time.time()
        print(f"First call with {method=!s} took: {end - start} seconds")
        print(f"{method=!s}: {jnp.mean(snr_db):.2f} dB")

    # Subsequent calls will be faster
    for method in NoiseEstimationMethod:
        start = time.time()
        snr_db, signal_power, noise_power = channel_noise(data, method)
        end = time.time()
        print(f"Second call with {method=!s} took: {end - start} seconds")
