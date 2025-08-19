"""Coherence-based image quality metrics for ultrasound.

This module implements coherence factor calculations for beamformed ultrasound data.
The coherence factor quantifies the degree of coherence between signals received
from different elements.
"""

from typing import Callable

import array_api_extra as xpx
from array_api_compat import array_namespace
from beartype import beartype as typechecker
from jaxtyping import Float, Num, jaxtyped

from .._utils.array_api import ArrayAPIObj


@jaxtyped(typechecker=typechecker)
def coherence_factor(
    channel_images: Num[ArrayAPIObj, "receive_elements *img_dims"],
    power_based: bool = True,
) -> Float[ArrayAPIObj, "*img_dims"]:
    """Compute the coherence factor of beamformed ultrasound data.

    The coherence factor [1][2] measures the degree of coherence between signals
    received from different elements. Two formulations are supported:

    **Power-based coherence (power_based=True, default) [1]_ [4]_:**
    C_R(r) = |Σ_m b̂(r,m)|² / (Σ_m |b̂(r,m)|² * M)

    **Amplitude-based coherence (power_based=False) [2]_ [3]_:**
    C_R(r) = |Σ_m b̂(r,m)| / Σ_m |b̂(r,m)|
    where:
    - b̂_m is the complex beamsum for receive element m
    - |·| denotes absolute value (magnitude)
    - |·|² denotes power (magnitude squared)
    - M is the number of receive elements
    - Σ_m denotes summation over all receive elements

    where b̂(r,m) is the beamsum for pixel r and receive element m, M is the
    number of receive elements, and the summation is over all M elements.
    The numerator represents the coherent sum (signals add constructively
    when in phase), while the denominator represents the incoherent sum.

    The coherence factor ranges from 0 to 1:
    - 1.0: Perfect coherence (all signals perfectly in phase)
    - 0.0: Complete incoherence (random phase relationships)

    High coherence typically indicates good focusing and strong scattering,
    while low coherence may indicate aberrations, noise, or weak scattering.

    Parameters
    ----------
    channel_images : array_like, shape (receive_elements, *img_dims)
        Complex-valued beamformed data before summation across receive elements.
        The first dimension corresponds to individual receive elements (M),
        and remaining dimensions represent the image coordinates.
        Can be 2D (receive_elements, pixels) or higher dimensional
        (receive_elements, height, width, ...).
    power_based : bool, optional
        If False, uses amplitude-based coherence as in [2].
        If True, uses power-based coherence with element normalization [5],
        similar to vbeam implementation [4].

    Returns
    -------
    coherence : array_like, shape (*img_dims)
        Coherence factor values ranging from 0 to 1. Higher values indicate
        better coherence between receive elements. Shape matches the image
        dimensions of the input (all dimensions except the first).

    Notes
    -----
    For ultrasound applications, the coherence factor is useful for:
    - Assessing focusing quality and aberration detection
    - Adaptive beamforming weight calculation
    - Sound speed estimation and correction
    - Tissue characterization based on scattering properties

    References
    ----------
    .. [1] Hollman, K. W., Rigby, K. W., & O'Donnell, M. (1999). Coherence factor of speckle from a multi-row probe.
           IEEE Ultrasonics Symposium.
    .. [2] Rigby, K. W., et al. (1999). Method and apparatus for coherence filtering of ultrasound images
    .. [3] Vr˚alstad, A.E. et al. (2024). Coherence Based Sound Speed Aberration
           Correction — with clinical validation in fetal ultrasound. arXiv:2411.16551
    """
    # Get the array namespace
    xp = array_namespace(channel_images)

    # Validate input
    if channel_images.ndim < 2:
        raise ValueError(
            f"Input must have at least 2 dimensions (receive_elements, *img_dims), got {channel_images.ndim}D"
        )

    # Get number of receive elements for power-based normalization
    num_elements = channel_images.shape[0]

    # Compute coherent sum: sum across receive elements (axis 0)
    coherent_sum: Num[ArrayAPIObj, "*img_dims"] = xp.sum(channel_images, axis=0)

    if power_based:
        # Power-based coherence: |sum|^2 / (sum(|x|^2) * M)
        coherent_numerator: Float[ArrayAPIObj, "*img_dims"] = xp.abs(coherent_sum) ** 2
        incoherent_denominator: Float[ArrayAPIObj, "*img_dims"] = (
            xp.sum(xp.abs(channel_images) ** 2, axis=0) * num_elements
        )
    else:
        # Magnitude-based coherence: |sum| / sum(|x|)
        coherent_numerator: Float[ArrayAPIObj, "*img_dims"] = xp.abs(coherent_sum)
        incoherent_denominator: Float[ArrayAPIObj, "*img_dims"] = xp.sum(xp.abs(channel_images), axis=0)

    # Handle division by zero: when denominator (and numerator) is 0, set result to 0
    # This handles the case where all signals are zero (coherence should be 0)
    coherence = xpx.apply_where(
        incoherent_denominator != 0,
        (coherent_numerator, incoherent_denominator),
        xp.divide,
        fill_value=0,
    )

    return coherence


@jaxtyped(typechecker=typechecker)
def generalized_coherence_factor(
    channel_images: Num[ArrayAPIObj, "receive_elements *img_dims"],
    m0: int = 1,
) -> Float[ArrayAPIObj, "*img_dims"]:
    """Compute the generalized coherence factor (GCF) of beamformed ultrasound data.

    The generalized coherence factor [1] is a more robust version of the standard
    coherence factor that uses spatial DFT across steering angles to reduce
    sensitivity to incoherent noise:

    GCF = Σ|X[k]|² / (M * Σ|xₘ[n]|²)

    where X[k] = Σₘ xₘ[n] * e^(-j2πkm/M) is the spatial DFT across elements,
    and the sum over k includes only the low-frequency region from -M0 to +M0.
    The low-frequency region can be viewed as the received signal from the angles
    around the transmit beam direction.

    Parameters
    ----------
    channel_images : array_like, shape (receive_elements, *img_dims)
        Complex-valued beamformed data before summation across receive elements.
    m0 : int, default=1
        Cutoff frequency for the low-frequency region. The GCF uses spatial
        frequencies from -m0 to +m0. Must be >= 0 and < num_elements/2.

        Selection guidelines [1]_:
        - m0=0: Point targets only (may introduce beam-splitting artifacts)
        - m0=1: Optimal for most diffuse scatterers and speckle patterns
        - m0=2-3: Alternative for diffuse scatterers, trades effectiveness for stability
        - Larger m0: Less effective but more stable

    Returns
    -------
    gcf : array_like, shape (*img_dims)
        Generalized coherence factor values ranging from 0 to 1.

    References
    ----------
    .. [1] Li, P. C., & Li, M. L. (2003). Adaptive imaging using the
           generalized coherence factor. IEEE Transactions on Ultrasonics,
           Ferroelectrics, and Frequency Control, 50(2), 128-141.
    """
    xp = array_namespace(channel_images)

    # Validate input
    if channel_images.ndim < 2:
        raise ValueError(
            f"Input must have at least 2 dimensions (receive_elements, *img_dims), got {channel_images.ndim}D"
        )

    num_elements = channel_images.shape[0]

    # Validate m0 parameter
    if m0 < 0:
        raise ValueError(f"m0 must be a non-negative integer, got {m0}")
    if m0 >= num_elements // 2:
        raise ValueError(f"m0 ({m0}) must be < num_elements/2 ({num_elements // 2})")

    if not (hasattr(xp, "fft") and hasattr(xp.fft, "fft") and isinstance(xp.fft.fft, Callable)):
        raise ValueError(f"GCF requires FFT, but {xp.__name__} does not support it")

    # Compute spatial DFT across elements (axis 0)
    # Use FFT for efficiency - this gives us X[k] for all k
    spatial_fft = xp.fft.fft(channel_images, axis=0)  # type: ignore  # noqa: PGH003

    # Extract low-frequency region from -m0 to +m0 as specified in paper
    # This corresponds to the "energy received from angles around transmit beam direction"
    dc_power = xp.abs(spatial_fft[0:1]) ** 2
    coherent_sum = xp.sum(dc_power, axis=0)

    if m0 > 0:
        # Take DC component and symmetric positive/negative frequencies
        # Positive frequencies: k=1, 2, ..., m0
        pos_power = xp.abs(spatial_fft[1 : m0 + 1]) ** 2

        # Negative frequencies: k=-m0, -m0+1, ..., -1
        # In FFT convention: k=-m0 corresponds to index num_elements-m0
        neg_power = xp.abs(spatial_fft[-m0:]) ** 2

        # Sum all contributions: DC + positive + negative frequencies
        coherent_sum = coherent_sum + xp.sum(pos_power, axis=0) + xp.sum(neg_power, axis=0)

    # Compute total energy (incoherent sum)
    element_powers = xp.abs(channel_images) ** 2
    total_energy = xp.sum(element_powers, axis=0) * num_elements

    # Compute GCF with numerical stability
    gcf = xpx.apply_where(
        total_energy != 0,
        (coherent_sum, total_energy),
        xp.divide,
        fill_value=0,
    )

    return gcf


@jaxtyped(typechecker=typechecker)
def sign_coherence_factor(
    channel_images: Num[ArrayAPIObj, "receive_elements *img_dims"],
    power: float = 1.0,
) -> Float[ArrayAPIObj, "*img_dims"]:
    """Compute the sign coherence factor (SCF) of beamformed ultrasound data.

    The sign coherence factor [1]_ uses only the polarity (sign) of signals,
    making it extremely efficient for hardware implementation:

    SCF^p[k] = |1 - sigma|^p

    where sigma = sqrt(1 - |1/M Sum(b_i[k])|²) and b_i[k] = sign(real(x_i[k]))

    The sign bit b_i[k] is +1 if real(x_i[k]) ≥ 0 and -1 if real(x_i[k]) < 0.
    The SCF considers signals fully coherent when all have the same polarity
    (strict coherence criterion) and completely incoherent when half are
    positive and half are negative.

    This can be considered a particular case of the phase coherence factor (PCF)
    where phase is quantized to just 1 bit (sign), making it highly efficient
    for hardware implementation while maintaining good performance.

    Parameters
    ----------
    channel_images : array_like, shape (receive_elements, *img_dims)
        Complex-valued beamformed data before summation across receive elements.
        Real part is used for sign computation.
    power : float, default=1.0
        Exponential parameter p ≥ 0 to adjust sensitivity. Higher values provide
        more aggressive suppression of incoherent signals.

    Returns
    -------
    scf : array_like, shape (*img_dims)
        Sign coherence factor values ranging from 0 to 1.

    Notes
    -----
    The SCF is maximum (1.0) when all aperture data have the same polarity,
    and minimum (0.0) when half are positive and half are negative.

    References
    ----------
    .. [1] Camacho, J., Parrilla, M., & Fritsch, C. (2009). Phase coherence
           imaging. IEEE Transactions on Ultrasonics, Ferroelectrics, and
           Frequency Control, 56(5), 958-974.
    """
    xp = array_namespace(channel_images)

    # Validate input
    if channel_images.ndim < 2:
        raise ValueError(
            f"Input must have at least 2 dimensions (receive_elements, *img_dims), got {channel_images.ndim}D"
        )

    if power < 0:
        raise ValueError(f"Power parameter must be non-negative, got {power}")

    # Compute sign bits: +1 if real part ≥ 0, -1 if < 0
    # For complex data, use real part for sign determination
    real_data = xp.real(channel_images)
    sign_bits = xp.sign(real_data)

    # Compute mean of sign bits across elements
    sign_mean = xp.mean(sign_bits, axis=0)  # Shape: (*img_dims)

    # Compute variance of sign bits: σ² = 1 - |mean|²
    # Since sign bits are ±1, Σbᵢ² = N, so variance simplifies
    sign_variance = 1.0 - xp.abs(sign_mean) ** 2

    # Standard deviation
    sign_std = xp.sqrt(xp.maximum(sign_variance, 0.0))  # Ensure non-negative

    # Sign coherence factor: SCF = |1 - sigma|^p
    scf = xp.abs(1.0 - sign_std) ** power

    return scf


@jaxtyped(typechecker=typechecker)
def phase_coherence_factor(
    channel_images: Num[ArrayAPIObj, "receive_elements *img_dims"],
    power: float = 1.0,
) -> Float[ArrayAPIObj, "*img_dims"]:
    """Compute the phase coherence factor (PCF) of beamformed ultrasound data.

    The phase coherence factor [1]_ measures coherence based on phase alignment
    of aperture data. This implementation uses the magnitude of the mean unit
    phasor, which is equivalent to phase coherence:

    PCF^p[k] = |mean(x_i[k] / |x_i[k]|)|^p

    This is a simplified but mathematically equivalent implementation of the
    phase coherence factor that avoids issues with phase wrapping around ±π.
    The PCF is amplitude-independent and focuses purely on phase alignment.

    The PCF provides similar benefits to the standard coherence factor but is
    more robust in the presence of amplitude variations, making it particularly
    useful for suppressing side lobes and improving lateral resolution.

    Parameters
    ----------
    channel_images : array_like, shape (receive_elements, *img_dims)
        Complex-valued beamformed data before summation across receive elements.
    power : float, default=1.0
        Exponential parameter p ≥ 0 to adjust sensitivity. Higher values provide
        more aggressive suppression of phase-incoherent signals.

    Returns
    -------
    pcf : array_like, shape (*img_dims)
        Phase coherence factor values ranging from 0 to 1.

    Notes
    -----
    The PCF is maximum (1.0) when all signals have identical phases,
    and approaches 0 when phases are randomly distributed. Unlike amplitude-based
    coherence factors, PCF is insensitive to magnitude variations across elements.

    References
    ----------
    .. [1] Camacho, J., Parrilla, M., & Fritsch, C. (2009). Phase coherence
           imaging. IEEE Transactions on Ultrasonics, Ferroelectrics, and
           Frequency Control, 56(5), 958-974.
    """
    xp = array_namespace(channel_images)

    # Validate input
    if channel_images.ndim < 2:
        raise ValueError(
            f"Input must have at least 2 dimensions (receive_elements, *img_dims), got {channel_images.ndim}D"
        )

    if power < 0:
        raise ValueError(f"Power parameter must be non-negative, got {power}")

    # Compute unit phasors: e^(jφᵢ) = xᵢ/|xᵢ|
    magnitudes = xp.abs(channel_images)

    # Safe division to avoid division by zero
    unit_phasors = xpx.apply_where(
        magnitudes != 0,
        (channel_images, magnitudes),
        xp.divide,
        fill_value=0,
    )

    # Compute mean unit phasor (coherent sum of normalized signals)
    mean_phasor = xp.mean(unit_phasors, axis=0)  # Shape: (*img_dims)

    # Phase coherence is the magnitude of the mean unit phasor
    # This is equivalent to computing circular variance and converting to coherence
    phase_coherence = xp.abs(mean_phasor)

    # Apply power parameter
    phase_coherence = phase_coherence**power

    return phase_coherence
