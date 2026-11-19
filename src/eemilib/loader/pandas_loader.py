"""Define a generic files loader.

Check the documentation of :meth:`.loader.PandasLoader.load_emission_yield` and
:meth:`.loader.PandasLoader.load_emission_energy_distribution` for expected file
formats.

"""

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pandas as pd

from eemilib.loader.helper import (
    DataPath,
    WritablePath,
    read_comments,
    read_header,
)
from eemilib.loader.loader import Loader
from eemilib.util.constants import COL_ENERGY, ImplementedPop


class PandasLoader(Loader):
    """Define the pandas loader."""

    def __init__(self, sep: str = ",", comment: str = "#") -> None:
        """Init object."""
        super().__init__()
        self.sep = sep
        self.comment = comment

    def load_emission_yield(
        self,
        *filepaths: DataPath,
        sep: str | None = None,
        comment: str | None = None,
        population: ImplementedPop | None = None,
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
        filepaths :
            Path to files holding data under study.
        sep :
            Column delimiter.
        comment :
            Comment character.
        population :
            Concerned population. Unused by this loader.

        Returns
        -------
        pandas.DataFrame
            Structure holding the data. Has a ``Energy [eV]`` column
            holding |PEs| energy. And one or several columns ``theta [deg]``,
            where ``theta`` is the value of the incidence angle and content is
            corresponding emission yield.

        """
        if len(filepaths) != 1:
            raise NotImplementedError("Can only load exactly one file.")
        filepath = filepaths[0]
        if sep is None:
            sep = self.sep
        if comment is None:
            comment = self.comment
        header, n_comments = read_header(filepath, sep, comment)
        df = pd.read_csv(
            filepath,
            comment=comment,
            sep=sep,
            names=header,
            skiprows=n_comments + 1,
        )
        logging.info(f"Successfully loaded emission yield file(s) {filepaths}")
        return df

    def load_emission_angle_distribution(self, *args) -> Any:
        """Load an emission angle file."""
        raise NotImplementedError

    def load_emission_energy_distribution(
        self,
        *filepaths: DataPath,
        population: ImplementedPop | None = None,
        sep: str | None = None,
        comment: str | None = None,
        **kwargs,
    ) -> dict[DataPath, tuple[pd.DataFrame, float | None]]:
        """Load and format the given emission energy files.

        It is expected that all files are associated to the same
        ``population``, but were measured at different |PE| energy.

        ``CSV`` files can have comments at the start of the file, starting with
        a ``#`` character. It is expected that the energy of |PEs| used for the
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

        Files in the :file:`data/example_ag/emission_energy` folder are
        correctly formatted.

        .. todo::
           Find a more robust way to handle energy of PEs. Some distributions
           do not need it.

        Parameters
        ----------
        filepaths :
            Path to files holding data under study, corresponding to several
            |PE| energies.
        population :
            Unused by this loader.
        sep :
            Column delimiter.
        comment :
            Comment character.
        kwargs :
            Unused by this loader.

        Returns
        -------
            For every filepath:

            - A pandas dataframe holding the data. Has a ``Energy [eV]`` column
              holding emitted electrons energy. And one or several columns
              ``theta [deg]``, where ``theta`` is the value of the incidence
              angle and content is corresponding emission energy distribution.
            - Energy of |PEs| in :unit:`eV`. If not found in the file comments,
              it will be inferred from the position of the |EBEs| peak.

        """
        if len(filepaths) == 0:
            raise ValueError("Cannot load, no file provided.")

        if sep is None:
            sep = self.sep
        if comment is None:
            comment = self.comment

        return {
            fp: self._load_single_emission_energy_distribution(
                fp, sep=sep, comment=comment
            )
            for fp in filepaths
        }

    def _load_single_emission_energy_distribution(
        self,
        filepath: DataPath,
        sep: str,
        comment: str,
        population: ImplementedPop | None = None,
    ) -> tuple[pd.DataFrame, float | None]:
        """Load and format a single emission energy distribution file.

        Parameters
        ----------
        filepath :
            Path to the file holding data under study.
        sep :
            Column delimiter.
        comment :
            Comment character.
        population :
            Unused.

        Returns
        -------
        pd.DataFrame
            Structure holding the data. Has a ``Energy [eV]`` column
            holding emitted electrons energy. And one or several columns
            ``theta [deg]``, where ``theta`` is the value of the incidence
            angle and content is corresponding emission energy distribution.
        float | None
            Energy of |PEs| in :unit:`eV`, or ``None`` if not found in the file
            comments.

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
            f"Successfully loaded emission energy distribution file(s) {filepath}"
        )
        return df, e_pe

    def export_emission_yield(
        self,
        data: pd.DataFrame,
        folder: WritablePath,
        prefix: str = "eemilib",
        *,
        population: ImplementedPop,
        comments: Sequence[str] | None = None,
    ) -> Path:
        """Export emission yield to a file.

        The file is named ``{prefix}_emission_yield_{population}.csv``. If it
        already exists, it is renamed with a ``.bak`` suffix, replacing any
        previous backup.

        Parameters
        ----------
        data :
            Emission yield to export.
        folder :
            Where to write the file. Created if missing.
        prefix :
            Start of the file name.
        population :
            Nature of the exported electrons.
        comments :
            Lines written at the start of the file, after the comment
            character.

        Returns
        -------
            Path to the written file.

        """
        path = Path(folder) / f"{prefix}_emission_yield_{population}.csv"
        self._write(data, path, comments or [])
        return path

    def export_emission_energy_distribution(
        self,
        data: pd.DataFrame,
        folder: WritablePath,
        prefix: str = "eemilib",
        *,
        population: ImplementedPop,
        e_pe: float,
        comments: Sequence[str] | None = None,
    ) -> Path:
        """Export a distribution to a file.

        The file is named
        ``{prefix}_emission_energy_{population}_{e_pe}eV.csv``. The first two
        comment lines hold the |PEs| energy, as expected by
        :meth:`load_emission_energy_distribution`; ``comments`` come next. If
        the file already exists, it is renamed with a ``.bak`` suffix,
        replacing any previous backup.

        Parameters
        ----------
        data :
            Emission energy distribution to export. Must hold the energy
            column and a single data column.
        folder :
            Where to write the file. Created if missing.
        prefix :
            Start of the file name.
        population :
            Nature of the exported electrons.
        e_pe :
            Energy of |PEs| in :unit:`eV`.
        comments :
            Lines written after the |PEs| energy.

        Returns
        -------
            Path to the written file.

        Raises
        ------
        ValueError
            If ``data`` does not have exactly two columns.

        """
        if len(data.columns) != 2:
            raise ValueError(
                "Can only export distributions with two columns (energy and "
                f"one incidence angle), got {list(data.columns)}."
            )
        path = (
            Path(folder)
            / f"{prefix}_emission_energy_{population}_{e_pe:g}eV.csv"
        )
        self._write(
            data,
            path,
            ["PEs energy in eV", str(float(e_pe)), *(comments or [])],
        )
        return path

    def _write(
        self, data: pd.DataFrame, path: Path, comments: Sequence[str]
    ) -> None:
        """Write ``comments`` then ``data``, backing up any existing file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            backup = path.with_name(path.name + ".bak")
            path.replace(backup)
            logging.info(f"{path} already existed, renamed to {backup}.")

        angles = [col for col in data.columns if col != COL_ENERGY]
        header = ["0.0", *(col.removesuffix(" [deg]") for col in angles)]
        with path.open("w", encoding="utf-8", newline="") as file:
            file.writelines(f"{self.comment} {c}\n" for c in comments)
            data[[COL_ENERGY, *angles]].to_csv(
                file,
                header=header,
                index=False,
                sep=self.sep,
                lineterminator="\n",
            )
        logging.info(f"Exported data to {path}.")
