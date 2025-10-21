"""Define functions to extract some characteristics from emission data."""

import numpy as np
import pandas as pd
from eemilib.util.constants import col_energy, col_normal


def trim(
    normal_ey: pd.DataFrame,
    min_e: float = -1.0,
    max_e: float = -1.0,
) -> pd.DataFrame:
    """Remove EY outside of given energy range (if provided).

    Parameters
    ----------
    normal_ey :
        Holds normal emission yield. Columns are ``EY_col1`` (energy, stored
        by increasing values) and ``EY_colnorm`` (normal EY).
    min_e :
        Energy at which the output dataframe should start (if provided). The
        default is a negative value, in which case the output dataframe is not
        bottom-trimed.
    max_e :
        Energy at which the output dataframe should end (if provided). The
        default is a negative value, in which case the output dataframe is not
        top-trimed.

    Returns
    -------
        ``normal_ey`` but with energies ranging only from ``min_e`` to
        ``max_e``.

    """
    if min_e >= 0:
        trimed = normal_ey[normal_ey[col_energy] >= min_e]
        assert isinstance(trimed, pd.DataFrame)
        normal_ey = trimed
    if max_e >= 0:
        trimed = normal_ey[normal_ey[col_energy] <= max_e]
        assert isinstance(trimed, pd.DataFrame)
        normal_ey = trimed

    return normal_ey.reset_index(drop=True)


def resample(ey: pd.DataFrame, n_interp: int = -1) -> pd.DataFrame:
    """Return the emission yield with more points and/or updated limits."""
    if n_interp < 0:
        return ey
    new_ey = {
        col_energy: np.linspace(
            ey[col_energy].min(), ey[col_energy].max(), n_interp
        )
    }
    for col_name in ey.columns:
        if col_name == col_energy:
            continue
        new_ey[col_name] = np.interp(
            x=new_ey[col_energy],
            xp=ey[col_energy],
            fp=ey[col_name],
        )

    return pd.DataFrame(new_ey)


def get_emax_eymax(normal_ey: pd.DataFrame) -> tuple[float, float]:
    """Get energy and max emission yields."""
    ser_max = normal_ey.loc[normal_ey[col_normal].idxmax()]
    e_max = ser_max[col_energy]
    ey_max = ser_max[col_normal]
    return e_max, ey_max


def get_crossover_energies(
    normal_ey: pd.DataFrame, e_max: float, min_e: float = 10.0
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Compute first and second crossover energies.

    Parameters
    ----------
    normal_ey :
        Holds energy of PEs as well as emission yield at nominal incidence.
    e_max :
        Energy of maximum emission yield. Used to discriminate
        :math:`E_{c1}` from :math:`E_{c2}`.
    min_e :
        Energy under which :math:`E_{c1}` is not searched. It is useful if
        emission yield data comes from a model which sets the emission
        yield to unity at very low energies (eg some implementations of
        Vaughan). The default value is 10 eV.

    Returns
    -------
    tuple[float, float]
        First crossover energy, corresponding emission yield.
    tuple[float, float]
        Second crossover energy, corresponding emission yield.

    """
    first_half = trim(normal_ey, min_e=min_e, max_e=e_max)
    ser_ec1 = first_half.loc[(first_half[col_normal] - 1.0).abs().idxmin()]
    ec1 = ser_ec1[col_energy]
    ey_ec1 = ser_ec1[col_normal]

    second_half = trim(normal_ey, min_e=e_max)
    ser_ec2 = second_half.loc[(second_half[col_normal] - 1.0).abs().idxmin()]
    ec2 = ser_ec2[col_energy]
    ey_ec2 = ser_ec2[col_normal]

    return (ec1, ey_ec1), (ec2, ey_ec2)


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
