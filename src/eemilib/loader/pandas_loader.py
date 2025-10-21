"""Define a generic files loader.

Check the documentation of :meth:`.PandasLoader.load_emission_yield` and
:meth:`.PandasLoader.load_emission_energy_distribution` for expected file
formats.

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
        sep: str = ",",
        comment: str = "#",
    ) -> pd.DataFrame:
        """Load and format the given emission yield file.

        ``CSV`` files can have comments at the start of the file, starting with
        a ``#`` character. Column separator must be ``,``. First non-commented
        line is incidence angle in degrees. First column is incident energy in
        :unit:`eV`. EY is the next columns (excluding the first line).
        Example:

        .. code-block::

            # Cu measurements
            # Some comments
            # Energy | 0deg | 20deg | 40deg | 60deg
            0,0,20,40,60
            0,0.814,0.781,0.866,0.918
            10,0.574,0.553,0.637,0.803
            20,0.632,0.594,0.671,0.817

        Files in the :file:`data/example_copper/` files are taken from
        :cite:`Placais2020b` and are correctly formatted.

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
        pandas.DataFrame
            Structure holding the data. Has a ``Energy [eV]`` column
            holding PEs energy. And one or several columns ``theta [deg]``,
            where ``theta`` is the value of the incidence angle and content is
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
        sep: str = ",",
        comment: str = "#",
    ) -> tuple[pd.DataFrame, float | None]:
        """Load and format the given emission energy file.

        ``CSV`` files can have comments at the start of the file, starting with
        a ``#`` character. It is expected that the energy of PEs used for the
        measurements is on the second commented line, in :unit:`eV`. Column
        separator must be ``,``. First non-commented line is incidence angle in
        degrees. First column is emission energy in :unit:`eV`. Distribution is
        in the next columns (excluding the first line).
        Example:

        .. code-block::

            # PEs energy in eV
            # 100
            0,0
            1.999999999999975131e-01,7.117578753770542783e-03
            3.999999999999968026e-01,1.138131444290255145e-02
            5.999999999999978684e-01,1.510969903349285159e-02

        Files in the :file:`data/example_ag/emission_energy` files are
        correctly formatted.

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
        float
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
        if len(df.columns) != 2:
            raise RuntimeError(
                f"Error loading {filepath}. "
                f"The file should have two columns, separated by a ``{sep}`` "
                f"character. File was read as:\n{df}"
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
