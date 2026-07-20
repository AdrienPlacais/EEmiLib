"""Define |SEs| related functions in Furman and Pivi model."""

import logging
import math
from typing import Callable

import numpy as np
from eemilib.model.furman_pivi.ebe import ebeey
from eemilib.model.furman_pivi.helper import remove_extrema
from eemilib.model.furman_pivi.ibe import ibeey
from eemilib.model.furman_pivi.physics import (
    DISTRIBUTION_T,
    M_MAX_SECONDARIES,
    NORMALIZATION_T,
    at_theta_incidence,
)
from eemilib.model.parameter import Parameter
from numpy.typing import NDArray
from scipy.special import gammainc
from scipy.stats import binom, poisson


def _seey_max(
    the: float,
    normal_delta_max: Parameter,
    t_1: Parameter,
    t_2: Parameter,
    tol: float = 1e-8,
    **kwargs,
) -> float:
    r"""Compute value of |SEEY| peak at non-normal incidence.

    .. math::
       \delta_{\mathrm{max}}(\theta) = \delta_{\mathrm{max}}(\theta=0\degree)
       \left[1 + t_1 \left(1 - \cos^{t_2}\theta \right) \right]

    In Furman and Pivi paper :cite:`Furman2002`, this is Eq. (48a):

    .. math::
       \hat \delta(\theta_0) = \hat \delta_{\mathrm{ts}}
       \left[1 + t_1 \left(1 - \cos^{t_2}\theta_0 \right) \right]

    See Also
    --------
    :func:`.at_theta_incidence`

    """
    return at_theta_incidence(
        the=the,
        at_normal=normal_delta_max,
        a_1=t_1,
        a_2=t_2,
        tol=tol,
        **kwargs,
    )


def _e_max_se(
    the: float,
    normal_e_max_se: Parameter,
    t_3: Parameter,
    t_4: Parameter,
    tol: float = 1e-8,
    **kwargs,
) -> float:
    r"""Compute position of |SEEY| peak at non-normal incidence.

    .. math::
       E_{\mathrm{max},\,\delta}(\theta) = E_{\mathrm{max},\,\delta}(\theta=0\degree)
       \left[1 + t_3 \left(1 - \cos^{t_4}\theta \right) \right]

    In Furman and Pivi paper :cite:`Furman2002`, this is Eq. (48b):

    .. math::
       \hat E(\theta_0) = \hat E_{\mathrm{ts}}
       \left[1 + t_3 \left(1 - \cos^{t_4}\theta_0 \right) \right]

    See Also
    --------
    :func:`.at_theta_incidence`

    """
    return at_theta_incidence(
        the=the, at_normal=normal_e_max_se, a_1=t_3, a_2=t_4, tol=tol, **kwargs
    )


def _d_func(x: float, s: Parameter) -> float:
    r"""Define function used in |SEEY|.

    .. math::
       D(x) = \frac{sx}{s-1+x^s}

    where :math:`s` is an adjustable parameter strictly greater than unity.

    In Furman and Pivi paper :cite:`Furman2002`, this is Eq. (32).

    """
    s_val = s.value
    return s_val * x / (s_val - 1 + x**s_val)


def seey(
    ene: float,
    the: float,
    normal_e_max_se: Parameter,
    normal_delta_max: Parameter,
    s: Parameter,
    t_1: Parameter,
    t_2: Parameter,
    t_3: Parameter,
    t_4: Parameter,
    tol: float = 1e-8,
    **kwargs,
) -> float:
    r"""Compute |SEEY|.

    .. math::
       \delta(E, \theta) = \delta_{\mathrm{max}}(\theta)
       D\left( \frac{E}{E_{\mathrm{max},\,\mathrm{SE}}(\theta)} \right)

    where :math:`\delta_{\mathrm{max}}(\theta)` is calculated using
    :func:`_seey_max` and :math:`E_{\mathrm{max},\,\mathrm{SE}}(\theta)` with
    :func:`_e_max_se`.

    In Furman and Pivi paper :cite:`Furman2002`, this is Eq. (31):

    .. math::
       \delta_{ts} = \hat \delta(\theta_0)D\left[E_0/\hat E(\theta_0)\right]

    """
    _delta_max = _seey_max(
        the=the,
        normal_delta_max=normal_delta_max,
        t_1=t_1,
        t_2=t_2,
        tol=tol,
        **kwargs,
    )
    e_max = _e_max_se(
        normal_e_max_se=normal_e_max_se,
        the=the,
        t_3=t_3,
        t_4=t_4,
        tol=tol,
        **kwargs,
    )

    return _delta_max * _d_func(ene / e_max, s=s)


PROBA_EMIT_N_SE = Callable[[float, int], float]


def _p_n_se(
    n: int,
    delta: float,
    eta_e: float,
    eta_i: float,
    proba_emit_n_se: PROBA_EMIT_N_SE,
    normalization: NORMALIZATION_T,
) -> float:
    r"""Compute probability to emit ``n`` |SEs|.

    Dispatches on ``normalization``:

    - ``"incident"``: :math:`P_{n,\,se}` is taken directly from
      ``proba_emit_n_se`` applied to :math:`\delta`, *cf* Eqs. (37)/(38) in
      :cite:`Furman2002`.
    - ``"penetrated"``: :math:`P_{n,\,se} = (1 - \eta_e - \eta_i)
      P^\prime_{n,\,se}`, where :math:`P^\prime_{n,\,se}` is
      ``proba_emit_n_se`` applied to :math:`\delta^\prime = \delta / (1 -
      \eta_e - \eta_i)`, *cf* Eqs. (39), (42), (45)/(46).

    Parameters
    ----------
    n :
        Number of |SEs|.
    delta :
        |SEEY| (:math:`\delta_{ts}` in :cite:`Furman2002`).
    eta_e :
        |EBEEY| (:math:`\delta_e` in :cite:`Furman2002`).
    eta_i :
        |IBEEY| (:math:`\delta_r` in :cite:`Furman2002`).
    proba_emit_n_se :
        Function computing probability to emit ``n`` |SEs|, *cf*
        :func:`set_number_of_secondaries_probability_function`.
    normalization :
        Selects Eq. (37)/(38) (``"incident"``) or Eq. (39), (42), (45)/(46)
        (``"penetrated"``).

    Return
    ------
        :math:`P_{n,\,se}` (:math:`P_{n,\,ts}` in :cite:`Furman2002`).

    """
    if normalization == "incident":
        return proba_emit_n_se(delta, n)

    available_fraction = 1.0 - eta_e - eta_i
    delta_prime = delta / available_fraction
    return available_fraction * proba_emit_n_se(delta_prime, n)


# TODO: to implement
def _p_n(
    n: int,
    delta: float,
    eta_e: float,
    eta_i: float,
    proba_emit_n_se: PROBA_EMIT_N_SE,
    normalization: NORMALIZATION_T,
) -> float:
    r"""Compute the overall :math:`P_n`, combining all electron types.

    Applies the mutual-exclusion assumption, Eq. (21) in :cite:`Furman2002`:

    - :math:`n \geq 2`: :math:`P_n = P_{n,\,se}`.
    - :math:`n = 1`: :math:`P_1 = P_{1,\,se} + \eta_e + \eta_i`.
    - :math:`n = 0`: :math:`P_0 = P_{0,\,se} - \eta_e - \eta_i` when
      ``normalization`` is ``"incident"`` (Eq. 35a); :math:`P_0 = P_{0,\,se}`
      when it is ``"penetrated"`` (Eq. 43a).

    Parameters
    ----------
    n :
        Number of |EEs|.
    delta :
        |SEEY| (:math:`\delta_{ts}` in :cite:`Furman2002`).
    eta_e :
        |EBEEY| (:math:`\delta_e` in :cite:`Furman2002`).
    eta_i :
        |IBEEY| (:math:`\delta_r` in :cite:`Furman2002`).
    proba_emit_n_se :
        Function computing probability to emit ``n`` |SEs|, *cf*
        :func:`set_number_of_secondaries_probability_function`.
    normalization :
        Selects Eq. (35) (``"incident"``) or Eq. (43) (``"penetrated"``).

    Return
    ------
        :math:`P_n`.

    """
    p_n_se = _p_n_se(n, delta, eta_e, eta_i, proba_emit_n_se, normalization)

    if n == 0:
        if normalization == "incident":
            return p_n_se - eta_e - eta_i
        return p_n_se

    if n == 1:
        return p_n_se + eta_e + eta_i

    return p_n_se


def _regularized_incomplete_gamma(
    a: float, x: NDArray[np.float64]
) -> NDArray[np.float64]:
    r"""Compute the regularized lower incomplete gamma function :math:`P(a,x)`.

    Thin wrapper around `gammainc`, handling the :math:`a=0` edge case with the
    convention :math:`P(0,\,x) = 1` for :math:`x \geq 0`, stated in Appendix A
    of :cite:`Furman2002` (just below Eq. (A8)). `gammainc` does not support
    ``a = 0`` directly.

    Parameters
    ----------
    a :
        Shape parameter.
    x :
        Upper integration bound(s). Values are clipped to be non-negative,
        since callers may evaluate this outside the physically valid range
        (the result is expected to be masked out separately in that case).

    Return
    ------
        :math:`P(a, x)`.

    """
    x_clipped = np.clip(x, 0.0, None)
    if a == 0.0:
        return np.ones_like(x_clipped)
    return gammainc(a, x_clipped)


def set_number_of_secondaries_probability_function(
    model: DISTRIBUTION_T = "Poisson",
) -> PROBA_EMIT_N_SE:
    """Set the function that computes probability to emit ``n`` secondaries.

    This let you choose between the two propositions in Furman and Pivi paper
    :cite:`Furman2002`, *cf* Eqs. (37) and (38).

    Parameters
    ----------
    model :
        Name of the model to use.

    Return
    ------
        A function that takes in the |SEEY| and the |SEs|, and returns the
        probability to emit this number of |SEs|.

    """

    if model == "Binomial":

        def probability(seey: float, n: int) -> float:
            return float(
                binom.pmf(n, M_MAX_SECONDARIES, seey / M_MAX_SECONDARIES)
            )

        return probability

    if model != "Poisson":
        logging.warning(
            f"Wrong model for number of emitted electrons. {model = } should "
            f"be in {DISTRIBUTION_T}. Fall back to "
            "'Poisson' model."
        )

    def probability(seey: float, n: int) -> float:
        return float(poisson.pmf(n, seey))

    return probability


def se_energy_distribution(
    e_pe: float,
    the: float,
    emission_energies: NDArray[np.float64],
    p_ns: list[Parameter],
    eps_ns: list[Parameter],
    proba_emit_n_se: PROBA_EMIT_N_SE,
    normalization: NORMALIZATION_T,
    **kwargs,
) -> NDArray[np.float64]:
    r"""Compute the aggregate |SE| emitted-energy spectrum.

    This is Eq. (52) in Furman and Pivi paper :cite:`Furman2002`:

    .. math::
       \frac{d\delta_{ts}}{dE} = \sum_{n=1}^{n_\mathrm{max}}
            \frac{
                n\,P_{n,\,ts}(E_0)\,(E/\varepsilon_n)^{p_n-1}
                \mathrm{e}^{-E/\varepsilon_n}
            }{
                \varepsilon_n\,\Gamma(p_n)\,P(np_n,\,E_0/\varepsilon_n)
            }
            \times P\left[(n-1)p_n,\,(E_0-E)/\varepsilon_n\right]

    where :math:`P(z,\,x)` is the regularized lower incomplete gamma
    function, computed with :func:`_regularized_incomplete_gamma`, and
    :math:`P_{n,\,ts}(E_0)` is computed with :func:`_p_n_se`.

    In our notation, :math:`\delta_{ts}` is denoted ``delta``, and the sum
    runs over the same ``n`` as the provided ``p_ns``/``eps_ns`` lists (so
    :math:`n_\mathrm{max}` is implicitly ``len(p_ns)``).

    Parameters
    ----------
    e_pe :
        Impact energy of the |PE| in :unit:`eV`.
    the :
        Impact angle of the |PE| in :math:`\degree`.
    emission_energies :
        |SE| emission energies you want the distribution from.
    p_ns :
        List of :math:`p_n` parameters, one per :math:`n`, starting at
        :math:`n=1`.
    eps_ns :
        List of :math:`\varepsilon_n` parameters, one per :math:`n`, starting
        at :math:`n=1`. Must be the same length as ``p_ns``.
    proba_emit_n_se :
        Function computing probability to emit ``n`` |SEs|, *cf*
        :func:`set_number_of_secondaries_probability_function`.
    normalization :
        Selects Eq. (35) (``"incident"``) or Eq. (43) (``"penetrated"``), *cf*
        :func:`_p_n_se`.
    kwargs :
        Furman and Pivi |SEEY|, |EBEEY|, |IBEEY| parameters, passed to
        :func:`seey`, :func:`.furman_pivi.ebe.ebeey`,
        :func:`.furman_pivi.ibe.ibeey` to compute :math:`\delta`,
        :math:`\eta_e`, :math:`\eta_i`.

    Returns
    -------
        Aggregate |SE| emitted-energy spectrum.

    """
    delta = seey(ene=e_pe, the=the, **kwargs)
    eta_e = ebeey(ene=e_pe, the=the, **kwargs)
    eta_i = ibeey(ene=e_pe, the=the, **kwargs)

    spectrum = np.zeros_like(emission_energies)
    for n, (p_n_param, eps_n_param) in enumerate(zip(p_ns, eps_ns), start=1):
        p_n = p_n_param.value
        eps_n = eps_n_param.value

        p_n_se = _p_n_se(
            n, delta, eta_e, eta_i, proba_emit_n_se, normalization
        )

        normalization_term = math.gamma(p_n) * _regularized_incomplete_gamma(
            n * p_n, np.array(e_pe / eps_n)
        )
        shape_term = (emission_energies / eps_n) ** (p_n - 1) * np.exp(
            -emission_energies / eps_n
        )
        tail_term = _regularized_incomplete_gamma(
            (n - 1) * p_n, (e_pe - emission_energies) / eps_n
        )

        spectrum += (
            n * p_n_se * shape_term * tail_term / (eps_n * normalization_term)
        )

    return remove_extrema(e_pe, emission_energies) * spectrum
