"""Define a loader adapted to DEESSE (ONERA, Toulouse) file format.

"""

from pathlib import Path
from typing import Any

import pandas as pd

from eemilib.loader.loader import Loader


class DeesseLoader(Loader):
    """Define the loader."""

    def __init__(self) -> None:
        """Raise an error for now.

        Ideally, this loader should detect correct input and columns. But it is
        not for now.

        """

    def load_emission_yield(self, *filepath: str | Path) -> pd.DataFrame:
        """Load and format the given emission yield files.

        Parameters
        ----------
        filepath : str | Path
            Path(s) to file holding data under study.

        Returns
        -------
        data : pd.DataFrame
            Structure holding the data. Must have a ``Energy [eV]`` column
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
        all_data = []
        for file in filepath:
            full_data = pd.read_csv(file, **kwargs)
            incidence_angle = float(full_data.iloc[5].iloc[-1][:-1])
            interesting_data = full_data[[col1, col2]].rename(
                columns={col1: "Energy [eV]", col2: f"{incidence_angle} [deg]"}
            )
            all_data.append(interesting_data)

        return pd.concat(all_data)

    def load_emission_angle_distribution(self, *args) -> Any:
        raise NotImplementedError

    def load_emission_energy_distribution(self, *args) -> Any:
        raise NotImplementedError
