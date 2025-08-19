"""Generalized Contrast-to-Noise Ratio (gCNR) metric.

Reference:
----------
.. [1] A. Rodriguez-Molares, O. M. Hoel Rindal, J. D'hooge, S. -E. Måsøy, A. Austeng
       and H. Torp, "The Generalized Contrast-to-Noise Ratio," 2018 IEEE International
       Ultrasonics Symposium (IUS), Kobe, Japan, 2018, pp. 1-4,
       doi: 10.1109/ULTSYM.2018.8580101.
"""

from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np
from array_api_compat import (
    array_namespace,
)
from array_api_compat import (
    size as xp_size,
)
from beartype import beartype as typechecker
from jaxtyping import Num, jaxtyped

from ultrasound_metrics._utils.array_api import ArrayAPIObj, histogram


@jaxtyped(typechecker=typechecker)
def gcnr(
    values_inside: Num[ArrayAPIObj, "*inside_dims"],
    values_outside: Num[ArrayAPIObj, "*outside_dims"],
    bins: Union[int, Num[ArrayAPIObj, " n_bins"]] = 100,
    ax: Optional[plt.Axes] = None,
) -> float:
    """
    Calculate the generalized Contrast-to-Noise Ratio (gCNR) between two regions.

    The gCNR is a robust metric for quantifying lesion detectability in medical imaging,
    particularly in ultrasound. It is defined as 1 - OVL, where OVL is the overlap area
    between the probability density functions of the pixel values inside and outside a lesion.

    Unlike traditional CNR, gCNR:
    1. Is robust against dynamic range alterations
    2. Can be applied to all kinds of images, units, or scales
    3. Has a simple statistical interpretation: the success rate expected from an ideal
       observer at the task of separating pixels

    Reference:
    ----------
    A. Rodriguez-Molares, O. M. Hoel Rindal, J. D'hooge, S. -E. Måsøy, A. Austeng
    and H. Torp, "The Generalized Contrast-to-Noise Ratio," 2018 IEEE International
    Ultrasonics Symposium (IUS), Kobe, Japan, 2018, pp. 1-4,
    doi: 10.1109/ULTSYM.2018.8580101.

    Parameters:
    -----------
    values_inside : ArrayAPIObj
        Pixel values from inside the lesion (I), i.e. the region of interest.
        For hypoechoic lesions like cysts, these are typically lower intensity values.
    values_outside : ArrayAPIObj
        Pixel values from outside the lesion (O), i.e. the background region.
    bins : int, optional
        Number of bins for histogram calculation, or a sequence of bin edges.
    ax : plt.Axes, optional
        If set, plots the PDFs and their overlap on the given Axes object.

    Returns:
    --------
    gCNR: float
        Generalized contrast-to-noise ratio (1 - OVL)

    Notes:
    ------
    - gCNR = 0: Complete overlap of distributions (impossible to distinguish regions)
    - gCNR = 1: No overlap (perfect distinction between regions)
    - Pmax represents the theoretical maximum success rate for an ideal observer
      trying to classify individual pixels as belonging to either region
    """
    # Get array namespace
    xp = array_namespace(values_inside)

    # Check if we have data in both regions
    if xp_size(values_inside) == 0 or xp_size(values_outside) == 0:
        raise ValueError("Empty region detected. Both inside and outside inputs must contain values.")

    # Determine histogram range
    min_val = min(float(xp.min(values_inside)), float(xp.min(values_outside)))
    max_val = max(float(xp.max(values_inside)), float(xp.max(values_outside)))

    # Calculate histograms using multi-backend-compatible histogram function
    pdf_inside, bin_edges = histogram(values_inside, bins=bins, range=(min_val, max_val), density=True)
    pdf_outside, _ = histogram(values_outside, bins=bin_edges, density=True)

    # Calculate the overlap (OVL)
    # Note: we follow the paper, which uses the PDF,
    # and deviate from the MATLAB implementation, which uses the normalized histogram counts (PMF)
    min_pdf = xp.minimum(pdf_inside, pdf_outside)
    bin_widths = bin_edges[1:] - bin_edges[:-1]
    ovl = float(xp.sum(bin_widths * min_pdf))  # Convert to float for consistent return type

    assert (ovl >= 0) and (ovl <= 1), "OVL must be between 0 and 1"

    g_cnr = 1 - ovl

    # Plot distributions if requested
    if ax is not None:
        p_max = 1 - ovl / 2
        title = f"gCNR = {g_cnr:.4f}, Pmax = {p_max:.4f}"
        _plot_gcnr_distributions(
            pdf_inside=pdf_inside, pdf_outside=pdf_outside, bin_edges=bin_edges, min_pdf=min_pdf, title=title, ax=ax
        )

    return g_cnr


def _plot_gcnr_distributions(
    pdf_inside: Num[ArrayAPIObj, " n_bins"],
    pdf_outside: Num[ArrayAPIObj, " n_bins"],
    bin_edges: Num[ArrayAPIObj, " n_bins"],
    min_pdf: Num[ArrayAPIObj, " n_bins"],
    ax: plt.Axes,
    title: Optional[str] = None,
) -> None:
    """Plot the distributions of the inside and outside intensities."""
    ax.stairs(
        pdf_inside,
        bin_edges,
        label="Inside lesion (pi)",
        color="r",
        linewidth=2,
        baseline=None,
    )
    ax.stairs(
        pdf_outside,
        bin_edges,
        label="Outside lesion (po)",
        color="b",
        linewidth=2,
        baseline=None,
    )

    # Fill the overlapping area using stairs
    ax.stairs(
        min_pdf,
        bin_edges,
        label="Overlap (OVL)",
        color="gray",
        fill=True,
        alpha=0.5,
        baseline=0,
    )

    ax.grid(True)
    ax.set_xlabel("Value")
    ax.set_ylabel("Probability density")
    ax.legend()
    if title is not None:
        ax.set_title(title)


def main() -> None:
    """Example usage with synthetic data."""
    # Create synthetic data simulating a hypoechoic lesion
    n_samples = 1000
    background = np.random.rayleigh(scale=1.0, size=n_samples)
    lesion = np.random.rayleigh(scale=0.3, size=n_samples)

    # Calculate gCNR
    _, ax = plt.subplots()
    g_cnr = gcnr(values_inside=lesion, values_outside=background, ax=ax)
    print(f"gCNR = {g_cnr:.4f}")
    plt.show()


if __name__ == "__main__":
    main()
