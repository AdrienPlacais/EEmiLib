r"""Create the Furman and Pivi model, to compute |SEEY|, |EBEEY|, |IBEEY|.

Also energy emission distributions. Even angular distributions?

This is an empirical model developed by Dionne :cite:`Furman2022,Furman2013`.

"""

import math
from typing import Any, TypedDict

from eemilib.core.model_config import ModelConfig
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.model.model import Model
from eemilib.model.parameter import Parameter
from eemilib.util.markdown import (
    DELTA_TS,
    E1,
    E2,
    NORMAL_E_MAX_EBE,
    NORMAL_E_MAX_IBE,
    NORMAL_E_MAX_SE,
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
    normal_e_max_ebe: Parameter  # 0.0
    normal_eta_e_max: Parameter  # 1.9
    W: Parameter  # 100
    e1: Parameter  # 0.26
    e2: Parameter  # 2.0
    P1_hat: Parameter  # 0.5
    P1_inf_ebe: Parameter  # 0.7
    p: Parameter  # 0.9

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
    """Define the Furman and Pivi model :cite:`Furman2022,Furman2013`."""

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
        },
        "normal_seey_max": {
            "markdown": DELTA_TS,
            "unit": "1",
            "value": 1.22,
            "lower_bound": 0.0,
            "description": "Maximum SEEY at normal incidence.",
            "is_locked": True,
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
        },
        "p_1_hat": {
            "markdown": P1_INF_EBE,
            "unit": "1",
            "value": 0.5,
            "lower_bound": 0.0,  # TODO: check min/max values
            "description": "Some kind of probability in EBEEY energy fit. Maybe a peak maximum?",  # TODO: check meaning
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
            "description": "Some kind of probability in EBEEY energy fit.",  # TODO: check meaning
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
        super().__init__(url_doc_override="manual/models/dionne")
        self.parameters: FurmanPiviParameters = {  # type: ignore
            name: Parameter(**kwargs)  # type: ignore
            for name, kwargs in self.initial_parameters.items()
        }
        self._generate_parameter_docs()
        if parameters_values is not None:
            self.set_parameters_values(parameters_values)

        self._func = dionne_func

    def evaluate(self, data_matrix: DataMatrix) -> dict[str, float]:
        """Evaluate the quality of the model using Fil criterions.

        Fil criterions :cite:`Fil2016a,Fil2020` are adapted to |TEEY| models.

        """
        return self._evaluate_for_teey_models(data_matrix)


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

    """
    if abs(the) < tol:
        return normal_delta_max.value

    return normal_delta_max.value * (
        1 + t1.value * (1 - math.cos(the) ** t2.value)
    )


def e_max_ts(
    the: float,
    normal_e_max_ts: Parameter,
    t3: Parameter,
    t4: Parameter,
    tol: float = 1e-8,
    **kwargs,
) -> float:
    r"""Compute position of |SEEY| peak at non-normal incidence.

    .. math::
       E_{\mathrm{max},\,\delta}(\theta) = E_{\mathrm{max},\,\delta}(\theta=0)
       \left[1 + t_3 \left(1 - \cos^{t_4}\theta \right) \right]

    """
    if abs(the) < tol:
        return normal_e_max_ts.value

    return normal_e_max_ts.value * (
        1 + t3.value * (1 - math.cos(the) ** t4.value)
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
    normal_e_max_ts: Parameter,
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
    e_max = e_max_ts(
        the=the,
        normal_e_max_ts=normal_e_max_ts,
        t3=t3,
        t4=t4,
        tol=tol,
        **kwargs,
    )

    return seey_max * _d_func(ene / e_max, s=s)


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += FurmanPivi._generate_parameter_docs()
