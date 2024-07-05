"""Define plotter relying on pandas."""

from typing import Any

import numpy as np
from matplotlib.axes import Axes

from eemilib.emission_data.emission_yield import EmissionYield
from eemilib.model.model import Model
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import EY_col_energy


class PandasPlotter(Plotter):
    """A :class:`.Plotter` using pandas lib."""

    def plot_emission_yield_data(
        self, emission_yield: EmissionYield, axes: Axes | None = None, **kwargs
    ) -> Axes:
        """Plot :class:`.EmissionYield` data."""
        axes = emission_yield.data.plot(
            x=EY_col_energy,
            ax=axes,
            grid=True,
            ylabel=emission_yield.label,
            **kwargs,
        )
        return axes

    def plot_emission_yield_model(
        self,
        model: Model,
        energies: np.ndarray,
        angles: np.ndarray,
        axes: Axes | None = None,
        **kwargs,
    ) -> Axes:
        """Plot the given emission yield, return Axes object."""
        if axes is not None:
            axes.set_prop_cycle(None)
        to_plot = model.teey(energies, angles)
        to_plot.plot(x=EY_col_energy, ax=axes, ls="--", grid=True, **kwargs)

    def plot_emission_energy_distribution(
        self, emission_energies: Any, distributions: Any, **kwargs
    ) -> object:
        """Plot the given emission energy distribution, return Axes object."""
        raise NotImplementedError

    def plot_emission_angle_distribution(
        self, emission_angles: Any, distributions: Any, **kwargs
    ) -> object:
        """Plot the given emission angles distribution, return Axes object."""
        raise NotImplementedError
