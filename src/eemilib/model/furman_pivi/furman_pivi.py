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
    Warning when |SEEY| exceeds max number of |SEs| :data:`_M_MAX_SECONDARIES`.

"""

import logging
from functools import partial
from typing import Any, Callable, cast

import numpy as np
import pandas as pd
from eemilib.core.model_config import ModelConfig
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.model.furman_pivi.all import all_energy_distribution, teey
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
    ImplementedEmissionData,
    ImplementedPop,
    col_energy,
)
from numpy.typing import NDArray

EMISSION_YIELD_FUNCS: dict[ImplementedPop, Callable] = {
    "SE": seey,
    "EBE": ebeey,
    "IBE": ibeey,
    "all": teey,
}


class FurmanPivi(Model):
    """Define the Furman and Pivi model :cite:`Furman2002,Furman2013`."""

    emission_data_types = ["Emission Yield", "Emission Energy"]
    populations = ["EBE", "IBE", "SE"]
    considers_energy = True
    is_3d = True
    is_dielectrics_compatible = False
    model_config = ModelConfig(
        emission_yield_files=("SE", "IBE", "EBE"),
        emission_energy_files=(),
        emission_angle_files=(),
    )
    initial_parameters = INITIAL_FURMAN_PIVI_PARAMETERS
    implementation_choices = {
        "distribution": FURMAN_PIVI_DISTRIBUTIONS,
        "normalization": FURMAN_PIVI_NORMALIZATIONS,
    }

    def __init__(
        self,
        distribution: DISTRIBUTION_T = "Poisson",
        normalization: NORMALIZATION_T = "incident",
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

        self._generate_parameter_docs()
        if parameters_values is not None:
            self.set_parameters_values(parameters_values)

        self.set_implementation("distribution", distribution)
        self._proba_emit_n_se: PROBA_EMIT_N_SE
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
                f"     - {kwargs.get("description","")}",
            ]
            doc_lines += doc
        return "\n".join(doc_lines)

    def _get_energy_distribution_data(
        self,
        population: ImplementedPop,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        impact_energy: float | None,
    ) -> pd.DataFrame | None:
        """Compute emitted-energy spectrum data for one population."""
        e_0 = impact_energy if impact_energy is not None else energy[-1]
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
                impact_energy=e_0,
                the=the,
                emission_energies=energy,
                **self.parameters,
            )

        out_dict = {
            col_energy: energy,
            **{f"{the} [deg]": out[:, j] for j, the in enumerate(theta)},
        }
        return pd.DataFrame(out_dict)

    def get_data(
        self,
        population: ImplementedPop,
        emission_data_type: ImplementedEmissionData,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        *args,
        impact_energy: float | None = None,
        **kwargs,
    ) -> pd.DataFrame | None:
        r"""Return desired data according to current model.

        Parameters
        ----------
        impact_energy :
            Only used when ``emission_data_type == "Emission Energy"``. Impact
            energy :math:`E_0` at which the emitted-energy spectrum is
            evaluated. If not given, defaults to the last value of ``energy``.

        """
        if emission_data_type == "Emission Angle":
            return super().get_data(
                population=population,
                emission_data_type=emission_data_type,
                energy=energy,
                theta=theta,
                *args,
                **kwargs,
            )

        if emission_data_type == "Emission Energy":
            data = self._get_energy_distribution_data(
                population=population,
                energy=energy,
                theta=theta,
                impact_energy=impact_energy,
            )
            if data is not None:
                return data
            return super().get_data(
                population=population,
                emission_data_type=emission_data_type,
                energy=energy,
                theta=theta,
                *args,
                **kwargs,
            )

        ey_func = EMISSION_YIELD_FUNCS.get(population)
        if ey_func is None:
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
                out[i, j] = ey_func(ene, the, **self.parameters)

        out_dict = {
            col_energy: energy,
            **{f"{the} [deg]": out[:, j] for j, the in enumerate(theta)},
        }
        return pd.DataFrame(out_dict)

    def find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        raise NotImplementedError

    def _find_ibe_parameters(self) -> None:
        r"""Find the best parameters for |IBE|.

        Specifically:

        1. Fit :math:`E_\mathrm{IBE}`, :math:`\eta_{i,\,\mathrm{max}}` and
           :math:`r` from the exponential law (:func:`._ibeey_normal`) on the
           normal incidence |IBEEY| measurements.
        2. Fit :math:`r_1` and :math:`r_2` from :func:`.at_theta_incidence`
           oblique incidence |IBEEY| measurements.
        3. Fit :math:`q` from :func:`.ibe_energy_distribution` on all the
           |IBE| emission energy distribution measurements.

        .. note::
           If you do not have specific measurement files for the |IBEEY|, it
           is important to have at least one |TEEY| measurement at normal
           incidence and high impact energies. Otherwise, it is hard to
           discriminate |SEEY| from |IBEEY|.

        """
        normal_ibeey_parameters = self._fit_normal_ibeey()
        self.set_parameters_values(normal_ibeey_parameters)

        # raise warning if we do not have normal incidence high energy files,
        # see note in docstring

        oblique_ibeey_parameters = self._fit_oblique_ibeey()
        self.set_parameters_values(oblique_ibeey_parameters)

        ibe_pdf_parameters = self._fit_ibe_energy_distribution()
        self.set_parameters_values(ibe_pdf_parameters)

    def _fit_normal_ibeey(self) -> dict[str, float]:
        raise NotImplementedError
        return {"e_ibe": -1.0, "eta_i_max": -1.0, "r": -1.0}

    def _fit_oblique_ibeey(self) -> dict[str, float]:
        raise NotImplementedError
        return {"r_1": -1.0, "r_2": -1.0}

    def _fit_ibe_energy_distribution(self) -> dict[str, float]:
        raise NotImplementedError
        return {"q": -1.0}

    def evaluate(self, data_matrix: DataMatrix) -> dict[str, float]:
        """Evaluate the quality of the model using Fil criterions.

        Fil criterions :cite:`Fil2016a,Fil2020` are adapted to |TEEY| models.

        """
        return self._evaluate_for_teey_models(data_matrix)


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += FurmanPivi._generate_parameter_docs()
