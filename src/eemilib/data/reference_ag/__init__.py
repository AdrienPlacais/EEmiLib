"""Provide "average" emission yield Ag curve.

It was obtained by N.~Fil *et al* by averaging several technical silver |TEEY|
:cite:`Fil2016a`. In their paper, it is called "Technical samples". Please use
this reference if you use it in your work.

This data can be loaded with :class:`.pandas_loader.PandasLoader`.

"""

from importlib import resources

files = resources.files(__name__)
emission_yield = files / "K-S8_AG_TECHNICAL_TEEY_REF.csv"
