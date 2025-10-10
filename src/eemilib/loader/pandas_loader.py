"""Define a generic files loader.

See the example TEEY in ``data/example_copper/`` for the expected file format.

"""

from pathlib import Path
from typing import Any

import pandas as pd
from eemilib.loader.loader import Loader
from eemilib.util.constants import col_energy


class PandasLoader(Loader):
    """Define the pandas loader."""

    def __init__(self) -> None:
        """Init object."""
        return super().__init__()

    def load_emission_yield(
        self,
        filepath: str | Path,
        sep: str = "\t",
        comment: str = "#",
    ) -> pd.DataFrame:
        """Load and format the given emission yield files.

        Parameters
        ----------
        filepath : str | pathlib.Path
            Path to file holding data under study.

        Returns
        -------
        data : pandas.DataFrame
            Structure holding the data. Has a ``Energy [eV]`` column
            holding PEs energy. And one or several columns ``theta [deg]``,
            where `theta` is the value of the incidence angle and content is
            corresponding emission yield.

        """
        headers = []
        i = 0
        with open(filepath) as file:
            for i, line in enumerate(file):
                if not line.startswith(comment):
                    headers = line.strip().split(sep)
                    break
        if not headers:
            raise OSError(
                "Error reading the given file. It seems there is no"
                f" uncommented line? Comment character is {comment}."
            )

        headers[0] = col_energy
        headers[1:] = [f"{float(h)} [deg]" for h in headers[1:]]

        df = pd.read_csv(
            filepath, comment=comment, sep=sep, names=headers, skiprows=i + 1
        )
        return df

    def load_emission_angle_distribution(self, *args) -> Any:
        raise NotImplementedError

    def load_emission_energy_distribution(self, *args) -> Any:
        raise NotImplementedError
