"""Define the base object that will store emission data.

.. todo::
    Add an ``interpolate`` or ``resample`` method. Would be used to have more
    points, in particular when there is few points.

"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Self

import pandas as pd

from eemilib.loader.loader import Loader
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import ImplementedPop


class EmissionData(ABC):
    """A yield, energy distribution or angular distribution."""

    def __init__(
        self,
        population: ImplementedPop,
        data: pd.DataFrame,
    ) -> None:
        """Instantiate the data.

        Parameters
        ----------
        population : ImplementedPop
            The concerned population of electrons.
        data : pd.DataFrame
            Structure holding the data. Column headers as well as units must
            follow specications (see subclasses documentation).

        """
        self.population = population
        self.data = data

    @classmethod
    @abstractmethod
    def from_filepath(
        cls,
        population: ImplementedPop,
        loader: Loader,
        *filepath: str | Path,
    ) -> Self:
        """Instantiate the data from files.

        Parameters
        ----------
        loader : Loader
            The object that will load the data.
        population : ImplementedPop
            The concerned population of electrons.
        *filepath : str | Path
            Path(s) to file holding data under study.

        """

    @property
    @abstractmethod
    def label(self) -> str:
        """Print markdown info."""

    @abstractmethod
    def plot[
        T
    ](self, plotter: Plotter, *args, axes: T | None = None, **kwargs) -> T:
        """Plot the contained data using plotter."""
