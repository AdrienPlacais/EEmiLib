"""Create the Chung and Everhart model, to compute SEs emission distribution.

You will need to provice emission energy distribution measurements.

"""

import logging
from typing import Any, TypedDict

import numpy as np
import pandas as pd
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.model.model import Model
from eemilib.model.model_config import ModelConfig
from eemilib.model.parameter import Parameter
from eemilib.util.constants import col_energy, col_normal
from numpy.typing import NDArray


class ChungEverhartParameters(TypedDict):
    W_f: Parameter


class ChungEverhart(Model):
    """Define the Chung and Everhart model, defined in :cite:`Chung1974`."""

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
            "unit": ":unit:`eV`",
            "value": 8.0,
            "lower_bound": 0.0,
            "description": "Material work function.",
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
        self.parameters: ChungEverhartParameters = {  # type: ignore
            name: Parameter(**kwargs)  # type: ignore
            for name, kwargs in self.initial_parameters.items()
        }
        self._generate_parameter_docs()
        if parameters_values is not None:
            self.set_parameters_values(parameters_values)

        self._func = _chung_everhart_func

    def se_energy_distribution(
        self, energy: NDArray[np.float64], *args
    ) -> pd.DataFrame:
        r"""Compute SEs energy distribution."""
        out = np.zeros(len(energy))
        for i, ene in enumerate(energy):
            out[i] = self._func(ene, W_f=self.parameters["W_f"])

        out_dict = {col_normal: out, col_energy: energy}
        return pd.DataFrame(out_dict)

    def find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        """Extract main TEEY curve parameters from measure."""
        if not data_matrix.has_all_mandatory_files(self.model_config):
            raise ValueError("Files are not all provided.")

        distribution = data_matrix.all_energy_distribution
        assert distribution.population == "all"

        logging.error("Setting constant W_f=8eV.")
        self.set_parameters_values({"W_f": 8.0})


def _chung_everhart_func(
    ene: float | NDArray[np.float64],
    W_f: Parameter,
    **parameters,
) -> float | NDArray[np.float64]:
    """Compute the energy distribution for incident energy E."""
    return ene / (ene + W_f.value) ** 4


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += ChungEverhart._generate_parameter_docs()
