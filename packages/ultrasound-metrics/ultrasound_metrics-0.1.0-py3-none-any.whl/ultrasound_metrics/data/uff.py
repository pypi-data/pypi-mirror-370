"""UFF dataset utilities for ultrasound data.

This module provides functions for loading UFF datasets that require pyuff_ustb.
If you don't work with UFF files, you can use the general utilities in visualize_bmode.py
without needing to install pyuff_ustb.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast

from ultrasound_metrics._utils.array_api import ArrayAPIObj
from ultrasound_metrics.data.downloads import cached_download

if TYPE_CHECKING:
    pass

# Check for pyuff_ustb availability at module level
try:
    import pyuff_ustb as uff
    from pyuff_ustb import BeamformedData, ChannelData, Uff
    from pyuff_ustb.readers.base import ReaderKeyError

    _HAS_PYUFF_USTB = True
except ImportError as err:
    if "pyuff_ustb" in str(err):
        # Only raise ImportError if this is the specific missing dependency
        raise ImportError(
            "pyuff_ustb is required. Install with: `uv pip install ultrasound-metrics[uff]` or `pip install pyuff_ustb`"
        ) from err
    else:
        # Re-raise other import errors
        raise


# Default cache directory for downloaded datasets
CACHE_DIR = Path.home() / ".cache" / "ultrasound-metrics" / "datasets"


class DatasetInfo(TypedDict):
    """Type definition for dataset information."""

    url: str
    filename: str
    description: str
    size: int


# Dataset registry with download URLs and metadata
USTB_DATASETS: dict[str, DatasetInfo] = {
    "picmus_resolution_experiment": {
        "url": "https://f004.backblazeb2.com/b2api/v1/b2_download_file_by_id?fileId=4_z81bac298ed734da8927d0614_f112a4a231dbce513_d20250729_m192149_c004_v0402004_t0044_u01753816909257",
        # We can also use the USTB URL, but it has rate-limits
        # "url": "http://www.ustb.no/datasets/PICMUS_experiment_resolution_distortion.uff",
        "filename": "PICMUS_experiment_resolution_distortion.uff",
        "description": "PICMUS challenge resolution/distortion test (experiment)",
        "size": 145518524,
    },
    "picmus_contrast_experiment": {
        "url": "https://f004.backblazeb2.com/b2api/v1/b2_download_file_by_id?fileId=4_z81bac298ed734da8927d0614_f100d6106d29bf5da_d20250729_m192144_c004_v0402027_t0027_u01753816904341",
        # We can also use the USTB URL, but it has rate-limits
        # "url": "http://www.ustb.no/datasets/PICMUS_experiment_contrast_speckle.uff",
        "filename": "PICMUS_experiment_contrast_speckle.uff",
        "description": "PICMUS challenge contrast/speckle test (experiment)",
        "size": 145518504,
    },
}


def _check_pyuff_ustb() -> None:
    """Check if pyuff_ustb is available and raise ImportError if not.

    Raises:
        ImportError: If pyuff_ustb is not installed
    """
    if not _HAS_PYUFF_USTB:
        raise ImportError("pyuff_ustb is required to load UFF datasets. Install with: pip install pyuff_ustb")


def list_available_datasets() -> dict[str, DatasetInfo]:
    """List all available datasets with their metadata.

    Returns:
        Dictionary mapping dataset names to their information
    """
    return USTB_DATASETS.copy()


def inspect_dataset(dataset_name: str) -> dict:
    """Inspect a specific dataset and its cache status.

    Args:
        dataset_name: Name of the dataset to inspect

    Returns:
        Dictionary with dataset metadata and cache information

    Raises:
        KeyError: If the dataset is not found

    Example:
        info = inspect_dataset("picmus_resolution_experiment")
        print(f"URL: {info['url']}")
        print(f"Cached: {info['cached']}")
        print(f"Size: {info['size']} bytes")
    """
    if dataset_name not in USTB_DATASETS:
        raise KeyError(f"Dataset {dataset_name} not found")

    dataset_info = USTB_DATASETS[dataset_name]
    cached_file = CACHE_DIR / dataset_info["filename"]

    result = {
        "name": dataset_name,
        "url": dataset_info["url"],
        "filename": dataset_info["filename"],
        "description": dataset_info["description"],
        "cached": cached_file.exists(),
        "cache_path": cached_file,
        "size": cached_file.stat().st_size if cached_file.exists() else None,
    }

    return result


def load_dataset(dataset_name: str, download_if_missing: bool = True, key: str = "/beamformed_data") -> ArrayAPIObj:
    """Load a dataset using pyuff_ustb.

    Args:
        dataset_name: Name of the dataset to load
        download_if_missing: Whether to download the dataset if not cached
        key: Key to read from the UFF file. Common keys include:
            - "/beamformed_data": Beamformed ultrasound data (default)
            - "/channel_data": Channel data for temporal analysis

    Returns:
        The loaded dataset as a numpy array (default key: "/beamformed_data")

    Raises:
        ImportError: If pyuff_ustb is not installed
        KeyError: If the dataset is not found
        FileNotFoundError: If dataset is not cached and download_if_missing=False

    Example:
        # Load beamformed data (default)
        data = load_dataset("picmus_resolution_experiment")
        print(f"Dataset shape: {data.shape}")

        # Load channel data for temporal analysis
        channel_data = load_dataset("picmus_resolution_experiment", key="/channel_data")
        print(f"Channel data shape: {channel_data.shape}")
    """
    # Fail fast if pyuff_ustb is not available
    _check_pyuff_ustb()

    if dataset_name not in USTB_DATASETS:
        raise KeyError(f"Dataset {dataset_name} not found")

    dataset_info = USTB_DATASETS[dataset_name]
    cached_file = CACHE_DIR / dataset_info["filename"]

    # Download if missing and requested
    if download_if_missing:
        cached_download(
            url=dataset_info["url"],
            filename=dataset_info["filename"],
            expected_size=dataset_info["size"],
        )
    elif not cached_file.exists():
        raise FileNotFoundError(f"Dataset {dataset_name} is not cached")

    # Load and return the actual data
    uff_file: Uff = Uff(str(cached_file))
    try:
        key_data = uff_file.read(key)
    except ReaderKeyError as err:
        raise KeyError(f"Key {key} not found in dataset {dataset_name}") from err

    if not hasattr(key_data, "data"):
        raise ValueError(f"Key {key} does not contain data")

    return cast(BeamformedData | ChannelData, key_data).data


def load_uff_dataset(dataset_name: str) -> tuple[ArrayAPIObj, Any]:
    """Load and reshape any UFF dataset.

    Parameters:
        dataset_name: Name of the dataset to load

    Returns:
        Tuple of (beamformed_image, scan_info)
    """
    # Get dataset information and download if not cached
    dataset_info = inspect_dataset(dataset_name)
    data_file = cached_download(
        url=dataset_info["url"],
        filename=dataset_info["filename"],
        expected_size=dataset_info.get("size"),
    )

    # Load using UFF
    uff_file = uff.Uff(str(data_file))
    beamformed_data = uff_file.read("/beamformed_data")
    beamformed_data: BeamformedData = cast(BeamformedData, beamformed_data)

    # Get scan geometry
    scan = beamformed_data.scan

    # Reshape data using scan geometry
    beamformed_image = beamformed_data.data.reshape(
        (scan.x_axis.size, scan.z_axis.size),
    )

    return beamformed_image, scan
