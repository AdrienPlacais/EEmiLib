"""Store the filepaths entered by user.

.. todo::
    Methods to reset filepaths/data

"""

from collections.abc import Collection
from pathlib import Path

from eemilib.emission_data.emission_angle_distribution import (
    EmissionAngleDistribution,
)
from eemilib.emission_data.emission_data import EmissionData
from eemilib.emission_data.emission_energy_distribution import (
    EmissionEnergyDistribution,
)
from eemilib.emission_data.emission_yield import EmissionYield
from eemilib.loader.loader import Loader
from eemilib.model.model_config import ModelConfig
from eemilib.util.constants import (
    IMPLEMENTED_EMISSION_DATA,
    ImplementedEmissionData,
    ImplementedPop,
)

pop_to_row = {"SE": 0, "EBE": 1, "IBE": 2, "all": 3}
row_to_pop = {val: key for key, val in pop_to_row.items()}
emission_data_type_to_col = {
    "Emission Yield": 0,
    "Emission Energy": 1,
    "Emission Angle": 2,
}
col_to_emission_data_type = {
    val: key for key, val in emission_data_type_to_col.items()
}


class DataMatrix:
    """Store all the input files and corresp data in a single object."""

    def __init__(self) -> None:
        """Instantiate the object."""
        self.files_matrix: list[
            list[None | str | Collection[str] | Path | Collection[Path]]
        ]
        self.files_matrix = [[None for _ in range(3)] for _ in range(4)]

        self.data_matrix: list[
            list[None | EmissionData | Collection[EmissionData]]
        ]
        self.data_matrix = [[None for _ in range(3)] for _ in range(4)]

    def _natures_to_indexes(
        self,
        population_type: ImplementedPop,
        emission_data_type: ImplementedEmissionData,
    ) -> tuple[int, int]:
        """Give the desired indexes."""
        row = pop_to_row[population_type]
        col = emission_data_type_to_col[emission_data_type]
        return row, col

    def _indexes_to_natures(
        self, row: int, col: int
    ) -> tuple[ImplementedPop, ImplementedEmissionData]:
        """Give the desired natures."""
        population_type = row_to_pop[row]
        assert isinstance(population_type, ImplementedPop)
        emission_data_type = col_to_emission_data_type[col]
        assert isinstance(emission_data_type, ImplementedEmissionData)
        return population_type, emission_data_type

    def set_files_by_index(
        self,
        files: str | Collection[str] | Path | Collection[Path],
        row: int,
        col: int,
    ) -> None:
        """Set the file(s) by position."""
        self.files_matrix[row][col] = files

    def set_data_by_index(
        self,
        emission_data: EmissionData | Collection[EmissionData],
        row: int,
        col: int,
    ) -> None:
        """Assign the :class:`.EmissionData` at proper indexes."""
        self.data_matrix[row][col] = emission_data

    def set_files_by_name(
        self,
        files: str | Collection[str] | Path | Collection[Path],
        population: ImplementedPop,
        emission_data_type: ImplementedEmissionData,
    ) -> None:
        """Set the file(s) by position."""
        row, col = self._natures_to_indexes(population, emission_data_type)
        self.set_files_by_index(files, row, col)

    def set_data_by_name(
        self,
        emission_data: EmissionData | Collection[EmissionData],
        population: ImplementedPop,
        emission_data_type: ImplementedEmissionData,
    ) -> None:
        """Set the data by position."""
        row, col = self._natures_to_indexes(population, emission_data_type)
        self.set_data_by_index(emission_data, row, col)

    def load_data(self, loader: Loader) -> None:
        """Load all filepaths in :attr:`files_matrix`.

        .. todo::
            Could be more concise.

        """
        for pop, row in pop_to_row.items():
            assert isinstance(pop, ImplementedPop)
            for data_type, col in emission_data_type_to_col.items():
                filepath = self.files_matrix[row][col]
                if filepath is None:
                    continue

                if data_type == "Emission Yield":
                    emission_data = EmissionYield.from_filepath(
                        pop, loader, *filepath
                    )
                    self.set_data_by_index(emission_data, row, col)

                if data_type == "Emission Energy":
                    emission_data = EmissionEnergyDistribution.from_filepath(
                        pop, loader, *filepath
                    )
                    self.set_data_by_index(emission_data, row, col)

                if data_type == "Emission Angle":
                    emission_data = EmissionAngleDistribution.from_filepath(
                        pop, loader, *filepath
                    )
                    self.set_data_by_index(emission_data, row, col)

    def assert_has_all_mandatory_files(
        self, model_config: ModelConfig
    ) -> None:
        """Tell if files defined by :attr:`.Model.model_config` are set."""
        for emission_data_type, corresponding_attribute in zip(
            IMPLEMENTED_EMISSION_DATA,
            (
                "emission_yield_files",
                "emission_energy_files",
                "emission_angle_files",
            ),
        ):
            mandatory_data_type = getattr(
                model_config, corresponding_attribute
            )

            for mandatory_population in mandatory_data_type:
                row, col = self._natures_to_indexes(
                    mandatory_population, emission_data_type
                )
                filepath = self.files_matrix[row][col]
                assert filepath is not None, (
                    f"You must define a {emission_data_type} filepath for"
                    + f" population {mandatory_population}"
                )
                data_object = self.data_matrix[row][col]
                assert data_object is not None, (
                    f"You must load {emission_data_type} filepath for "
                    + f"population {mandatory_population}"
                )
