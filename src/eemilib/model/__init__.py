"""Define the electron emission models."""

from .chung_and_everhart import ChungEverhart as _ChungEverhart
from .sombrin import Sombrin as _Sombrin
from .vaughan import Vaughan as _Vaughan

# Trick to avoid Sphinx duplicate reference warning
_ChungEverhart.__module__ = "eemilib.model"
ChungEverhart = _ChungEverhart
_Sombrin.__module__ = "eemilib.model"
Sombrin = _Sombrin
_Vaughan.__module__ = "eemilib.model"
Vaughan = _Vaughan

__all__ = ["ChungEverhart", "Sombrin", "Vaughan"]
