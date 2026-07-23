"""Define the ABC :class:`Plotter` to produce the plots."""

from abc import ABC, abstractmethod

import pandas as pd
from eemilib.util.constants import ImplementedEmissionData, ImplementedPop
from eemilib.util.helper import documentation_url

DEFAULT_POPULATIONS_STYLES: dict[ImplementedPop, dict[str, str | float]] = {
    "all": {"ls": "-"},
    "SE": {"ls": "--"},
    "EBE": {"ls": "-."},
    "IBE": {"ls": ":"},
}
DEFAULT_IS_MODEL_STYLES: dict[bool, dict[str, str | float]] = {
    False: {"marker": "+", "lw": 0},
    True: {"marker": "", "lw": 1.0},
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

    def plot[T](
        self,
        emission_data_type: ImplementedEmissionData,
        df: pd.DataFrame,
        axes: T | None = None,
        population: ImplementedPop | None = None,
        is_model: bool = True,
        **kwargs,
    ) -> T:
        """Call the appropriate plot method.

        See Also
        --------
        :meth:`.plot_emission_yield`
        :meth:`.plot_emission_energy_distribution`
        :meth:`.plot_emission_angle_distribution`

        """
        if emission_data_type == "Emission Yield":
            meth = self.plot_emission_yield
        elif emission_data_type == "Emission Energy":
            meth = self.plot_emission_energy_distribution
        elif emission_data_type == "Emission Angle":
            meth = self.plot_emission_angle_distribution
        else:
            raise ValueError(
                f"{emission_data_type = } should be in {ImplementedEmissionData}."
            )
        return meth(
            df=df,
            axes=axes,
            population=population,
            is_model=is_model,
            **kwargs,
        )

    @abstractmethod
    def plot_emission_yield[T](
        self,
        df: pd.DataFrame,
        axes: T | None = None,
        population: ImplementedPop | None = None,
        is_model: bool = True,
        e_pe: float | None = None,
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
