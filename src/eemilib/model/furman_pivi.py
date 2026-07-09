r"""Create the Furman and Pivi model, to compute |SEEY|, |EBEEY|, |IBEEY|.

Also energy emission distributions. Even angular distributions?

This is an empirical model developed by Dionne :cite:`Furman2002,Furman2013`.

.. todo::
    Energy distributions depend on impact energy, in contrary to Chung and
    Everhart that were always the same.

.. todo::
   Separate implementation into two dropdowns in GUI.

.. todo::
   Store the max number of secondaries in the Model, make it editable, like
   from the Parameters section in the GUI.

.. todo::
    Warning when |SEEY| exceeds max number of |SEs| :data:`_M_MAX_SECONDARIES`.

"""

import logging
import math
from typing import Any, Callable, Literal, TypedDict, cast

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
)
from eemilib.util.markdown import (
    DELTA_MAX,
    DELTA_MAX_FP,
    E1,
    E2,
    NORMAL_E_MAX_EBE,
    NORMAL_E_MAX_EBE_FP,
    NORMAL_E_MAX_IBE,
    NORMAL_E_MAX_IBE_FP,
    NORMAL_E_MAX_SE,
    NORMAL_E_MAX_SE_FP,
    P1_HAT,
    P1_INF_EBE,
    P1_INF_IBE,
    R1,
    R2,
    SIGMA,
    T1,
    T2,
    T3,
    T4,
    P,
    Q,
    R,
    S,
    W,
)
from numpy.typing import NDArray
from scipy.special import erf, gammainc
from scipy.stats import binom, poisson

FurmanPiviImplementation = Literal[
    "poisson-incident",
    "poisson-penetrated",
    "binomial-incident",
    "binomial-penetrated",
]
FURMAN_PIVI_IMPLEMENTATIONS = (
    "poisson-incident",
    "poisson-penetrated",
    "binomial-incident",
    "binomial-penetrated",
)
NORMALIZATION_T = Literal["incident", "penetrated"]
PROBABILITY_TO_EMIT_N_SECONDARIES_T = Literal["poisson", "binomial"]
#: Max number of |SEs|. In Furman and Pivi paper, this is denoted :math:`M`.
_M_MAX_SECONDARIES = 10


class FurmanPiviParameters(TypedDict):
    # =========================================================================
    # True secondary emission
    # =========================================================================
    # Emax for normal SEY. could also be E_ts with a ^
    normal_e_max_se: Parameter
    # normal SEYmax. could also be delta_ts with a ^
    normal_delta_max: Parameter
    t_1: Parameter
    t_2: Parameter
    t_3: Parameter
    t_4: Parameter
    s: Parameter
    # Resulting epsN: 1, 2
    # Resulting pN: 1, 2

    # =========================================================================
    # EBE
    # =========================================================================
    normal_e_max_ebe: Parameter
    p_1_hat: Parameter
    sigma: Parameter
    p_1_inf_ebe: Parameter
    W: Parameter
    p: Parameter
    e_1: Parameter
    e_2: Parameter

    # =========================================================================
    # IBE
    # =========================================================================
    normal_e_max_ibe: Parameter
    p_1_inf_ibe: Parameter
    r: Parameter
    q: Parameter
    r_1: Parameter
    r_2: Parameter


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
    initial_parameters = {
        # =====================================================================
        # Secondary Electrons (or "True Secondaries")
        # =====================================================================
        "normal_e_max_se": {
            "markdown": NORMAL_E_MAX_SE,
            "unit": "eV",
            "value": 310.0,
            "lower_bound": 0.0,
            "description": "Energy where SEEY is maximum at normal incidence.",
            "is_locked": True,
            "furman_pivi_notation": NORMAL_E_MAX_SE_FP,
        },
        "normal_delta_max": {
            "markdown": DELTA_MAX,
            "unit": "1",
            "value": 1.22,
            "lower_bound": 0.0,
            "description": "Maximum SEEY at normal incidence.",
            "is_locked": True,
            "furman_pivi_notation": DELTA_MAX_FP,
        },
        "t_1": {
            "markdown": T1,
            "unit": "1",
            "value": 0.66,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Scaling parameter in SEEY impact angle fit.",
        },
        "t_2": {
            "markdown": T2,
            "unit": "1",
            "value": 0.80,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Exponent parameter in SEEY impact angle fit.",
        },
        "t_3": {
            "markdown": T3,
            "unit": "1",
            "value": 0.70,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Scaling parameter in SEEY energy impact angle fit.",
        },
        "t_4": {
            "markdown": T4,
            "unit": "1",
            "value": 1.0,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Exponent parameter in SEEY energy impact angle fit.",
        },
        "s": {
            "markdown": S,
            "unit": "1",
            "value": 1.813,
            "lower_bound": 1.0 + 1e-12,
            "description": "Parameter in the D function.",
        },
        "eps_1": {
            "markdown": "eps_1",
            "unit": "1",
            "value": 3.9,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "eps_2": {
            "markdown": "eps_2",
            "unit": "1",
            "value": 6.2,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "eps_3": {
            "markdown": "eps_3",
            "unit": "1",
            "value": 13.0,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "eps_4": {
            "markdown": "eps_4",
            "unit": "1",
            "value": 8.8,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "eps_5": {
            "markdown": "eps_5",
            "unit": "1",
            "value": 6.25,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "eps_6": {
            "markdown": "eps_6",
            "unit": "1",
            "value": 2.25,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "eps_7": {
            "markdown": "eps_7",
            "unit": "1",
            "value": 9.20,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "eps_8": {
            "markdown": "eps_8",
            "unit": "1",
            "value": 5.3,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "eps_9": {
            "markdown": "eps_9",
            "unit": "1",
            "value": 17.8,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "eps_10": {
            "markdown": "eps_10",
            "unit": "1",
            "value": 10.0,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "p_1": {
            "markdown": "p_1",
            "unit": "1",
            "value": 1.6,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "p_2": {
            "markdown": "p_2",
            "unit": "1",
            "value": 2.0,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "p_3": {
            "markdown": "p_3",
            "unit": "1",
            "value": 1.8,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "p_4": {
            "markdown": "p_4",
            "unit": "1",
            "value": 4.7,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "p_5": {
            "markdown": "p_5",
            "unit": "1",
            "value": 1.8,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "p_6": {
            "markdown": "p_6",
            "unit": "1",
            "value": 2.4,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "p_7": {
            "markdown": "p_7",
            "unit": "1",
            "value": 1.8,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "p_8": {
            "markdown": "p_8",
            "unit": "1",
            "value": 1.8,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "p_9": {
            "markdown": "p_9",
            "unit": "1",
            "value": 2.3,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        "p_10": {
            "markdown": "p_10",
            "unit": "1",
            "value": 1.8,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": ".",
        },
        # =====================================================================
        # Elastically Backscattered Electrons (or "Reflected")
        # =====================================================================
        "normal_e_max_ebe": {
            "markdown": NORMAL_E_MAX_EBE,
            "unit": "eV",
            "value": 0.0,
            "lower_bound": 0.0,
            "description": "Energy where EBEEY is maximum at normal incidence.",
            "is_locked": True,
            "furman_pivi_notation": NORMAL_E_MAX_EBE_FP,
        },
        "p_1_hat": {
            "markdown": P1_HAT,
            "unit": "1",
            "value": 0.5,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": (
                "Some kind of probability in EBEEY energy fit. Maybe a peak maximum? "
                f"Must be bigger than :math:`{P1_INF_EBE}`, which is "
                "currently not enforced."
            ),  # TODO: check meaning
            "is_locked": True,
        },
        "sigma": {
            "markdown": SIGMA,
            "unit": "1",
            "value": 1.9,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Parameter in EBE PDF function.",
        },
        "p_1_inf_ebe": {
            "markdown": P1_INF_EBE,
            "unit": "1",
            "value": 0.07,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": (
                "Some kind of probability in EBEEY energy fit. "
                f"Must be lower than :math:`{P1_HAT}`, which is currently "
                "not enforced."
            ),  # TODO: check meaning
        },
        "W": {
            "markdown": W,
            "unit": "eV",
            "value": 100.0,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Parameter in the EBEEY energy fit.",
        },
        "p": {
            "markdown": P,
            "unit": "1",
            "value": 0.9,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Exponent parameter in the EBEEY energy fit.",
        },
        "e_1": {
            "markdown": E1,
            "unit": "1",
            "value": 0.26,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Scaling parameter in EBEEY impact angle fit.",
        },
        "e_2": {
            "markdown": E2,
            "unit": "1",
            "value": 2.0,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Exponent parameter in EBEEY impact angle fit.",
        },
        # =====================================================================
        # Inelastically Backscattered Electrons (or "Rediffused")
        # =====================================================================
        "normal_e_max_ibe": {
            "markdown": NORMAL_E_MAX_IBE,
            "unit": "eV",
            "value": 40.0,
            "lower_bound": 0.0,
            "description": "Energy where IBEEY is maximum at normal incidence.",
            "is_locked": True,
            "furman_pivi_notation": NORMAL_E_MAX_IBE_FP,
        },
        "p_1_inf_ibe": {
            "markdown": P1_INF_IBE,
            "unit": "1",
            "value": 0.74,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Some kind of probability in IBEEY energy fit.",  # TODO: check meaning
        },
        "r": {
            "markdown": R,
            "unit": "1",
            "value": 1.0,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Exponent in IBEEY energy fit.",
        },
        "q": {
            "markdown": Q,
            "unit": "1",
            "value": 0.4,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Parameter in the IBEEY PDF function.",
        },
        "r_1": {
            "markdown": R1,
            "unit": "1",
            "value": 0.26,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Scaling parameter in IBEEY impact angle fit.",
        },
        "r_2": {
            "markdown": R2,
            "unit": "1",
            "value": 2.0,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Exponent parameter in IBEEY impact angle fit.",
        },
    }
    implementations = FURMAN_PIVI_IMPLEMENTATIONS

    def __init__(
        self,
        implementation: FurmanPiviImplementation = "poisson-incident",
        parameters_values: dict[str, Any] | None = None,
    ) -> None:
        r"""Instantiate the object.

        Parameters
        ----------
        implementation :
            Selects the distribution used for the number of |SEs| emitted
            per event (``"poisson"`` or ``"binomial"``, *cf* Eqs. (37)/(38)
            in :cite:`Furman2002`) and the normalization used for the
            associated probabilities (``"incident"`` or ``"penetrated"``,
            *cf* Eqs. (35) and (43)). Can be changed later with
            :meth:`set_implementation`.
        parameters_values :
            Contains name of parameters and associated value. If provided, will
            override the default values set in ``initial_parameters``.

        """
        super().__init__(url_doc_override="manual/models/furman_pivi")

        for parameters_kwargs in self.initial_parameters.values():
            _add_furman_pivi_notation(parameters_kwargs)

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

        self._proba_emit_n_se: _PROBA_EMIT_N_SE
        self._normalization: NORMALIZATION_T
        self.current_implementation: FurmanPiviImplementation
        self.set_implementation(implementation)

    def set_implementation(
        self, implementation: FurmanPiviImplementation
    ) -> None:
        r"""Update the |SE| number distribution and probability normalization.

        Parameters
        ----------
        implementation :
            One of :data:`FURMAN_PIVI_IMPLEMENTATIONS`. The part before the
            ``"-"`` selects the distribution for the number of emitted |SEs|
            (``"poisson"`` or ``"binomial"``). The part after selects the
            probability normalization (``"incident"``, *cf* Eq. (35), or
            ``"penetrated"``, *cf* Eq. (43)).

        """
        distribution_name, normalization = implementation.split("-")
        self._proba_emit_n_se = (
            _set_number_of_secondaries_probability_function(
                cast(
                    PROBABILITY_TO_EMIT_N_SECONDARIES_T,
                    distribution_name,
                )
            )
        )
        self._normalization = cast(NORMALIZATION_T, normalization)
        self.current_implementation = implementation

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
            _add_furman_pivi_notation(kwargs)
            doc = [
                f"   * - :math:`{kwargs.get('markdown', '')}`",
                f"     - {name}",
                f"     - :unit:`{kwargs.get('unit', '')}`",
                f"     - :math:`{kwargs.get('value', '')}`",
                f"     - {kwargs.get("description","")}",
            ]
            doc_lines += doc
        return "\n".join(doc_lines)

    def get_data(
        self,
        population: ImplementedPop,
        emission_data_type: ImplementedEmissionData,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        *args,
        **kwargs,
    ) -> pd.DataFrame | None:
        """Return desired data according to current model."""
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
            raise NotImplementedError("Emission Energy not yet implemented.")

        ey_func = EMISSION_YIELD_FUNCS[population]
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

    def evaluate(self, data_matrix: DataMatrix) -> dict[str, float]:
        """Evaluate the quality of the model using Fil criterions.

        Fil criterions :cite:`Fil2016a,Fil2020` are adapted to |TEEY| models.

        """
        return self._evaluate_for_teey_models(data_matrix)


def _add_furman_pivi_notation(
    parameters_kwargs: dict[str, str | float | bool],
) -> None:
    """Modify dict in-place to mention original Furman and Pivi notation.

    Parameters
    ----------
    parameters_kwargs :
        A :class:`.Parameter` kwargs. If a ``"furman_pivi_notation"`` key is
        found, it is removed and added to the ``"description"`` value --
        provided that both keys are valid strings.

    """
    description = parameters_kwargs.get("description")
    if not isinstance(description, str):
        return
    furman_pivi_notation = parameters_kwargs.pop("furman_pivi_notation", None)
    if not isinstance(furman_pivi_notation, str):
        return
    parameters_kwargs["description"] = " ".join(
        (
            description,
            f" Denoted :math:`{furman_pivi_notation}` by Furman and Pivi.",
        )
    )


# =============================================================================
# SEs
# =============================================================================
def _seey_max(
    the: float,
    normal_delta_max: Parameter,
    t_1: Parameter,
    t_2: Parameter,
    tol: float = 1e-8,
    **kwargs,
) -> float:
    r"""Compute value of |SEEY| peak at non-normal incidence.

    .. math::
       \delta_{\mathrm{max}}(\theta) = \delta_{\mathrm{max}}(\theta=0\degree)
       \left[1 + t_1 \left(1 - \cos^{t_2}\theta \right) \right]

    In Furman and Pivi paper :cite:`Furman2002`, this is Eq. (48a):

    .. math::
       \hat \delta(\theta_0) = \hat \delta_{\mathrm{ts}}
       \left[1 + t_1 \left(1 - \cos^{t_2}\theta_0 \right) \right]

    See Also
    --------
    :func:`at_theta_incidence`

    """
    return at_theta_incidence(
        the=the,
        at_normal=normal_delta_max,
        a_1=t_1,
        a_2=t_2,
        tol=tol,
        **kwargs,
    )


def _e_max_se(
    the: float,
    normal_e_max_se: Parameter,
    t_3: Parameter,
    t_4: Parameter,
    tol: float = 1e-8,
    **kwargs,
) -> float:
    r"""Compute position of |SEEY| peak at non-normal incidence.

    .. math::
       E_{\mathrm{max},\,\delta}(\theta) = E_{\mathrm{max},\,\delta}(\theta=0\degree)
       \left[1 + t_3 \left(1 - \cos^{t_4}\theta \right) \right]

    In Furman and Pivi paper :cite:`Furman2002`, this is Eq. (48b):

    .. math::
       \hat E(\theta_0) = \hat E_{\mathrm{ts}}
       \left[1 + t_3 \left(1 - \cos^{t_4}\theta_0 \right) \right]

    See Also
    --------
    :func:`at_theta_incidence`

    """
    return at_theta_incidence(
        the=the, at_normal=normal_e_max_se, a_1=t_3, a_2=t_4, tol=tol, **kwargs
    )


def _d_func(x: float, s: Parameter) -> float:
    r"""Define function used in |SEEY|.

    .. math::
       D(x) = \frac{sx}{s-1+x^s}

    where :math:`s` is an adjustable parameter strictly greater than unity.

    In Furman and Pivi paper :cite:`Furman2002`, this is Eq. (32).

    """
    s_val = s.value
    return s_val * x / (s_val - 1 + x**s_val)


def seey(
    ene: float,
    the: float,
    normal_e_max_se: Parameter,
    normal_delta_max: Parameter,
    s: Parameter,
    t_1: Parameter,
    t_2: Parameter,
    t_3: Parameter,
    t_4: Parameter,
    tol: float = 1e-8,
    **kwargs,
) -> float:
    r"""Compute |SEEY|.

    .. math::
       \delta(E, \theta) = \delta_{\mathrm{max}}(\theta)
       D\left( \frac{E}{E_{\mathrm{max},\,\mathrm{SE}}(\theta)} \right)

    where :math:`\delta_{\mathrm{max}}(\theta)` is calculated using
    :func:`_seey_max` and :math:`E_{\mathrm{max},\,\mathrm{SE}}(\theta)` with
    :func:`_e_max_se`.

    In Furman and Pivi paper :cite:`Furman2002`, this is Eq. (31):

    .. math::
       \delta_{ts} = \hat \delta(\theta_0)D\left[E_0/\hat E(\theta_0)\right]

    """
    _delta_max = _seey_max(
        the=the,
        normal_delta_max=normal_delta_max,
        t_1=t_1,
        t_2=t_2,
        tol=tol,
        **kwargs,
    )
    e_max = _e_max_se(
        normal_e_max_se=normal_e_max_se,
        the=the,
        t_3=t_3,
        t_4=t_4,
        tol=tol,
        **kwargs,
    )

    return _delta_max * _d_func(ene / e_max, s=s)


_PROBA_EMIT_N_SE = Callable[[float, int], float]


def _p_n_se(
    n: int,
    delta: float,
    eta_e: float,
    eta_i: float,
    proba_emit_n_se: _PROBA_EMIT_N_SE,
    normalization: NORMALIZATION_T,
) -> float:
    r"""Compute probability to emit ``n`` |SEs|.

    Dispatches on ``normalization``:

    - ``"incident"``: :math:`P_{n,\,se}` is taken directly from
      ``proba_emit_n_se`` applied to :math:`\delta`, *cf* Eqs. (37)/(38) in
      :cite:`Furman2002`.
    - ``"penetrated"``: :math:`P_{n,\,se} = (1 - \eta_e - \eta_i)
      P^\prime_{n,\,se}`, where :math:`P^\prime_{n,\,se}` is
      ``proba_emit_n_se`` applied to :math:`\delta^\prime = \delta / (1 -
      \eta_e - \eta_i)`, *cf* Eqs. (39), (42), (45)/(46).

    Parameters
    ----------
    n :
        Number of |SEs|.
    delta :
        |SEEY| (:math:`\delta_{ts}` in :cite:`Furman2002`).
    eta_e :
        |EBEEY| (:math:`\delta_e` in :cite:`Furman2002`).
    eta_i :
        |IBEEY| (:math:`\delta_r` in :cite:`Furman2002`).
    proba_emit_n_se :
        Function computing probability to emit ``n`` |SEs|, *cf*
        :func:`_set_number_of_secondaries_probability_function`.
    normalization :
        Selects Eq. (37)/(38) (``"incident"``) or Eq. (39), (42), (45)/(46)
        (``"penetrated"``).

    Return
    ------
        :math:`P_{n,\,se}` (:math:`P_{n,\,ts}` in :cite:`Furman2002`).

    """
    if normalization == "incident":
        return proba_emit_n_se(delta, n)

    available_fraction = 1.0 - eta_e - eta_i
    delta_prime = delta / available_fraction
    return available_fraction * proba_emit_n_se(delta_prime, n)


def _p_n(
    n: int,
    delta: float,
    eta_e: float,
    eta_i: float,
    proba_emit_n_se: _PROBA_EMIT_N_SE,
    normalization: NORMALIZATION_T,
) -> float:
    r"""Compute the overall :math:`P_n`, combining all electron types.

    Applies the mutual-exclusion assumption, Eq. (21) in :ref:`Furman2002`:

    - :math:`n \geq 2`: :math:`P_n = P_{n,\,se}`.
    - :math:`n = 1`: :math:`P_1 = P_{1,\,se} + \eta_e + \eta_i`.
    - :math:`n = 0`: :math:`P_0 = P_{0,\,se} - \eta_e - \eta_i` when
      ``normalization`` is ``"incident"`` (Eq. 35a); :math:`P_0 = P_{0,\,se}`
      when it is ``"penetrated"`` (Eq. 43a).

    Parameters
    ----------
    n :
        Number of |EEs|.
    delta :
        |SEEY| (:math:`\delta_{ts}` in :cite:`Furman2002`).
    eta_e :
        |EBEEY| (:math:`\delta_e` in :cite:`Furman2002`).
    eta_i :
        |IBEEY| (:math:`\delta_r` in :cite:`Furman2002`).
    proba_emit_n_se :
        Function computing probability to emit ``n`` |SEs|, *cf*
        :func:`_set_number_of_secondaries_probability_function`.
    normalization :
        Selects Eq. (35) (``"incident"``) or Eq. (43) (``"penetrated"``).

    Return
    ------
        :math:`P_n`.

    """
    p_n_se = _p_n_se(n, delta, eta_e, eta_i, proba_emit_n_se, normalization)

    if n == 0:
        if normalization == "incident":
            return p_n_se - eta_e - eta_i
        return p_n_se

    if n == 1:
        return p_n_se + eta_e + eta_i

    return p_n_se


def _regularized_incomplete_gamma(
    a: float, x: NDArray[np.float64]
) -> NDArray[np.float64]:
    r"""Compute the regularized lower incomplete gamma function :math:`P(a,x)`.

    Thin wrapper around :func:`scipy.special.gammainc`, handling the
    :math:`a=0` edge case with the convention :math:`P(0,\,x) = 1` for
    :math:`x \geq 0`, stated in Appendix A of :cite:`Furman2002` (just below
    Eq. (A8)). :func:`scipy.special.gammainc` does not support ``a = 0``
    directly.

    Parameters
    ----------
    a :
        Shape parameter.
    x :
        Upper integration bound(s). Values are clipped to be non-negative,
        since callers may evaluate this outside the physically valid range
        (the result is expected to be masked out separately in that case).

    Return
    ------
        :math:`P(a, x)`.

    """
    x_clipped = np.clip(x, 0.0, None)
    if a == 0.0:
        return np.ones_like(x_clipped)
    return gammainc(a, x_clipped)


def _set_number_of_secondaries_probability_function(
    model: PROBABILITY_TO_EMIT_N_SECONDARIES_T = "poisson",
) -> _PROBA_EMIT_N_SE:
    """Set the function that computes probability to emit ``n`` secondaries.

    This let you choose between the two propositions in Furman and Pivi paper
    :cite:`Furman2002`, *cf* Eqs. (37) and (38).

    Parameters
    ----------
    model :
        Name of the model to use.

    Return
    ------
        A function that takes in the |SEEY| and the |SEs|, and returns the
        probability to emit this number of |SEs|.

    """

    if model == "binomial":

        def probability(seey: float, n: int) -> float:
            return float(
                binom.pmf(n, _M_MAX_SECONDARIES, seey / _M_MAX_SECONDARIES)
            )

        return probability

    if model != "poisson":
        logging.warning(
            f"Wrong model for number of emitted electrons. {model = } should "
            f"be in {PROBABILITY_TO_EMIT_N_SECONDARIES_T}. Fall back to "
            "'poisson' model."
        )

    def probability(seey: float, n: int) -> float:
        return float(poisson.pmf(n, seey))

    return probability


def se_energy_distribution(
    impact_energy: float,
    the: float,
    emission_energies: NDArray[np.float64],
    p_ns: list[Parameter],
    eps_ns: list[Parameter],
    proba_emit_n_se: _PROBA_EMIT_N_SE,
    normalization: NORMALIZATION_T,
    **kwargs,
) -> NDArray[np.float64]:
    r"""Compute the aggregate |SE| emitted-energy spectrum.

    This is Eq. (52) in Furman and Pivi paper :cite:`Furman2002`:

    .. math::
       \frac{d\delta_{ts}}{dE} = \sum_{n=1}^{n_\mathrm{max}}
            \frac{
                n\,P_{n,\,ts}(E_0)\,(E/\varepsilon_n)^{p_n-1}
                \mathrm{e}^{-E/\varepsilon_n}
            }{
                \varepsilon_n\,\Gamma(p_n)\,P(np_n,\,E_0/\varepsilon_n)
            }
            \times P\left[(n-1)p_n,\,(E_0-E)/\varepsilon_n\right]

    where :math:`P(z,\,x)` is the regularized lower incomplete gamma
    function, computed with :func:`_regularized_incomplete_gamma`, and
    :math:`P_{n,\,ts}(E_0)` is computed with :func:`_p_n_se`.

    In our notation, :math:`\delta_{ts}` is denoted ``delta``, and the sum
    runs over the same ``n`` as the provided ``p_ns``/``eps_ns`` lists (so
    :math:`n_\mathrm{max}` is implicitly ``len(p_ns)``).

    Parameters
    ----------
    impact_energy :
        Impact energy of the |PE| in :unit:`eV`.
    the :
        Impact angle of the |PE| in :math:`\degree`.
    emission_energies :
        |SE| emission energies you want the distribution from.
    p_ns :
        List of :math:`p_n` parameters, one per :math:`n`, starting at
        :math:`n=1`.
    eps_ns :
        List of :math:`\varepsilon_n` parameters, one per :math:`n`, starting
        at :math:`n=1`. Must be the same length as ``p_ns``.
    proba_emit_n_se :
        Function computing probability to emit ``n`` |SEs|, *cf*
        :func:`_set_number_of_secondaries_probability_function`.
    normalization :
        Selects Eq. (35) (``"incident"``) or Eq. (43) (``"penetrated"``), *cf*
        :func:`_p_n_se`.
    kwargs :
        Furman and Pivi |SEEY|, |EBEEY|, |IBEEY| parameters, passed to
        :func:`seey`, :func:`ebeey`, :func:`ibeey` to compute :math:`\delta`,
        :math:`\eta_e`, :math:`\eta_i`.

    Returns
    -------
        Aggregate |SE| emitted-energy spectrum.

    """
    delta = seey(ene=impact_energy, the=the, **kwargs)
    eta_e = ebeey(ene=impact_energy, the=the, **kwargs)
    eta_i = ibeey(ene=impact_energy, the=the, **kwargs)

    spectrum = np.zeros_like(emission_energies)
    for n, (p_n_param, eps_n_param) in enumerate(zip(p_ns, eps_ns), start=1):
        p_n = p_n_param.value
        eps_n = eps_n_param.value

        p_n_se = _p_n_se(
            n, delta, eta_e, eta_i, proba_emit_n_se, normalization
        )

        normalization_term = math.gamma(p_n) * _regularized_incomplete_gamma(
            n * p_n, np.array(impact_energy / eps_n)
        )
        shape_term = (emission_energies / eps_n) ** (p_n - 1) * np.exp(
            -emission_energies / eps_n
        )
        tail_term = _regularized_incomplete_gamma(
            (n - 1) * p_n, (impact_energy - emission_energies) / eps_n
        )

        spectrum += (
            n * p_n_se * shape_term * tail_term / (eps_n * normalization_term)
        )

    return _remove_extrema(impact_energy, emission_energies) * spectrum


# =============================================================================
# EBEs
# =============================================================================
def _ebeey_normal(
    ene: float,
    normal_e_max_ebe: Parameter,
    p_1_hat: Parameter,
    p_1_inf_ebe: Parameter,
    W: Parameter,
    p: Parameter,
) -> float:
    r"""Compute |EBEEY| at normal incidence.

    .. math::
       \eta_e(E,\,\theta=0\degree) =
            P_{1,\,e}(\infty)
            + \left[ \hat P_{1,\,e} - P_{1,\,e}(\infty) \right]
            \mathrm{e}^{
                - \left( \left| E - E_{\mathrm{max},\,\mathrm{EBE}} \right|
                  / W \right)^p
                  / p
            }

    In Furman and Pivi paper :cite:`Furman2002`, this is Eq. (25):

    .. math::
       \delta_e(E_0,\,0) =
            P_{1,\,e}(\infty)
            + \left[ \hat P_{1,\,e} - P_{1,\,e}(\infty) \right]
            \mathrm{e}^{
                - \left( \left| E_0 - \hat E_e \right|
                  / W \right)^p
                  / p
            }

    """
    _in_exp = (abs(ene - normal_e_max_ebe.value) / W.value) ** p.value
    return p_1_inf_ebe.value + (p_1_hat.value - p_1_inf_ebe.value) * math.exp(
        -_in_exp / p.value
    )


def ebeey(
    ene: float,
    the: float,
    normal_e_max_ebe: Parameter,
    p_1_hat: Parameter,
    p_1_inf_ebe: Parameter,
    W: Parameter,
    p: Parameter,
    e_1: Parameter,
    e_2: Parameter,
    **kwargs,
) -> float:
    """Compute |EBEEY|.

    First, we compute |EBEEY| at normal incidence using :func:`_ebeey_normal`.
    Then, we compute it at provided incidence angle using
    :func:`at_theta_incidence`.

    """
    return at_theta_incidence(
        the=the,
        at_normal=_ebeey_normal(
            ene=ene,
            normal_e_max_ebe=normal_e_max_ebe,
            p_1_hat=p_1_hat,
            p_1_inf_ebe=p_1_inf_ebe,
            W=W,
            p=p,
        ),
        a_1=e_1,
        a_2=e_2,
    )


def ebe_energy_distribution(
    impact_energy: float,
    the: float,
    emission_energies: NDArray[np.float64],
    normal_e_max_ebe: Parameter,
    p_1_hat: Parameter,
    p_1_inf_ebe: Parameter,
    W: Parameter,
    p: Parameter,
    e_1: Parameter,
    e_2: Parameter,
    sigma_e: Parameter,
    **kwargs,
) -> NDArray[np.float64]:
    r"""Compute PDF for |EBEs|.

    This is Eq. (26) in Furman and Pivi paper :cite:`Furman2002`:

    .. math::
       f_{1,\,e} = \theta(E)\theta(E_0 - E)\delta_e(E_0,\,\theta_0)\frac{
            2\mathrm{e}^{-\left(E-E_0\right)^2/2\sigma_e^2}
       }{
            \sqrt{2\pi}\sigma_e\mathrm{erf}\left(E_0 / \sqrt{2}\sigma_e\right)
       }

    Parameters
    ----------
    impact_energy :
        Impact energy of the |PE| in :unit:`eV`.
    theta :
        Impact angle of the |PE| in :unit:`\degree`.
    emission_energies :
        |EBE| emission energies you want the distribution from.
    normal_e_max_ebe :
        Furman and Pivi |EBEEY| parameter.
    p_1_hat :
        Furman and Pivi |EBEEY| parameter.
    p_1_inf_ebe :
        Furman and Pivi |EBEEY| parameter.
    W :
        Furman and Pivi |EBEEY| parameter.
    p :
        Furman and Pivi |EBEEY| parameter.
    e_1 :
        Furman and Pivi |EBEEY| parameter.
    e_2 :
        Furman and Pivi |EBEEY| parameter.
    sigma_e :
        Furman and Pivi |EBE| PDF parameter.
    kwargs :
        Other unused parameters.

    Returns
    -------
        PDF of |EBE|.

    """
    return (
        _remove_extrema(impact_energy, emission_energies)
        * ebeey(
            ene=impact_energy,
            the=the,
            normal_e_max_ebe=normal_e_max_ebe,
            p_1_hat=p_1_hat,
            p_1_inf_ebe=p_1_inf_ebe,
            W=W,
            p=p,
            e_1=e_1,
            e_2=e_2,
        )
        * 2
        * np.exp(
            -((impact_energy - emission_energies) ** 2)
            / (2 * sigma_e.value**2)
        )
        / (
            math.sqrt(2 * math.pi)
            * sigma_e.value
            * erf(impact_energy / (math.sqrt(2) * sigma_e.value))
        )
    )


# =============================================================================
# IBEs
# =============================================================================
def _ibeey_normal(
    ene: float,
    normal_e_max_ibe: Parameter,
    p_1_inf_ibe: Parameter,
    r: Parameter,
) -> float:
    r"""Compute |IBEEY| at normal incidence.

    .. math::
       \eta_i(E,\,\theta=0\degree) =
            P_{1,\,r}(\infty)
            \mathrm{e}^{
                -\left( E / E_{\mathrm{max},\,\mathrm{IBE}} \right)^r
            }

    In Furman and Pivi paper :cite:`Furman2002`, this is Eq. (28):

    .. math::
       \delta_r(E_0,\,0) =
            P_{1,\,r}(\infty)
            \mathrm{e}^{
                -\left( E / E_r \right)^r
            }

    """
    return p_1_inf_ibe.value * (
        1 - math.exp(-((ene / normal_e_max_ibe.value) ** r.value))
    )


def ibeey(
    ene: float,
    the: float,
    normal_e_max_ibe: Parameter,
    p_1_inf_ibe: Parameter,
    r: Parameter,
    r_1: Parameter,
    r_2: Parameter,
    **kwargs,
) -> float:
    """Compute |IBEEY|.

    First, we compute |IBEEY| at normal incidence using :func:`_ibeey_normal`.
    Then, we compute it at provided incidence angle using
    :func:`at_theta_incidence`.

    """
    return at_theta_incidence(
        the=the,
        at_normal=_ibeey_normal(
            ene=ene,
            normal_e_max_ibe=normal_e_max_ibe,
            p_1_inf_ibe=p_1_inf_ibe,
            r=r,
        ),
        a_1=r_1,
        a_2=r_2,
    )


def ibe_energy_distribution(
    impact_energy: float,
    the: float,
    emission_energies: NDArray[np.float64],
    normal_e_max_ibe: Parameter,
    p_1_inf_ibe: Parameter,
    r: Parameter,
    r_1: Parameter,
    r_2: Parameter,
    q: Parameter,
    **kwargs,
) -> NDArray[np.float64]:
    r"""Compute PDF for |IBEs|.

    This is Eq. (29) in Furman and Pivi paper :cite:`Furman2002`:

    .. math::
       f_{1,\,r} = \theta(E)\theta(E_0 - E)\delta_r(E_0,\,\theta_0)\frac{
            (q+1)E^q
       }{
            E_0^{q+1}
       }

    Parameters
    ----------
    impact_energy :
        Impact energy of the |PE| in :unit:`eV`.
    theta :
        Impact angle of the |PE| in :unit:`\degree`.
    emission_energies :
        |IBE| emission energies you want the distribution from.
    normal_e_max_ibe :
        Furman and Pivi |IBEEY| parameter.
    p_1_inf_ibe :
        Furman and Pivi |IBEEY| parameter.
    r :
        Furman and Pivi |IBEEY| parameter.
    r_1 :
        Furman and Pivi |IBEEY| parameter.
    r_2 :
        Furman and Pivi |IBEEY| parameter.
    q :
        Furman and Pivi |IBE| PDF parameter.

    Returns
    -------
        PDF of |IBE|.

    """
    q_val = q.value
    return (
        _remove_extrema(impact_energy, emission_energies)
        * ibeey(
            ene=impact_energy,
            the=the,
            normal_e_max_ibe=normal_e_max_ibe,
            p_1_inf_ibe=p_1_inf_ibe,
            r=r,
            r_1=r_1,
            r_2=r_2,
        )
        * (q_val + 1)
        * emission_energies**q_val
        / impact_energy ** (q_val + 1)
    )


# =============================================================================
# Generic
# =============================================================================
def at_theta_incidence(
    the: float,
    at_normal: float | Parameter,
    a_1: Parameter,
    a_2: Parameter,
    tol: float = 1e-8,
    **kwargs,
) -> float:
    r"""Compute given quantity at non-normal incidence.

    This function is used in calculations of |SEEY| peak, |SEEY| peak position,
    |EBEEY|, |IBEEY|:

    .. math::
       x(E,\,\theta) =
            x(E,\,\theta=0\degree)
            \left[1 + a_1 \left(1 - \cos^{a_2}\theta \right) \right]

    In Furman and Pivi paper :cite:`Furman2002`, this is used for Eq. (47a),
    (47b), (48a), (48b).

    This relation is valid for incident angles in the range
    :math:`0\degree \leq \theta \lesssim 84\degree`.

    Parameters
    ----------
    the :
        Incidence angle in :unit:`\degree`.
    at_normal :
        Quantity at :math:`\theta = 0\degree`.
    a_1 :
        Scaling parameter.
    a_2 :
        Exponent parameter.
    tol :
        Angle limit under which we consider incidence angle to be normal.

    Return
    ------
        ``at_normal`` but at :math:`\theta` incidence.

    """
    if isinstance(at_normal, Parameter):
        at_normal = at_normal.value

    if abs(the) < tol:
        return at_normal

    if abs(the) >= 84.0:
        logging.warning("Relation invalid for angles greater than 84 degrees.")

    return at_normal * (
        1 + a_1.value * math.cos(math.radians(the)) ** a_2.value
    )


def _theta_func(x: NDArray[np.float64]) -> NDArray[np.float64]:
    """Compute the Heaviside step function.

    Parameters
    ----------
    x :
        Input values.

    Returns
    -------
        1 where ``x >= 0``, 0 where ``x < 0``.

    """
    return np.heaviside(x, 1.0)


def _remove_extrema(
    impact_energy: float, emission_energies: NDArray[np.float64]
) -> NDArray[np.float64]:
    """Zero out emission energies outside ``[0, impact_energy]``.

    Parameters
    ----------
    impact_energy :
        Impact energy :math:`E_0`.
    emission_energies :
        Emission energies :math:`E`.

    Returns
    -------
        1 where ``0 <= emission_energies <= impact_energy``, 0 elsewhere.

    """
    return _theta_func(emission_energies) * _theta_func(
        impact_energy - emission_energies
    )


def teey(ene: float, the: float, **kwargs) -> float:
    r"""Compute |TEEY|.

    Parameters
    ----------
    ene :
        Impact energy in :unit:`eV`.
    the :
        Impact angle in :unit:`\degree`.
    kwargs :
        Model parameters.

    Return
    ------
        |TEEY|.

    """
    return (
        seey(ene, the, **kwargs)
        + ebeey(ene, the, **kwargs)
        + ibeey(ene, the, **kwargs)
    )


EMISSION_YIELD_FUNCS: dict[ImplementedPop, Callable] = {
    "SE": seey,
    "EBE": ebeey,
    "IBE": ibeey,
    "all": teey,
}


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += FurmanPivi._generate_parameter_docs()
