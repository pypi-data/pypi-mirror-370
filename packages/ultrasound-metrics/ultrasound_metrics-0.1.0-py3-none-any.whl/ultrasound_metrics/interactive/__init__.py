"""Interactive visualization utilities for ultrasound data.

This module provides interactive visualization tools using napari for
ROI selection and real-time metric computation.

Optional dependencies required:
- napari[all]>=0.5.0

Install with: pip install ultrasound-metrics[interactive]
"""

# Check for interactive dependencies at module level
try:
    import napari  # noqa: F401

    _HAS_INTERACTIVE_DEPS = True
except ImportError as err:
    raise ImportError(
        "Interactive visualization requires napari. Install with: uv pip install 'ultrasound-metrics[interactive]'"
    ) from err


from .napari_utils import (
    load_ultrasound_for_napari,
)

__all__ = [
    "load_ultrasound_for_napari",
]
