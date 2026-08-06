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


def add_furman_pivi_notation(
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
            f"Denoted :math:`{furman_pivi_notation}` by Furman and Pivi.",
        )
    )
