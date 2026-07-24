"""This module holds everything |IBE| related."""

import numpy as np
from eemilib.model.furman_pivi.helper import remove_extrema
from eemilib.model.furman_pivi.physics import at_theta_incidence
from eemilib.model.parameter import Parameter
from numpy.typing import NDArray

#: Parameters used for calculation of |IBEEY| at normal incidence.
NORMAL_IBEEY_PARAM_KEYS = ("e_ibe", "eta_i_max", "r")
#: Additional parameters used for calculation of |IBEEY| at oblique incidence.
OBLIQUE_IBEEY_PARAM_KEYS = ("r_1", "r_2")
#: Additional parameters used for energy distribution calculation.
IBE_DISTRIB_PARAMETERS = ("q",)


def ibeey_normal(
    ene: float,
    e_ibe: Parameter | float,
    eta_i_max: Parameter | float,
    r: Parameter | float,
    **kwargs,
) -> float:
    r"""Compute |IBEEY| at normal incidence.

    .. math::
       \eta_i(E,\,\theta=0\degree) =
            \eta_{i,\,\mathrm{max}} \left(
            1 - \mathrm{e}^{
                -\left( E / E_\mathrm{IBE} \right)^r
            }
            \right)

    In Furman and Pivi paper :cite:`Furman2002`, this is Eq. (28):

    .. math::
       \delta_r(E_0,\,0) =
            P_{1,\,r}(\infty) \left(
            1 - \mathrm{e}^{
                -\left( E / E_r \right)^r
            }
            \right)

    """
    return eta_i_max * (1 - np.exp(-((ene / e_ibe) ** r)))


def ibeey(
    ene: float,
    the: float,
    e_ibe: Parameter | float,
    eta_i_max: Parameter | float,
    r: Parameter | float,
    r_1: Parameter | float,
    r_2: Parameter | float,
    **kwargs,
) -> float:
    """Compute |IBEEY|.

    First, we compute |IBEEY| at normal incidence using :func:`_ibeey_normal`.
    Then, we compute it at provided incidence angle using
    :func:`.at_theta_incidence`.

    """
    return at_theta_incidence(
        the=the,
        at_normal=ibeey_normal(ene=ene, e_ibe=e_ibe, eta_i_max=eta_i_max, r=r),
        a_1=r_1,
        a_2=r_2,
    )


def ibe_energy_distribution(
    e_pe: float,
    the: float,
    emission_energies: NDArray[np.float64],
    e_ibe: Parameter | float,
    eta_i_max: Parameter | float,
    r: Parameter | float,
    r_1: Parameter | float,
    r_2: Parameter | float,
    q: Parameter | float,
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
    e_pe :
        Impact energy of the |PE| in :unit:`eV`.
    theta :
        Impact angle of the |PE| in :unit:`\degree`.
    emission_energies :
        |IBE| emission energies you want the distribution from.
    e_ibe :
        Furman and Pivi |IBEEY| parameter.
    eta_i_max :
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
    return (
        remove_extrema(e_pe, emission_energies)
        * ibeey(
            ene=e_pe,
            the=the,
            e_ibe=e_ibe,
            eta_i_max=eta_i_max,
            r=r,
            r_1=r_1,
            r_2=r_2,
        )
        * (q + 1)
        * emission_energies**q
        / e_pe ** (q + 1)
    )
