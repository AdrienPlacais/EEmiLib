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
from typing import Any, cast

import numpy as np
import pandas as pd
from eemilib.core.model_config import ModelConfig
from eemilib.emission_data import DataMatrix
from eemilib.emission_data.emission_data import MissingDataError
from eemilib.emission_data.emission_energy_distribution import (
    AllEmissionEnergyDistribution,
    EBEEmissionEnergyDistribution,
    EmissionEnergyDistribution,
    IBEEmissionEnergyDistribution,
    SEEmissionEnergyDistribution,
)
from eemilib.emission_data.emission_yield import (
    EBEEY,
    IBEEY,
    SEEY,
    TEEY,
    EmissionYield,
)
from eemilib.model.furman_pivi.all import (
    NORMAL_TEEY_PARAM_KEYS,
    all_energy_distribution,
    teey,
    teey_normal,
)
from eemilib.model.furman_pivi.ebe import (
    EBE_DISTRIB_PARAMETERS,
    NORMAL_EBEEY_PARAM_KEYS,
    OBLIQUE_EBEEY_PARAM_KEYS,
    double_peak,
    ebe_energy_distribution,
    ebeey,
    ebeey_normal,
)
from eemilib.model.furman_pivi.helper import add_furman_pivi_notation
from eemilib.model.furman_pivi.ibe import (
    IBE_DISTRIB_PARAMETERS,
    NORMAL_IBEEY_PARAM_KEYS,
    OBLIQUE_IBEEY_PARAM_KEYS,
    ibe_energy_distribution,
    ibeey,
    ibeey_normal,
)
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
    NORMAL_SEEY_PARAM_KEYS,
    OBLIQUE_SEEY_PARAM_KEYS,
    PROBA_EMIT_N_SE,
    SE_DISTRIB_PARAMETERS,
    se_energy_distribution,
    seey,
    seey_normal,
    set_number_of_secondaries_probability_function,
)
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

EMISSION_YIELD_FUNCS: dict[ImplementedPop, Callable] = {
    "SE": seey,
    "EBE": ebeey,
    "IBE": ibeey,
    "all": teey,
}


class FurmanPivi(Model):
    """Define the Furman and Pivi model :cite:`Furman2002,Furman2013`."""

    data_types = ["Emission Yield", "Emission Energy"]
    populations = ["EBE", "IBE", "SE"]
    considers_energy = True
    is_3d = True
    is_dielectrics_compatible = False
    model_config = ModelConfig(
        emission_yield_files=("all",),
        emission_energy_files=("all",),
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
                f"     - {kwargs.get("description","")}",
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
            col_energy: energy,
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
        e_pe :
            Only used when ``data_type == "Emission Energy"``. Impact
            energy :math:`E_0` at which the emitted-energy spectrum is
            evaluated. If not given, defaults to the last value of ``energy``.

        """
        if data_type == "Emission Angle":
            return super().get_data(
                population=population,
                data_type=data_type,
                energy=energy,
                theta=theta,
                *args,
                **kwargs,
            )

        if data_type == "Emission Energy":
            data = self._get_energy_distribution_data(
                population=population, energy=energy, theta=theta, e_pe=e_pe
            )
            if data is not None:
                return data
            return super().get_data(
                population=population,
                data_type=data_type,
                energy=energy,
                theta=theta,
                *args,
                **kwargs,
            )

        ey_func = EMISSION_YIELD_FUNCS.get(population)
        if ey_func is None:
            return super().get_data(
                population=population,
                data_type=data_type,
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
        """Fit all Furman and Pivi parameters on measurements.

        Parameters
        ----------
        data_matrix :
            Measurement data to fit. Must contain emission yield and emission
            energy.

        """
        if not data_matrix.has_all_mandatory_files(self.model_config):
            raise MissingDataError("Files are not all provided.")

        teeys = data_matrix.get_data("Emission Yield", "all")
        self.find_normal_ey_params(teeys)

        self._find_oblique_emission_yields_parameters(data_matrix)

        distribs = data_matrix.get_data("Emission Energy", "all")
        self._find_energy_distribution_parameters(distribs)

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
            self.parameters["normal_e_max_se"].value = _teey.e_max

        self._fit_teey(teeys)

    def _fit_teey(self, teeys: Sequence[TEEY]) -> None:
        """Fit |TEEY| parameters."""

        def _aggregate_residue(x: NDArray[np.float64]) -> NDArray[np.float64]:
            kwargs = dict(zip(NORMAL_TEEY_PARAM_KEYS, x))
            residuals = []
            for _teey in teeys:
                measured = _teey.data[col_normal].to_numpy()
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
    def _find_oblique_emission_yields_parameters(
        self, data_matrix: DataMatrix
    ) -> None:
        """Orchestrate fitting of all oblique emission yields parameters."""
        logging.info("Skipping oblique incidence fit for now.")

    def _find_ibe_parameters(self, ibe_shares: Sequence[IBEEY]) -> None:
        r"""Find the best parameters for |IBE|.

        Specifically:

        1. Fit :math:`E_\mathrm{IBE}`, :math:`\eta_{i,\,\mathrm{max}}` and
           :math:`r` from the exponential law (:func:`.ibe.ibeey_normal`) on
           the normal incidence |IBEEY| measurements.
        2. Fit :math:`r_1` and :math:`r_2` from
           :func:`.furman_pivi.physics.at_theta_incidence` oblique incidence
           |IBEEY| measurements.
        3. Fit :math:`q` from :func:`.ibe.ibe_energy_distribution` on all the
           |IBE| emission energy distribution measurements.

        .. note::
            If you do not have specific measurement files for the |IBEEY|, it
            is important to have at least one |TEEY| measurement at normal
            incidence and high impact energies. Otherwise, it is hard to
            discriminate |SEEY| from |IBEEY|.

        Parameters
        ----------
        ibe_shares :
            Decomposed |IBEEY| shares, one per measured |TEEY|, *cf*
            :meth:`_decompose_teeys`.

        """
        fitted = self._fit_normal_yield(
            ibe_shares, ibeey_normal, NORMAL_IBEEY_PARAM_KEYS
        )
        self.set_parameters_values(fitted)

        # raise warning if we do not have normal incidence high energy files,
        # see note in docstring

        oblique_ibeey_parameters = self._fit_oblique_ibeey()
        self.set_parameters_values(oblique_ibeey_parameters)

        ibe_pdf_parameters = self._fit_ibe_energy_distribution()
        self.set_parameters_values(ibe_pdf_parameters)

    # =========================================================================
    # 3. Find best parameters for emission distribution at normal incidence
    # =========================================================================
    def _find_energy_distribution_parameters(
        self, distribs: Sequence[AllEmissionEnergyDistribution]
    ) -> None:
        """Orchestrate fitting of all normal energy distribution parameters.

        1. De-normalize emission energy measurements.

        """
        for d in distribs:
            d.norm = 1.0
            d.normalize()

        se_shares, ebe_shares, ibe_shares = (
            self._decompose_energy_distributions(distribs)
        )
        self._find_se_pdf_parameters(se_shares)
        self._find_ebe_pdf_parameters(ebe_shares)
        self._find_ibe_pdf_parameters(ibe_shares)

    # Actual finders
    def _find_se_pdf_parameters(
        self, se_shares: Sequence[SEEmissionEnergyDistribution]
    ) -> None:
        p_ns = [
            self.parameters[f"p_{i}"] for i in range(1, M_MAX_SECONDARIES + 1)
        ]
        eps_ns = [
            self.parameters[f"eps_{i}"]
            for i in range(1, M_MAX_SECONDARIES + 1)
        ]
        all_normal_yield_keys = (
            NORMAL_SEEY_PARAM_KEYS
            + OBLIQUE_SEEY_PARAM_KEYS
            + NORMAL_EBEEY_PARAM_KEYS
            + OBLIQUE_EBEEY_PARAM_KEYS
            + NORMAL_IBEEY_PARAM_KEYS
            + OBLIQUE_IBEEY_PARAM_KEYS
        )
        fitted = self._fit_energy_distribution(
            se_shares,
            se_energy_distribution,
            SE_DISTRIB_PARAMETERS,
            extra_kwargs={
                **{key: self.parameters[key] for key in all_normal_yield_keys},
                "p_ns": p_ns,
                "eps_ns": eps_ns,
                "proba_emit_n_se": self._proba_emit_n_se,
                "normalization": self._normalization,
            },
        )
        self.set_parameters_values(fitted)

    def _find_ebe_pdf_parameters(
        self, ebe_shares: Sequence[EBEEmissionEnergyDistribution]
    ) -> None:
        r"""Fit |EBE| distribution parameter :math:`\sigma_e`.

        Following :cite:`Furman2002` (discussion after Eq. 27): since the
        analytic |EBE| distribution, Eq. (26), is truncated at :math:`E_0` --
        exactly where its peak sits -- fitting it directly against measured
        data would underestimate the peak's contribution to the area (hence to
        :math:`\eta_e`). The paper compensates by doubling the height of the
        measured peak before fitting; we do the same here, on a copy of each
        share so the original (un-doubled) measured data is left intact for
        plotting/inspection.

        Parameters
        ----------
        ebe_shares :
            Decomposed |EBEEY| shares, one per measured ``"all"`` energy
            distribution, *cf* :meth:`_decompose_energy_distributions`.

        """
        doubled_shares = [double_peak(share) for share in ebe_shares]
        fitted = self._fit_energy_distribution(
            doubled_shares,
            ebe_energy_distribution,
            EBE_DISTRIB_PARAMETERS,
            extra_kwargs={
                key: self.parameters[key]
                for key in NORMAL_EBEEY_PARAM_KEYS + OBLIQUE_EBEEY_PARAM_KEYS
            },
        )
        self.set_parameters_values(fitted)

    def _find_ibe_pdf_parameters(
        self, ibe_shares: Sequence[IBEEmissionEnergyDistribution]
    ) -> None:
        fitted = self._fit_energy_distribution(
            ibe_shares,
            ibe_energy_distribution,
            IBE_DISTRIB_PARAMETERS,
            extra_kwargs={
                key: self.parameters[key]
                for key in NORMAL_IBEEY_PARAM_KEYS + OBLIQUE_IBEEY_PARAM_KEYS
            },
        )
        self.set_parameters_values(fitted)

    # Helpers
    def _decompose_energy_distributions(
        self, all_distrib: Sequence[AllEmissionEnergyDistribution]
    ) -> tuple[
        list[SEEmissionEnergyDistribution],
        list[EBEEmissionEnergyDistribution],
        list[IBEEmissionEnergyDistribution],
    ]:
        """Decompose every measured 'all' energy distribution into shares."""
        p_ns = [
            self.parameters[f"p_{i}"] for i in range(1, M_MAX_SECONDARIES + 1)
        ]
        eps_ns = [
            self.parameters[f"eps_{i}"]
            for i in range(1, M_MAX_SECONDARIES + 1)
        ]

        se_shares: list[SEEmissionEnergyDistribution] = []
        ebe_shares: list[EBEEmissionEnergyDistribution] = []
        ibe_shares: list[IBEEmissionEnergyDistribution] = []
        for dist in all_distrib:

            def se_shape(
                energies: NDArray[np.float64], e_pe: float = dist.e_pe
            ) -> NDArray[np.float64]:
                return se_energy_distribution(
                    e_pe=e_pe,
                    the=0.0,
                    emission_energies=energies,
                    p_ns=p_ns,
                    eps_ns=eps_ns,
                    proba_emit_n_se=self._proba_emit_n_se,
                    normalization=self._normalization,
                    **self.parameters,
                )

            def ebe_shape(
                energies: NDArray[np.float64], e_pe: float = dist.e_pe
            ) -> NDArray[np.float64]:
                return ebe_energy_distribution(
                    e_pe=e_pe,
                    the=0.0,
                    emission_energies=energies,
                    **self.parameters,
                )

            def ibe_shape(
                energies: NDArray[np.float64], e_pe: float = dist.e_pe
            ) -> NDArray[np.float64]:
                return ibe_energy_distribution(
                    e_pe=e_pe,
                    the=0.0,
                    emission_energies=energies,
                    **self.parameters,
                )

            se_share, ebe_share, ibe_share = dist.decompose(
                se_shape, ebe_shape, ibe_shape
            )
            se_shares.append(se_share)
            ebe_shares.append(ebe_share)
            ibe_shares.append(ibe_share)

        return se_shares, ebe_shares, ibe_shares

    def _fit_energy_distribution(
        self,
        shares: Sequence[EmissionEnergyDistribution],
        pdf_func: Callable[..., NDArray[np.float64]],
        param_keys: tuple[str, ...],
        extra_kwargs: dict[str, Any] | None = None,
    ) -> dict[str, float]:
        """Jointly fit an emission energy distribution function's parameters.

        Stacks residuals across every decomposed share (one per measured
        ``"all"`` energy distribution) into a single least-squares problem.
        Unlike :meth:`_fit_normal_yield`, ``pdf_func`` also needs fixed,
        non-fitted context (impact energy, incidence angle, emission energies,
        and -- for |SEs| -- the truncated-sum machinery), supplied via
        ``e_pe``/``the``/``emission_energies`` (bound per share) and
        ``extra_kwargs`` (bound once, shared across every share).

        Parameters
        ----------
        shares :
            Decomposed emission energy distribution shares, *cf*
            :meth:`.AllEmissionEnergyDistribution.decompose`.
        pdf_func :
            Function computing the emission energy distribution. Takes
            ``e_pe``, ``the``, ``emission_energies`` as keyword arguments, plus
            the parameters named in ``param_keys``, plus anything in
            ``extra_kwargs``.
        param_keys :
            Names of ``pdf_func``'s keyword parameters to fit, matching keys in
            :attr:`.FurmanPivi.parameters`.
        extra_kwargs :
            Additional fixed keyword arguments ``pdf_func`` needs but that are
            not being fitted (e.g. ``p_ns``, ``eps_ns``, ``proba_emit_n_se``,
            ``normalization`` for
            :func:`.furman_pivi.se.se_energy_distribution`).

        Return
        ------
            Dict mapping each of ``param_keys`` to its fitted value.

        """
        extra_kwargs = extra_kwargs or {}

        def _aggregate_residue(x: NDArray[np.float64]) -> NDArray[np.float64]:
            kwargs = dict(zip(param_keys, x))
            residuals = []
            for share in shares:
                measured = share.data[col_normal].to_numpy()
                predicted = pdf_func(
                    e_pe=share.e_pe,
                    the=0.0,
                    emission_energies=share.energies,
                    **kwargs,
                    **extra_kwargs,
                )
                residuals.append(measured - predicted)
            return np.concatenate(residuals)

        x0 = [self.parameters[key].value for key in param_keys]
        lower_bounds = [self.parameters[key].lower_bound for key in param_keys]
        upper_bounds = [self.parameters[key].upper_bound for key in param_keys]

        lsq = least_squares(
            fun=_aggregate_residue, x0=x0, bounds=(lower_bounds, upper_bounds)
        )
        return dict(zip(param_keys, lsq.x))

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
