"""Define plotter relying on pandas."""

import matplotlib.pyplot as plt
import pandas as pd
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import EY_col_energy
from matplotlib.axes import Axes


class PandasPlotter(Plotter):
    """A :class:`.Plotter` using pandas lib."""

    def plot_emission_yield(
        self,
        emission_yield: pd.DataFrame,
        *args,
        axes: Axes | None = None,
        **kwargs,
    ) -> Axes:
        """Plot :class:`.EmissionYield` data."""
        if axes is not None:
            axes.set_prop_cycle(None)
        axes = emission_yield.plot(
            *args,
            x=EY_col_energy,
            ax=axes,
            **kwargs,
        )
        assert isinstance(axes, Axes)
        plt.show()
        return axes

    def plot_emission_energy_distribution(
        self,
        emission_energy: pd.DataFrame,
        *args,
        axes: Axes | None = None,
        **kwargs,
    ) -> Axes:
        """Plot the given emission energy distribution, return Axes object."""
        raise NotImplementedError

    def plot_emission_angle_distribution(
        self,
        emission_angles: pd.DataFrame,
        *args,
        axes: Axes | None = None,
        **kwargs,
    ) -> Axes:
        """Plot the given emission angles distribution, return Axes object."""
        raise NotImplementedError
