"""Emission energy measurements realized at ONERA, Toulouse, France using the
DEESSE test facility on 2018-05-30.

This is an Ag sample that was heated at 200 celsius during 2 hours. It is
called "heated Ag#1" in my PhD :cite:`Placais2021`.

Emission energy data at normal incidence. Corrected using M. Villemant
procedure :cite:`Villemant2018`. Can be loaded using :class:`.loader.PandasLoader`.
This data can be loaded with :class:`.pandas_loader.PandasLoader`.

"""

from importlib import resources

files = resources.files(__name__)

distrib_10eV = files / "corrected_cleanAg0_10eV_2018.05.30.csv"
distrib_20eV = files / "corrected_cleanAg0_20eV_2018.05.30.csv"
distrib_30eV = files / "corrected_cleanAg0_30eV_2018.05.30.csv"
distrib_50eV = files / "corrected_cleanAg0_50eV_2018.05.30.csv"
distrib_70eV = files / "corrected_cleanAg0_70eV_2018.05.30.csv"
distrib_100eV = files / "corrected_cleanAg0_100eV_2018.05.30.csv"
distrib_150eV = files / "corrected_cleanAg0_150eV_2018.05.30.csv"

distribs = (
    distrib_10eV,
    distrib_20eV,
    distrib_30eV,
    distrib_50eV,
    distrib_70eV,
    distrib_100eV,
    distrib_150eV,
)
