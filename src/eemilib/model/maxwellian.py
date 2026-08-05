"""Create a Maxwellian distribution, to compute |SEs| emission distribution.

You will need to provide emission energy distribution measurements.

"""

import math
from typing import Any, Literal, TypedDict, cast, overload

import numpy as np
import pandas as pd
from eemilib.core.model_config import ModelConfig
from eemilib.emission_data import DataMatrix
from eemilib.emission_data.emission_data import MissingDataError
from eemilib.model.model import Model
from eemilib.model.parameter import Parameter
from eemilib.util.constants import (
    COL_ENERGY,
    COL_NORMAL,
    ImplementedEmissionData,
    ImplementedPop,
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

    data_types = ("Emission Energy",)
    populations = ("SE",)
    considers_energy = True
    is_3d = False
    is_dielectrics_compatible = False
    model_config = ModelConfig(
        emission_yield_files=(),
        emission_energy_files=("all",),
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
        super().__init__(url_doc_override="manual/models/maxwellian")
        self.parameters = cast(
            MaxwellianParameters,
            {
                name: Parameter(**cast(dict, kwargs))
                for name, kwargs in self.initial_parameters.items()
            },
        )
        self._generate_parameter_docs()
        if parameters_values is not None:
            self.set_parameters_values(parameters_values)

        self._func = maxwellian_pdf

    def get_data(
        self,
        population: ImplementedPop,
        data_type: ImplementedEmissionData,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        *args,
        **kwargs,
    ) -> pd.DataFrame | None:
        """Return desired data according to current model.

        Will return a dataframe only if the |SEs| energy distribution is asked.

        """
        if population != "SE" or data_type != "Emission Energy":
            return super().get_data(
                population, data_type, energy, theta, *args, **kwargs
            )
        out = np.zeros(len(energy))
        for i, ene in enumerate(energy):
            out[i] = self._func(
                ene,
                temperature=self.parameters["temperature"],
                norm=self.parameters["norm"],
            )

        out_dict = {COL_ENERGY: energy, COL_NORMAL: out}
        return pd.DataFrame(out_dict)

    def find_optimal_parameters(
        self,
        data_matrix: DataMatrix,
        population: Literal["SE", "all"] = "all",
        **kwargs,
    ) -> None:
        """Fit model parameters on measurements.

        Parameters
        ----------
        data_matrix :
            Object holding measurements.
        population :
            Population on which data should be fitted. Even if the model is
            about |SEs|, we fit on ``"all"`` population by default because in
            general we measure the distribution energy of all electrons.

        """
        if not data_matrix.has_all_mandatory_files(self.model_config):
            raise MissingDataError("Files are not all provided.")

        distributions = data_matrix.get_data("Emission Energy", population)
        if not distributions:
            raise MissingDataError(f"Missing emission energy for {population}")

        def _aggregate_residue(temperature: float) -> NDArray[np.float64]:
            """Compute residues on all distributions."""
            return np.concatenate(
                [
                    _residue(
                        temperature,
                        distribution.data[COL_ENERGY].to_numpy(),
                        distribution.data[COL_NORMAL].to_numpy(),
                    )
                    for distribution in distributions
                ]
            )

        param = self.parameters["temperature"]
        lsq = least_squares(
            fun=_aggregate_residue,
            x0=param,
            bounds=Bounds(param.lower_bound, param.upper_bound),
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
    norm: Parameter | float = 1.0,
    **parameters,
) -> float: ...


@overload
def maxwellian_pdf(
    ene: NDArray[np.float64],
    temperature: Parameter | float,
    norm: Parameter | float = 1.0,
    **parameters,
) -> NDArray[np.float64]: ...


def maxwellian_pdf(
    ene: float | NDArray[np.float64],
    temperature: Parameter | float,
    norm: Parameter | float = 1.0,
    **parameters,
) -> float | NDArray[np.float64]:
    """Compute the energy distribution."""
    return (
        norm
        * np.sqrt(ene**2 / (pi * temperature**3))
        * np.exp(-ene / temperature)
    )


def _residue(
    temp: float, ene: NDArray[np.float64], measured: NDArray[np.float64]
) -> NDArray[np.float64]:
    """Compute array of residues between model and measurements."""
    return maxwellian_pdf(ene, temp) - measured


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += Maxwellian._generate_parameter_docs()
