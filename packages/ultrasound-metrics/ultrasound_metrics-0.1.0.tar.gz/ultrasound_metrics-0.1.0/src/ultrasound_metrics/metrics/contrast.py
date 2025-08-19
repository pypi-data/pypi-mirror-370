"""Contrast metric.

Reference:
----------
.. [1] A. Rodriguez-Molares, O. M. Hoel Rindal, J. D'hooge, S. -E. Måsøy, A. Austeng
       and H. Torp, "The Generalized Contrast-to-Noise Ratio," 2018 IEEE International
       Ultrasonics Symposium (IUS), Kobe, Japan, 2018, pp. 1-4,
       doi: 10.1109/ULTSYM.2018.8580101.
       Equations 1-4
.. [2] Smith S, Lopez H, and Bodine W,
       "Frequency independent ultrasound contrast-detail analysis,"
       Ultrasound in Medicine and Biology, vol. 11, no. 3, pp. 467-477, 1985.
       Equation 1
"""

from array_api_compat import array_namespace
from beartype import beartype as typechecker
from jaxtyping import Num, jaxtyped

from ultrasound_metrics._utils.array_api import ArrayAPIObj


@jaxtyped(typechecker=typechecker)
def contrast(
    values_inside: Num[ArrayAPIObj, "*inside_dims"],
    values_outside: Num[ArrayAPIObj, "*outside_dims"],
    *,
    db: bool = False,
) -> float:
    """Calculate the contrast between two regions.

    Equation and argument names follow the convention from [1]_ :
    - inside: the region of interest (e.g. lesion)
    - outside: the background region
    - contrast: power-contrast ratio, not dB or amplitude-ratio

    The contrast between two regions is defined as:

    .. math::

        C = \\frac{\\mu_i}{\\mu_o}

    where:

    .. math::

        \\mu_i = \\mathbb{E}\\left\\{|s_i|^2\\right\\}

    .. math::

        \\mu_o = \\mathbb{E}\\left\\{|s_o|^2\\right\\}

    are, respectively, the mean signal power inside and outside the lesion, where
    :math:`s` denotes the signal. Contrast can take any positive real value, and
    :math:`C \\to \\infty` as :math:`\\mu_o \\to 0`.

    Contrast is often expressed in decibels as:

    .. math::

        C[\\text{dB}] = 10\\log_{10} C

    Parameters:
    -----------
    values_inside : ArrayAPIObj
        Pixel values from inside the lesion (I), i.e. the region of interest.
        For hypoechoic lesions like cysts, these are typically lower intensity values.
    values_outside : ArrayAPIObj
        Pixel values from outside the lesion (O), i.e. the background region.
    db : bool
        Whether to return the contrast in dB.

    Returns:
    --------
    contrast : float
        The power-contrast between the inside and outside regions.
    """
    xp = array_namespace(values_inside)

    mean_signal_power_inside = xp.mean(xp.abs(values_inside) ** 2)
    mean_signal_power_outside = xp.mean(xp.abs(values_outside) ** 2)

    contrast = mean_signal_power_inside / mean_signal_power_outside

    if db and xp.isfinite(contrast):
        contrast = 10 * xp.log10(contrast)

    return float(contrast)
