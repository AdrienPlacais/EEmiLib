"""Define objects to store electron emission data."""

from .data_matrix import DataMatrix as _DataMatrix

# Trick to avoid Sphinx duplicate reference warning
_DataMatrix.__module__ = "eemilib.emission_data"
DataMatrix = _DataMatrix

__all__ = ["DataMatrix"]
