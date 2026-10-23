"""Define helpers for array manipulation, better documentation."""

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
    e_pe: float, emission_energies: NDArray[np.float64]
) -> NDArray[np.float64]:
    """Zero out emission energies outside ``[0, e_pe]``.

    Parameters
    ----------
    e_pe :
        Impact energy :math:`E_0`.
    emission_energies :
        Emission energies :math:`E`.

    Returns
    -------
        1 where ``0 <= emission_energies <= e_pe``, 0 elsewhere.

    """
    return _theta_func(emission_energies) * _theta_func(
        e_pe - emission_energies
    )
