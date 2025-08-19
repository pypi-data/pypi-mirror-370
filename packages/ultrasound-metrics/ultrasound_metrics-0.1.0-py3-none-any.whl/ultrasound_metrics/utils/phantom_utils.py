from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from numpy.typing import NDArray
from skimage.transform import resize

# Pixel sizes below were determined empiricallly by aligning with US images
PHANTOMJPG_X_PX_SZE_MM = 0.102
PHANTOMJPG_Y_PX_SZE_MM = 0.105


def get_phantom_jpg(px_sze_mm: Optional[float] = None) -> tuple[NDArray[np.floating], dict[str, int]]:
    """Get digital phantom stored as jpg image"""
    phantom_path = Path(__file__).parent / ".." / "assets"
    img = cv2.imread(str(phantom_path / "ATS359.jpg"), cv2.IMREAD_GRAYSCALE)
    phantom = np.array(img)

    nX = len(phantom[0])
    nY = len(phantom)

    if px_sze_mm is not None:
        resize_ratio_x = PHANTOMJPG_X_PX_SZE_MM / px_sze_mm
        resize_ratio_y = PHANTOMJPG_Y_PX_SZE_MM / px_sze_mm
        print(f"Resize ratio: {resize_ratio_x},{resize_ratio_y}")
        new_nX = int(nX * resize_ratio_x)
        new_nY = int(nY * resize_ratio_y)

        resized_phantom = resize(phantom, output_shape=(new_nY, new_nX))
    else:
        resized_phantom = phantom
        new_nX = nX
        new_nY = nY

    return resized_phantom, {"x": new_nX, "y": new_nY}


def find_position(
    us_image: NDArray[np.floating], phantom: NDArray[np.floating]
) -> tuple[NDArray[np.floating], dict[str, np.integer]]:
    """Find position of the targets in the US image on the digital phantom"""
    us_image = np.array(us_image)
    phantom = np.array(phantom)
    us_im_sze = (len(us_image[0]), len(us_image))
    corr = np.array(cv2.filter2D(phantom, ddepth=-1, kernel=us_image), dtype=float)
    max_lin_idx = np.argmax(corr)
    y, x = np.unravel_index(max_lin_idx, corr.shape)
    xpos = x - round(us_im_sze[0] / 2)
    ypos = y - round(us_im_sze[1] / 2)
    return corr, {"x": xpos, "y": ypos}
