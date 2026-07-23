"""Define plotter relying on pandas."""

import logging
from typing import Any

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
        is_model: bool = True,
        e_pe: float | None = None,
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
            Type of population currently plotted. This is used to set plot
            legends and linestyles.
        is_model :
            Whether data being plotted comes from a model. Used to set plot
            linestyles.
        e_pe :
            Unused for this method.
        kwargs :
            Additional keyword arguments passed to the |dfplot| method.

        """
        if axes is not None:
            axes.set_prop_cycle(None)
        if e_pe is not None:
            logging.warning(
                "You gave `e_pe` argument to the `plot_emission_yield` method,"
                "which does not make any sense. Energy of PEs is given by "
                "`energy` argument."
            )
        explicit = explicit_column_names(
            df.columns,
            population=population,
            emission_data_type="Emission Yield",
            is_model=is_model,
        )
        updated = df.rename(columns=explicit, inplace=False)
        merged_kwargs = self._merge_kwargs(
            population=population, is_model=is_model, kwargs=kwargs
        )

        axes = updated.plot(
            *args,
            x=explicit[col_energy],
            ax=axes,
            ylabel=md_ylabel["Emission Yield"],
            **merged_kwargs,
        )

        assert isinstance(axes, Axes)
        return axes

    def plot_emission_energy_distribution(
        self,
        df: pd.DataFrame,
        *args,
        axes: Axes | None = None,
        population: ImplementedPop | None = None,
        is_model: bool = True,
        e_pe: float | None = None,
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
        is_model :
            Whether data being plotted comes from a model. Used to set plot
            linestyles.
        e_pe :
            Energy of |PEs| in :unit:`eV`.
        kwargs :
            Additional keyword arguments passed to the |dfplot| method.

        """
        if axes is not None:
            axes.set_prop_cycle(None)
        explicit = explicit_column_names(
            df.columns,
            population=population,
            emission_data_type="Emission Energy",
            e_pe=e_pe,
            is_model=is_model,
        )
        updated = df.rename(columns=explicit, inplace=False)
        merged_kwargs = self._merge_kwargs(
            population=population, is_model=is_model, kwargs=kwargs
        )
        axes = updated.plot(
            *args,
            x=explicit[col_energy],
            ax=axes,
            ylabel=md_ylabel["Emission Energy"],
            **merged_kwargs,
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

    def _merge_kwargs(
        self,
        population: ImplementedPop | None,
        is_model: bool,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """Resolve plot kwargs.

        Priority is the following: ``population`` < ``is_model`` < ``kwargs``.

        """
        merged_kwargs = {}
        if population is not None:
            merged_kwargs.update(self.population_styles[population])
        merged_kwargs.update(self.is_model_styles[is_model])
        merged_kwargs.update(kwargs)
        return merged_kwargs
