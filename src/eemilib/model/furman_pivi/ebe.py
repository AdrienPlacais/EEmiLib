"""This module define functions related to |EBEs|."""

import math

import numpy as np
from eemilib.model.furman_pivi.helper import remove_extrema
from eemilib.model.furman_pivi.physics import at_theta_incidence
from eemilib.model.parameter import Parameter
from numpy.typing import NDArray
from scipy.special import erf


def _ebeey_normal(
    ene: float,
    normal_e_max_ebe: Parameter,
    eta_e_max: Parameter,
    eta_e_min: Parameter,
    W: Parameter,
    p: Parameter,
) -> float:
    r"""Compute |EBEEY| at normal incidence.

    .. math::
       \eta_e(E,\,\theta=0\degree) =
            \eta_{e,\,\mathrm{min}}
            + \left[ \eta_{e,\,\mathrm{max}} - \eta_{e,\,\mathrm{min}} \right]
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
    return eta_e_min.value + (eta_e_max.value - eta_e_min.value) * math.exp(
        -_in_exp / p.value
    )


def ebeey(
    ene: float,
    the: float,
    normal_e_max_ebe: Parameter,
    eta_e_max: Parameter,
    eta_e_min: Parameter,
    W: Parameter,
    p: Parameter,
    e_1: Parameter,
    e_2: Parameter,
    **kwargs,
) -> float:
    """Compute |EBEEY|.

    First, we compute |EBEEY| at normal incidence using :func:`_ebeey_normal`.
    Then, we compute it at provided incidence angle using
    :func:`.physics.at_theta_incidence`.

    """
    return at_theta_incidence(
        the=the,
        at_normal=_ebeey_normal(
            ene=ene,
            normal_e_max_ebe=normal_e_max_ebe,
            eta_e_max=eta_e_max,
            eta_e_min=eta_e_min,
            W=W,
            p=p,
        ),
        a_1=e_1,
        a_2=e_2,
    )


def ebe_energy_distribution(
    e_pe: float,
    the: float,
    emission_energies: NDArray[np.float64],
    normal_e_max_ebe: Parameter,
    eta_e_max: Parameter,
    eta_e_min: Parameter,
    W: Parameter,
    p: Parameter,
    e_1: Parameter,
    e_2: Parameter,
    sigma: Parameter,
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
    e_pe :
        Impact energy of the |PE| in :unit:`eV`.
    theta :
        Impact angle of the |PE| in :unit:`\degree`.
    emission_energies :
        |EBE| emission energies you want the distribution from.
    normal_e_max_ebe :
        Furman and Pivi |EBEEY| parameter.
    eta_e_max :
        Furman and Pivi |EBEEY| parameter.
    eta_e_min :
        Furman and Pivi |EBEEY| parameter.
    W :
        Furman and Pivi |EBEEY| parameter.
    p :
        Furman and Pivi |EBEEY| parameter.
    e_1 :
        Furman and Pivi |EBEEY| parameter.
    e_2 :
        Furman and Pivi |EBEEY| parameter.
    sigma :
        Furman and Pivi |EBE| PDF parameter.
    kwargs :
        Other unused parameters.

    Returns
    -------
        PDF of |EBE|.

    """
    return (
        remove_extrema(e_pe, emission_energies)
        * ebeey(
            ene=e_pe,
            the=the,
            normal_e_max_ebe=normal_e_max_ebe,
            eta_e_max=eta_e_max,
            eta_e_min=eta_e_min,
            W=W,
            p=p,
            e_1=e_1,
            e_2=e_2,
        )
        * 2
        * np.exp(-((e_pe - emission_energies) ** 2) / (2 * sigma.value**2))
        / (
            math.sqrt(2 * math.pi)
            * sigma.value
            * erf(e_pe / (math.sqrt(2) * sigma.value))
        )
    )
