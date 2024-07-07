"""Store the filepaths entered by user."""

from collections.abc import Collection

from eemilib.util.constants import ImplementedEmissionData, ImplementedPop

pop_to_row = {"SE": 0, "EBE": 1, "IBE": 2, "all": 3}
emission_data_to_col = {
    "Emission Yield": 0,
    "Emission Energy": 1,
    "Emission Angle": 2,
}


class FilesMatrix:
    """Store all the input files in a single object."""

    def __init__(self) -> None:
        """Instantiate the object."""
        self.matrix: list[list[None | str | Collection[str]]]
        self.matrix = [[None for _ in range(3)] for _ in range(4)]

    def set_files_by_index(
        self, files: str | Collection[str], row: int, col: int
    ) -> None:
        """Set the file(s) by position."""
        self.matrix[row][col] = files

    def set_files_by_name(
        self,
        files: str | Collection[str],
        population: ImplementedPop,
        emission_data: ImplementedEmissionData,
    ) -> None:
        """Set the file(s) by position."""
        row = pop_to_row[population]
        col = emission_data_to_col[emission_data]
        self.set_files_by_index(files, row, col)
