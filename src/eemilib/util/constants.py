"""Define some types and constants."""

from typing import Literal

q = 1.6e-19

#: The three types of emission data.
ImplementedEmissionData = Literal[
    "Emission Yield", "Emission Energy", "Emission Angle"
]
IMPLEMENTED_EMISSION_DATA = (
    "Emission Yield",
    "Emission Energy",
    "Emission Angle",
)

#: Implemented populations.
ImplementedPop = Literal["SE", "EBE", "IBE", "all"]
IMPLEMENTED_POP = ("SE", "EBE", "IBE", "all")

#: Typical column where energy is stored in dataframes.
#: In emission yield data, this is the energy of |PEs|. In emission energy data,
#: this is the energy of emitted electrons.
COL_ENERGY = "Energy [eV]"
#: Typical column where normal incidence data is stored in dataframes.
COL_NORMAL = "0.0 [deg]"
