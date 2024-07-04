"""Define functions to extract some characteristics from emission data."""

import numpy as np
import pandas as pd

from eemilib.loader.loader import EY_col1, EY_colnorm


def trim(
    normal_ey: pd.DataFrame,
    min_e: float = -1.0,
    max_e: float = -1.0,
) -> pd.DataFrame:
    """Remove EY outside of given energy range (if provided).

    Parameters
    ----------
    normal_ey : pd.DataFrame
        Holds normal emission yield. Columns are ``EY_col1`` (energy, stored
        by increasing values) and ``EY_colnorm`` (normal EY).
    min_e : float, optional
        Energy at which the output dataframe should start (if provided). The
        default is a negative value, in which case the output dataframe is not
        bottom-trimed.
    max_e : float, optional
        Energy at which the output dataframe should end (if provided). The
        default is a negative value, in which case the output dataframe is not
        top-trimed.

    Returns
    -------
    trimed : pd.DataFrame
        ``normal_ey`` but with energies ranging only from ``min_e`` to
        ``max_e``.

    """
    if min_e >= 0:
        trimed = normal_ey[normal_ey[EY_col1] >= min_e]
        assert isinstance(trimed, pd.DataFrame)
        normal_ey = trimed
    if max_e >= 0:
        trimed = normal_ey[normal_ey[EY_col1] <= max_e]
        assert isinstance(trimed, pd.DataFrame)
        normal_ey = trimed

    return normal_ey.reset_index(drop=True)


def resample(ey: pd.DataFrame, n_interp: int = -1) -> pd.DataFrame:
    """Return the emission yield with more points and/or updated limits."""
    if n_interp < 0:
        return ey
    new_ey = {
        EY_col1: np.linspace(ey[EY_col1].min(), ey[EY_col1].max(), n_interp)
    }
    for col_name in ey.columns:
        if col_name == EY_col1:
            continue
        new_ey[col_name] = np.interp(
            x=new_ey[EY_col1],
            xp=ey[EY_col1],
            fp=ey[col_name],
        )

    return pd.DataFrame(new_ey)


def get_ec1(
    normal_ey: pd.DataFrame,
    min_e: float = -1.0,
    max_e: float = -1.0,
    n_interp: int = -1,
    **kwargs,
) -> float:
    """Interpolate the energy vs teey array and give the E_c1."""
    if min_e < 0.0:
        min_e = np.nanmin()
    ene_interp = np.linspace(0.0, 500.0, 10001)

    # Whith Vaughan, and with seey_low = 1, avoid detecting ec1 below E0
    if min_e is not None:
        ene_interp = np.linspace(min_e + 1.0, 500.0, 1001)

    teey_interp = np.interp(ene_interp, ey[:, 0], ey[:, 1], left=0.0)
    idx = np.argmin(np.abs(teey_interp - 1.0))
    ec1 = ene_interp[idx]
    return ec1


def get_max(teey: np.ndarray, E0: float = None, **kwargs) -> (float, float):
    """Interpolate the energy vs teey array and give the E and sigma max."""
    ene_interp = np.linspace(0.0, 1e3, 10001)

    # Whith Vaughan, and with seey_low = 1, avoid detecting ec1 below E0
    if E0 is not None:
        ene_interp = np.linspace(E0 + 1.0, 1e3, 1001)

    teey_interp = np.interp(ene_interp, teey[:, 0], teey[:, 1], left=0.0)
    idx = np.argmax(teey_interp)
    return ene_interp[idx], teey_interp[idx]
