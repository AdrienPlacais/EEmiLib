r"""Create the Furman and Pivi model, to compute |SEEY|, |EBEEY|, |IBEEY|.

Also energy emission distributions. Even angular distributions?

This is an empirical model developed by Dionne :cite:`Furman2002,Furman2013`.

"""

import logging
import math
from typing import Any, TypedDict

from eemilib.core.model_config import ModelConfig
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.model.model import Model
from eemilib.model.parameter import Parameter
from eemilib.util.markdown import (
    DELTA_MAX,
    DELTA_MAX_FP,
    E1,
    E2,
    NORMAL_E_MAX_EBE,
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


class FurmanPiviParameters(TypedDict):
    # =========================================================================
    # True secondary emission
    # =========================================================================
    # Emax for normal SEY. could also be E_ts with a ^
    normal_e_max_ts: Parameter
    # normal SEYmax. could also be delta_ts with a ^
    normal_delta_max: Parameter
    s: Parameter
    t1: Parameter
    t2: Parameter
    t3: Parameter
    t4: Parameter
    # Resulting epsN: 1, 2
    # Resulting pN: 1, 2

    # =========================================================================
    # EBE
    # =========================================================================
    normal_e_max_ebe: Parameter
    W: Parameter
    e1: Parameter
    e2: Parameter
    P1_hat: Parameter
    P1_inf_ebe: Parameter
    p: Parameter

    # =========================================================================
    # IBE
    # =========================================================================
    normal_e_max_ibe: Parameter
    P1_inf_ibe: Parameter
    r: Parameter
    q: Parameter
    r1: Parameter
    r2: Parameter


class FurmanPivi(Model):
    """Define the Furman and Pivi model :cite:`Furman2002,Furman2013`."""

    emission_data_types = ["Emission Yield"]
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
        "normal_seey_max": {
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
            "lower_bound": 0.0,
            "upper_bound": 1.0,  # TODO: check min/max values
            "description": "Parameter in the D function.",
        },
        # =====================================================================
        # Elastically Backscattered Electrons (or "Reflected")
        # =====================================================================
        "normal_e_max_ebe": {
            "markdown": NORMAL_E_MAX_EBE,
            "unit": "eV",
            "value": 00.0,
            "lower_bound": 0.0,
            "description": "Energy where EBEEY is maximum at normal incidence.",
            "is_locked": True,
            "furman_pivi_notation": NORMAL_E_MAX_IBE_FP,
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

    def __init__(
        self,
        parameters_values: dict[str, Any] | None = None,
    ) -> None:
        r"""Instantiate the object.

        Parameters
        ----------
        parameters_values :
            Contains name of parameters and associated value. If provided, will
            override the default values set in ``initial_parameters``.

        """
        super().__init__(url_doc_override="manual/models/furman_pivi")

        for parameters_kwargs in self.initial_parameters.values():
            _add_furman_pivi_notation(parameters_kwargs)

        self.parameters: FurmanPiviParameters = {  # type: ignore
            name: Parameter(**kwargs)  # type: ignore
            for name, kwargs in self.initial_parameters.items()
        }

        self._generate_parameter_docs()
        if parameters_values is not None:
            self.set_parameters_values(parameters_values)

        self._func = None
        raise ValueError("_func should not be None")

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
def delta_max(
    the: float,
    normal_delta_max: Parameter,
    t1: Parameter,
    t2: Parameter,
    tol: float = 1e-8,
    **kwargs,
) -> float:
    r"""Compute value of |SEEY| peak at non-normal incidence.

    .. math::
       \delta_{\mathrm{max}}(\theta) = \delta_{\mathrm{max}}(\theta=0)
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
        the=the, at_normal=normal_delta_max, a_1=t1, a_2=t2, tol=tol, **kwargs
    )


def e_max_se(
    the: float,
    normal_e_max_se: Parameter,
    t3: Parameter,
    t4: Parameter,
    tol: float = 1e-8,
    **kwargs,
) -> float:
    r"""Compute position of |SEEY| peak at non-normal incidence.

    .. math::
       E_{\mathrm{max},\,\delta}(\theta) = E_{\mathrm{max},\,\delta}(\theta=0)
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
        the=the, at_normal=normal_e_max_se, a_1=t3, a_2=t4, tol=tol, **kwargs
    )


def _d_func(x: float, s: Parameter) -> float:
    r"""Define function used in |SEEY|.

    .. math::
       D(x) = \frac{sx}{s-1+x^s}

    where :math:`s` is also a Furman and Pivi parameter.

    """
    s_val = s.value
    return s_val * x / (s_val - 1 + x**s_val)


def seey(
    ene: float,
    the: float,
    normal_e_max_se: Parameter,
    normal_delta_max: Parameter,
    s: Parameter,
    t1: Parameter,
    t2: Parameter,
    t3: Parameter,
    t4: Parameter,
    tol: float = 1e-8,
    **kwargs,
) -> float:
    r"""Compute |SEEY|.

    .. math::
       \delta(E, \theta) = \delta_{\mathrm{max}}(\theta)
       D\left( \frac{E}{E_{\mathrm{max},\,\delta}(\theta)} \right)

    """
    seey_max = delta_max(
        the=the,
        normal_delta_max=normal_delta_max,
        t1=t1,
        t2=t2,
        tol=tol,
        **kwargs,
    )
    e_max = e_max_se(
        normal_e_max_se=normal_e_max_se,
        the=the,
        t3=t3,
        t4=t4,
        tol=tol,
        **kwargs,
    )

    return seey_max * _d_func(ene / e_max, s=s)


# =============================================================================
# EBEs
# =============================================================================
def ebeey_normal(
    ene: float,
    normal_e_max_ebe: Parameter,
    P1_hat: Parameter,
    P1_inf_ebe: Parameter,
    W: Parameter,
    p: Parameter,
) -> float:
    r"""Compute |EBEEY| at normal incidence.

    .. math::
       \eta_e(E,\,\theta=0) =
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
    return P1_inf_ebe.value + (P1_hat.value - P1_inf_ebe.value) * math.exp(
        -_in_exp / p.value
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
            x(E,\,\theta=0)
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


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += FurmanPivi._generate_parameter_docs()
