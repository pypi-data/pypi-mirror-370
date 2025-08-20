"""
Utility functions for cog2tiles.

Author: Kshitij Raj Sharma
Copyright: 2025
License: MIT
"""

import numpy as np
from numba import jit, prange


@jit(nopython=True, parallel=True)
def normalize_array(data: np.ndarray, dtype_max: int = 255) -> np.ndarray:
    """
    Normalize array values to uint8 range using Numba JIT compilation.

    Args:
        data: Input array to normalize
        dtype_max: Maximum value for output dtype (default: 255 for uint8)

    Returns:
        Normalized uint8 array
    """
    flat = data.flatten()
    min_val = np.min(flat)
    max_val = np.max(flat)

    if max_val == min_val:
        return np.zeros_like(data, dtype=np.uint8)

    result = np.empty_like(data, dtype=np.uint8)
    for i in prange(data.size):
        flat_idx = i
        normalized = (flat[flat_idx] - min_val) * dtype_max / (max_val - min_val)

        if normalized < 0:
            clipped = 0
        elif normalized > dtype_max:
            clipped = dtype_max
        else:
            clipped = normalized
        result.flat[i] = np.uint8(clipped)

    return result


def process_bands(data: np.ndarray) -> np.ndarray:
    """
    Process multi-band raster data for tile output.

    Args:
        data: Input array with shape (bands, height, width)

    Returns:
        Processed array suitable for image creation
    """
    bands, height, width = data.shape

    if bands == 1:
        return data[0]
    elif bands >= 3:
        result = np.empty((height, width, min(bands, 4)), dtype=data.dtype)
        for b in range(min(bands, 4)):
            result[:, :, b] = data[b]
        return result
    else:
        return data[0]
