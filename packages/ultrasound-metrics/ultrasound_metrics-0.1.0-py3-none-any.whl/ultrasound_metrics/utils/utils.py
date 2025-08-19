"""docstring for module"""

import glob
import json
from pathlib import Path
from typing import Optional, Union

import cv2
import numpy as np
import yaml
from numpy.typing import NDArray
from skimage.measure import label


def moving_average(data: NDArray[np.floating], window_size: int) -> NDArray[np.floating]:
    cumsum: NDArray[np.floating] = np.cumsum(data)
    cumsum[window_size:] = cumsum[window_size:] - cumsum[:-window_size]
    return cumsum[window_size - 1 :] / window_size


def smooth(data: NDArray[np.floating], window_size: int) -> NDArray[np.floating]:
    kernel = np.ones(window_size) / window_size
    return np.convolve(data, kernel, "same")


def preproc_bf(
    bf_data: NDArray[np.floating], target_mode: str = "point", thresh: Optional[float] = 0.3
) -> NDArray[np.floating]:
    """Pre-process the beamformed image for more-conducive registration
    - Processing parameters are hard-coded assuming that the same sequence
      is used for positional registration. which is a fine assumption
      since we don't need to use any given sequence for the sake of positioning.
    """
    bf_image: NDArray[np.floating] = np.array(bf_data[0, :, 0, :].T)
    bf_image /= np.max(bf_image)
    d = smooth(np.mean(bf_image, axis=1), 15)
    d /= np.max(d)
    bf_image /= d[:, np.newaxis]

    # Bmode specific processing
    # a. Point target: remove bg noise (speckle)
    # b. Lesion: smooth speckle and invert
    if target_mode == "point":
        if thresh is not None:
            bf_image *= bf_image > 0.3
        bf_image /= np.max(bf_image)
    elif target_mode == "lesion":
        # Work in progress
        k_sze = 15
        kernel2 = np.ones((k_sze, k_sze), np.float32) / k_sze**2
        bf_image = cv2.filter2D(src=bf_image, ddepth=-1, kernel=kernel2).astype(float, copy=False)
        bf_image = 1 - bf_image
        bf_image /= np.max(bf_image)
        # bf_image *= bf_image > 0.8

    return bf_image


def preproc_phantom(phantom: NDArray[np.floating], target_mode: str = "point") -> NDArray[np.floating]:
    # Invert the phantom so that lesions are bright since registration looks at peak
    if target_mode == "lesion":
        phantom = 1 - phantom
        phantom /= np.max(phantom)

    return phantom


def load_bmode_px_sze(bf_file: Union[str, Path]) -> float:
    """Get the bmode pixel size based on TX frequency and beamforming parameters
    Inputs:
        bf_file: Path to the file to be beamformed
    Outputs:
        px_sze_mm: Bmode pixel size in mm
    """
    bf_file_path = Path(bf_file).parent
    config_file_options = glob.glob(str(bf_file_path / "config*/config.yaml"))
    if len(config_file_options) == 0:
        raise ValueError("Could not find a config file for the beamforming!")
    bf_config_file = config_file_options[0]
    bf_configs = None
    with open(str(bf_config_file)) as stream:
        bf_configs = yaml.safe_load(stream)

    poseidon_metadata_file = bf_file_path.parent / "metadata" / "poseidon_config.json"
    poseidon_configs = None
    with open(str(poseidon_metadata_file)) as f:
        poseidon_configs = json.load(f)

    if bf_configs is None or poseidon_configs is None:
        raise ValueError("Could not get config data for calculating pixel size.")

    return float(
        bf_configs["speed_of_sound"] / poseidon_configs["tx_freq_hz"] * bf_configs["pixel_size_wavelengths"] * 1e3
    )


def match_phantom_im_size_to_input_bf_data(
    phantom_im: NDArray[np.floating], pos: dict[str, int], bf_shape: tuple[int, ...], dims: list[int]
) -> NDArray[np.floating]:
    row_start = pos["y"]
    row_end = row_start + bf_shape[dims[1]]
    col_start = pos["x"]
    col_end = col_start + bf_shape[dims[0]]

    phantom_im = crop_phantom_im_to_match_bmode(phantom_im, (row_start, row_end), (col_start, col_end))
    phantom_im /= np.max(phantom_im)

    phantom_im = np.transpose([[phantom_im]], (1, 3, 0, 2))  # fix me

    return phantom_im


def crop_phantom_im_to_match_bmode(
    phantom_img: NDArray[np.floating], row_range: tuple[int, int], col_range: tuple[int, int]
) -> NDArray[np.floating]:
    n_rows = phantom_img.shape[0]
    n_cols = phantom_img.shape[1]

    phantom_img = phantom_img[
        max(row_range[0], 0) : min(row_range[1], n_rows), max(col_range[0], 0) : min(col_range[1], n_cols)
    ]

    row_pad = (abs(min(row_range[0], 0)), abs(max(row_range[1] - n_rows, 0)))
    col_pad = (abs(min(col_range[0], 0)), max(col_range[1] - n_cols, 0))

    padded_img = np.pad(phantom_img, (row_pad, col_pad))
    return padded_img


def convert_phantom_img_to_roi_img(phantom_img: NDArray[np.floating]) -> NDArray[np.integer]:
    labels: NDArray[np.integer] = label(phantom_img > 0.9)
    return labels
