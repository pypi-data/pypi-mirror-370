"""
cog2tiles - High-Performance COG to Web Map Tiles Converter

Author: Kshitij Raj Sharma
Copyright: 2025
License: MIT
"""

from ._version import __version__

__author__ = "Kshitij Raj Sharma"
__email__ = "krschap@duck.com"

from .tiler import COGTiler
from .utils import normalize_array, process_bands

__all__ = ["COGTiler", "normalize_array", "process_bands", "__version__"]
