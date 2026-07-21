"""Create the Chung and Everhart model, to compute |SEs| emission distribution.

You will need to provide emission energy distribution measurements.

.. todo::
    Let usr choose from GUI if we should fit on SEs or all.

"""

from typing import Any, Literal, TypedDict, cast

import numpy as np
import pandas as pd
from eemilib.core.model_config import ModelConfig
from eemilib.emission_data.data_matrix import DataMatrix, MissingDataError
from eemilib.model.model import Model
from eemilib.model.parameter import Parameter
from eemilib.util.constants import (
    ImplementedEmissionData,
    ImplementedPop,
    col_energy,
    col_normal,
)
from eemilib.util.markdown import NORM, W_F
from numpy.typing import NDArray
from scipy.optimize import Bounds, least_squares


class ChungEverhartParameters(TypedDict):
    W_f: Parameter
    norm: Parameter


class ChungEverhart(Model):
    """Chung and Everhart model, defined in :cite:`Chung1974`."""

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
            "markdown": W_F,
            "unit": "eV",
            "value": 8.0,
            "lower_bound": 0.0,
            "description": "Material work function.",
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
        self.parameters = cast(
            ChungEverhartParameters,
            {
                name: Parameter(**cast(dict, kwargs))
                for name, kwargs in self.initial_parameters.items()
            },
        )

        self._generate_parameter_docs()
        if parameters_values is not None:
            self.set_parameters_values(parameters_values)

        self._func = chung_everhart_func

    def get_data(
        self,
        population: ImplementedPop,
        emission_data_type: ImplementedEmissionData,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        *args,
        **kwargs,
    ) -> pd.DataFrame | None:
        r"""Return desired data according to current model.

        Will return a dataframe only if the |SEs| energy distribution is asked.

        Parameters
        ----------
        population :
            Type of population you want data from. Only |SEs| are modelled by
            this model.
        emission_data_type :
            Desired type of emission data. Only ``"Emission Energy"`` for this
            model.
        energy :
            Array of |SEs| emission energies in :unit:`eV`. By convention, the
            last element of the array is the impact energy of the |PE|. It is
            not used in this model, allowing unphysical |SEs| with energy
            higher than the |PE|.
        theta :
            Array of |PE| electrons impact angle in :unit:`\degree`. Will be
            ignored, as this model models only normal incidence impact.
        args :
            Other arguments passed to model functions.
        kwargs :
            Other arguments passed to model functions.

        Returns
        -------
            ``None`` if ``population`` is different from ``"SE"`` and
            ``emission_data_type`` is not ``"Emission Energy"``. Otherwise, a
            dataframe where first column ``"Energy [eV]"`` holds emission
            energy, and second column ``"0.0 [deg]"`` the corresponding
            normalized emission energy distribution.

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

        out_dict = {col_energy: energy, col_normal: out}
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
            raise ValueError("Files are not all provided.")

        distributions = data_matrix.get_data(
            population=population, emission_data_type="Emission Energy"
        )
        if not distributions:
            raise MissingDataError(f"Missing emission energy for {population}")

        def _aggregate_residue(w_f: float) -> NDArray[np.float64]:
            """Compute residues on all distributions."""
            return np.concatenate(
                [
                    _residue(
                        w_f,
                        distribution.data[col_energy].to_numpy(),
                        distribution.data[col_normal].to_numpy(),
                    )
                    for distribution in distributions
                ]
            )

        param = self.parameters["W_f"]
        lsq = least_squares(
            fun=_aggregate_residue,
            x0=param.value,
            bounds=Bounds(param.lower_bound, param.upper_bound),
        )
        w_f = lsq.x[0]
        self.set_parameters_values(
            {"W_f": w_f, "norm": _chung_everhart_norm(w_f)}
        )


def _chung_everhart_norm(w_f: float) -> float:
    """Return norm value to have distribution maximum to unity."""
    return 256.0 * w_f**3 / 27.0


def chung_everhart_func(
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
    return chung_everhart_func(ene, w_f) - measured


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += ChungEverhart._generate_parameter_docs()
