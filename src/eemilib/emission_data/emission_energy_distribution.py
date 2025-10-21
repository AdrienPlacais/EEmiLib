"""Define an object to store an emission energy distribution."""

from pathlib import Path
from typing import Self

import pandas as pd
from eemilib.emission_data.emission_data import EmissionData
from eemilib.loader.loader import Loader
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import (
    ImplementedPop,
    col_energy,
    col_normal,
    md_energy_distrib,
)


class EmissionEnergyDistribution(EmissionData):
    """An emission energy distribution."""

    def __init__(
        self,
        population: ImplementedPop,
        data: pd.DataFrame,
        e_pe: float | None = None,
        norm: float | None = None,
    ) -> None:
        """Instantiate the data.

        Parameters
        ----------
        population :
            The concerned population of electrons.
        data :
            Structure holding the data. Must have a ``Energy (eV)`` column
            holding ``population`` energy. And one or several columns
            ``theta [deg]``, where ``theta`` is the value of the incidence
            angle and content is corresponding emission energy.
        e_pe :
            Energy of primary electrons in :unit:`eV`.
        norm :
            To specify re-normalization constant. If not provided, we try to
            set the maximum of SEs to unity. Provide ``1.0`` to avoid any
            normalization.

        """
        super().__init__(population, data)
        self.energies = data[col_energy].to_numpy()
        self.angles = [
            float(col.split()[0]) for col in data.columns if col != col_energy
        ]

        #: Energy at the maximum of SEs in :unit:`eV`. Defined for SEs and
        #: distribution of all electrons.
        self.e_peak_se: float
        i_peak_se, self.e_peak_se = self._find_SE_peak()
        #: Energy at the maximum of EBEs in :unit:`eV`. Defined for EBEs and
        #: distribution of all electrons.
        self.e_peak_ebe: float
        #: Position of EBE peak.
        self.i_peak_ebe: int
        self.i_peak_ebe, self.e_peak_ebe = self._find_EBE_peak()

        #: Energy of PEs in :unit:`eV`. If this information is not found in
        #: the file header, we set it to the value of ``self.e_peak_ebe``.
        self.e_pe: float
        if e_pe:
            self.e_pe = e_pe
        self.e_pe = e_pe if e_pe else self.e_peak_ebe

        #: Re-normalization factor of distribution.
        self.norm: float = (
            norm if norm else self.data.at[i_peak_se, col_normal]
        )
        self._normalize()

    @classmethod
    def from_filepath(
        cls,
        population: ImplementedPop,
        loader: Loader,
        *filepath: str | Path,
    ) -> Self:
        """Instantiate the data from files.

        Parameters
        ----------
        loader :
            The object that will load the data.
        population :
            The concerned population of electrons.
        *filepath :
            Path(s) to file holding data under study.

        """
        data, e_pe = loader.load_emission_energy_distribution(*filepath)
        return cls(population, data, e_pe=e_pe)

    @property
    def label(self) -> str:
        """Print nature of data (markdown)."""
        return md_energy_distrib[self.population]

    def plot[T](
        self,
        plotter: Plotter,
        *args,
        lw: float | None = 0.0,
        marker: str | None = "+",
        axes: T | None = None,
        grid: bool = True,
        population: ImplementedPop | None = None,
        **kwargs,
    ) -> T:
        """Plot the contained data using plotter.

        This wrapper simply calls the
        :meth:`.Plotter.plot_emission_energy_distribution` method.
        method.

        """
        return plotter.plot_emission_energy_distribution(
            df=self.data,
            *args,
            axes=axes,
            lw=lw,
            marker=marker,
            grid=grid,
            label=self.label,
            population=population,
            **kwargs,
        )

    def _normalize(self) -> None:
        """Normalize the distribution."""
        data_columns = [c for c in self.data.columns if c != col_energy]
        self.data[data_columns] /= self.norm

    @property
    def _se_ebe_limit(self) -> int:
        """Arbitrary index limit between SEs and EBEs."""
        return int(self._n_points / 4)

    def _find_SE_peak(self) -> tuple[int, float]:
        """Find the SEs maximum."""
        i = self.data[: self._se_ebe_limit][col_normal].argmax()
        e_peak_se = self.data.at[i, col_energy]
        return int(i), float(e_peak_se)

    def _find_EBE_peak(self) -> tuple[int, float]:
        """Find the position of the EBE peak."""
        i = (
            self.data[self._se_ebe_limit :][col_normal].argmax()
            + self._se_ebe_limit
        )
        e_peak_ebe = self.data.at[i, col_energy]
        return int(i), float(e_peak_ebe)
