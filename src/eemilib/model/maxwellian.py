"""Create a Maxwellian distribution, to compute |SEs| emission distribution.

You will need to provide emission energy distribution measurements.

"""

import math
from typing import Any, TypedDict, overload

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
from eemilib.util.markdown import NORM, TEMPERATURE
from numpy.typing import NDArray
from scipy.constants import pi
from scipy.optimize import Bounds, least_squares


class MaxwellianParameters(TypedDict):
    temperature: Parameter
    norm: Parameter


class Maxwellian(Model):
    """Maxwellian distribution."""

    emission_data_types = ["Emission Energy"]
    populations = ["SE"]
    considers_energy = True
    is_3d = False
    is_dielectrics_compatible = False
    model_config = ModelConfig(
        emission_yield_files=(),
        emission_energy_files=("SE",),
        emission_angle_files=(),
    )
    initial_parameters = {
        "temperature": {
            "markdown": TEMPERATURE,
            "unit": "eV",
            "value": 7.5,
            "lower_bound": 0.0,
            "description": "Temperature distribution.",
        },
        "norm": {
            "markdown": NORM,
            "unit": "1",
            "value": 1.0,
            "lower_bound": 0.0,
            "description": "Distribution re-normalization constant.",
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
        super().__init__(url_doc_override="manual/models/chung_and_everhart")
        self.parameters: MaxwellianParameters = MaxwellianParameters(
            **{
                name: Parameter(**kwargs)
                for name, kwargs in self.initial_parameters.items()
            }
        )
        self._generate_parameter_docs()
        if parameters_values is not None:
            self.set_parameters_values(parameters_values)

        self._func = maxwellian_pdf

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

        Will return a dataframe only if the |SEs| energy distribution is asked.

        """
        if population != "SE" or emission_data_type != "Emission Energy":
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
                temperature=self.parameters["temperature"],
                norm=self.parameters["norm"],
            )

        out_dict = {col_normal: out, col_energy: energy}
        return pd.DataFrame(out_dict)

    def find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        """Fit model parameters on measurements."""
        if not data_matrix.has_all_mandatory_files(self.model_config):
            raise ValueError("Files are not all provided.")

        distribution = data_matrix.se_energy_distribution
        assert distribution.population == "SE"

        param = self.parameters["temperature"]

        lsq = least_squares(
            fun=_residue,
            x0=param.value,
            bounds=Bounds(param.lower_bound, param.upper_bound),
            args=(
                distribution.data[col_energy].to_numpy(),
                distribution.data[col_normal].to_numpy(),
            ),
        )
        temp = lsq.x[0]
        self.set_parameters_values(
            {"temperature": temp, "norm": _maxwellian_norm(temp)}
        )


def _maxwellian_norm(temp: float) -> float:
    """Return norm value to have distribution maximum to unity.

    Maximum is at :math:`T/2`.

    """
    return temp * math.sqrt(2 * pi) / (2 * math.exp(-0.5))


@overload
def maxwellian_pdf(
    ene: float,
    temperature: Parameter | float,
    norm: Parameter | None = None,
    **parameters,
) -> float: ...


@overload
def maxwellian_pdf(
    ene: NDArray[np.float64],
    temperature: Parameter | float,
    norm: Parameter | None = None,
    **parameters,
) -> NDArray[np.float64]: ...


def maxwellian_pdf(
    ene: float | NDArray[np.float64],
    temperature: Parameter | float,
    norm: Parameter | None = None,
    **parameters,
) -> float | NDArray[np.float64]:
    """Compute the energy distribution."""
    temp = (
        temperature.value
        if isinstance(temperature, Parameter)
        else temperature
    )
    norm_value = _maxwellian_norm(temp) if not norm else norm.value
    return 2 * norm_value * np.sqrt(ene / (pi * temp**3)) * np.exp(-ene / temp)


def _residue(
    temp: float, ene: NDArray[np.float64], measured: NDArray[np.float64]
) -> NDArray[np.float64]:
    """Compute array of residues between model and measurements."""
    return maxwellian_pdf(ene, temp) - measured


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += Maxwellian._generate_parameter_docs()
