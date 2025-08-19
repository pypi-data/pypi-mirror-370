from typing import Optional, Union

import numpy as np
from numpy.typing import NDArray
from pandas import DataFrame


def organize_data_by_target_and_sequence(
    df: DataFrame, metric: str, dimensions: Optional[Union[list[int], NDArray[np.integer]]] = None
) -> dict[str, dict[str, NDArray[np.floating]]]:
    output: dict[str, dict[str, NDArray[np.floating]]] = {}
    target_numbers = df["target_number"].unique()
    sequences = df["sequence"].unique()
    for target in target_numbers:
        seq_data: dict[str, NDArray[np.floating]] = {}
        for seq in sequences:
            target_data = df.query("sequence == " + '"' + seq + '"').query("target_number == " + str(target))
            # NOTE: the function should be passed in as a Callable instead of as a string for `eval`
            # Apply eval then convert to numpy array
            data_array = target_data[metric].apply(eval).apply(np.array)
            fwhm = np.vstack(data_array)
            if dimensions is not None:
                fwhm = fwhm[:, dimensions]
            seq_data.update({seq: fwhm})
        output.update({"target_" + str(target): seq_data})
    return output
