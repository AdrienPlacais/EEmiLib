"""Define the ABC :class:`Plotter` to produce the plots."""

from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from eemilib.emission_data.emission_yield import EmissionYield
from eemilib.model.model import Model


class Plotter(ABC):
    """A generic object to plot distributions, emission yields, etc."""

    @abstractmethod
    def plot_emission_yield_data[
        T
    ](
        self, emission_yield: EmissionYield, axes: T | None = None, **kwargs
    ) -> T:
        """Plot :class:`.EmissionYield` data."""

    @abstractmethod
    def plot_emission_yield_model[
        T
    ](
        self,
        model: Model,
        energies: np.ndarray,
        angles: np.ndarray,
        axes: T | None = None,
        **kwargs,
    ) -> T:
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
