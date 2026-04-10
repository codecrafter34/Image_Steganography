"""
Steganography package for image steganography research.

This package provides:
- Bit-plane manipulation utilities
- Three embedding methods (LSB, random, adaptive)
- Corresponding extraction methods
- Dataset generation tools
"""

from . import utils
from . import embed
from . import extract

__all__ = ['utils', 'embed', 'extract']
