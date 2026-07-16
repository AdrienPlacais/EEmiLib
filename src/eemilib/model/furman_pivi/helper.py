"""Define helpers for array manipulation."""

import numpy as np
from numpy.typing import NDArray


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


def remove_extrema(
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
