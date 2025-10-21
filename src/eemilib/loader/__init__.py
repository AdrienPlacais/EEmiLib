"""Define objects to load the different formats of electron emission files."""

from .deesse_loader import DeesseLoader as _DeesseLoader
from .pandas_loader import PandasLoader as _PandasLoader

# Trick to avoid Sphinx duplicate reference warning
_DeesseLoader.__module__ = "eemilib.loader"
DeesseLoader = _DeesseLoader
_PandasLoader.__module__ = "eemilib.loader"
PandasLoader = _PandasLoader

__all__ = ["DeesseLoader", "PandasLoader"]
