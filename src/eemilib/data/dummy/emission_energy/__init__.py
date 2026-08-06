"""Define dummy energy distributions, mainly for test purposes."""

from importlib import resources

files = resources.files(__name__)

#: Maxwellian energy distribution at :math:`7.5\,\mathrm{eV}` generated with
#: CST.
maxwellian = files / "cst_energy_distribution_7.5eV_maxwellian.txt"

maxwellian_parameters_values = {"temperature": 7.5}
