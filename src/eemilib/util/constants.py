"""Define some types and constants."""

from typing import Literal

q = 1.6e-19

ImplementedEmissionData = Literal[
    "Emission Yield", "Emission Energy", "Emission Angle"
]
IMPLEMENTED_EMISSION_DATA = (
    "Emission Yield",
    "Emission Energy",
    "Emission Angle",
)

ImplementedPop = Literal["SE", "EBE", "IBE", "all"]
IMPLEMENTED_POP = ("SE", "EBE", "IBE", "all")

col_energy = "Energy [eV]"
col_normal = "0.0 [deg]"

md_ey: dict[ImplementedPop, str] = {
    "SE": r"SEEY $\delta$",
    "EBE": r"EBEEY $\eta_e$",
    "IBE": r"IBEEY $\eta_i$",
    "all": r"TEEY $\sigma$",
}
md_energy_distrib: dict[ImplementedPop, str] = {
    "SE": r"$f_\mathrm{SE} [\mathrm{eV}^{-1}]$",
    "EBE": r"$f_\mathrm{EBE} [\mathrm{eV}^{-1}]$",
    "IBE": r"$f_\mathrm{IBE} [\mathrm{eV}^{-1}]$",
    "all": r"$f_\mathrm{all} [\mathrm{eV}^{-1}]$",
}
md_ylabel: dict[ImplementedEmissionData, str] = {
    "Emission Yield": "Emission Yield",
    "Emission Energy": "Emission Energy Distribution",
    "Emission Angle": "Emission Angle Distribution",
}
