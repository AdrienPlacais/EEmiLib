"""Define the ABC :class:`Plotter` to produce the plots."""

from abc import ABC, abstractmethod

import pandas as pd
from eemilib.util.constants import ImplementedPop
from eemilib.util.helper import documentation_url


class Plotter(ABC):
    """A generic object to plot distributions, emission yields, etc."""

    def __init__(self, *args, gui: bool = False, **kwargs) -> None:
        """Instantiate the object.

        Parameters
        ----------
        gui :
            Can be used if using the GUI, eg to activate interactive mode.

        """
        self.doc_url = documentation_url(self)

    @abstractmethod
    def plot_emission_yield[T](
        self,
        df: pd.DataFrame,
        axes: T | None = None,
        population: ImplementedPop | None = None,
        **kwargs,
    ) -> T:
        """Plot emission yield data."""

    @abstractmethod
    def plot_emission_energy_distribution[T](
        self,
        df: pd.DataFrame,
        axes: T | None = None,
        population: ImplementedPop | None = None,
        **kwargs,
    ) -> T:
        """Plot the given emission energy distribution, return Axes object."""

    @abstractmethod
    def plot_emission_angle_distribution[T](
        self,
        df: pd.DataFrame,
        axes: T | None = None,
        population: ImplementedPop | None = None,
        **kwargs,
    ) -> T:
        """Plot the given emission angles distribution, return Axes object."""
