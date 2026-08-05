r"""Provide data for niobium.

It was manually extracted from following papers:
- :math:`300\,\mathrm{\degrees}` baked out niobium: :cite:`Piel1988`.
- Degreased niobium: :cite:`Aull2015`.
- Sputtered niobium: :cite:`Aull2015`.

This data can be loaded using :class:`.loader.PandasLoader`.

"""

from importlib import resources

files = resources.files(__name__)

nb_baked_out = files / "Nb_baked-out-at-300_CERN_WPD.csv"
nb_degreased = files / "Nb_degreased_WPD.csv"
nb_sputtered = files / "Nb_sputtered_WPD.csv"
