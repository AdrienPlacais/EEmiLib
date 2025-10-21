"""Create the Chung and Everhart model, to compute SEs emission distribution.

You will need to provice emission energy distribution measurements.

"""

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
from scipy.optimize import least_squares


class ChungEverhartParameters(TypedDict):
    W_f: Parameter
    norm: Parameter


class ChungEverhart(Model):
    """Define the Chung and Everhart model, defined in :cite:`Chung1974`."""

    emission_data_types = ["Emission Energy"]
    populations = ["SE"]
    considers_energy = True
    is_3d = False
    is_dielectrics_compatible = False
    model_config = ModelConfig(
        emission_yield_files=(),
        emission_energy_files=("all",),
        emission_angle_files=(),
    )
    initial_parameters = {
        "W_f": {
            "markdown": r"W_f",
            "unit": "eV",
            "value": 8.0,
            "lower_bound": 0.0,
            "description": "Material work function.",
        },
        "norm": {
            "markdown": r"k",
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
            override the default values set in ``initial`_parameters``.

        """
        super().__init__(url_doc_override="manual/models/chung_and_everhart")
        self.parameters: ChungEverhartParameters = {  # type: ignore
            name: Parameter(**kwargs)  # type: ignore
            for name, kwargs in self.initial_parameters.items()
        }
        self._generate_parameter_docs()
        if parameters_values is not None:
            self.set_parameters_values(parameters_values)

        self._func = _chung_everhart_func

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

        Will return a dataframe only if the SEs energy distribution is asked.

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
                ene, W_f=self.parameters["W_f"], norm=self.parameters["norm"]
            )

        out_dict = {col_normal: out, col_energy: energy}
        return pd.DataFrame(out_dict)

    def find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        """Fit model parameters on measurements."""
        if not data_matrix.has_all_mandatory_files(self.model_config):
            raise ValueError("Files are not all provided.")

        distribution = data_matrix.all_energy_distribution
        assert distribution.population == "all"

        lsq = least_squares(
            fun=_residue,
            x0=8.0,
            bounds=(0, np.inf),
            args=(
                distribution.data[col_energy].to_numpy(),
                distribution.data[col_normal].to_numpy(),
            ),
        )
        w_f = lsq.x[0]
        self.set_parameters_values(
            {"W_f": w_f, "norm": _chung_everhart_norm(w_f)}
        )


def _chung_everhart_norm(w_f: float) -> float:
    """Return norm value to have distribution maximum to unity."""
    return 256.0 * w_f**3 / 27.0


def _chung_everhart_func(
    ene: float | NDArray[np.float64],
    W_f: Parameter | float,
    norm: Parameter | None = None,
    **parameters,
) -> float | NDArray[np.float64]:
    """Compute the energy distribution."""
    w_f_value = W_f.value if isinstance(W_f, Parameter) else W_f
    norm_value = (
        norm.value if norm is not None else _chung_everhart_norm(w_f_value)
    )
    return norm_value * ene / (ene + w_f_value) ** 4


def _residue(
    w_f: float, ene: NDArray[np.float64], measured: NDArray[np.float64]
) -> NDArray[np.float64]:
    """Compute array of residues between model and measurements."""
    return _chung_everhart_func(ene, w_f) - measured


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += ChungEverhart._generate_parameter_docs()
