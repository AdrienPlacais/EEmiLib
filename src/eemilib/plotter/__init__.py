"""Define the object that will take care of plotting the data."""

from .pandas import PandasPlotter as _PandasPlotter

# Trick to avoid Sphinx duplicate reference warning
_PandasPlotter.__module__ = "eemilib.plotter"
PandasPlotter = _PandasPlotter

__all__ = ["PandasPlotter"]
