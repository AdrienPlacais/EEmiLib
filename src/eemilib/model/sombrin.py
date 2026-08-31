"""Create the Sombrin model, to compute |TEEY|.

It is very precise on the first crossover energy, but does not take the
incident angle into account.

"""

import math
from typing import Any, ClassVar, TypedDict, cast

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from eemilib.core.model_config import ModelConfig
from eemilib.emission_data import DataMatrix
from eemilib.model.model import Model
from eemilib.model.parameter import Parameter
from eemilib.util.constants import (
    COL_ENERGY,
    ImplementedEmissionData,
    ImplementedPop,
)
from eemilib.util.exceptions import MissingDataError
from eemilib.util.markdown import E_MAX, EC_1, SIGMA_MAX


class SombrinParameters(TypedDict):
    """Parameters for :class:`.Sombrin`."""

    E_max: Parameter
    teey_max: Parameter
    E_c1: Parameter


class Sombrin(Model):
    """Define the Sombrin model, defined in :cite:`Sombrin1993`.

    We use the implementation from :cite:`Fil2016a`.

    """

    data_types = ("Emission Yield",)
    populations = ("all",)
    considers_energy = True
    is_3d = False
    is_dielectrics_compatible = False
    model_config = ModelConfig(
        emission_yields=("all",), emission_energies=(), emission_angles=()
    )
    initial_parameters: ClassVar[dict[str, dict[str, str | float | bool]]] = {
        "E_max": {
            "markdown": E_MAX,
            "unit": "eV",
            "value": 1.0,
            "lower_bound": 0.0,
            "description": "Energy at maximum TEEY.",
        },
        "teey_max": {
            "markdown": SIGMA_MAX,
            "unit": "1",
            "value": 0.0,
            "lower_bound": 0.0,
            "description": "Maximum TEEY, directly taken from the measurement.",
        },
        "E_c1": {
            "markdown": EC_1,
            "unit": "eV",
            "value": 0.0,
            "lower_bound": 0.0,
            "description": "First crossover energy.",
        },
    }
    _url_doc_override = "manual/models/sombrin"

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
        super().__init__(parameters_values)
        self.parameters = cast(SombrinParameters, self.parameters)
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

    def compute_data(
        self,
        data_type: ImplementedEmissionData,
        population: ImplementedPop,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        *args,
        **kwargs,
    ) -> pd.DataFrame | None:
        """Return desired data according to current model.

        Will return a dataframe only if the |TEEY| is asked.

        """
        if population != "all" or data_type != "Emission Yield":
            return super().compute_data(
                data_type, population, energy, theta, *args, **kwargs
            )
        out = np.zeros(len(energy))
        for i, ene in enumerate(energy):
            out[i] = sombrin_func(
                ene,
                E_max=self.parameters["E_max"],
                teey_max=self.parameters["teey_max"],
                E_c1=self.parameters["E_c1"],
                E_param=self.E,
            )

        out_dict = {
            COL_ENERGY: energy,
            **{f"{the} [deg]": out for the in theta},
        }
        return pd.DataFrame(out_dict)

    def set_parameter_value(self, name: str, value: Any) -> None:
        """Set ``E`` to None before updating the parameter."""
        if self._E is not None:
            self._E = None
        return super().set_parameter_value(name, value)

    def find_optimal_parameters(
        self, data_matrix: DataMatrix | None = None, **kwargs
    ) -> None:
        """Extract main |TEEY| curve parameters from measurements.

        This method does not involve optimization, it simply takes the
        crossover and maximum |TEEY| positions.

        """
        data_matrix = self._resolve_data_matrix(data_matrix)
        if not data_matrix.holds_required_data(self.model_config):
            raise MissingDataError("Files are not all provided.")

        teey = data_matrix.teey
        self.set_parameters_values(
            {"E_max": teey.e_max, "teey_max": teey.ey_max, "E_c1": teey.e_c1}
        )

    def evaluate(self, data_matrix: DataMatrix) -> dict[str, float]:
        """Evaluate the quality of the model using Fil criterions.

        Fil criterions :cite:`Fil2016a,Fil2020` are adapted to |TEEY| models.

        """
        return self._evaluate_for_teey_models(data_matrix)


def sombrin_func(
    ene: float | NDArray[np.float64],
    E_max: Parameter | float,
    teey_max: Parameter | float,
    E_c1: Parameter | float,
    E_param: float | None,
    **parameters,
) -> float | NDArray[np.float64]:
    """Compute the |TEEY| for incident energy E."""
    if E_param is None:
        E_param = _e_parameter(teey_max, E_max, E_c1)
    num = 2 * teey_max * (ene / E_max) ** E_param
    denom = 1 + (ene / E_max) ** (2 * E_param)
    return num / denom


def _e_parameter(
    sigma_max: Parameter | float,
    E_max: Parameter | float,
    E_c1: Parameter | float,
) -> float:
    """Compute parameter ``E`` in Sombrin model."""
    E_param = math.log(sigma_max - math.sqrt(sigma_max**2 - 1)) / math.log(
        E_c1 / E_max
    )
    return E_param


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += Sombrin._generate_parameter_docs()
