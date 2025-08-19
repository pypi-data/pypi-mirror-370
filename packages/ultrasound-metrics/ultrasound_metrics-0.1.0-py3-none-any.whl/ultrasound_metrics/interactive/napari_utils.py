"""Napari utilities for ultrasound data visualization.

This module provides functions to load and display ultrasound data in napari
with proper coordinate scaling and B-mode processing.

TODO: Improve ROI selection workflow in select_rois_with_labels:
1. Add support for Napari shapes layer as alternative to labels layer
2. Add interactive matplotlib selection for backend-agnostic ROI selection
3. Create unified interface that works across different visualization backends
"""

from typing import Any, Optional

import numpy as np
from array_api_compat import array_namespace

from ultrasound_metrics._utils.array_api import ArrayAPIObj
from ultrasound_metrics.data import create_bmode_image, db_zero
from ultrasound_metrics.data.uff import load_uff_dataset

# Check for napari availability at module level
try:
    import napari

    _HAS_NAPARI = True
except ImportError:
    _HAS_NAPARI = False


def _check_napari() -> None:
    """Check if napari is available and raise ImportError if not.

    Raises:
        ImportError: If napari is not installed
    """
    if not _HAS_NAPARI:
        raise ImportError("napari is required for interactive visualization. Install with: pip install napari")


def load_ultrasound_for_napari(
    dataset_name: str,
    use_db_scale: bool = True,
    db_range: tuple[float, float] = (-60.0, 0.0),
) -> tuple[ArrayAPIObj, dict[str, Any], Any]:
    """Load ultrasound dataset and prepare it for napari visualization.

    This function loads a UFF dataset, converts it to B-mode, and prepares
    the coordinate information needed for napari display and ROI selection.
    Internal processing uses Array API for backend compatibility, and returns
    a backend-agnostic array for computation. Convert to NumPy only for visualization.

    Parameters
    ----------
    dataset_name : str
        Name of the dataset to load (e.g., "picmus_resolution_experiment").
    use_db_scale : bool, optional
        Whether to convert to dB scale for display (default: True).
    db_range : tuple[float, float], optional
        Display range in dB if use_db_scale=True (default: (-60, 0)).

    Returns
    -------
    image_data : ArrayAPIObj
        2D backend-agnostic array for computation. Convert to NumPy for visualization.
    metadata : dict
        Dictionary containing coordinate information and display parameters.
    scan : Any
        Original scan geometry object from UFF dataset.
    """
    _check_napari()

    # Load the ultrasound dataset
    beamformed_image, scan = load_uff_dataset(dataset_name)

    # Convert to B-mode magnitude
    bmode_data = create_bmode_image(beamformed_image)

    # Convert to dB scale if requested
    if use_db_scale:
        display_data = db_zero(bmode_data)
        # Clip to specified range for better visualization using array API
        xp = array_namespace(display_data)
        display_data = xp.clip(display_data, db_range[0], db_range[1])
    else:
        display_data = bmode_data

    # Get array namespace for backend compatibility
    xp = array_namespace(display_data)

    # Napari expects (row, col) = (z, x) for 2D images
    # Transpose to match napari's coordinate convention
    display_data_t = xp.matrix_transpose(display_data)

    # Convert to numpy for napari compatibility (napari requires numpy arrays)
    napari_image = np.asarray(display_data_t)

    # Get physical coordinate axes - keep backend-agnostic for computation
    x_coords_backend = scan.x_axis  # could be any array API backend
    z_coords_backend = scan.z_axis

    # Only convert to numpy for visualization (Napari)
    x_coords = np.asarray(x_coords_backend)
    z_coords = np.asarray(z_coords_backend)

    # Calculate napari scaling and translation for coordinate mapping (for visualization)

    # Extract spacing values based on coordinate range and image dimensions
    if len(z_coords) > 1:
        z_min_val = float(np.asarray(z_coords.min()).flatten()[0])
        z_max_val = float(np.asarray(z_coords.max()).flatten()[0])
        z_range = z_max_val - z_min_val
        z_spacing = z_range / (napari_image.shape[0] - 1) if napari_image.shape[0] > 1 else z_range
    else:
        z_spacing = 1.0

    if len(x_coords) > 1:
        x_min_val = float(np.asarray(x_coords.min()).flatten()[0])
        x_max_val = float(np.asarray(x_coords.max()).flatten()[0])
        x_range = x_max_val - x_min_val
        x_spacing = x_range / (napari_image.shape[1] - 1) if napari_image.shape[1] > 1 else x_range
    else:
        x_spacing = 1.0

    scale = (z_spacing, x_spacing)

    # Extract origin values - flatten first in case of complex structures
    z_origin = np.asarray(z_coords[0]).flatten()
    x_origin = np.asarray(x_coords[0]).flatten()
    translate = (float(z_origin[0]), float(x_origin[0]))

    # Prepare metadata for coordinate conversion and ROI operations
    metadata = {
        "x_axis": x_coords,
        "z_axis": z_coords,
        "scale": scale,
        "translate": translate,
        "use_db_scale": use_db_scale,
        "db_range": db_range,
        "original_shape": display_data.shape,  # (z, x) in original coordinates
        "napari_shape": napari_image.shape,  # (z, x) in napari coordinates
    }

    # Instead of napari_image, return display_data_t (backend-agnostic)
    return display_data_t, metadata, scan


def select_rois_with_labels(
    image: ArrayAPIObj,
    label_map: Optional[ArrayAPIObj] = None,
    signal_label: int = 1,
    noise_label: int = 2,
    interactive: bool = True,
    viewer_kwargs: Optional[dict] = None,
) -> dict:
    """
    Select ROIs for signal and noise using a Napari labels layer, or process a pre-made label map.

    Parameters
    ----------
    image : ArrayAPIObj
        The image to display and extract pixel values from (backend-agnostic).
    label_map : ArrayAPIObj, optional
        If provided, use this label map directly (no GUI). Otherwise, open Napari for manual labeling.
    signal_label : int, default=1
        The integer label for the signal region.
    noise_label : int, default=2
        The integer label for the noise region.
    interactive : bool, default=True
        If True and label_map is None, open Napari for manual labeling.
    viewer_kwargs : dict, optional
        Additional kwargs to pass to napari.Viewer().

    Returns
    -------
    result : dict
        Dictionary with keys:
        - 'label_map': the integer label array (np.ndarray)
        - 'mask_signal': boolean mask for signal_label (np.ndarray)
        - 'mask_noise': boolean mask for noise_label (np.ndarray)
        - 'values_signal': pixel values from image where label_map == signal_label (np.ndarray)
        - 'values_noise': pixel values from image where label_map == noise_label (np.ndarray)
    """
    if interactive:
        _check_napari()

    if label_map is None and interactive:
        if viewer_kwargs is None:
            viewer_kwargs = {}
        viewer = napari.Viewer(**viewer_kwargs)
        image_np = np.asarray(image)
        viewer.add_image(image_np, name="Image")
        labels_data = np.zeros_like(image_np, dtype=int)
        labels_layer = viewer.add_labels(labels_data, name="ROI Labels")
        print(
            f"""
            INSTRUCTIONS:\n
            1. Use the paintbrush tool to paint your signal region (label {signal_label})\n
            2. Change the label to {noise_label} and paint your noise region\n"
            3. After painting both regions, close the Napari window.\n
            The function will return the masks and pixel values.\n
            """
        )
        napari.run()
        label_map = labels_layer.data
    elif label_map is None:
        raise ValueError("label_map must be provided if interactive is False.")

    # Convert to numpy for mask/value extraction
    image_np = np.asarray(image)
    label_map_np = np.asarray(label_map)
    mask_signal = label_map_np == signal_label
    mask_noise = label_map_np == noise_label
    values_signal = image_np[mask_signal]
    values_noise = image_np[mask_noise]

    # Add helpful error if no signal or noise pixels were selected
    if values_signal.size == 0:
        raise ValueError(
            f"No signal pixels were selected (label {signal_label}). "
            "Please use the paintbrush tool in Napari to paint the signal region before closing the window."
        )
    if values_noise.size == 0:
        raise ValueError(
            f"No noise pixels were selected (label {noise_label}). "
            "Please use the paintbrush tool in Napari to paint the noise region before closing the window."
        )

    return {
        "label_map": label_map_np,
        "mask_signal": mask_signal,
        "mask_noise": mask_noise,
        "values_signal": values_signal,
        "values_noise": values_noise,
    }
