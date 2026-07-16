"""Define the ABC :class:`Plotter` to produce the plots."""

from abc import ABC, abstractmethod

import pandas as pd
from eemilib.util.constants import ImplementedPop
from eemilib.util.helper import documentation_url

DEFAULT_POPULATIONS_STYLES: dict[ImplementedPop, dict[str, str | float]] = {
    "all": {"ls": "-"},
    "SE": {"ls": "--"},
    "EBE": {"ls": "-."},
    "IBE": {"ls": ":"},
}
DEFAULT_IS_MODEL_STYLES: dict[bool, dict[str, str | float]] = {
    False: {"marker": "+", "lw": 0.5},
    True: {"marker": ""},
}


class Plotter(ABC):
    """A generic object to plot distributions, emission yields, etc."""

    #: Determine plot styles according to population nature.
    population_styles: dict[ImplementedPop, dict[str, str | float]] = (
        DEFAULT_POPULATIONS_STYLES
    )
    #: Determine plot styles according to whether data is modelled or measured.
    is_model_styles: dict[bool, dict[str, str | float]] = (
        DEFAULT_IS_MODEL_STYLES
    )

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
        is_model: bool = True,
        **kwargs,
    ) -> T:
        """Plot emission yield data."""

    @abstractmethod
    def plot_emission_energy_distribution[T](
        self,
        df: pd.DataFrame,
        axes: T | None = None,
        population: ImplementedPop | None = None,
        is_model: bool = True,
        e_pe: float | None = None,
        **kwargs,
    ) -> T:
        """Plot the given emission energy distribution, return Axes object."""

    @abstractmethod
    def plot_emission_angle_distribution[T](
        self,
        df: pd.DataFrame,
        axes: T | None = None,
        population: ImplementedPop | None = None,
        is_model: bool = True,
        **kwargs,
    ) -> T:
        """Plot the given emission angles distribution, return Axes object."""
