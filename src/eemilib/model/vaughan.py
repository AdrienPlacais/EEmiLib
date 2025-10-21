r"""Create the Vaughan model, to compute TEEY.

TEEY at non-normal incidence will not be taken into account into the fit
(FIXME).

.. todo::
    Make this more robust. Especially the _vaughan_func.

"""

import logging
import math
from typing import Any, Literal, TypedDict

import numpy as np
import pandas as pd
from eemilib.core.model_config import ModelConfig
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.model.model import Model
from eemilib.model.parameter import Parameter
from eemilib.util.constants import ImplementedEmissionData, ImplementedPop
from numpy.typing import NDArray
from scipy.optimize import least_squares

VaughanImplementation = Literal["original", "CST", "SPARK3D"]
E_0_SPARK3D = 10.0


class VaughanParameters(TypedDict):
    E_0: Parameter
    E_max: Parameter
    delta_E_transition: Parameter
    teey_low: Parameter
    teey_max: Parameter
    k_s: Parameter
    k_se: Parameter
    E_c1: Parameter


class Vaughan(Model):
    """Define the classic Vaughan model."""

    emission_data_types = ["Emission Yield"]
    populations = ["all"]
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
            "description": r"Threshold energy. By default, locked to "
            + r":math:`12.5\mathrm{\,eV}`. If unlocked, will be fitted to "
            + r"retrieve :math:`E_{c,\,1}`.",
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
            + " smoothing the transition. Currently not implemented.",
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
        "E_c1": {
            "markdown": r"E_{c,\,1}",
            "unit": "eV",
            "value": 0.0,
            "description": r"First crossover energy. Must be provided instead"
            + " of E_0 for SPARK3D Vaughan.",
            "is_locked": False,
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
        implementation:
            Modifies certain presets to match different interpretations of the
            model by calling :meth:`.preset_implementation`. These parameter
            modifications have precedence over the ones set in
            `parameters_values`.
        parameters_values :
            Contains name of parameters and associated value. If provided, will
            override the default values set in ``initial_parameters``.

        """
        super().__init__(url_doc_override="manual/models/vaughan")
        self.parameters: VaughanParameters = {  # type: ignore
            name: Parameter(**kwargs)  # type: ignore
            for name, kwargs in self.initial_parameters.items()
        }
        self._generate_parameter_docs()
        if parameters_values is not None:
            self.set_parameters_values(parameters_values)
        self._func = _vaughan_func
        self.preset_implementation(implementation)

    def preset_implementation(
        self,
        implementation: VaughanImplementation,
    ) -> None:
        r"""Update some parameters to reproduce a specific implementation.

        Vaughan CST:

            - :math:`\sigma_\mathrm{low}` is set to 0.

        Vaughan SPARK3D:

            - :math:`\sigma_\mathrm{low}` is set to 0.
            - :math:`E_0` is unlocked, so that it will be fitted to match
              :math:`E_{c,\,1}`.
            - Below :math:`10` :unit:`eV`, TEEY is 0.

        """
        if implementation == "original":
            return
        if implementation == "CST":
            self.set_parameter_value("teey_low", 0.0)
            return
        if implementation == "SPARK3D":
            self.set_parameters_values(
                {"teey_low": 0.0, "delta_E_transition": 2.0}
            )
            self.parameters["E_0"].is_locked = False

            E_0 = self._E_0_matching(E_c1=self.parameters["E_c1"].value)
            if np.isnan(E_0):
                return
            self.set_parameter_value("E_0", E_0)
            self._func = _vaughan_spark3d

            return
        logging.error(f"{implementation = } not in {VaughanImplementation}")

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

        .. todo::
            This method could be so much simpler and efficient.

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
        out = np.zeros((len(energy), len(theta)))
        for i, ene in enumerate(energy):
            for j, the in enumerate(theta):
                out[i, j] = self._func(ene, the, **self.parameters)

        out_dict = {f"{the} [deg]": out[:, j] for j, the in enumerate(theta)}
        out_dict["Energy [eV]"] = energy
        return pd.DataFrame(out_dict)

    def find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        """Match with position of first crossover and maximum."""
        if not data_matrix.has_all_mandatory_files(self.model_config):
            logging.info(
                "Files are not all provided. If Ec1 was given, I will try to "
                "find the corresponding E_0."
            )
            self.find_e_0()
            return

        emission_yield = data_matrix.teey
        assert emission_yield.population == "all"

        self.set_parameters_values(
            {
                "E_max": emission_yield.e_max,
                "teey_max": emission_yield.ey_max,
            }
        )
        if not self.parameters["E_c1"].is_locked:
            self.set_parameter_value("E_c1", emission_yield.e_c1)
        if not self.parameters["E_0"].is_locked:
            E_0 = self._E_0_matching(E_c1=self.parameters["E_c1"].value)
            self.set_parameter_value("E_0", E_0)

    def find_e_0(self) -> None:
        """Find E_0 with error handling."""
        e_0 = self.parameters["E_0"]
        assert not e_0.is_locked, "Unlock E_0 to allow for a fit."

        for key in ("E_c1", "E_max", "teey_max"):
            value = self.parameters[key].value
            assert value is not None, f"You must provide a value for {key}"

        E_0 = self._E_0_matching(E_c1=self.parameters["E_c1"].value)
        self.set_parameter_value("E_0", E_0)
        return

    def _E_0_matching(self, *, E_c1: float) -> float:
        """Fit E_0 to retrieve E_c1 (SPARK3D)"""
        parameters = self.parameters.copy()

        def _to_minimize(E_0: float) -> float:
            parameters["E_0"].value = E_0
            teey_at_crossover = _vaughan_func(ene=E_c1, the=0.0, **parameters)
            if isinstance(teey_at_crossover, np.ndarray):
                teey_at_crossover = teey_at_crossover[0]
            return abs(teey_at_crossover - 1.0)

        optimized_E_0 = least_squares(_to_minimize, x0=12.5).x
        return float(optimized_E_0[0])

    def evaluate(self, data_matrix: DataMatrix) -> dict[str, float]:
        """Evaluate the quality of the model using Fil criterions.

        Fil criterions :cite:`Fil2016a,Fil2020` are adapted to TEEY models.

        """
        return self._evaluate_for_teey_models(data_matrix)


def _vaughan_func(
    ene: float,
    the: float,
    E_0: Parameter,
    E_max: Parameter,
    teey_max: Parameter,
    teey_low: Parameter,
    k_se: Parameter,
    k_s: Parameter,
    delta_E_transition: Parameter,
    **parameters,
) -> float | NDArray[np.float64]:
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


def _vaughan_spark3d(
    ene: float,
    the: float,
    E_0: Parameter,
    E_max: Parameter,
    teey_max: Parameter,
    teey_low: Parameter,
    k_se: Parameter,
    k_s: Parameter,
    delta_E_transition: Parameter,
    **parameters,
) -> float | NDArray[np.float64]:
    r"""Compute TEEY as SPARK3D would.

    This is a classic Vaughan, but TEEY is null for energies below
    ``E_0_SPARK3D=10.0``. This parameter is different from the classic ``E_0``
    that appears in the expression of :math:`\xi`.

    """
    if ene >= E_0_SPARK3D:
        return _vaughan_func(
            ene=ene,
            the=the,
            E_0=E_0,
            E_max=E_max,
            teey_max=teey_max,
            teey_low=teey_low,
            k_se=k_se,
            k_s=k_s,
            delta_E_transition=delta_E_transition,
            **parameters,
        )
    return teey_low.value


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += Vaughan._generate_parameter_docs()
