"""Define a structure to select a :class:`.Model` mandatory files."""

from collections.abc import Collection
from dataclasses import dataclass

from eemilib.util.constants import (
    IMPLEMENTED_EMISSION_DATA,
    ImplementedEmissionData,
    ImplementedPop,
)


@dataclass
class ModelConfig:
    """Define mandatory files for a :class:`.Model`."""

    emission_yield_files: Collection[ImplementedPop]
    emission_energy_files: Collection[ImplementedPop]
    emission_angle_files: Collection[ImplementedPop]

    def mandatory_populations(
        self, emission_data_type: ImplementedEmissionData
    ) -> list[ImplementedPop]:
        """Tell which population should be given in files, for a data type."""
        if emission_data_type == "Emission Yield":
            return list(self.emission_yield_files)
        if emission_data_type == "Emission Energy":
            return list(self.emission_energy_files)
        if emission_data_type == "Emission Angle":
            return list(self.emission_angle_files)
        raise RuntimeError(
            f"{emission_data_type = } is not in {IMPLEMENTED_EMISSION_DATA = }"
        )
