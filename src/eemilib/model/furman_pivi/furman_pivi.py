r"""Create the Furman and Pivi model, to compute |SEEY|, |EBEEY|, |IBEEY|.

Also energy emission distributions. Even angular distributions?

This is an empirical model developed by Dionne :cite:`Furman2002,Furman2013`.

.. todo::
   Store the max number of secondaries in the Model, make it editable, like
   from the Implementations section in the GUI.

   .. warning::
      This would influence number of mandatory :math:`\epsilon_i` and
      :math:`p_i` parameters. This is a significant refactor. And it would not
      be very useful -- except for niche use cases... So this is not
      prioritary.

.. todo::
    Warning when |SEEY| exceeds max number of |SEs| :data:`.M_MAX_SECONDARIES`.

"""

import logging
from collections.abc import Callable, Sequence
from functools import partial
from typing import Any, ClassVar, cast

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.optimize import least_squares

from eemilib.core.model_config import ModelConfig
from eemilib.emission_data import DataMatrix
from eemilib.emission_data.emission_data import MissingDataError
from eemilib.emission_data.emission_energy_distribution import (
    AllEmissionEnergyDistribution,
    EmissionEnergyDistribution,
)
from eemilib.emission_data.emission_yield import TEEY
from eemilib.model.furman_pivi.all import (
    ALL_DISTRIB_PARAMETERS,
    NORMAL_TEEY_PARAM_KEYS,
    OBLIQUE_TEEY_PARAM_KEYS,
    all_energy_distribution,
    teey,
    teey_normal,
)
from eemilib.model.furman_pivi.ebe import ebe_energy_distribution, ebeey
from eemilib.model.furman_pivi.helper import add_furman_pivi_notation
from eemilib.model.furman_pivi.ibe import ibe_energy_distribution, ibeey
from eemilib.model.furman_pivi.physics import (
    DISTRIBUTION_T,
    FURMAN_PIVI_DISTRIBUTIONS,
    FURMAN_PIVI_NORMALIZATIONS,
    INITIAL_FURMAN_PIVI_PARAMETERS,
    M_MAX_SECONDARIES,
    NORMALIZATION_T,
    FurmanPiviParameters,
)
from eemilib.model.furman_pivi.se import (
    PROBA_EMIT_N_SE,
    se_energy_distribution,
    seey,
    set_number_of_secondaries_probability_function,
)
from eemilib.model.model import Model
from eemilib.model.parameter import Parameter
from eemilib.util.constants import (
    COL_ENERGY,
    ImplementedEmissionData,
    ImplementedPop,
)

EMISSION_YIELD_FUNCS: dict[ImplementedPop, Callable] = {
    "SE": seey,
    "EBE": ebeey,
    "IBE": ibeey,
    "all": teey,
}


class FurmanPivi(Model):
    """Define the Furman and Pivi model :cite:`Furman2002,Furman2013`."""

    data_types = ("Emission Yield", "Emission Energy")
    populations = ("EBE", "IBE", "SE")
    considers_energy = True
    is_3d = True
    is_dielectrics_compatible = False
    model_config = ModelConfig(
        emission_yield_files=("all",),
        emission_energy_files=("all",),
        emission_angle_files=(),
    )
    initial_parameters: ClassVar[dict[str, dict[str, str | float | bool]]] = (
        INITIAL_FURMAN_PIVI_PARAMETERS
    )
    implementation_choices: ClassVar[dict[str, tuple[str, ...]]] = {
        "distribution": FURMAN_PIVI_DISTRIBUTIONS,
        "normalization": FURMAN_PIVI_NORMALIZATIONS,
    }

    def __init__(
        self,
        distribution: DISTRIBUTION_T = "Poisson",
        normalization: NORMALIZATION_T = "penetrated",
        parameters_values: dict[str, Any] | None = None,
    ) -> None:
        r"""Instantiate the object.

        Parameters
        ----------
        distribution :
            Distribution used for the number of |SEs| emitted per event, *cf*
            Eqs. (37)/(38) in :cite:`Furman2002`. Can be changed later with
            :meth:`set_implementation`.
        normalization :
            Normalization used for the associated probabilities, *cf* Eqs.
            (35) and (43). Can be changed later with
            :meth:`set_implementation`.
        parameters_values :
            Contains name of parameters and associated value. If provided, will
            override the default values set in ``initial_parameters``.

        """
        super().__init__(url_doc_override="manual/models/furman_pivi")

        for parameters_kwargs in self.initial_parameters.values():
            add_furman_pivi_notation(parameters_kwargs)

        self.parameters = cast(
            FurmanPiviParameters,
            {
                name: Parameter(**cast(dict, kwargs))
                for name, kwargs in self.initial_parameters.items()
            },
        )
        for parameter in self.parameters.values():
            parameter.subscribe(self._on_parameter_changed)

        self._generate_parameter_docs()
        if parameters_values is not None:
            self.set_parameters_values(parameters_values)

        self.set_implementation("distribution", distribution)
        self._proba_emit_n_se: PROBA_EMIT_N_SE
        self._normalization: NORMALIZATION_T
        self.set_implementation("normalization", normalization)

    def set_implementation(self, name: str, value: str) -> None:
        r"""Update one implementation axis.

        Parameters
        ----------
        name :
            ``"distribution"`` or ``"normalization"``.
        value :
            For ``"distribution"``: ``"Poisson"`` or ``"Binomial"``, *cf*
            Eqs. (37)/(38). For ``"normalization"``: ``"incident"`` (Eq. 35)
            or ``"penetrated"`` (Eq. 43).

        """
        if name == "distribution":
            self._proba_emit_n_se = (
                set_number_of_secondaries_probability_function(
                    cast(DISTRIBUTION_T, value)
                )
            )
            self.current_implementations["distribution"] = value
            return

        if name == "normalization":
            self._normalization = cast(NORMALIZATION_T, value)
            self.current_implementations["normalization"] = value
            return

        logging.error(f"Unknown implementation axis {name = } for FurmanPivi.")

    @classmethod
    def _generate_parameter_docs(cls) -> str:
        """Generate documentation for the :class:`.Parameter`.

        Override default to add the notation from Furman and Pivi.

        """
        doc_lines = [
            "",
            "Model parameters",
            "================",
            "",
            ".. list-table::",
            "   :widths: 5 10 5 5 65",
            "   :header-rows: 1",
            "",
            "   * - Parameter",
            "     - Name",
            "     - Unit",
            "     - Initial",
            "     - Description",
        ]
        for name, kwargs in cls.initial_parameters.items():
            add_furman_pivi_notation(kwargs)
            doc = [
                f"   * - :math:`{kwargs.get('markdown', '')}`",
                f"     - {name}",
                f"     - :unit:`{kwargs.get('unit', '')}`",
                f"     - :math:`{kwargs.get('value', '')}`",
                f"     - {kwargs.get('description', '')}",
            ]
            doc_lines += doc
        return "\n".join(doc_lines)

    def _get_energy_distribution_data(
        self,
        population: ImplementedPop,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        e_pe: float | None,
    ) -> pd.DataFrame | None:
        """Compute emitted-energy spectrum data for one population."""
        e_0 = e_pe if e_pe is not None else energy[-1]
        p_ns = [
            self.parameters[f"p_{i}"] for i in range(1, M_MAX_SECONDARIES + 1)
        ]
        eps_ns = [
            self.parameters[f"eps_{i}"]
            for i in range(1, M_MAX_SECONDARIES + 1)
        ]
        se_kwargs = {
            "p_ns": p_ns,
            "eps_ns": eps_ns,
            "proba_emit_n_se": self._proba_emit_n_se,
            "normalization": self._normalization,
        }

        dist_funcs: dict[ImplementedPop, Callable] = {
            "EBE": ebe_energy_distribution,
            "IBE": ibe_energy_distribution,
            "SE": partial(se_energy_distribution, **se_kwargs),
            "all": partial(all_energy_distribution, **se_kwargs),
        }
        dist_func = dist_funcs.get(population)
        if dist_func is None:
            return None

        out = np.zeros((len(energy), len(theta)))
        for j, the in enumerate(theta):
            out[:, j] = dist_func(
                e_pe=e_0, the=the, emission_energies=energy, **self.parameters
            )

        out_dict = {
            COL_ENERGY: energy,
            **{f"{the} [deg]": out[:, j] for j, the in enumerate(theta)},
        }
        return pd.DataFrame(out_dict)

    def get_data(
        self,
        population: ImplementedPop,
        data_type: ImplementedEmissionData,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        e_pe: float | None = None,
        *args,
        **kwargs,
    ) -> pd.DataFrame | None:
        r"""Return desired data according to current model.

        Parameters
        ----------
        population :
            Type of electrons to data from.
        data_type :
            Type of data to get.
        energy :
            Energies at which you want data.
        theta :
            Angles at which you want data.
        e_pe :
            Only used when ``data_type == "Emission Energy"``. Impact
            energy :math:`E_0` at which the emitted-energy spectrum is
            evaluated. If not given, defaults to the last value of ``energy``.
        args :
            Other arguments passed to mother method.
        kwargs :
            Other arguments passed to mother method.

        """
        if data_type == "Emission Angle":
            return super().get_data(
                population, data_type, energy, theta, *args, **kwargs
            )

        if data_type == "Emission Energy":
            data = self._get_energy_distribution_data(
                population=population, energy=energy, theta=theta, e_pe=e_pe
            )
            if data is not None:
                return data
            return super().get_data(
                population, data_type, energy, theta, *args, **kwargs
            )

        ey_func = EMISSION_YIELD_FUNCS.get(population)
        if ey_func is None:
            return super().get_data(
                population, data_type, energy, theta, *args, **kwargs
            )
        out = np.zeros((len(energy), len(theta)))
        for i, ene in enumerate(energy):
            for j, the in enumerate(theta):
                out[i, j] = ey_func(ene, the, **self.parameters)

        out_dict = {
            COL_ENERGY: energy,
            **{f"{the} [deg]": out[:, j] for j, the in enumerate(theta)},
        }
        return pd.DataFrame(out_dict)

    def find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        """Fit all Furman and Pivi parameters on measurements.

        Parameters
        ----------
        data_matrix :
            Measurement data to fit. Must contain emission yield and emission
            energy.
        kwargs :
            Unused kwargs.

        """
        if not data_matrix.has_all_mandatory_files(self.model_config):
            raise MissingDataError("Files are not all provided.")

        teeys = data_matrix.get_data("Emission Yield", "all")
        self.find_normal_ey_params(teeys)
        self.find_oblique_ey_params(teeys)

        distribs = data_matrix.get_data("Emission Energy", "all")
        self.find_energy_distribution_parameters(distribs)

    # =========================================================================
    # 1. Find best parameters for emission yield at normal incidence
    # =========================================================================
    def find_normal_ey_params(self, teeys: Sequence[TEEY]) -> None:
        """Orchestrate the find of |TEEY| parameters.

        Parameters
        ----------
        teeys :
            All |TEEY| stored in a :class:`.DataMatrix`. *A priori*, there is
            only one |TEEY| in the list.

        """
        if len(teeys) > 1:
            logging.warning(
                "Method not actually adapted to several TEEY objects"
            )
        for _teey in teeys:
            normal_e_max_se = self.parameters["normal_e_max_se"]
            normal_e_max_se.value = _teey.e_max
            normal_e_max_se.lower_bound = _teey.e_max - 5.0
            normal_e_max_se.upper_bound = _teey.e_max + 5.0

        self._fit_normal_teey(teeys)

    def _fit_normal_teey(self, teeys: Sequence[TEEY]) -> None:
        """Fit |TEEY| parameters."""

        def _aggregate_residue(x: NDArray[np.float64]) -> NDArray[np.float64]:
            kwargs = dict(zip(NORMAL_TEEY_PARAM_KEYS, x))
            residuals = []
            for _teey in teeys:
                measured = _teey.normal_data
                predicted = teey_normal(_teey.energies, **kwargs)
                residuals.append(measured - predicted)
            return np.concatenate(residuals)

        x0 = [self.parameters[key].value for key in NORMAL_TEEY_PARAM_KEYS]
        lower_bounds = [
            self.parameters[key].lower_bound for key in NORMAL_TEEY_PARAM_KEYS
        ]
        upper_bounds = [
            self.parameters[key].upper_bound for key in NORMAL_TEEY_PARAM_KEYS
        ]

        lsq = least_squares(
            fun=_aggregate_residue, x0=x0, bounds=(lower_bounds, upper_bounds)
        )
        fitted = dict(zip(NORMAL_TEEY_PARAM_KEYS, lsq.x))
        self.set_parameters_values(fitted)

    # =========================================================================
    # 2. Find best parameters for emission yield at oblique incidence
    # =========================================================================
    def find_oblique_ey_params(self, teeys: Sequence[TEEY]) -> None:
        """Orchestrate fitting of all oblique emission yields parameters."""
        if len(teeys) > 1:
            logging.warning(
                "Method not actually adapted to several TEEY objects"
            )
        self._fit_oblique_teey(teeys)

    def _fit_oblique_teey(self, teeys: Sequence[TEEY]) -> None:
        r"""Find oblique |TEEY| parameters."""
        extra_kwargs = {
            **{key: self.parameters[key] for key in NORMAL_TEEY_PARAM_KEYS}
        }

        def _aggregate_residue(x: NDArray[np.float64]) -> NDArray[np.float64]:
            kwargs = dict(zip(OBLIQUE_TEEY_PARAM_KEYS, x))
            residuals = []
            for _teey in teeys:
                for theta, measured in zip(
                    _teey.angles[1:], _teey.oblique_data, strict=True
                ):
                    predicted = teey(
                        _teey.energies, theta, **kwargs, **extra_kwargs
                    )
                    residuals.append(measured - predicted)
            return np.concatenate(residuals)

        x0 = [self.parameters[key].value for key in OBLIQUE_TEEY_PARAM_KEYS]
        lower_bounds = [
            self.parameters[key].lower_bound for key in OBLIQUE_TEEY_PARAM_KEYS
        ]
        upper_bounds = [
            self.parameters[key].upper_bound for key in OBLIQUE_TEEY_PARAM_KEYS
        ]

        lsq = least_squares(
            fun=_aggregate_residue, x0=x0, bounds=(lower_bounds, upper_bounds)
        )
        fitted = dict(zip(OBLIQUE_TEEY_PARAM_KEYS, lsq.x))
        self.set_parameters_values(fitted)

    # =========================================================================
    # 3. Find best parameters for emission distribution at normal incidence
    # =========================================================================
    def find_energy_distribution_parameters(
        self, distribs: Sequence[AllEmissionEnergyDistribution]
    ) -> None:
        """Orchestrate fitting of all normal energy distribution parameters."""
        self._fit_energy_distribs(distribs)

    def _fit_energy_distribs(
        self, distribs: Sequence[EmissionEnergyDistribution]
    ) -> None:
        """Fit energy distributions parameters."""
        p_ns = [
            self.parameters[f"p_{i}"] for i in range(1, M_MAX_SECONDARIES + 1)
        ]
        eps_ns = [
            self.parameters[f"eps_{i}"]
            for i in range(1, M_MAX_SECONDARIES + 1)
        ]
        extra_kwargs = {
            **{
                key: self.parameters[key]
                for key in NORMAL_TEEY_PARAM_KEYS + OBLIQUE_TEEY_PARAM_KEYS
            },
            "p_ns": p_ns,
            "eps_ns": eps_ns,
            "proba_emit_n_se": self._proba_emit_n_se,
            "normalization": self._normalization,
        }

        def _aggregate_residue(x: NDArray[np.float64]) -> NDArray[np.float64]:
            kwargs = dict(zip(ALL_DISTRIB_PARAMETERS, x))
            residuals = []
            for distrib in distribs:
                measured = distrib.normal_data
                predicted = all_energy_distribution(
                    e_pe=distrib.e_pe,
                    the=0.0,
                    emission_energies=distrib.energies,
                    halve_ebe_contribution=True,
                    **kwargs,
                    **extra_kwargs,
                )
                residuals.append(measured - predicted)
            return np.concatenate(residuals)

        x0 = [self.parameters[key].value for key in ALL_DISTRIB_PARAMETERS]
        lower_bounds = [
            self.parameters[key].lower_bound for key in ALL_DISTRIB_PARAMETERS
        ]
        upper_bounds = [
            self.parameters[key].upper_bound for key in ALL_DISTRIB_PARAMETERS
        ]

        lsq = least_squares(
            fun=_aggregate_residue, x0=x0, bounds=(lower_bounds, upper_bounds)
        )
        fitted = dict(zip(ALL_DISTRIB_PARAMETERS, lsq.x))
        self.set_parameters_values(fitted)

    # =========================================================================
    # 4. Post
    # =========================================================================
    def evaluate(self, data_matrix: DataMatrix) -> dict[str, float]:
        """Evaluate the quality of the model using Fil criterions.

        Fil criterions :cite:`Fil2016a,Fil2020` are adapted to |TEEY| models.

        """
        return self._evaluate_for_teey_models(data_matrix)


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += FurmanPivi._generate_parameter_docs()
