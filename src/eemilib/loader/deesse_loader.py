"""Define a loader adapted to DEESSE (ONERA, Toulouse) file format.

"""

from pathlib import Path
from typing import Any

import pandas as pd
from eemilib.loader.loader import Loader
from eemilib.util.constants import EY_col_energy


class DeesseLoader(Loader):
    """Define the loader."""

    def __init__(self) -> None:
        """Raise an error for now.

        Ideally, this loader should detect correct input and columns. But it is
        not for now.

        """
        super().__init__()

    def load_emission_yield(self, *filepath: str | Path) -> pd.DataFrame:
        """Load and format the given emission yield files.

        Parameters
        ----------
        filepath : str | pathlib.Path
            Path(s) to file holding data under study.

        Returns
        -------
        data : pandas.DataFrame
            Structure holding the data. Has a ``Energy [eV]`` column
            holding PEs energy. And one or several columns ``theta [deg]``,
            where `theta` is the value of the incidence angle and content is
            corresponding emission yield.

        """
        col1 = "Energie réelle des électrons (eV)"
        col2 = "TEEY"
        kwargs = {
            "sep": ";",
            "encoding": "latin1",
            "header": 5,
        }
        all_df = []
        for file in filepath:
            full_df = pd.read_csv(file, **kwargs)
            incidence_angle = self._extract_incidence_angle(full_df)
            of_interest_df = full_df[[col1, col2]].rename(
                columns={col1: EY_col_energy, col2: f"{incidence_angle} [deg]"}
            )
            all_df.append(of_interest_df.set_index(EY_col_energy))

        concatenated = pd.concat(all_df, axis=1)
        return concatenated.reset_index()

    def _extract_incidence_angle(self, full_data: pd.DataFrame) -> float:
        """Try to get the incidence angle in the file."""
        row_number = 5
        col_number = -1
        angle_as_str = full_data.iloc[row_number].iloc[col_number]
        assert isinstance(angle_as_str, str)
        try:
            angle = float(angle_as_str)
        except ValueError:
            angle = float(angle_as_str[:-1])
        return angle

    def load_emission_angle_distribution(self, *args) -> Any:
        raise NotImplementedError

    def load_emission_energy_distribution(self, *args) -> Any:
        raise NotImplementedError
