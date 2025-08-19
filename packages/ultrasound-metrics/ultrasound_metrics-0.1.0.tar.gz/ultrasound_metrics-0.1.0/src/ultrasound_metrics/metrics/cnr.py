from typing import Callable

from array_api_compat import array_namespace
from array_api_compat import size as array_size
from beartype import beartype as typechecker
from jaxtyping import jaxtyped

from ultrasound_metrics._utils.array_api import ArrayAPIObj


# Backend-agnostic aggregation functions
def get_agg_func(xp: ArrayAPIObj, name: str) -> Callable[[ArrayAPIObj], ArrayAPIObj]:
    if name == "MEAN":
        return lambda arr: xp.mean(arr)
    elif name == "MEDIAN":
        return lambda arr: xp.median(arr)
    else:
        raise ValueError(f"Unknown aggregation function: {name}")


@jaxtyped(typechecker=typechecker)
def compute_cnr(
    values_signal: ArrayAPIObj,
    values_noise: ArrayAPIObj,
    fun_signal: str = "MEAN",
    fun_noise: str = "MEAN",
    *,
    use_signal_variance: bool = True,
    use_noise_variance: bool = True,
) -> float:
    """
    Computes the contrast-to-noise ratio (CNR) between two regions.

    Parameters
    ----------
    values_signal : array
        Pixel values from the signal region (e.g., inside a lesion).
    values_noise : array
        Pixel values from the noise/background region (e.g., outside a lesion).
    fun_signal : str
        Aggregation function for the signal region ("MEAN" or "MEDIAN").
    fun_noise : str
        Aggregation function for the noise region ("MEAN" or "MEDIAN").
    use_signal_variance : bool
        Whether to include signal variance in the denominator.
    use_noise_variance : bool
        Whether to include noise variance in the denominator.

    Returns
    -------
    cnr : float
        The contrast-to-noise ratio.
    """
    xp = array_namespace(values_signal)

    if array_size(values_signal) == 0 or array_size(values_noise) == 0:
        raise ValueError("Input arrays must not be empty.")

    # Aggregation functions
    agg_signal = get_agg_func(xp, fun_signal)
    agg_noise = get_agg_func(xp, fun_noise)

    # Match the original: use squared values for mean and variance
    values_signal_sq = xp.abs(values_signal) ** 2
    values_noise_sq = xp.abs(values_noise) ** 2

    mu_signal = agg_signal(values_signal_sq)
    mu_noise = agg_noise(values_noise_sq)
    out = mu_signal - mu_noise

    if use_noise_variance or use_signal_variance:
        sigma_signal = agg_signal((values_signal_sq - mu_signal) ** 2)
        sigma_noise = agg_noise((values_noise_sq - mu_noise) ** 2)
        denom = xp.sqrt(sigma_signal * int(use_signal_variance) + sigma_noise * int(use_noise_variance))
        out = out / denom

    return float(out)
