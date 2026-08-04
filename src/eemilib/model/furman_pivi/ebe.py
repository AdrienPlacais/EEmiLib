"""This module define functions related to |EBEs|."""

import numpy as np
from eemilib.emission_data.emission_energy_distribution import (
    EBEEmissionEnergyDistribution,
)
from eemilib.model.furman_pivi.helper import remove_extrema
from eemilib.model.furman_pivi.physics import at_theta_incidence
from eemilib.model.parameter import Parameter
from eemilib.util.constants import col_energy
from numpy.typing import NDArray
from scipy.special import erf

#: Parameters used for calculation of |EBEEY| at normal incidence.
NORMAL_EBEEY_PARAM_KEYS = (
    "normal_e_max_ebe",
    "eta_e_max",
    "eta_e_min",
    "W",
    "p",
)
#: Additional parameters used for calculation of |EBEEY| at oblique incidence.
OBLIQUE_EBEEY_PARAM_KEYS = ("e_1", "e_2")
#: Additional parameters used for energy distribution calculation.
EBE_DISTRIB_PARAMETERS = ("sigma",)


def ebeey_normal(
    ene: float,
    normal_e_max_ebe: Parameter | float,
    eta_e_max: Parameter | float,
    eta_e_min: Parameter | float,
    W: Parameter | float,
    p: Parameter | float,
    **kwargs,
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
    _in_exp = (abs(ene - normal_e_max_ebe) / W) ** p
    return eta_e_min + (eta_e_max - eta_e_min) * np.exp(-_in_exp / p)


def ebeey(
    ene: float,
    the: float,
    normal_e_max_ebe: Parameter | float,
    eta_e_max: Parameter | float,
    eta_e_min: Parameter | float,
    W: Parameter | float,
    p: Parameter | float,
    e_1: Parameter | float,
    e_2: Parameter | float,
    **kwargs,
) -> float:
    """Compute |EBEEY|.

    First, we compute |EBEEY| at normal incidence using :func:`ebeey_normal`.
    Then, we compute it at provided incidence angle using
    :func:`.physics.at_theta_incidence`.

    """
    return at_theta_incidence(
        the=the,
        at_normal=ebeey_normal(
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
    normal_e_max_ebe: Parameter | float,
    eta_e_max: Parameter | float,
    eta_e_min: Parameter | float,
    W: Parameter | float,
    p: Parameter | float,
    e_1: Parameter | float,
    e_2: Parameter | float,
    sigma: Parameter | float,
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
        * np.exp(-((e_pe - emission_energies) ** 2) / (2 * sigma**2))
        / (np.sqrt(2 * np.pi) * sigma * erf(e_pe / (np.sqrt(2) * sigma)))
    )


def double_peak(
    share: EBEEmissionEnergyDistribution, double_only_peak_value: bool = False
) -> EBEEmissionEnergyDistribution:
    r"""Return a copy of ``share`` with its peak height doubled.

    Follows the fitting convention described in :cite:`Furman2002` (text
    following Eq. 27): since the analytic |EBE| curve, Eq. (26), is
    truncated exactly at its peak (:math:`E=E_0`), only "half" of the
    physical peak is captured when integrating over :math:`[0, E_0]`.
    Doubling the measured peak's height before fitting compensates for
    this, so that the fitted area properly matches :math:`\delta_e`.

    Parameters
    ----------
    share :
        Decomposed |EBEEY| share.

    Return
    ------
        A new :class:`.EBEEmissionEnergyDistribution`, identical to
        ``share`` except for the doubled peak.

    """
    doubled_data = share.data.copy()
    data_columns = [c for c in doubled_data.columns if c != col_energy]
    if double_only_peak_value:
        i_peak = share.i_peak
        doubled_data.loc[i_peak, data_columns] *= 2.0
    else:
        doubled_data.loc[:, data_columns] *= 2.0

    return EBEEmissionEnergyDistribution(
        doubled_data, e_pe=share.e_pe, norm=1.0
    )
