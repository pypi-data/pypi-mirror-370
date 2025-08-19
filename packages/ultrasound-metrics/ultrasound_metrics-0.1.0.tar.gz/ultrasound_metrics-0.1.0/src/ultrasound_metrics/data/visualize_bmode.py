"""B-mode visualization utilities for ultrasound data.

This module provides general utility functions for converting complex beamformed data
to B-mode images and decibel calculations. These functions work with any array data
and don't require optional dependencies.

For UFF-specific functionality, see the uff.py module.
"""

from array_api_compat import array_namespace

from ultrasound_metrics._utils.array_api import ArrayAPIObj


def decibel(values: ArrayAPIObj) -> ArrayAPIObj:
    """Compute the dB amplitude of the signal.

    Parameters:
        values: Input signal.

    Returns:
        dB magnitude of the signal.
    """
    xp = array_namespace(values)
    magnitude = xp.abs(values)
    db = 20 * xp.log10(magnitude + xp.finfo(magnitude.dtype).eps)

    assert db.shape == values.shape, "Expected same shape as input"

    return db


def db_zero(values: ArrayAPIObj) -> ArrayAPIObj:
    """Compute the dB amplitude of the signal, with 0 dB at the maximum value.

    Parameters:
        values: Input signal.

    Returns:
        dB amplitude of the signal.
    """
    xp = array_namespace(values)
    db = decibel(values)
    # Subtract max to get 0 dB at max
    db_max = xp.max(db)
    db = db - db_max

    assert db.shape == values.shape, "Expected same shape as input"

    return db


def create_bmode_image(complex_data: ArrayAPIObj) -> ArrayAPIObj:
    """Convert complex beamformed data to B-mode magnitude.

    Parameters:
        complex_data: Complex-valued beamformed data

    Returns:
        Real-valued magnitude data suitable for visualization
    """
    xp = array_namespace(complex_data)
    return xp.abs(complex_data)
