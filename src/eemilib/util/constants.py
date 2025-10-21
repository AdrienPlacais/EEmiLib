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
#: In emission yield data, this is the energy of PEs. In emission energy data,
#: this is the energy of emitted electrons.
col_energy = "Energy [eV]"
#: Typical column where normal incidence data is stored in dataframes.
col_normal = "0.0 [deg]"

md_ey: dict[ImplementedPop, str] = {
    "SE": r"SEEY $\delta$",
    "EBE": r"EBEEY $\eta_e$",
    "IBE": r"IBEEY $\eta_i$",
    "all": r"TEEY $\sigma$",
}
md_energy_distrib: dict[ImplementedPop, str] = {
    "SE": r"$f_\mathrm{SE}$",
    "EBE": r"$f_\mathrm{EBE}$",
    "IBE": r"$f_\mathrm{IBE}$",
    "all": r"$f_\mathrm{all}$",
}
#: y-label in plots for the different emission data type.
md_ylabel: dict[ImplementedEmissionData, str] = {
    "Emission Yield": "Emission Yield",
    "Emission Energy": r"Emission Energy Distribution [$\mathrm{eV}^{-1}$]",
    "Emission Angle": "Emission Angle Distribution",
}
