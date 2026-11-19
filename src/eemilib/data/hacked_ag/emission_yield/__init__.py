r"""|TEEY| for Ag.

This is Ag from :mod:`.data.ag`, but some data at :math:`0\degree` and
:math:`20\degree` were inverted in order to preserve
:math:`\sigma\right(E,\,20\degree\left) > \sigma\right(E,\,20\degree\left)
\forall E`.

In particular, data at :math:`0\degree` and :math:`20\degree` was inverted for
energies higher or equal as :math:`80\,\unit{eV}`.

"""

from importlib import resources

files = resources.files(__name__)

teey_ag_1_heated_pd = files / "cleanAg_TEEY.csv"
