"""Define functions related to 'all' population."""

import numpy as np
from eemilib.model.furman_pivi.ebe import (
    EBE_DISTRIB_PARAMETERS,
    NORMAL_EBEEY_PARAM_KEYS,
    OBLIQUE_EBEEY_PARAM_KEYS,
    ebe_energy_distribution,
    ebeey,
    ebeey_normal,
)
from eemilib.model.furman_pivi.ibe import (
    IBE_DISTRIB_PARAMETERS,
    NORMAL_IBEEY_PARAM_KEYS,
    OBLIQUE_IBEEY_PARAM_KEYS,
    ibe_energy_distribution,
    ibeey,
    ibeey_normal,
)
from eemilib.model.furman_pivi.physics import NORMALIZATION_T
from eemilib.model.furman_pivi.se import (
    NORMAL_SEEY_PARAM_KEYS,
    OBLIQUE_SEEY_PARAM_KEYS,
    PROBA_EMIT_N_SE,
    SE_DISTRIB_PARAMETERS,
    se_energy_distribution,
    seey,
    seey_normal,
)
from eemilib.model.parameter import Parameter
from numpy.typing import NDArray

#: Parameters used for calculation of |TEEY| at normal incidence.
NORMAL_TEEY_PARAM_KEYS = (
    NORMAL_SEEY_PARAM_KEYS + NORMAL_EBEEY_PARAM_KEYS + NORMAL_IBEEY_PARAM_KEYS
)
#: Additional parameters used for calculation of |TEEY| at oblique incidence.
OBLIQUE_TEEY_PARAM_KEYS = (
    OBLIQUE_SEEY_PARAM_KEYS
    + OBLIQUE_EBEEY_PARAM_KEYS
    + OBLIQUE_IBEEY_PARAM_KEYS
)
#: Additional parameters used for energy distribution calculation.
ALL_DISTRIB_PARAMETERS = (
    SE_DISTRIB_PARAMETERS + EBE_DISTRIB_PARAMETERS + IBE_DISTRIB_PARAMETERS
)


def teey_normal(
    ene: float,
    normal_e_max_se: Parameter | float,
    normal_delta_max: Parameter | float,
    s: Parameter | float,
    normal_e_max_ebe: Parameter | float,
    eta_e_max: Parameter | float,
    eta_e_min: Parameter | float,
    W: Parameter | float,
    p: Parameter | float,
    e_ibe: Parameter | float,
    eta_i_max: Parameter | float,
    r: Parameter | float,
    **kwargs,
) -> float:
    """Compute |TEEY| at normal incidence."""
    return (
        seey_normal(
            ene,
            normal_e_max_se=normal_e_max_se,
            normal_delta_max=normal_delta_max,
            s=s,
        )
        + ebeey_normal(
            ene,
            normal_e_max_ebe=normal_e_max_ebe,
            eta_e_max=eta_e_max,
            eta_e_min=eta_e_min,
            W=W,
            p=p,
        )
        + ibeey_normal(ene, e_ibe=e_ibe, eta_i_max=eta_i_max, r=r)
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


def all_energy_distribution(
    e_pe: float,
    the: float,
    emission_energies: NDArray[np.float64],
    p_ns: list[Parameter | float],
    eps_ns: list[Parameter | float],
    proba_emit_n_se: PROBA_EMIT_N_SE,
    normalization: NORMALIZATION_T,
    halve_ebe_contribution: bool = False,
    **kwargs,
) -> NDArray[np.float64]:
    r"""Compute the overall emitted-energy spectrum.

    This is Eq. (51) in Furman and Pivi paper :cite:`Furman2002`:

    .. math::
       \frac{d\delta}{dE} = f_{1,\,e} + f_{1,\,r} + \frac{d\delta_{ts}}{dE}

    Each term is already normalized to integrate to its own yield (Eqs. 27,
    30, 50), so no additional weighting is applied here.

    Parameters
    ----------
    e_pe :
        Impact energy of the |PE| in :unit:`eV`.
    the :
        Impact angle of the |PE| in :math:`\degree`.
    emission_energies :
        Emission energies you want the distribution from.
    p_ns :
        List of :math:`p_n` parameters, *cf*
        :func:`.se.se_energy_distribution`.
    eps_ns :
        List of :math:`\varepsilon_n` parameters, *cf*
        :func:`.se.se_energy_distribution`.
    proba_emit_n_se :
        Function computing probability to emit ``n`` |SEs|, *cf*
        :func:`.se.se_energy_distribution`.
    normalization :
        Selects Eq. (35) or Eq. (43), *cf* :func:`.se.se_energy_distribution`.
    halve_ebe_contribution :
        Divide |EBE| contribution by two. Used during the fit in order to
        preserve height of the peak, cf Ref. :cite:`Furman2002`: "When When
        fitting the backscattered peak, as seen in Figs. 5 and 7, we
        deliberately tried to double the height of the experimentally measured
        peak. The reason is that our fitting curve for
        :math:`\mathrm{d}\delta/\mathrm{d}E` stops exactly at the maximum of
        the peak [viz. Eq. (26)], hence by doubling the height we ensure that
        the area under the peak, which we believe to be a better measure of
        :math:`\delta_e`, matches the measured value."

    kwargs :
        Furman and Pivi |SEEY|, |EBEEY|, |IBEEY|, |EBE| and |IBE| PDF
        parameters.

    Returns
    -------
        Overall emitted-energy spectrum.

    """
    ebe_factor = 1.0 if not halve_ebe_contribution else 0.5
    return (
        se_energy_distribution(
            e_pe=e_pe,
            the=the,
            emission_energies=emission_energies,
            p_ns=p_ns,
            eps_ns=eps_ns,
            proba_emit_n_se=proba_emit_n_se,
            normalization=normalization,
            **kwargs,
        )
        + ebe_factor
        * ebe_energy_distribution(
            e_pe=e_pe, the=the, emission_energies=emission_energies, **kwargs
        )
        + ibe_energy_distribution(
            e_pe=e_pe, the=the, emission_energies=emission_energies, **kwargs
        )
    )
