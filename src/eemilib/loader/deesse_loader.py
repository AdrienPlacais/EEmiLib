"""Define a loader adapted to DEESSE (ONERA, Toulouse) file format."""

import logging
from collections.abc import Sequence
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any

import pandas as pd

from eemilib.loader.helper import DataPath
from eemilib.loader.loader import Loader
from eemilib.util.constants import COL_ENERGY, COL_NORMAL, ImplementedPop


class DeesseLoader(Loader):
    """Define the loader."""

    def __init__(self) -> None:
        """Init the object.

        Ideally, this loader should detect correct input and columns. But it is
        not for now.

        """
        super().__init__()

    def load_emission_yield(
        self, *filepath: DataPath, population: ImplementedPop | None = None
    ) -> pd.DataFrame:
        """Load and format the given emission yield files.

        Parameters
        ----------
        filepath :
            Path(s) to file holding data under study.
        population :
            Concerned population of electrons. Unused by this loader.

        Returns
        -------
        pandas.DataFrame
            Structure holding the data. Has a ``Energy [eV]`` column
            holding |PEs| energy. And one or several columns ``theta [deg]``,
            where `theta` is the value of the incidence angle and content is
            corresponding emission yield.

        """
        col1 = "Energie réelle des électrons (eV)"
        col2 = "TEEY"
        kwargs = {"sep": ";", "encoding": "latin1", "header": 5}
        all_df = []
        for file in filepath:
            if isinstance(filepath, Traversable):
                raise NotImplementedError("Not yet handling Traversable")
            full_df = pd.read_csv(file, **kwargs)
            incidence_angle = self._extract_incidence_angle(full_df)
            of_interest_df = full_df[[col1, col2]].rename(
                columns={col1: COL_ENERGY, col2: f"{incidence_angle} [deg]"}
            )
            all_df.append(of_interest_df.set_index(COL_ENERGY))

        concatenated = pd.concat(all_df, axis=1)
        logging.info(f"Successfully loaded emission yield file(s) {filepath}")
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
        """Load an emission angle file."""
        raise NotImplementedError

    def load_emission_energy_distribution(
        self,
        *filepaths: DataPath,
        population: ImplementedPop | None = None,
        e_pes: Sequence[float] | None = None,
        **kwargs,
    ) -> dict[DataPath, tuple[pd.DataFrame, float | None]]:
        """Load and format several emission energy files from DEESSE.

        Parameters
        ----------
        filepaths :
            Path to files holding data under study.
        population :
            Unused.
        e_pes :
            Energy of |PEs| in :unit:`eV`, for every path in ``filepaths``.
            Should be manually provided, as not present in DEESSE files.
        kwargs :
            Unused additional arguments.

        Returns
        -------
            For every filepath:

            - A pandas dataframe holding the data. Has a ``Energy [eV]`` column
              holding emitted electrons energy. And one or several columns
              ``theta [deg]``, where ``theta`` is the value of the incidence
              angle and content is corresponding emission energy distribution.
            - Energy of |PEs| in :unit:`eV`.

        """
        if len(filepaths) == 0:
            raise ValueError("Cannot load, no file provided.")

        if e_pes is None:
            raise ValueError("DesseLoader nees PEs energy to work.")

        return {
            fp: self._load_single_emission_energy_distribution(fp, e_pe=e_pe)
            for fp, e_pe in zip(filepaths, e_pes, strict=True)
        }

    def _load_single_emission_energy_distribution(
        self,
        filepath: DataPath,
        e_pe: float | None = None,
        population: ImplementedPop | None = None,
    ) -> tuple[pd.DataFrame, float | None]:
        """Load and format a single emission energy file from DEESSE.

        Parameters
        ----------
        filepath :
            Path to file holding data under study.
        e_pe :
            Energy of |PEs| in :unit:`eV`. Should be manually provided, as not
            present in DEESSE files.
        population :
            Concerned population. Unused by this loader.

        Returns
        -------
        pandas.DataFrame
            Structure holding the data. Has a ``Energy [eV]`` column
            holding emitted electrons energy. And one or several columns
            ``theta [deg]``, where ``theta`` is the value of the incidence
            angle and content is corresponding emission energy distribution.
        float
            Energy of |PEs| in :unit:`eV`. If not found in the file comments,
            it will be inferred from the position of the |EBEs| peak.

        """
        col1 = "Kinetic Energy [eV]"
        col2 = "Intensity[cts/s]"
        if isinstance(filepath, Traversable):
            raise NotImplementedError("Not yet handling Traversable")
        extension = Path(filepath).suffix
        if extension == ".csv":
            df = pd.read_csv(filepath, sep=";")
        elif extension == ".xlsx":
            df = pd.read_excel(filepath)
        else:
            raise RuntimeError(f"Filetype of {filepath} is not supported.")
        df = df[[col1, col2]].rename(
            columns={col1: COL_ENERGY, col2: COL_NORMAL}
        )
        return df, e_pe
