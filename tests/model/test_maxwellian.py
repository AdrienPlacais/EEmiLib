"""Define tests for the Maxwellian model."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from eemilib import emission_energy_ag
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.emission_data.emission_energy_distribution import (
    EmissionEnergyDistribution,
)
from eemilib.loader import PandasLoader
from eemilib.model import Maxwellian
from pytest import approx


@pytest.fixture
def maxwellian_model() -> Maxwellian:
    """Create a default instance of :class:`.Maxwellian` model."""
    return Maxwellian()


class MockDataMatrix(DataMatrix):
    """Mock a data matrix with only an energy distribution for |SEs|."""

    def __init__(self, emission_data: EmissionEnergyDistribution) -> None:
        """Set emission energy pdf for 'SEs' population."""
        self.data_matrix = [
            [None, emission_data, None],
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ]

    def has_all_mandatory_files(self, *args, **kwargs) -> bool:
        """Skip this check."""
        return True


def test_initial_parameters(maxwellian_model: Maxwellian) -> None:
    """Check that the mandatory parameters are defined."""
    expected_parameters = {"temperature", "norm"}
    assert (
        set(maxwellian_model.initial_parameters.keys()) == expected_parameters
    )


def test_emission_energy_distribution_output_shape(
    maxwellian_model: Maxwellian,
) -> None:
    """Check that energy pdf array has proper shape."""
    energy = np.linspace(0, 100, 5, dtype=np.float64)
    theta = np.linspace(0, 90, 3, dtype=np.float64)  # will be ignored
    result = maxwellian_model.se_energy_distribution(energy, theta)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (5, 2)  # 1 theta column + 1 energy column


@pytest.mark.parametrize(
    "filepath,expected",
    [
        pytest.param(
            emission_energy_ag / "corrected_cleanAg0_150eV_2018.05.30.csv",
            {"temperature": 4.909026, "norm": 10.143843},
            id="Measured emission energy on Ag",
        )
    ],
)
def test_find_optimal_parameters(
    filepath: str, expected: dict[str, float]
) -> None:
    """Test on several samples that the fit gives expected results."""
    data_matrix = DataMatrix()
    data_matrix.set_files(
        [Path(filepath)],
        population="SE",
        emission_data_type="Emission Energy",
    )
    data_matrix.load_data(PandasLoader())
    model = Maxwellian()
    model.find_optimal_parameters(data_matrix)
    found_parameters = {
        name: val.value for name, val in model.parameters.items()
    }
    assert found_parameters == approx(expected)
