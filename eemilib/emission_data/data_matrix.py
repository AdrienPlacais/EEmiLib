"""Store the filepaths entered by user."""

from collections.abc import Collection

from eemilib.emission_data.emission_data import EmissionData
from eemilib.loader.loader import Loader
from eemilib.util.constants import ImplementedEmissionData, ImplementedPop

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
        self.files_matrix: list[list[None | str | Collection[str]]]
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
        emission_data_type = col_to_emission_data_type[col]
        return population_type, emission_data_type

    def set_files_by_index(
        self, files: str | Collection[str], row: int, col: int
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
        files: str | Collection[str],
        population: ImplementedPop,
        emission_data_name: ImplementedEmissionData,
    ) -> None:
        """Set the file(s) by position."""
        row = pop_to_row[population]
        col = emission_data_type_to_col[emission_data_name]
        self.set_files_by_index(files, row, col)

    def set_data_by_name(
        self,
        emission_data: EmissionData | Collection[EmissionData],
        population: ImplementedPop,
        emission_data_name: ImplementedEmissionData,
    ) -> None:
        """Set the data by position."""
        row = pop_to_row[population]
        col = emission_data_type_to_col[emission_data_name]
        self.set_data_by_index(emission_data, row, col)

    def load_data(self, loader: Loader):
        """Load all the data in the object."""
        for row, pop in zip(self.files_matrix, ImplementedPop):
            for filepath, method_name in zip(
                row,
                (
                    "load_emission_yield",
                    "load_emission_energy_distribution",
                    "load_emission_angle_distribution",
                ),
            ):
                if filepath is None:
                    continue
                loader_method = getattr(loader, method_name)

                if isinstance(filepath, str):
                    emission_data_df = loader_method(filepath)
