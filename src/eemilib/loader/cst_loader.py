"""Define a loader for files exported from CST Particle Studio.

Check the documentation of :meth:`.CSTLoader.load_emission_yield` and
:meth:`.CSTLoader.load_emission_energy_distribution` for expected file
formats.

"""

import re
from typing import Any

import pandas as pd
from eemilib.loader.helper import read_text
from eemilib.loader.loader import DataPath, Loader
from eemilib.util.constants import ImplementedPop, col_energy

#: Maps the population name used in CST exports to the project's own
#: population identifiers.
_CST_POPULATION_TO_IMPLEMENTED: dict[str, ImplementedPop] = {
    "Elastic": "EBE",
    "Rediff": "IBE",
    "True": "SE",
    "Total": "all",
}

#: Matches a CST block header, e.g. ``"Incident Energy @ Incident Angle 0° /
#: eV"	"Elastic [Real]"``. Captures the incidence angle.
_ANGLE_RE = re.compile(r"Angle\s+([\d.]+)\s*°")
#: Captures the population name, e.g. ``"Elastic"`` from ``"Elastic [Real]"``.
_POPULATION_RE = re.compile(r'"(\w+)\s*\[')


class CSTLoader(Loader):
    """Load files exported from CST Particle Studio."""

    def __init__(self, sep: str = "\t", comment: str = "#") -> None:
        """Instantiate the object."""
        super().__init__()
        self.sep = sep
        self.comment = comment

    def _parse_blocks(
        self,
        filepath: DataPath,
        sep: str | None = None,
        comment: str | None = None,
    ) -> dict[str, pd.DataFrame]:
        r"""Parse a CST file into one DataFrame per raw population name.

        ``TSV`` files hold several blocks, one per population. Each block
        starts with a bare comment line, followed by a comment line holding
        the incidence angle and population name, followed by a comment
        separator line, followed by the data itself (two tab-separated
        columns, no header). Example:

        .. code-block::

            #
            #"Incident Energy @ Incident Angle 0° / eV"\t"Elastic [Real]"
            #-----------------------------------------------------------
            0.0\t0.5
            1.0\t0.49249401688576
            #
            #"Incident Energy @ Incident Angle 0° / eV"\t"Rediff [Real]"
            #----------------------------------------------------------
            0.0\t0.0
            1.0\t0.018270665779710

        Only one incidence angle per file is expected.

        Parameters
        ----------
        filepath :
            Path to file holding data under study.
        sep :
            Column delimiter.
        comment :
            Comment character.

        Return
        ------
            Dict mapping the raw CST population name (e.g. ``"Elastic"``) to
            a two-column DataFrame (``"x"``, ``"y"``).

        """
        if sep is None:
            sep = self.sep
        if comment is None:
            comment = self.comment

        lines = read_text(filepath)

        blocks: dict[str, pd.DataFrame] = {}
        current_name: str | None = None
        current_rows: list[tuple[float, float]] = []

        def _flush() -> None:
            if current_name is None:
                return
            blocks[current_name] = pd.DataFrame(
                current_rows, columns=["x", "y"]
            )

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith(comment):
                population_match = _POPULATION_RE.search(stripped)
                if population_match is not None:
                    _flush()
                    current_name = population_match.group(1)
                    current_rows = []
                continue

            if current_name is None:
                continue
            x_str, y_str = stripped.split(sep)
            current_rows.append((float(x_str), float(y_str)))

        _flush()
        return blocks

    def _angle(self, filepath: DataPath, comment: str | None = None) -> float:
        """Extract the (single) incidence angle from a CST file.

        Parameters
        ----------
        filepath :
            Path to file holding data under study.
        comment :
            Comment character.

        Return
        ------
            Incidence angle in :unit:`deg`.

        """
        if comment is None:
            comment = self.comment
        for line in read_text(filepath):
            stripped = line.strip()
            if not stripped.startswith(comment):
                continue
            angle_match = _ANGLE_RE.search(stripped)
            if angle_match is not None:
                return float(angle_match.group(1))
        raise RuntimeError(f"Could not find incidence angle in {filepath}.")

    def load_emission_yields(
        self,
        *filepaths: DataPath,
        sep: str | None = None,
        comment: str | None = None,
    ) -> dict[ImplementedPop, pd.DataFrame]:
        """Load and format every population from a CST emission yield file.

        See :meth:`_parse_blocks` for the expected file format.

        Parameters
        ----------
        filepaths :
            Path to files holding data under study.
        sep :
            Column delimiter.
        comment :
            Comment character.

        Return
        ------
            Dict mapping each population found in the file to a DataFrame
            with a ``"Energy [eV]"`` column (|PEs| impact energy) and one
            ``"{theta} [deg]"`` column.

        """
        if len(filepaths) != 1:
            raise NotImplementedError("Can only load exactly one file.")
        filepath = filepaths[0]
        angle = self._angle(filepath, comment=comment)
        blocks = self._parse_blocks(filepath, sep=sep, comment=comment)

        out: dict[ImplementedPop, pd.DataFrame] = {}
        for cst_name, population in _CST_POPULATION_TO_IMPLEMENTED.items():
            if cst_name not in blocks:
                continue
            block = blocks[cst_name]
            out[population] = pd.DataFrame(
                {col_energy: block["x"], f"{angle} [deg]": block["y"]}
            )
        return out

    def load_emission_yield(
        self,
        *filepaths: DataPath,
        population: ImplementedPop,
        sep: str | None = None,
        comment: str | None = None,
    ) -> pd.DataFrame:
        """Load and format one population from a CST emission yield file.

        See :meth:`load_emission_yields` for the expected file format.

        Parameters
        ----------
        filepath :
            Path to files holding data under study.
        population :
            Population to extract from the file.
        sep :
            Column delimiter.
        comment :
            Comment character.

        Return
        ------
            DataFrame with a ``"Energy [eV]"`` column (|PEs| impact energy)
            and one ``"{theta} [deg]"`` column, for the requested population.

        """
        if len(filepaths) != 1:
            raise NotImplementedError("Can only load exactly one file.")
        filepath = filepaths[0]
        return self.load_emission_yields(filepath, sep=sep, comment=comment)[
            population
        ]

    def load_emission_angle_distribution(self, *args) -> Any:
        raise NotImplementedError

    def load_emission_energy_distributions(
        self,
        filepath: DataPath,
        sep: str | None = None,
        comment: str | None = None,
    ) -> dict[ImplementedPop, tuple[pd.DataFrame, float]]:
        """Load every population from a single CST emission energy file.

        Loads only **one** file corresponding to **one** |PE| energy.

        See :meth:`_parse_blocks` for the expected file format. The energy of
        |PEs| is taken to be the last emission energy present in the file.

        Parameters
        ----------
        filepath :
            Path to file holding data under study.
        sep :
            Column delimiter.
        comment :
            Comment character.

        Return
        ------
            Dict mapping each population found in the file to a tuple of a
            DataFrame (``"Energy [eV]"`` column holding emission energy, and
            one ``"{theta} [deg]"`` column) and the |PE| energy in
            :unit:`eV`.

        """
        angle = self._angle(filepath, comment=comment)
        blocks = self._parse_blocks(filepath, sep=sep, comment=comment)

        out: dict[ImplementedPop, tuple[pd.DataFrame, float]] = {}
        for cst_name, population in _CST_POPULATION_TO_IMPLEMENTED.items():
            if cst_name not in blocks:
                continue
            block = blocks[cst_name]
            e_pe = float(block["x"].iloc[-1])
            df = pd.DataFrame(
                {col_energy: block["x"], f"{angle} [deg]": block["y"]}
            )
            out[population] = (df, e_pe)
        return out

    def load_emission_energy_distribution(
        self,
        *filepaths: DataPath,
        population: ImplementedPop | None = None,
        sep: str | None = None,
        comment: str | None = None,
        **kwargs,
    ) -> dict[DataPath, tuple[pd.DataFrame, float | None]]:
        """Load the given electron emission energy distribution files.

        .. note::
           All populations are stored in the same file, so you need to precise
           which population you want to load.

        See :meth:`load_emission_energy_distributions` for the expected file
        format.

        Parameters
        ----------
        filepaths :
            Path to files holding data under study, corresponding to several
            |PE| energies.
        population :
            Population to extract from the file. If ``None``, a ``ValueError``
            is raised.
        sep :
            Column delimiter.
        comment :
            Comment character.

        Returns
        -------
            For every filepath:

            - A pandas dataframe holding the data. Has a ``Energy [eV]`` column
              holding emitted electrons energy. And one or several columns
              ``theta [deg]``, where ``theta`` is the value of the incidence
              angle and content is corresponding emission energy distribution.
            - Energy of Primary Electrons in :unit:`eV`. If not found in the
              file comments, it will be inferred from the position of the
              |EBEs| peak.


        """
        if population is None:
            raise ValueError("population arg must be given")
        return {
            fp: self.load_emission_energy_distributions(
                fp, sep=sep, comment=comment
            )[population]
            for fp in filepaths
        }


if __name__ == "__main__":
    from eemilib.data.fp_stainless_steel import (
        cst_emission_yields,
        cst_energy_distributions,
    )

    loader = CSTLoader()

    print("=== Emission yields ===")
    yields = loader.load_emission_yields(cst_emission_yields)
    for population, df in yields.items():
        print(f"--- {population} ---")
        print(df.head())

    print("\n=== Emission energy distributions ===")
    energy_dists = loader.load_emission_energy_distributions(
        cst_energy_distributions
    )
    for population, (df, e_pe) in energy_dists.items():
        print(f"--- {population} (E_PE = {e_pe} eV) ---")
        print(df.head())
