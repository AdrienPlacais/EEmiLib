r"""Create the Vaughan model, to compute TEEY.

TEEY at non-normal incidence will not be taken into account into the fit
(FIXME).

.. todo::
    Make this more robust. Especially the _vaughan_func.

"""

import math
from typing import Any, Literal

import numpy as np
import pandas as pd
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.emission_data.emission_yield import EmissionYield
from eemilib.model.model import Model
from eemilib.model.model_config import ModelConfig
from eemilib.model.parameter import Parameter

VaughanImplementation = Literal["original", "CST", "SPARK3D"]


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
    initial_parameters = {
        "E_0": {
            "markdown": r"E_0",
            "unit": "eV",
            "value": 12.5,
            "description": r"Threshold energy. Can be used to fit  "
            + r":math:`E_{c,\,1}`. By default, locked to "
            + r":math:`12.5\mathrm{\,eV}`.",
            "is_locked": True,
        },
        "E_max": {
            "markdown": r"E_\mathrm{max}",
            "unit": "eV",
            "value": 0.0,
            "lower_bound": 0.0,
            "description": "Energy at maximum TEEY.",
        },
        "delta_E_transition": {
            "markdown": r"\Delta E_{tr}",
            "unit": "eV",
            "value": 1.0,
            "description": "Energy over which we switch from"
            + r" :math:`\sigma_\mathrm{low}` to actual Vaughan TEEY. Useful for"
            + " smoothing the transition.",
            "is_locked": True,
        },
        "teey_low": {
            "markdown": r"\sigma_\mathrm{low}",
            "unit": "1",
            "value": 0.5,
            "lower_bound": 0.0,
            "description": "TEEY below :math:`E_0`.",
            "is_locked": True,
        },
        "teey_max": {
            "markdown": r"\sigma_\mathrm{max}",
            "unit": "1",
            "value": 0.0,
            "lower_bound": 0.0,
            "description": "Maximum TEEY, directly taken from the measurement.",
        },
        "k_s": {
            "markdown": r"k_s",
            "unit": "1",
            "value": 1.0,
            "lower_bound": 0.0,
            "upper_bound": 2.0,
            "description": r"Roughness factor (:math:`\sigma_\mathrm{max}`). "
            + " Locked by default, but could be used for more precise fits.",
            "is_locked": True,
        },
        "k_se": {
            "markdown": r"k_{se}",
            "unit": "1",
            "value": 1.0,
            "lower_bound": 0.0,
            "upper_bound": 2.0,
            "description": r"Roughness factor (:math:`E_\mathrm{max}`). "
            + " Locked by default, but could be used for more precise fits.",
            "is_locked": True,
        },
    }

    def __init__(
        self,
        implementation: VaughanImplementation = "original",
        parameters_values: dict[str, Any] | None = None,
    ) -> None:
        """Instantiate the object.

        .. note::
            Parameter values set by ``implementation`` have priority over
            values given in ``parameters_values``.

        Parameters
        ----------
        implementation: Literal["original", "CST", "SPARK3D"], optional
            Modifies certain presets to match different interpretations of the
            model.
        parameters_values : dict[str, Any] | None, optional
            Contains name of parameters and associated value. If provided, will
            override the default values set in ``initial_parameters``.

        """
        super().__init__(url_doc_override="manual/models/vaughan")
        self.parameters = {
            name: Parameter(**kwargs)  # type: ignore
            for name, kwargs in self.initial_parameters.items()
        }
        self._generate_parameter_docs()
        if parameters_values is not None:
            self.set_parameters_values(parameters_values)
        self._preset_flavour(implementation)

    def _preset_flavour(self, implementation: VaughanImplementation) -> None:
        """Update some parameters to reproduce a specific implementation."""
        if implementation == "original":
            return
        if implementation == "CST":
            self.set_parameter_value("teey_low", 0.0)
            return
        if implementation == "SPARK3D":
            self.set_parameters_values(
                {"teey_low": 0.0, "delta_E_transition": 2.0}
            )
            print(
                f"Warning! In SPARK3D, you do not provide E_0 but first crossover!"
            )
            return
        print(f"Warning! {implementation = } not in {VaughanImplementation}")

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

        emission_yield = data_matrix.data_matrix[3][0]
        assert isinstance(
            emission_yield, EmissionYield
        ), f"Incorrect type for emission_yield: {type(emission_yield)}"
        assert emission_yield.population == "all"

        self.set_parameters_values(
            {"E_max": emission_yield.e_max, "teey_max": emission_yield.ey_max}
        )


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


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += Vaughan._generate_parameter_docs()
