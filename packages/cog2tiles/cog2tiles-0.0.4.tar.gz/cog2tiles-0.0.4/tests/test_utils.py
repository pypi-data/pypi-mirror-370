"""
Basic tests for cog2tiles package.

Author: Kshitij Raj Sharma
Copyright: 2025
License: MIT
"""

import numpy as np
import pytest

from cog2tiles.utils import normalize_array, process_bands


def test_normalize_array():
    """Test array normalization function."""
    # Test with simple data
    data = np.array([[0, 128, 255]], dtype=np.float32)
    result = normalize_array(data)

    assert result.dtype == np.uint8
    assert result.shape == data.shape
    assert np.min(result) == 0
    assert np.max(result) == 255


def test_process_bands_single_band():
    """Test processing single band data."""
    data = np.random.rand(1, 10, 10).astype(np.float32)
    result = process_bands(data)

    assert result.shape == (10, 10)


def test_process_bands_multi_band():
    """Test processing multi-band data."""
    data = np.random.rand(4, 10, 10).astype(np.float32)
    result = process_bands(data)

    assert result.shape == (10, 10, 4)


if __name__ == "__main__":
    pytest.main([__file__])
