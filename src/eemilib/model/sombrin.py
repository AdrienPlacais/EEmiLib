"""Create the Sombrin model, to compute TEEY.

It is very precise on the first crossover energy, but does not take the
incident angle into account.

"""

import math
from typing import Any, TypedDict

import numpy as np
import pandas as pd
from eemilib.core.model_config import ModelConfig
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.model.model import Model
from eemilib.model.parameter import Parameter
from eemilib.util.constants import (
    ImplementedEmissionData,
    ImplementedPop,
    col_energy,
    col_normal,
)
from numpy.typing import NDArray


class SombrinParameters(TypedDict):
    E_max: Parameter
    teey_max: Parameter
    E_c1: Parameter


class Sombrin(Model):
    """Define the Sombrin model, defined in :cite:`Sombrin1993`.

    We use the implementation from :cite:`Fil2016a`.

    """

    emission_data_types = ["Emission Yield"]
    populations = ["all"]
    considers_energy = True
    is_3d = False
    is_dielectrics_compatible = False
    model_config = ModelConfig(
        emission_yield_files=("all",),
        emission_energy_files=(),
        emission_angle_files=(),
    )
    initial_parameters = {
        "E_max": {
            "markdown": r"E_\mathrm{max}",
            "unit": "eV",
            "value": 1.0,
            "lower_bound": 0.0,
            "description": "Energy at maximum TEEY.",
        },
        "teey_max": {
            "markdown": r"\sigma_\mathrm{max}",
            "unit": "1",
            "value": 0.0,
            "lower_bound": 0.0,
            "description": "Maximum TEEY, directly taken from the measurement.",
        },
        "E_c1": {
            "markdown": r"E_{c,\,1}",
            "unit": "eV",
            "value": 0.0,
            "lower_bound": 0.0,
            "description": (
                "First crossover energy. Must be provided instead of E_0 for "
                "SPARK3D Vaughan."
            ),
        },
    }

    def __init__(
        self, parameters_values: dict[str, Any] | None = None
    ) -> None:
        """Instantiate the object.

        Parameters
        ----------
        parameters_values :
            Contains name of parameters and associated value. If provided, will
            override the default values set in ``initial_parameters``.

        """
        super().__init__(url_doc_override="manual/models/sombrin")
        self.parameters: SombrinParameters = {  # type: ignore
            name: Parameter(**kwargs)  # type: ignore
            for name, kwargs in self.initial_parameters.items()
        }
        self._generate_parameter_docs()
        if parameters_values is not None:
            self.set_parameters_values(parameters_values)

        self._func = _sombrin_func
        self._E: float | None = None

    @property
    def E(self) -> float:
        """Return the ``E`` parameter in Sombrin model. Not incident energy."""
        if self._E is not None:
            return self._E
        self._E = _e_parameter(
            self.parameters["teey_max"],
            self.parameters["E_max"],
            self.parameters["E_c1"],
        )
        return self._E

    def get_data(
        self,
        population: ImplementedPop,
        emission_data_type: ImplementedEmissionData,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        *args,
        **kwargs,
    ) -> pd.DataFrame | None:
        """Return desired data according to current model.

        Will return a dataframe only if the TEEY is asked.

        """
        if population != "all" or emission_data_type != "Emission Yield":
            return super().get_data(
                population=population,
                emission_data_type=emission_data_type,
                energy=energy,
                theta=theta,
                *args,
                **kwargs,
            )
        out = np.zeros(len(energy))
        for i, ene in enumerate(energy):
            out[i] = self._func(
                ene,
                E_max=self.parameters["E_max"],
                teey_max=self.parameters["teey_max"],
                E_c1=self.parameters["E_c1"],
                E_param=self.E,
            )

        out_dict = {col_normal: out, col_energy: energy}
        return pd.DataFrame(out_dict)

    def set_parameter_value(self, name: str, value: Any) -> None:
        """Set ``E`` to None before updating the parameter."""
        if self._E is not None:
            self._E = None
        return super().set_parameter_value(name, value)

    def find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        """Extract main TEEY curve parameters from measure."""
        if not data_matrix.has_all_mandatory_files(self.model_config):
            raise ValueError("Files are not all provided.")

        emission_yield = data_matrix.teey
        assert emission_yield.population == "all"

        self.set_parameters_values(
            {
                "E_max": emission_yield.e_max,
                "teey_max": emission_yield.ey_max,
                "E_c1": emission_yield.e_c1,
            }
        )

    def evaluate(self, data_matrix: DataMatrix) -> dict[str, float]:
        """Evaluate the quality of the model using Fil criterions.

        Fil criterions :cite:`Fil2016a,Fil2020` are adapted to TEEY models.

        """
        return self._evaluate_for_teey_models(data_matrix)


def _sombrin_func(
    ene: float | NDArray[np.float64],
    E_max: Parameter,
    teey_max: Parameter,
    E_c1: Parameter,
    E_param: float | None,
    **parameters,
) -> float | NDArray[np.float64]:
    """Compute the TEEY for incident energy E."""
    if E_param is None:
        E_param = _e_parameter(teey_max, E_max, E_c1)
    num = 2 * teey_max.value * (ene / E_max.value) ** E_param
    denom = 1 + (ene / E_max.value) ** (2 * E_param)
    return num / denom


def _e_parameter(
    sigma_max: Parameter, E_max: Parameter, E_c1: Parameter
) -> float:
    """Compute parameter ``E`` in Sombrin model."""
    E_param = math.log(
        sigma_max.value - math.sqrt(sigma_max.value**2 - 1)
    ) / math.log(E_c1.value / E_max.value)
    return E_param


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += Sombrin._generate_parameter_docs()
