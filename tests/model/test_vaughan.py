import numpy as np
import pandas as pd
import pytest
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.model.vaughan import Vaughan
from tests.model.mocks.mock_emission_yield import MockEmissionYield


@pytest.fixture
def vaughan_model() -> Vaughan:
    """Create a default instance of :class:`.Vaughan` model."""
    return Vaughan()


class MockDataMatrix(DataMatrix):
    """Mock a data matrix with only a TEEY."""

    def __init__(self, emission_data):
        """Set emission yield for 'all' population."""
        self.data_matrix = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
            [emission_data, None, None],
        ]

    def assert_has_all_mandatory_files(self, *args, **kwargs) -> None:
        """Skip this check."""
        pass


def test_initial_parameters(vaughan_model: Vaughan) -> None:
    """Check that the mandatory parameters are defined."""
    expected_parameters = {
        "E_0",
        "E_max",
        "delta_E_transition",
        "teey_low",
        "teey_max",
        "k_s",
        "k_se",
    }
    assert set(vaughan_model.initial_parameters.keys()) == expected_parameters


def test_teey_output_shape(vaughan_model: Vaughan) -> None:
    """Check that TEEY array has proper shape."""
    energy = np.linspace(0, 100, 5)
    theta = np.linspace(0, 90, 3)
    result = vaughan_model.teey(energy, theta)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (5, 4)  # 3 theta columns + 1 energy column


@pytest.mark.parametrize(
    "emission_yield,expected",
    [
        (
            MockEmissionYield.cu_eroded_one(),
            {
                "E_0": 12.5,
                "E_max": 550.5505505505506,
                "delta_E_transition": 1.0,
                "teey_low": 0.5,
                "teey_max": 1.525944944944945,
                "k_s": 1.0,
                "k_se": 1.0,
            },
        ),
        pytest.param(
            MockEmissionYield.cu_as_received_two(),
            {
                "E_0": 12.5,
                "E_max": 250.34034034034033,
                "delta_E_transition": 1.0,
                "teey_low": 0.5,
                "teey_max": 2.236948948948949,
                "k_s": 1.0,
                "k_se": 1.0,
            },
            marks=pytest.mark.smoke,
        ),
        (
            MockEmissionYield.cu_heated_two(),
            {
                "E_0": 12.5,
                "E_max": 389.63963963963965,
                "delta_E_transition": 1.0,
                "teey_low": 0.5,
                "teey_max": 1.695873873873874,
                "k_s": 1.0,
                "k_se": 1.0,
            },
        ),
    ],
)
def test_find_optimal_parameters(
    vaughan_model: Vaughan,
    emission_yield: MockEmissionYield,
    expected: dict[str, float],
) -> None:
    """Test on several samples that the fit gives expected results."""
    mock_data_matrix = MockDataMatrix(emission_yield)
    vaughan_model.find_optimal_parameters(mock_data_matrix)
    found_parameters = {
        name: val.value for name, val in vaughan_model.parameters.items()
    }
    assert expected == found_parameters
