"""Create the Vaughan model, to compute TEEY.

.. todo::
    Make this robust. Especially the _vaughan_func.

.. todo::
    Clarify the Vaughan shade. Traditional? SPARK3D? CST?

"""

import math

import numpy as np
import pandas as pd
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.emission_data.emission_yield import EmissionYield
from eemilib.model.model_config import ModelConfig
from eemilib.model.parameter import Parameter

from eemilib.model.model import Model


class Vaughan(Model):
    """Define the classic Vaughan model."""

    considers_energy = True
    is_3d = True
    is_dielectrics_compatible = False
    model_config = ModelConfig(
        emission_yield_files=("all",),
        emission_energy_files=(),
        emission_angle_files=(),
    )

    def __init__(self) -> None:
        """Instantiate the object.

        .. todo::
            Replace the E_0p by a delta_transition=1eV or something.

        """
        super().__init__()
        self.parameters = {
            "E_0": Parameter(
                r"E_0", "eV", 12.5, description="Threshold energy."
            ),
            "E_0p": Parameter(
                r"E_0_p", "eV", 11.5, description="To smoothen transition."
            ),
            "E_max": Parameter(r"E_{max}", "eV", 0.0, lower_bound=0.0),
            "teey_low": Parameter(
                r"\sigma_{low}",
                "1",
                0.5,
                lower_bound=0.0,
                description="TEEY below E_0.",
                is_locked=True,
            ),
            "teey_max": Parameter(r"\sigma_{max}", "1", 0.0, lower_bound=0.0),
            "k_se": Parameter(
                r"k_{se}",
                "1",
                1.0,
                lower_bound=0.0,
                upper_bound=2.0,
                description="Roughness factor.",
            ),
            "k_s": Parameter(
                r"k_s",
                "1",
                1.0,
                lower_bound=0.0,
                upper_bound=2.0,
                description="Roughness factor.",
            ),
        }

    def teey(self, energy: np.ndarray, theta: np.ndarray) -> pd.DataFrame:
        r"""Compute TEEY :math:`\sigma`.

        .. todo::
            This method could be so much simpler and efficient.

        """
        out = np.zeros((len(energy), len(theta)))
        for i, ene in enumerate(energy):
            for j, the in enumerate(theta):
                out[i, j] = _vaughan_func(ene, the, **self.parameters)

        out_dict = {f"{the} [deg]": out[:, j] for j, the in enumerate(theta)}
        out_dict["Energy [eV]"] = energy
        return pd.DataFrame(out_dict)

    def find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        """Match with position of first crossover and maximum."""
        data_matrix.assert_has_all_mandatory_files(self.model_config)

        # Could be more compact
        emission_yield = data_matrix.data_matrix[3][0]
        assert isinstance(emission_yield, EmissionYield)
        assert emission_yield.population == "all"

        self.parameters["E_max"].value = emission_yield.e_max
        self.parameters["teey_max"].value = emission_yield.ey_max


def _vaughan_func(
    ene: float,
    the: float,
    E_0: Parameter,
    E_max: Parameter,
    teey_max: Parameter,
    teey_low: Parameter,
    k_se: Parameter,
    k_s: Parameter,
    **parameters,
) -> float | np.ndarray:
    """Compute the TEEY for incident energy E."""
    mod_e_max = E_max.value * (
        1.0 + k_se.value * math.radians(the) ** 2 / (2.0 * math.pi)
    )
    mod_teey_max = teey_max.value * (
        1.0 + k_s.value * math.radians(the) ** 2 / (2.0 * math.pi)
    )
    if ene < E_0.value:
        return teey_low.value

    xi = (ene - E_0.value) / (mod_e_max - E_0.value)

    if xi <= 1.0:
        k = 0.56
    elif xi <= 3.6:
        k = 0.25
    else:
        return mod_teey_max * 1.125 / (xi**0.35)

    return mod_teey_max * (xi * np.exp(1.0 - xi)) ** k
