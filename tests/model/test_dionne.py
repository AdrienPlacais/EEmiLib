"""Define tests for the Dionne model.

The reference values come from three sources:

- closed forms derived by hand from Eqs. (26) and (29) of Dionne (1973);
- limits (no absorption, ``n = 1``) that must hold analytically;
- the tables of the paper (constant loss only) and a direct, independent
  integration of Eq. (18) (power law).

.. note::
   The power law entries of Tables I and II of the paper are *not* reproduced
   by its own Eq. (18), which is why they are not used here.

"""

import itertools
import logging

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose
from numpy.typing import NDArray
from scipy.integrate import quad
from scipy.special import expn

from eemilib.emission_data import DataMatrix
from eemilib.emission_data.emission_yield import SEEY
from eemilib.model.dionne import (
    ENERGY_LOSS,
    SCATTERING,
    Dionne,
    EnergyLoss,
    Scattering,
    _escape_profile,
    dionne_func,
    generation,
    power_law_range,
    transport_constant_loss,
    transport_power_law,
)

#: Parameters in the reduced units of the paper: with them, the yield is the
#: reduced yield and the range is the reduced depth.
REDUCED = {
    "excitation_energy": 1.0,
    "diffusion_length": 1.0,
    "escape_probability": 1.0,
}
COMBINATIONS = list(itertools.product(ENERGY_LOSS, SCATTERING))


def _reduced(n: float) -> dict[str, float]:
    """Give the parameters for which ``delta = delta'`` and ``R = alpha d``."""
    return {**REDUCED, "power_law_scale": 1.0 / n, "power_law_exponent": n}


@pytest.fixture
def dionne_model() -> Dionne:
    """Create a default instance of :class:`.Dionne` model."""
    return Dionne()


# =============================================================================
# Model definition
# =============================================================================
def test_initial_parameters(dionne_model: Dionne) -> None:
    """Check that the mandatory parameters are defined."""
    expected_parameters = {
        "excitation_energy",
        "diffusion_length",
        "escape_probability",
        "power_law_scale",
        "power_law_exponent",
    }
    assert set(dionne_model.initial_parameters.keys()) == expected_parameters


def test_implementation_choices(dionne_model: Dionne) -> None:
    """Check that the two axes of the paper are exposed to the GUI."""
    assert dionne_model.implementation_choices == {
        "energy_loss": ENERGY_LOSS,
        "secondary_scattering": SCATTERING,
    }


@pytest.mark.parametrize(("energy_loss", "scattering"), COMBINATIONS)
def test_set_implementation_at_init(
    energy_loss: EnergyLoss, scattering: Scattering
) -> None:
    """Check that every combination can be selected."""
    model = Dionne(energy_loss=energy_loss, secondary_scattering=scattering)
    assert model.current_implementations["energy_loss"] == energy_loss
    assert model.current_implementations["secondary_scattering"] == scattering


def test_set_implementation_later(dionne_model: Dionne) -> None:
    """Check that an axis can be changed after instantiation."""
    dionne_model.set_implementation("secondary_scattering", "3D")
    assert dionne_model.current_implementations["secondary_scattering"] == "3D"
    dionne_model.set_implementation("energy_loss", "Constant loss")
    assert dionne_model.current_implementations["energy_loss"] == (
        "Constant loss"
    )


def test_set_implementation_unknown_axis(
    dionne_model: Dionne, caplog: pytest.LogCaptureFixture
) -> None:
    """Check that an unknown axis is refused, and changes nothing."""
    before = dict(dionne_model.current_implementations)
    with caplog.at_level(logging.ERROR):
        dionne_model.set_implementation("not_an_axis", "1D")
    assert "Unknown implementation axis" in caplog.text
    assert dionne_model.current_implementations == before


def test_set_implementation_unknown_value(
    dionne_model: Dionne, caplog: pytest.LogCaptureFixture
) -> None:
    """Check that an unknown value is refused, and changes nothing."""
    before = dict(dionne_model.current_implementations)
    with caplog.at_level(logging.ERROR):
        dionne_model.set_implementation("energy_loss", "CSDA")
    assert "Unknown value" in caplog.text
    assert dionne_model.current_implementations == before


# =============================================================================
# Building blocks
# =============================================================================
def test_power_law_range() -> None:
    """Check Eq. (13): ``R = E^n / (A n)``."""
    ene = np.array([1.0, 4.0, 9.0])
    result = power_law_range(ene, power_law_scale=0.5, power_law_exponent=2.0)
    assert_allclose(result, ene**2 / (0.5 * 2.0))


def test_generation() -> None:
    """Check ``G = E / (R Phi)``, and that null ranges give 0."""
    ene = np.array([10.0, 20.0, 30.0])
    ranges = np.array([5.0, 0.0, 15.0])
    result = generation(ene, ranges, excitation_energy=2.0)
    assert_allclose(result, [1.0, 0.0, 1.0])


def test_escape_profile() -> None:
    """Check ``f(x)/S`` at the surface and far from it."""
    x = np.array([0.0, 2.0])
    assert_allclose(_escape_profile(x, 2.0, "1D"), [1.0, np.exp(-1.0)])
    assert_allclose(_escape_profile(x, 2.0, "3D"), [0.5, 0.5 * expn(2, 1.0)])


@pytest.mark.parametrize(
    ("scattering", "far_limit"), [("1D", 1.0), ("3D", 0.25)]
)
def test_transport_constant_loss_limits(
    scattering: Scattering, far_limit: float
) -> None:
    """Check ``T -> 0`` for ``R -> 0`` and ``T -> d * far_limit`` for large R.

    ``far_limit`` is 1 in 1D and 1/4 in 3D (Eqs. (26) and (29)).

    """
    d = 3.0
    small = transport_constant_loss(np.array([1e-9]), d, scattering)
    far = transport_constant_loss(np.array([1e3]), d, scattering)
    assert_allclose(small, 0.0, atol=1e-8)
    assert_allclose(far, d * far_limit, rtol=1e-6)


def test_transport_constant_loss_closed_forms() -> None:
    """Compare with Eqs. (26) and (29), written as in the paper."""
    d = 2.0
    ranges = np.array([0.5, 2.0, 7.0])
    assert_allclose(
        transport_constant_loss(ranges, d, "1D"),
        d * (1.0 - np.exp(-ranges / d)),
    )
    assert_allclose(
        transport_constant_loss(ranges, d, "3D"),
        0.5 * d * (0.5 - expn(3, ranges / d)),
    )


@pytest.mark.parametrize("scattering", SCATTERING)
def test_power_law_with_n_equal_one_is_constant_loss(
    scattering: Scattering,
) -> None:
    """Check that ``n = 1`` gives a constant ``dE/dx``, thus constant loss."""
    ranges = np.array([0.3, 1.0, 4.0, 12.0])
    d = 2.0
    power_law = transport_power_law(ranges, 1.0, d, scattering)
    constant = transport_constant_loss(ranges, d, scattering)
    assert_allclose(power_law, constant, rtol=1e-6)


# =============================================================================
# dionne_func
# =============================================================================
@pytest.mark.parametrize(("energy_loss", "scattering"), COMBINATIONS)
def test_dionne_func_vectorized(
    energy_loss: EnergyLoss, scattering: Scattering
) -> None:
    """Check that passing an array equals looping over scalars."""
    energies = np.array([5.0, 50.0, 500.0])
    kwargs = {**_reduced(1.35), "energy_loss": energy_loss}
    kwargs["scattering"] = scattering
    array = dionne_func(energies, **kwargs)
    scalars = [float(dionne_func(e, **kwargs)[0]) for e in energies]
    assert array.shape == energies.shape
    assert_allclose(array, scalars)


@pytest.mark.parametrize(("energy_loss", "scattering"), COMBINATIONS)
def test_dionne_func_no_absorption(
    energy_loss: EnergyLoss, scattering: Scattering
) -> None:
    """Check energy balance when the diffusion length is huge.

    All |SEs| reach the surface in 1D, so ``delta = S E / Phi``. In 3D, half
    of them are emitted towards the bulk.

    """
    energies = np.array([1.0, 5.0, 20.0])
    parameters = {
        "excitation_energy": 4.6,
        "diffusion_length": 1e6,
        "escape_probability": 0.5,
        "power_law_scale": 1.0,
        "power_law_exponent": 1.3,
    }
    result = dionne_func(
        energies, energy_loss=energy_loss, scattering=scattering, **parameters
    )
    expected = 0.5 * energies / 4.6 * (1.0 if scattering == "1D" else 0.5)
    assert_allclose(result, expected, rtol=1e-3)


def test_dionne_func_constant_loss_1d_is_g_t_s() -> None:
    """Check that the default is the historical ``G * T * S`` formula."""
    ene = np.array([10.0, 100.0, 300.0])
    xi, d, s, a, n = 4.6, 2.0, 0.5, 1.0, 1.2
    ranges = ene**n / (a * n)
    expected = (ene / (ranges * xi)) * d * (1.0 - np.exp(-ranges / d)) * s
    result = dionne_func(
        ene,
        excitation_energy=xi,
        diffusion_length=d,
        escape_probability=s,
        power_law_scale=a,
        power_law_exponent=n,
        energy_loss="Constant loss",
        scattering="1D",
    )
    assert_allclose(result, expected)


def test_dionne_func_unknown_energy_loss() -> None:
    """Check that an unknown energy loss law is not silently accepted."""
    with pytest.raises(ValueError, match="Unknown energy_loss"):
        dionne_func(
            np.array([10.0]),
            **_reduced(1.35),
            energy_loss="CSDA",  # type: ignore
        )


@pytest.mark.parametrize(
    ("n", "scattering", "expected_yield", "expected_depth"),
    [
        # Tables I and II of Dionne (1973), constant loss columns
        pytest.param(1.35, "3D", 0.20, 1.4, id="n=1.35, 3D"),
        pytest.param(1.35, "1D", 0.73, 2.3, id="n=1.35, 1D"),
        pytest.param(1.66, "3D", 0.20, 0.95, id="n=1.66, 3D"),
        pytest.param(1.66, "1D", 0.66, 1.6, id="n=1.66, 1D"),
        pytest.param(2.0, "3D", 0.20, 0.7, id="n=2.0, 3D"),
        pytest.param(2.0, "1D", 0.64, 1.3, id="n=2.0, 1D"),
    ],
)
def test_constant_loss_reduced_maximum(
    n: float,
    scattering: Scattering,
    expected_yield: float,
    expected_depth: float,
) -> None:
    """Compare the maximum of the reduced yield curve with the paper.

    In the reduced parameters, ``delta`` is the reduced yield and ``R`` the
    reduced depth ``alpha d``. The paper gives two digits at best, hence the
    tolerances.

    """
    energies = np.linspace(0.02, 8.0, 2000)
    result = dionne_func(
        energies,
        **_reduced(n),
        energy_loss="Constant loss",
        scattering=scattering,
    )
    i_max = result.argmax()
    assert result[i_max] == pytest.approx(expected_yield, abs=0.01)
    assert energies[i_max] ** n == pytest.approx(expected_depth, abs=0.05)


def _eq_18_reference(
    reduced_depth: float, n: float, scattering: Scattering
) -> float:
    """Integrate Eq. (18) (1D) or its 3D counterpart without substitution."""

    def integrand(x: float) -> float:
        profile = np.exp(-x) if scattering == "1D" else 0.5 * expn(2, x)
        return profile / (n * (reduced_depth - x) ** ((n - 1.0) / n))

    value, _ = quad(integrand, 0.0, reduced_depth, limit=200)
    return value


@pytest.mark.parametrize("n", [1.35, 1.66, 2.0])
@pytest.mark.parametrize("scattering", SCATTERING)
def test_power_law_matches_direct_integration(
    n: float, scattering: Scattering
) -> None:
    """Compare with a direct integration of the singular integral, Eq. (18).

    The model integrates after the substitution ``x = R (1 - w^n)``, which
    removes the singularity. This test uses the original form.

    """
    energies = np.array([0.5, 1.0, 2.0])
    result = dionne_func(
        energies, **_reduced(n), energy_loss="Power law", scattering=scattering
    )
    reduced_depths = energies**n
    expected = [
        _eq_18_reference(depth, n, scattering) for depth in reduced_depths
    ]
    assert_allclose(result, expected, rtol=1e-3)


# =============================================================================
# Model interface
# =============================================================================
@pytest.mark.parametrize(("energy_loss", "scattering"), COMBINATIONS)
def test_compute_data(energy_loss: EnergyLoss, scattering: Scattering) -> None:
    """Check output format, and consistency with :func:`.dionne_func`."""
    model = Dionne(energy_loss=energy_loss, secondary_scattering=scattering)
    energy = np.linspace(1.0, 1000.0, 7)
    theta = np.linspace(0.0, 60.0, 3)

    result = model.compute_data("Emission Yield", "SE", energy, theta)

    assert isinstance(result, pd.DataFrame)
    assert result.shape == (7, 4)  # 3 theta columns + 1 energy column
    expected = dionne_func(
        energy,
        energy_loss=energy_loss,
        scattering=scattering,
        **{name: p.value for name, p in model.parameters.items()},
    )
    for column in result.columns[1:]:
        assert_allclose(result[column].to_numpy(), expected)


def _seey(energies: NDArray[np.float64], values: NDArray[np.float64]) -> SEEY:
    """Create a |SEEY| from arrays."""
    return SEEY(
        data=pd.DataFrame({"Energy [eV]": energies, "0.0 [deg]": values})
    )


def test_find_optimal_parameters() -> None:
    """Fit a curve generated by the model itself, check it is retrieved.

    Parameters are partially degenerate (``S`` and ``A`` partly compensate),
    so we compare curves rather than parameter values.

    """
    energies = np.linspace(10.0, 1000.0, 60)
    truth = {
        "excitation_energy": 4.6,
        "diffusion_length": 3.0,
        "escape_probability": 0.4,
        "power_law_scale": 0.8,
        "power_law_exponent": 1.3,
    }
    measured = dionne_func(
        energies, **truth, energy_loss="Constant loss", scattering="1D"
    )
    data_matrix = DataMatrix()
    data_matrix.set_data(_seey(energies, measured), "Emission Yield", "SE")

    model = Dionne(energy_loss="Constant loss", secondary_scattering="1D")
    model.find_optimal_parameters(data_matrix)

    fitted = dionne_func(
        energies,
        energy_loss="Constant loss",
        scattering="1D",
        **{name: p.value for name, p in model.parameters.items()},
    )
    rms = np.sqrt(np.mean((fitted - measured) ** 2))
    assert rms < 0.02 * measured.max()
