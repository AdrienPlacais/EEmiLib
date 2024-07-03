"""Define the base class for all electron emission models."""

from abc import ABC, abstractmethod

import numpy as np

from eemilib.model.parameter import Parameter


class Model(ABC):
    """Define the base electron emission model."""

    considers_energy: bool
    is_3d: bool
    is_dielectrics_compatible: bool

    def __init__(self) -> None:
        """Instantiate the object."""
        self.parameters: dict[str, Parameter]

    def teey(
        self, energy: np.ndarray, theta: np.ndarray, *args, **kwargs
    ) -> np.ndarray:
        r"""Compute TEEY :math:`\sigma`."""
        return _default_ey(energy, theta)

    def seey(
        self, energy: np.ndarray, theta: np.ndarray, *args, **kwargs
    ) -> np.ndarray:
        r"""Compute SEEY :math:`\delta`."""
        return _default_ey(energy, theta)

    @abstractmethod
    def find_optimal_parameters(self, *args, **kwargs) -> None:
        """Find the best parameters for the current model."""


def _default_ey(energy: np.ndarray, theta: np.ndarray) -> np.ndarray:
    """Return a null array with proper shape."""
    n_energy = len(energy)
    n_theta = len(theta)
    return np.zeros((n_energy, n_theta))
