"""Define some types and constants."""

from typing import Literal

ImplementedEmissionData = Literal[
    "Emission Yield", "Emission Energy", "Emission Angle"
]
ImplementedPop = Literal["SE", "EBE", "IBE", "all"]
EY_col_energy = "Energy [eV]"
EY_col_normal = "0.0 [deg]"
