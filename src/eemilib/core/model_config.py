"""Structure defining which data a :class:`.Model` will need to be fitted ."""

from collections.abc import Collection
from dataclasses import dataclass

from eemilib.util.constants import (
    IMPLEMENTED_EMISSION_DATA,
    IMPLEMENTED_POP,
    ImplementedEmissionData,
    ImplementedPop,
)
from eemilib.util.exceptions import NotImplementedPopulationError


@dataclass
class ModelConfig:
    """Defines which data a :class:`.Model` will need to be fitted ."""

    emission_yields: Collection[ImplementedPop]
    emission_energies: Collection[ImplementedPop]
    emission_angles: Collection[ImplementedPop]

    def __post_init__(self) -> None:
        """Validate given data."""
        for populations in (
            self.emission_yields,
            self.emission_energies,
            self.emission_angles,
        ):
            for population in populations:
                if population not in IMPLEMENTED_POP:
                    raise NotImplementedPopulationError(
                        f"{population = } is not in the list of implemented "
                        f"populations, ie {IMPLEMENTED_POP}."
                    )

    @property
    def populations_by_data_type(
        self,
    ) -> dict[ImplementedEmissionData, Collection[ImplementedPop]]:
        """Map each emission data type to its required populations."""
        return {
            "Emission Yield": self.emission_yields,
            "Emission Energy": self.emission_energies,
            "Emission Angle": self.emission_angles,
        }

    def mandatory_populations(
        self, data_type: ImplementedEmissionData
    ) -> list[ImplementedPop]:
        """Tell which populations should be given for the ``data_type``.

        In general, it will be ``["all"]``, because :class:`.Model` are to be
        fitted on experimental data, and it experimentally complex to
        discriminate the different emitted populations.

        """
        if data_type not in IMPLEMENTED_EMISSION_DATA:
            raise RuntimeError(
                f"{data_type = } is not in {IMPLEMENTED_EMISSION_DATA = }"
            )
        return list(self.populations_by_data_type[data_type])
