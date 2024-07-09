"""Define the base class for all electron emission models.

.. todo::
    Define all the properties: EBEEY, emission energy distributions, etc.

"""

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.model.model_config import ModelConfig
from eemilib.model.parameter import Parameter


class Model(ABC):
    """Define the base electron emission model.

    Attributes
    ----------
    considers_energy : bool
        Tell if the model has a dependency over PES impact energy.
    is_3d : bool
        Tell if the model has a dependency over PES impact angle.
    is_dielectrics_compatible : bool
        Tell if the model can take the surface-trapped charges into account.
    model_config : ModelConfig
        List the files that the model needs to know in order to work.

    """

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
    ) -> pd.DataFrame:
        r"""Compute SEEY :math:`\delta`."""
        return _default_ey(energy, theta)

    @abstractmethod
    def find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        """Find the best parameters for the current model."""


def _default_ey(energy: np.ndarray, theta: np.ndarray) -> pd.DataFrame:
    """Return a null array with proper shape."""
    n_energy = len(energy)
    n_theta = len(theta)
    out = np.zeros((n_energy, n_theta))
    out_dict = {f"{the} [deg]": out[:, j] for the, j in enumerate(theta)}
    out_dict["Energy [eV]"] = energy
    return pd.DataFrame(out_dict)
