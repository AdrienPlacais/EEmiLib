"""Define a generic files loader.

See the example TEEY in ``data/example_copper/`` for the expected file format.

"""

import logging
from pathlib import Path
from typing import Any

import pandas as pd
from eemilib.loader.helper import read_comments, read_header
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
    ) -> tuple[pd.DataFrame, float | None]:
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
        pd.DataFrame
            Structure holding the data. Has a ``Energy [eV]`` column
            holding emitted electrons energy. And one or several columns
            ``theta [deg]``, where ``theta`` is the value of the incidence
            angle and content is corresponding emission energy distribution.
        e_pe
            Energy of Primary Electrons in :unit:`eV`. If not found in the file
            comments, it will be inferred from the position of the EBEs peak.

        """
        header, n_comments = read_header(filepath, sep, comment)
        df = pd.read_csv(
            filepath,
            comment=comment,
            sep=sep,
            names=header,
            skiprows=n_comments + 1,
        )

        comments = read_comments(filepath, comment=comment)

        if len(comments) < 2:
            logging.error(
                f"Error loading {filepath}. "
                "PandasLoader expects at least two lines of comments at the "
                "start of filepath. (Second line should hold energy of primary"
                "electrons in eV). Will try to infer this quantity from the "
                "position of EBEs peak."
            )
            return df, None

        try:
            e_pe = float(comments[1])

        except ValueError as e:
            logging.error(
                f"Error loading {filepath}. "
                "PandasLoader expects the second comment line to hold the "
                "energy of PEs, in eV. Will try to infer this quantity "
                f"from the position of EBEs peak.\n{e}"
            )
            return df, None

        logging.info(
            "Successfully loaded emission energy distribution file(s) "
            f"{filepath}"
        )
        return df, e_pe
