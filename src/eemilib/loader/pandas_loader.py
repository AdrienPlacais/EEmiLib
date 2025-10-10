"""Define a generic files loader.

See the example TEEY in ``data/example_copper/`` for the expected file format.

"""

import logging
from pathlib import Path
from typing import Any

import pandas as pd
from eemilib.loader.helper import read_header
from eemilib.loader.loader import Loader


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
        """Load and format the given emission yield file.

        Parameters
        ----------
        filepath :
            Path to file holding data under study.
        sep :
            Column delimiter.
        comment :
            Comment character.

        Returns
        -------
            Structure holding the data. Has a ``Energy [eV]`` column
            holding PEs energy. And one or several columns ``theta [deg]``,
            where `theta` is the value of the incidence angle and content is
            corresponding emission yield.

        """
        header, n_comments = read_header(filepath, sep, comment)
        df = pd.read_csv(
            filepath,
            comment=comment,
            sep=sep,
            names=header,
            skiprows=n_comments + 1,
        )
        logging.info(f"Successfully loaded emission yield file(s) {filepath}")
        return df

    def load_emission_angle_distribution(self, *args) -> Any:
        raise NotImplementedError

    def load_emission_energy_distribution(
        self,
        filepath: str | Path,
        sep: str = "\t",
        comment: str = "#",
    ) -> pd.DataFrame:
        """Load and format the given emission energy file.

        Parameters
        ----------
        filepath :
            Path to file holding data under study.
        sep :
            Column delimiter.
        comment :
            Comment character.

        Returns
        -------
            Structure holding the data. Has a ``Energy [eV]`` column
            holding emitted electrons energy. And one or several columns
            ``theta [deg]``, where ``theta`` is the value of the incidence
            angle and content is corresponding emission energy distribution.

        """
        header, n_comments = read_header(filepath, sep, comment)
        df = pd.read_csv(
            filepath,
            comment=comment,
            sep=sep,
            names=header,
            skiprows=n_comments + 1,
        )
        logging.info(
            "Successfully loaded emission energy distribution file(s) "
            f"{filepath}"
        )
        return df
