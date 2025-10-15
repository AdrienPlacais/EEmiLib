"""Define an object to store an emission energy distribution."""

import logging
from pathlib import Path
from typing import Self

import numpy as np
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
from numpy.typing import NDArray


class EmissionEnergyDistribution(EmissionData):
    """An emission energy distribution."""

    def __init__(
        self,
        population: ImplementedPop,
        data: pd.DataFrame,
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

        """
        super().__init__(population, data)
        self.energies: NDArray[np.float64] = data[col_energy].to_numpy()
        self.angles = [
            float(col.split()[0]) for col in data.columns if col != col_energy
        ]
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
        data = loader.load_emission_energy_distribution(*filepath)
        return cls(population, data)

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
        **kwargs,
    ) -> T:
        """Plot the contained data using plotter."""
        return plotter.plot_emission_energy_distribution(
            emission_energy=self.data,
            *args,
            axes=axes,
            lw=lw,
            marker=marker,
            grid=grid,
            label=self.label,
            **kwargs,
        )

    def _normalize(self) -> None:
        """Normalize the distribution.

        Current implementation will be shite when backscattered peak is higher
        the SEs.

        """
        logging.info(
            "Renormalizing distribution data to have maximum of SEs = 1. "
            "Detection is not clean at all for now, we consider that SEs peak"
            "is the maximum among the 80% first percent of the data array."
        )
        n_points = len(self.data)
        SE_points = int(0.8 * n_points)

        factor = self.data[col_normal][:SE_points].max()

        data_columns = [c for c in self.data.columns if c != col_energy]
        self.data[data_columns] /= factor
