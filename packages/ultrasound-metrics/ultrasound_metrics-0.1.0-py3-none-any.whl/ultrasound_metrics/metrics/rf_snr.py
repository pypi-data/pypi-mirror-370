"""Radiofrequency Signal-to-Noise Ratio (RF SNR) metric.

This module provides functions to calculate the Signal-to-Noise Ratio (SNR)
for radiofrequency ultrasound data. SNR quantifies how much stronger the
signal (pulse echo) is compared to background noise.

Reference:
----------
.. [1] H. Liebgott, A. Rodriguez-Molares, F. Cervenansky, J. A. Jensen and O. Bernard,
       "Plane-Wave Imaging Challenge in Medical Ultrasound," 2016 IEEE International
       Ultrasonics Symposium (IUS), Tours, France, 2016, pp. 1-4,
       doi: 10.1109/ULTSYM.2016.7728908.

.. [2] P. Ecarlat, E. Carcreff, F. Varray, H. Liebgott and B. Nicolas, "Get Ready to Spy on Ultrasound: Meet ultraspy,"
       2023 IEEE International Ultrasonics Symposium (IUS), Montreal, QC, Canada, 2023, pp. 1-4,
       doi: 10.1109/IUS51837.2023.10307778.

"""

from typing import Optional, Union

import matplotlib.pyplot as plt
from array_api_compat import array_namespace
from beartype import beartype as typechecker
from jaxtyping import Num, jaxtyped

from ultrasound_metrics._utils.array_api import ArrayAPIObj


@jaxtyped(typechecker=typechecker)
def compute_rf_snr(
    signal_data: Num[ArrayAPIObj, "*signal_dims"],
    noise_data: Num[ArrayAPIObj, "*noise_dims"],
    *,
    center: bool = True,
    max_power: bool = False,
    show: bool = False,
    ax: Optional[plt.Axes] = None,
) -> float:
    """
    Calculate the Signal-to-Noise Ratio (SNR) for radiofrequency data.

    SNR quantifies how much stronger the signal (pulse echo) is compared to
    background noise. The calculation uses the formula:

    SNR (dB) = 10 * log10(signal_power / noise_power)

    where power is calculated as the Root Mean Square (RMS) squared.

    Parameters
    ----------
    signal_data : ArrayAPIObj
        The signal region data to evaluate. Should be a 1D array of RF values.
    noise_data : ArrayAPIObj
        The noise region data to evaluate. Should be a 1D array of RF values.
    center : bool, optional
        If True, center the signal and noise regions to zero mean before
        calculating power. This removes DC offset effects.
    max_power : bool, optional
        If True, use the maximum squared value in the signal region instead
        of the average power. Default is False (use average power).
    show : bool, optional
        If True, display a plot showing the signal and noise data.
    ax : plt.Axes, optional
        If set, plots the signal and noise data on the given Axes object.

    Returns
    -------
    float
        The Signal-to-Noise Ratio in decibels (dB).

    Notes
    -----
    - Higher SNR values indicate better signal quality
    - Typical SNR values range from 30-100 dB for good quality RF data
    - Centering the data (center=True) is recommended to remove DC offset
    """
    xp = array_namespace(signal_data)

    # Check that we have data in both regions
    if signal_data.size == 0 or noise_data.size == 0:
        raise ValueError("Signal or noise data is empty. Both inputs must contain values.")

    # Center data if requested (remove DC offset)
    if center:
        signal_data = signal_data - xp.mean(signal_data)
        noise_data = noise_data - xp.mean(noise_data)

    # Calculate power (RMS squared)
    if max_power:
        # Use maximum squared value for signal
        signal_power = float(xp.max(signal_data**2))
    else:
        # Use average power (RMS squared)
        signal_power = float(xp.mean(signal_data**2))

    # Always use average power for noise
    noise_power = float(xp.mean(noise_data**2))

    # Check for zero noise power
    if noise_power <= 0:
        raise ValueError("Noise power is zero or negative. Check noise data.")

    # Calculate SNR in dB
    snr_db = 10.0 * float(xp.log10(signal_power / noise_power))

    # Optional visualization
    if show or ax is not None:
        _plot_rf_snr_data(signal_data, noise_data, snr_db, ax=ax)

    return snr_db


def find_signal_and_noise(
    data: Num[ArrayAPIObj, "*dims"],
    signal_width: Union[int, list[int]] = 20,
    noise_offset: int = 50,
    ignore_until: int = 0,
    noise_size: Optional[int] = None,
    show: bool = False,
    ax: Optional[plt.Axes] = None,
) -> tuple[Num[ArrayAPIObj, "*signal_dims"], Num[ArrayAPIObj, "*noise_dims"]]:
    """
    Automatically estimate signal and noise regions in RF data.

    This function finds the maximum value in the data (after ignoring initial samples)
    and defines signal and noise regions around it based on the provided parameters.

    Parameters
    ----------
    data : ArrayAPIObj
        The RF data to analyze. Should be a 1D array.
    signal_width : int or list[int], optional
        Width of the signal region. If int, defines total width centered on max.
        If list[int], defines [samples_before_max, samples_after_max].
    noise_offset : int, optional
        Number of samples to skip between signal and noise regions.
    ignore_until : int, optional
        Number of initial samples to ignore (e.g., to avoid startup artifacts).
    noise_size : int, optional
        Maximum number of samples for noise region. If None, uses all available.
    show : bool, optional
        If True, display a plot showing the estimated regions.
    ax : plt.Axes, optional
        If set, plots the signal and noise data on the given Axes object.

    Returns
    -------
    tuple[ArrayAPIObj, ArrayAPIObj]
        (signal_data, noise_data) where each is the extracted data array.

    Notes
    -----
    - The signal region is centered on the maximum value in the data
    - The noise region is placed after the signal region with the specified offset
    - This is a heuristic approach and may need manual adjustment for best results
    """
    xp = array_namespace(data)

    # Find the maximum value after ignoring initial samples
    data_analyze = data[ignore_until:]
    max_idx = int(xp.argmax(xp.abs(data_analyze))) + ignore_until

    # Define signal region
    if isinstance(signal_width, int):
        # Total width centered on max
        half_width = signal_width // 2
        signal_start = max(0, max_idx - half_width)
        signal_end = min(len(data), max_idx + half_width)
    else:
        # [samples_before, samples_after]
        signal_start = max(0, max_idx - signal_width[0])
        signal_end = min(len(data), max_idx + signal_width[1])

    # Define noise region
    noise_start = min(len(data), signal_end + noise_offset)

    if noise_size is None:
        # Use all remaining samples
        noise_end = len(data)
    else:
        # Use specified number of samples
        noise_end = min(len(data), noise_start + noise_size)

    # Extract signal and noise data
    signal_data = data[signal_start:signal_end]
    noise_data = data[noise_start:noise_end]

    # Optional visualization
    if show or ax is not None:
        _plot_find_signal_and_noise(signal_data, noise_data, ax=ax)

    return signal_data, noise_data


def _plot_rf_snr_data(
    signal_data: Num[ArrayAPIObj, "*signal_dims"],
    noise_data: Num[ArrayAPIObj, "*noise_dims"],
    snr_db: float,
    ax: Optional[plt.Axes] = None,
) -> None:
    """Plot signal and noise data."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
        show_plot = True
    else:
        show_plot = False

    # Get array namespace for backend-agnostic operations
    xp = array_namespace(signal_data)

    # Plot signal data
    signal_indices = xp.arange(len(signal_data))
    ax.plot(signal_indices, signal_data, "g-", linewidth=1, label="Signal Data")

    # Plot noise data (offset to the right for visualization)
    noise_indices = xp.arange(len(signal_data), len(signal_data) + len(noise_data))
    ax.plot(noise_indices, noise_data, "r-", linewidth=1, label="Noise Data")

    # Add a vertical line to separate signal and noise
    ax.axvline(x=len(signal_data), color="k", linestyle="--", alpha=0.7, label="Signal/Noise Boundary")

    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Amplitude")
    ax.set_title(f"Signal and Noise Data (SNR = {snr_db:.2f} dB)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    if show_plot:
        plt.tight_layout()
        plt.show()


def _plot_find_signal_and_noise(
    signal_data: Num[ArrayAPIObj, "*signal_dims"],
    noise_data: Num[ArrayAPIObj, "*noise_dims"],
    ax: Optional[plt.Axes] = None,
) -> None:
    """Plot signal and noise data with detection information."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
        show_plot = True
    else:
        show_plot = False

    # Get array namespace for backend-agnostic operations
    xp = array_namespace(signal_data)

    # Plot signal data
    signal_indices = xp.arange(len(signal_data))
    ax.plot(signal_indices, signal_data, "g-", linewidth=1, label="Signal Data")

    # Plot noise data (offset to the right for visualization)
    noise_indices = xp.arange(len(signal_data), len(signal_data) + len(noise_data))
    ax.plot(noise_indices, noise_data, "r-", linewidth=1, label="Noise Data")

    # Add a vertical line to separate signal and noise
    ax.axvline(x=len(signal_data), color="k", linestyle="--", alpha=0.7, label="Signal/Noise Boundary")

    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Amplitude")
    ax.set_title("Automatic Signal and Noise Region Detection")
    ax.legend()
    ax.grid(True, alpha=0.3)

    if show_plot:
        plt.tight_layout()
        plt.show()
