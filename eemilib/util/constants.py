"""Define some types and constants."""

from typing import Literal

ImplementedEmissionData = Literal[
    "Emission Yield", "Emission Energy", "Emission Angle"
]
ImplementedPop = Literal["SE", "EBE", "IBE", "all"]
EY_col_energy = "Energy [eV]"
EY_col_normal = "0.0 [deg]"

markdown = {
    "SE": r"SEEY $\delta$",
    "EBE": r"EBEEY $\eta_e$",
    "IBE": r"IBEEY $\eta_i$",
    "all": r"TEEY $\sigma$",
}
