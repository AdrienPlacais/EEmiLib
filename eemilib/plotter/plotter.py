"""Define the ABC :class:`Plotter` to produce the plots."""

from abc import ABC, abstractmethod
from typing import Any


class Plotter(ABC):
    """A generic object to plot distributions, emission yields, etc."""

    @abstractmethod
    def plot_emission_yield(
        self, energies: Any, yields: Any, **kwargs
    ) -> object:
        """Plot the given emission yield, return Axes object."""

    @abstractmethod
    def plot_emission_energy_distribution(
        self, emission_energies: Any, distributions: Any, **kwargs
    ) -> object:
        """Plot the given emission energy distribution, return Axes object."""

    @abstractmethod
    def plot_emission_angle_distribution(
        self, emission_angles: Any, distributions: Any, **kwargs
    ) -> object:
        """Plot the given emission angles distribution, return Axes object."""
