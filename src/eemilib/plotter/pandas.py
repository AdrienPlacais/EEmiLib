"""Define plotter relying on pandas."""

import matplotlib.pyplot as plt
import pandas as pd
from eemilib.plotter.helper import explicit_column_names
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import ImplementedPop, col_energy, md_ylabel
from matplotlib.axes import Axes


class PandasPlotter(Plotter):
    """A :class:`.Plotter` using pandas lib."""

    def __init__(self, *args, gui: bool = False, **kwargs) -> None:
        """Instantiate object.

        Parameters
        ----------
        gui :
            Activates interactive plotting if using GUI.

        """
        if gui:
            plt.ion()
        return super().__init__(*args, gui=gui, **kwargs)

    def plot_emission_yield(
        self,
        df: pd.DataFrame,
        *args,
        axes: Axes | None = None,
        population: ImplementedPop | None = None,
        **kwargs,
    ) -> Axes:
        """Plot :class:`.EmissionYield` data with |dfplot| method.

        Parameters
        ----------
        df :
            Dataframe holding data to plot.
        *args :
            Additional arguments passed to the |dfplot| method.
        axes :
            Axes to re-use if given.
        population :
            Type of population currently plotted. This is used to make the
            plot legends more precise.
        kwargs :
            Additional keyword arguments passed to the |dfplot| method.

        """
        if axes is not None:
            axes.set_prop_cycle(None)
        explicit = explicit_column_names(
            df.columns,
            population=population,
            emission_data_type="Emission Yield",
        )
        updated = df.rename(columns=explicit, inplace=False)
        axes = updated.plot(
            *args,
            x=explicit[col_energy],
            ax=axes,
            ylabel=md_ylabel["Emission Yield"],
            **kwargs,
        )
        assert isinstance(axes, Axes)
        return axes

    def plot_emission_energy_distribution(
        self,
        df: pd.DataFrame,
        *args,
        axes: Axes | None = None,
        population: ImplementedPop | None = None,
        **kwargs,
    ) -> Axes:
        """Plot :class:`.EmissionEnergyDistribution` data with |dfplot| method.

        Parameters
        ----------
        df :
            Dataframe holding data to plot.
        *args :
            Additional arguments passed to the |dfplot| method.
        axes :
            Axes to re-use if given.
        population :
            Type of population currently plotted. This is used to make the
            plot legends more precise.
        kwargs :
            Additional keyword arguments passed to the |dfplot| method.

        """
        if axes is not None:
            axes.set_prop_cycle(None)
        explicit = explicit_column_names(
            df.columns,
            population=population,
            emission_data_type="Emission Energy",
        )
        df.rename(columns=explicit, inplace=True)
        axes = df.plot(
            *args,
            x=explicit[col_energy],
            ax=axes,
            ylabel=md_ylabel["Emission Energy"],
            **kwargs,
        )
        assert isinstance(axes, Axes)
        return axes

    def plot_emission_angle_distribution(
        self,
        df: pd.DataFrame,
        *args,
        axes: Axes | None = None,
        population: ImplementedPop | None = None,
        **kwargs,
    ) -> Axes:
        """Plot the given emission angles distribution, return Axes object."""
        raise NotImplementedError(
            "Plotting emission angle distribution not implemented yet."
        )
