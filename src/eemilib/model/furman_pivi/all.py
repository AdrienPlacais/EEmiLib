"""Define functions related to 'all' population."""

import numpy as np
from eemilib.model.furman_pivi.ebe import ebe_energy_distribution, ebeey
from eemilib.model.furman_pivi.ibe import ibe_energy_distribution, ibeey
from eemilib.model.furman_pivi.physics import NORMALIZATION_T
from eemilib.model.furman_pivi.se import (
    PROBA_EMIT_N_SE,
    se_energy_distribution,
    seey,
)
from eemilib.model.parameter import Parameter
from numpy.typing import NDArray


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
    impact_energy: float,
    the: float,
    emission_energies: NDArray[np.float64],
    p_ns: list[Parameter],
    eps_ns: list[Parameter],
    proba_emit_n_se: PROBA_EMIT_N_SE,
    normalization: NORMALIZATION_T,
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
    impact_energy :
        Impact energy of the |PE| in :unit:`eV`.
    the :
        Impact angle of the |PE| in :math:`\degree`.
    emission_energies :
        Emission energies you want the distribution from.
    p_ns :
        List of :math:`p_n` parameters, *cf* :func:`se_energy_distribution`.
    eps_ns :
        List of :math:`\varepsilon_n` parameters, *cf*
        :func:`se_energy_distribution`.
    proba_emit_n_se :
        Function computing probability to emit ``n`` |SEs|, *cf*
        :func:`se_energy_distribution`.
    normalization :
        Selects Eq. (35) or Eq. (43), *cf* :func:`se_energy_distribution`.
    kwargs :
        Furman and Pivi |SEEY|, |EBEEY|, |IBEEY|, |EBE| and |IBE| PDF
        parameters.

    Returns
    -------
        Overall emitted-energy spectrum.

    """
    return (
        ebe_energy_distribution(
            impact_energy=impact_energy,
            the=the,
            emission_energies=emission_energies,
            **kwargs,
        )
        + ibe_energy_distribution(
            impact_energy=impact_energy,
            the=the,
            emission_energies=emission_energies,
            **kwargs,
        )
        + se_energy_distribution(
            impact_energy=impact_energy,
            the=the,
            emission_energies=emission_energies,
            p_ns=p_ns,
            eps_ns=eps_ns,
            proba_emit_n_se=proba_emit_n_se,
            normalization=normalization,
            **kwargs,
        )
    )
