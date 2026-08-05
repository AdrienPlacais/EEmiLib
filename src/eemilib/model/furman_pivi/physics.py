"""Define physics helpers."""

import logging
import math
from typing import Literal, TypedDict

from eemilib.model.parameter import Parameter
from eemilib.util.markdown import (
    DELTA_MAX,
    DELTA_MAX_FP,
    E1,
    E2,
    E_IBE,
    E_IBE_FP,
    EPS_1,
    EPS_2,
    EPS_3,
    EPS_4,
    EPS_5,
    EPS_6,
    EPS_7,
    EPS_8,
    EPS_9,
    EPS_10,
    ETA_E_MAX,
    ETA_E_MIN,
    ETA_I_MAX,
    ETA_I_MAX_FP,
    NORMAL_E_MAX_EBE,
    NORMAL_E_MAX_EBE_FP,
    NORMAL_E_MAX_SE,
    NORMAL_E_MAX_SE_FP,
    P_1,
    P_2,
    P_3,
    P_4,
    P_5,
    P_6,
    P_7,
    P_8,
    P_9,
    P_10,
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

#: Distribution for the number of emitted |SEs| at a given |SEEY|.
FURMAN_PIVI_DISTRIBUTIONS = ("Poisson", "Binomial")
#: Probability normalization, *cf* Eqs. (35) and (36) in :cite:`Furman2002`.
FURMAN_PIVI_NORMALIZATIONS = ("incident", "penetrated")

NORMALIZATION_T = Literal["incident", "penetrated"]
DISTRIBUTION_T = Literal["Poisson", "Binomial"]
#: Max number of |SEs|. In Furman and Pivi paper, this is denoted :math:`M`.
M_MAX_SECONDARIES = 10


def at_theta_incidence(
    the: float,
    at_normal: Parameter | float,
    a_1: Parameter | float,
    a_2: Parameter | float,
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
    if abs(the) < tol:
        return (
            at_normal.value if isinstance(at_normal, Parameter) else at_normal
        )

    if abs(the) >= 84.0:
        logging.warning("Relation invalid for angles greater than 84 degrees.")

    return at_normal * (1 + a_1 * math.cos(math.radians(the)) ** a_2)


class FurmanPiviParameters(TypedDict):
    # =========================================================================
    # True secondary emission
    # =========================================================================
    normal_e_max_se: Parameter
    normal_delta_max: Parameter
    t_1: Parameter
    t_2: Parameter
    t_3: Parameter
    t_4: Parameter
    s: Parameter
    eps_1: Parameter
    eps_2: Parameter
    eps_3: Parameter
    eps_4: Parameter
    eps_5: Parameter
    eps_6: Parameter
    eps_7: Parameter
    eps_8: Parameter
    eps_9: Parameter
    eps_10: Parameter
    p_1: Parameter
    p_2: Parameter
    p_3: Parameter
    p_4: Parameter
    p_5: Parameter
    p_6: Parameter
    p_7: Parameter
    p_8: Parameter
    p_9: Parameter
    p_10: Parameter

    # =========================================================================
    # EBE
    # =========================================================================
    normal_e_max_ebe: Parameter
    eta_e_max: Parameter
    sigma: Parameter
    eta_e_min: Parameter
    W: Parameter
    p: Parameter
    e_1: Parameter
    e_2: Parameter

    # =========================================================================
    # IBE
    # =========================================================================
    e_ibe: Parameter
    eta_i_max: Parameter
    r: Parameter
    q: Parameter
    r_1: Parameter
    r_2: Parameter


INITIAL_FURMAN_PIVI_PARAMETERS = {
    # =====================================================================
    # Secondary Electrons (or "True Secondaries")
    # =====================================================================
    "normal_e_max_se": {
        "markdown": NORMAL_E_MAX_SE,
        "unit": "eV",
        "value": 310.0,
        "lower_bound": 0.0,
        "description": "Energy where SEEY is maximum at normal incidence.",
        "furman_pivi_notation": NORMAL_E_MAX_SE_FP,
    },
    "normal_delta_max": {
        "markdown": DELTA_MAX,
        "unit": "1",
        "value": 1.22,
        "lower_bound": 0.0,
        "description": "Maximum SEEY at normal incidence.",
        "furman_pivi_notation": DELTA_MAX_FP,
    },
    "t_1": {
        "markdown": T1,
        "unit": "1",
        "value": 0.66,
        "description": "Scaling parameter in SEEY impact angle fit.",
    },
    "t_2": {
        "markdown": T2,
        "unit": "1",
        "value": 0.80,
        "description": "Exponent parameter in SEEY impact angle fit.",
    },
    "t_3": {
        "markdown": T3,
        "unit": "1",
        "value": 0.70,
        "description": "Scaling parameter in SEEY energy impact angle fit.",
    },
    "t_4": {
        "markdown": T4,
        "unit": "1",
        "value": 1.0,
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
        "markdown": EPS_1,
        "unit": "1",
        "value": 3.9,
        "lower_bound": 0.0,
        "description": (
            "Scale parameter for n=1 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "eps_2": {
        "markdown": EPS_2,
        "unit": "1",
        "value": 6.2,
        "lower_bound": 0.0,
        "description": (
            "Scale parameter for n=2 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "eps_3": {
        "markdown": EPS_3,
        "unit": "1",
        "value": 13.0,
        "lower_bound": 0.0,
        "description": (
            "Scale parameter for n=3 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "eps_4": {
        "markdown": EPS_4,
        "unit": "1",
        "value": 8.8,
        "lower_bound": 0.0,
        "description": (
            "Scale parameter for n=4 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "eps_5": {
        "markdown": EPS_5,
        "unit": "1",
        "value": 6.25,
        "lower_bound": 0.0,
        "description": (
            "Scale parameter for n=5 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "eps_6": {
        "markdown": EPS_6,
        "unit": "1",
        "value": 2.25,
        "lower_bound": 0.0,
        "description": (
            "Scale parameter for n=6 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "eps_7": {
        "markdown": EPS_7,
        "unit": "1",
        "value": 9.20,
        "lower_bound": 0.0,
        "description": (
            "Scale parameter for n=7 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "eps_8": {
        "markdown": EPS_8,
        "unit": "1",
        "value": 5.3,
        "lower_bound": 0.0,
        "description": (
            "Scale parameter for n=8 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "eps_9": {
        "markdown": EPS_9,
        "unit": "1",
        "value": 17.8,
        "lower_bound": 0.0,
        "description": (
            "Scale parameter for n=9 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "eps_10": {
        "markdown": EPS_10,
        "unit": "1",
        "value": 10.0,
        "lower_bound": 0.0,
        "description": (
            "Scale parameter for n=10 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "p_1": {
        "markdown": P_1,
        "unit": "1",
        "value": 1.6,
        "lower_bound": 0.0,
        "description": (
            "Shape parameter for n=1 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "p_2": {
        "markdown": P_2,
        "unit": "1",
        "value": 2.0,
        "lower_bound": 0.0,
        "description": (
            "Shape parameter for n=2 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "p_3": {
        "markdown": P_3,
        "unit": "1",
        "value": 1.8,
        "lower_bound": 0.0,
        "description": (
            "Shape parameter for n=3 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "p_4": {
        "markdown": P_4,
        "unit": "1",
        "value": 4.7,
        "lower_bound": 0.0,
        "description": (
            "Shape parameter for n=4 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "p_5": {
        "markdown": P_5,
        "unit": "1",
        "value": 1.8,
        "lower_bound": 0.0,
        "description": (
            "Shape parameter for n=5 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "p_6": {
        "markdown": P_6,
        "unit": "1",
        "value": 2.4,
        "lower_bound": 0.0,
        "description": (
            "Shape parameter for n=6 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "p_7": {
        "markdown": P_7,
        "unit": "1",
        "value": 1.8,
        "lower_bound": 0.0,
        "description": (
            "Shape parameter for n=7 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "p_8": {
        "markdown": P_8,
        "unit": "1",
        "value": 1.8,
        "lower_bound": 0.0,
        "description": (
            "Shape parameter for n=8 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "p_9": {
        "markdown": P_9,
        "unit": "1",
        "value": 2.3,
        "lower_bound": 0.0,
        "description": (
            "Shape parameter for n=9 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    "p_10": {
        "markdown": P_10,
        "unit": "1",
        "value": 1.8,
        "lower_bound": 0.0,
        "description": (
            "Shape parameter for n=10 in the SEs energy spectrum, Eq. (33)."
        ),
    },
    # =====================================================================
    # Elastically Backscattered Electrons (or "Reflected")
    # =====================================================================
    "normal_e_max_ebe": {
        "markdown": NORMAL_E_MAX_EBE,
        "unit": "eV",
        "value": 0.0,
        "lower_bound": 0.0,
        "is_locked": True,
        "description": "Energy where EBEEY is maximum at normal incidence.",
        "furman_pivi_notation": NORMAL_E_MAX_EBE_FP,
    },
    "eta_e_max": {
        "markdown": ETA_E_MAX,
        "unit": "1",
        "value": 0.5,
        "lower_bound": 0.0,
        "upper_bound": 1.0,
        "description": (
            "EBEEY maximum. "
            f"Must be bigger than :math:`{ETA_E_MIN}`, which is currently "
            "not enforced."
        ),
    },
    "sigma": {
        "markdown": SIGMA,
        "unit": "1",
        "value": 1.9,
        "lower_bound": 0.1,  # TODO: check min/max values
        "upper_bound": 10.0,
        "description": "Parameter in EBE PDF function.",
    },
    "eta_e_min": {
        "markdown": ETA_E_MIN,
        "unit": "1",
        "value": 0.07,
        "lower_bound": 0.0,
        "upper_bound": 0.2,
        "description": (
            "EBEEY asymptotic minimum. Must be lower than "
            rf":math:`{ETA_E_MAX}`, which is currently not enforced."
        ),
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
        "description": "Scaling parameter in EBEEY impact angle fit.",
    },
    "e_2": {
        "markdown": E2,
        "unit": "1",
        "value": 2.0,
        "description": "Exponent parameter in EBEEY impact angle fit.",
    },
    # =====================================================================
    # Inelastically Backscattered Electrons (or "Rediffused")
    # =====================================================================
    "e_ibe": {
        "markdown": E_IBE,
        "unit": "eV",
        "value": 40.0,
        "lower_bound": 0.0,
        "description": (
            "Normal incidence characteristic energy. At this energy, IBEEY"
            r" has reached :math:`63.2\,\%` of its asymptotic "
            "maximum."
        ),
        "furman_pivi_notation": E_IBE_FP,
    },
    "eta_i_max": {
        "markdown": ETA_I_MAX,
        "unit": "1",
        "value": 0.74,
        "lower_bound": 0.0,
        "upper_bound": 1.0,
        "description": "IBEEY asymptotic maximum.",
        "furman_pivi_notation": ETA_I_MAX_FP,
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
        "description": "Parameter in the IBEEY PDF function.",
    },
    "r_1": {
        "markdown": R1,
        "unit": "1",
        "value": 0.26,
        "description": "Scaling parameter in IBEEY impact angle fit.",
    },
    "r_2": {
        "markdown": R2,
        "unit": "1",
        "value": 2.0,
        "description": "Exponent parameter in IBEEY impact angle fit.",
    },
}
