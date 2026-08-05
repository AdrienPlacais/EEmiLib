"""Define the base object that will store emission data.

.. todo::
    Add an ``interpolate`` or ``resample`` method. Would be used to have more
    points, in particular when there is few points.

"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from eemilib.loader.loader import Loader
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import COL_ENERGY, COL_NORMAL, ImplementedPop
from eemilib.util.helper import documentation_url


class MissingDataError(ValueError):
    """Error raised when data is missing."""


class EmissionData(ABC):
    """A yield, energy distribution or angular distribution."""

    def __init__(self, population: ImplementedPop, data: pd.DataFrame) -> None:
        """Instantiate the data.

        Parameters
        ----------
        population :
            The concerned population of electrons.
        data :
            Structure holding the data. Column headers as well as units must
            follow specications (see subclasses documentation).

        """
        self.doc_url = documentation_url(self)
        self.population: ImplementedPop = population
        self.data = data
        self._n_points = len(self.data)

        self.energies: NDArray[np.float64] | list[float]
        self.angles: NDArray[np.float64] | list[float]

    @classmethod
    @abstractmethod
    def _from_filepath(
        cls, loader: Loader, *filepath: str | Path, population: ImplementedPop
    ) -> Self:
        """Instantiate the data from files.

        Parameters
        ----------
        loader :
            The object that will load the data.
        *filepath :
            Path(s) to file holding data under study.
        population :
            The concerned population of electrons.

        """

    @property
    @abstractmethod
    def label(self) -> str:
        """Print markdown info."""

    @abstractmethod
    def plot[T](
        self, plotter: Plotter, *args, axes: T | None = None, **kwargs
    ) -> T:
        """Plot the contained data using plotter."""

    @property
    def normal_data(self) -> NDArray[np.float64]:
        """Get data stored in the ``col_normal`` column."""
        return self.data[COL_NORMAL].to_numpy()

    @property
    def _oblique_columns(self) -> list[str]:
        """Get list of columns containing non-normal data."""
        return [
            c for c in self.data.columns if c not in {COL_ENERGY, COL_NORMAL}
        ]

    @property
    def oblique_data(self) -> list[NDArray[np.float64]]:
        return [self.data[x].to_numpy() for x in self._oblique_columns]
