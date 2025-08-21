"""
## H5Lib

An object-oriented reader for HDF5 files in python wrapped around `h5py`.
"""

from .reader import HDF5Reader
from .library import H5Library

__all__ = [
    "HDF5Reader",
    "H5Library"
]
