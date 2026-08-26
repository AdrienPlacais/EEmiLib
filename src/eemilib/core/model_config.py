"""Structure defining which data a :class:`.Model` will need to be fitted ."""

from collections.abc import Collection
from dataclasses import dataclass

from eemilib.util.constants import (
    IMPLEMENTED_EMISSION_DATA,
    ImplementedEmissionData,
    ImplementedPop,
)


@dataclass
class ModelConfig:
    """Defines which data a :class:`.Model` will need to be fitted ."""

    emission_yields: Collection[ImplementedPop]
    emission_energies: Collection[ImplementedPop]
    emission_angles: Collection[ImplementedPop]

    def mandatory_populations(
        self, data_type: ImplementedEmissionData
    ) -> list[ImplementedPop]:
        """Tell which populations should be given for the ``data_type``.

        In general, it will be ``["all"]``, because :class:`.Model` are to be
        fitted on experimental data, and it experimentally complex to
        discriminate the different emitted populations.

        """
        if data_type == "Emission Yield":
            return list(self.emission_yields)
        if data_type == "Emission Energy":
            return list(self.emission_energies)
        if data_type == "Emission Angle":
            return list(self.emission_angles)
        raise RuntimeError(
            f"{data_type = } is not in {IMPLEMENTED_EMISSION_DATA = }"
        )
