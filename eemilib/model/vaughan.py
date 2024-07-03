"""Create the Vaughan model, to compute TEEY."""

import numpy as np

from eemilib.model.model import Model
from eemilib.model.parameter import Parameter


class Vaughan(Model):
    """Define the classic Vaughan model."""

    considers_energy = True
    is_3d = True
    is_dielectrics_compatible = False

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
                r"E_0", "eV", 11.5, description="To smoothen transition."
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

    def teey(self, energy: np.ndarray, theta: np.ndarray) -> np.ndarray:
        r"""Compute TEEY :math:`\sigma`."""
        return super().teey(energy, theta)

    def find_optimal_parameters(self) -> None:
        """Match with position of first crossover and maximum. """
        return super().find_optimal_parameters()
