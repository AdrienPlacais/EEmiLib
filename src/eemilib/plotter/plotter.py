"""Define the ABC :class:`Plotter` to produce the plots."""

from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import pandas as pd

from eemilib.util.constants import ImplementedEmissionData, ImplementedPop
from eemilib.util.helper import documentation_url

_COLORS_LIST = plt.rcParams["axes.prop_cycle"].by_key()["color"]

#: Maps populations to their plotting style for emission yield plots.
POP_STYLES_EY: dict[ImplementedPop, dict[str, str | float]] = {
    "all": {"ls": "-"},
    "SE": {"ls": "--"},
    "EBE": {"ls": "-."},
    "IBE": {"ls": ":"},
}
#: Maps populations to their plotting style for emission energy plots.
POP_STYLES_EMISSION_ENERGY: dict[ImplementedPop, dict[str, str | float]] = {
    "all": {"ls": "-", "color": _COLORS_LIST[0]},
    "SE": {"ls": "--", "color": _COLORS_LIST[1]},
    "EBE": {"ls": "-.", "color": _COLORS_LIST[2]},
    "IBE": {"ls": ":", "color": _COLORS_LIST[3]},
}


DEFAULT_IS_MODEL_STYLES: dict[bool, dict[str, str | float]] = {
    False: {"marker": "+", "lw": 0},
    True: {"marker": "", "lw": 1.0},
}


class Plotter(ABC):
    """A generic object to plot distributions, emission yields, etc."""

    #: Determine plot styles according to population nature for emission yield
    #: plots.
    pop_styles_ey: dict[ImplementedPop, dict[str, str | float]] = POP_STYLES_EY
    #: Determine plot styles according to population nature for emission
    #: energy plots.
    pop_styles_emission_energy: dict[
        ImplementedPop, dict[str, str | float]
    ] = POP_STYLES_EMISSION_ENERGY
    #: Determine plot styles according to whether data is modelled or measured.
    is_model_styles: dict[bool, dict[str, str | float]] = (
        DEFAULT_IS_MODEL_STYLES
    )

    def __init__(self) -> None:
        """Instantiate the object."""
        self.doc_url = documentation_url(self)

    def plot[T](
        self,
        data_type: ImplementedEmissionData,
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
        if data_type == "Emission Yield":
            meth = self.plot_emission_yield
        elif data_type == "Emission Energy":
            meth = self.plot_emission_energy_distribution
        elif data_type == "Emission Angle":
            meth = self.plot_emission_angle_distribution
        else:
            raise ValueError(
                f"{data_type = } should be in {ImplementedEmissionData}."
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
