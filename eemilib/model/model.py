"""Define the base class for all electron emission models."""

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from eemilib.model.model_config import ModelConfig
from eemilib.model.parameter import Parameter


class Model(ABC):
    """Define the base electron emission model."""

    considers_energy: bool
    is_3d: bool
    is_dielectrics_compatible: bool
    model_config: ModelConfig

    def __init__(self) -> None:
        """Instantiate the object."""
        self.parameters: dict[str, Parameter]

    def teey(
        self, energy: np.ndarray, theta: np.ndarray, *args, **kwargs
    ) -> pd.DataFrame:
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


def _default_ey(energy: np.ndarray, theta: np.ndarray) -> pd.DataFrame:
    """Return a null array with proper shape."""
    n_energy = len(energy)
    n_theta = len(theta)
    out = np.zeros((n_energy, n_theta))
    out_dict = {f"{the} [deg]": out[:, j] for the, j in enumerate(theta)}
    out_dict["Energy [eV]"] = energy
    return pd.DataFrame(out_dict)
