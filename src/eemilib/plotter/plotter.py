"""Define the ABC :class:`Plotter` to produce the plots."""

from abc import ABC, abstractmethod

import pandas as pd


class Plotter(ABC):
    """A generic object to plot distributions, emission yields, etc."""

    @abstractmethod
    def plot_emission_yield[
        T
    ](
        self, emission_yield: pd.DataFrame, axes: T | None = None, **kwargs
    ) -> T:
        """Plot emission yield data."""

    @abstractmethod
    def plot_emission_energy_distribution[
        T
    ](
        self,
        emission_energy: pd.DataFrame,
        axes: T | None = None,
        **kwargs,
    ) -> T:
        """Plot the given emission energy distribution, return Axes object."""

    @abstractmethod
    def plot_emission_angle_distribution[
        T
    ](
        self,
        emission_angles: pd.DataFrame,
        axes: T | None = None,
        **kwargs,
    ) -> T:
        """Plot the given emission angles distribution, return Axes object."""
