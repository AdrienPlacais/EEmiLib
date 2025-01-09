"""Define unit tests for Vaughan model."""

import numpy as np
import pandas as pd
import pytest
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.emission_data.emission_yield import EmissionYield
from eemilib.model.model_config import ModelConfig
from eemilib.model.parameter import Parameter
from eemilib.model.vaughan import Vaughan, _vaughan_func
from tests.model.mocks.mock_emission_yield import MockEmissionYield


@pytest.fixture
def vaughan_model() -> Vaughan:
    """Create a default instance of :class:`.Vaughan` model."""
    return Vaughan()


@pytest.fixture
def mock_data_matrix() -> DataMatrix:
    """Instantiate a fake :class:`.DataMatrix`."""

    class MockEmissionYield:
        """Make object corresponding to Cu 2 (as received)."""

        def __init__(self, e_max, ey_max):
            self.e_max = e_max
            self.ey_max = ey_max
            self.population = "all"

    class MockDataMatrix:
        def __init__(self):
            self.data_matrix = [
                [None, None, None, [MockEmissionYield(e_max=20, ey_max=1.5)]]
            ]

        def assert_has_all_mandatory_files(self, *args, **kwargs) -> None:
            """Pass the files testing."""
            pass

    return MockDataMatrix()


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


def test_find_optimal_parameters_with_different_datasets(
    vaughan_model: Vaughan,
) -> None:
    """Test on several samples that the fit gives expected results."""
    expected_parameters = [
        {  # Cu eroded 1
            "E_0": 12.5,
            "E_max": 550.5505505505506,
            "delta_E_transition": 1.0,
            "teey_low": 0.5,
            "teey_max": 1.525944944944945,
            "k_s": 1.0,
            "k_se": 1.0,
        },
        {  # Cu as-received 2
            "E_0": 12.5,
            "E_max": 250.34034034034033,
            "delta_E_transition": 1.0,
            "teey_low": 0.5,
            "teey_max": 2.236948948948949,
            "k_s": 1.0,
            "k_se": 1.0,
        },
        {  # Cu heated 2
            "E_0": 12.5,
            "E_max": 389.63963963963965,
            "delta_E_transition": 1.0,
            "teey_low": 0.5,
            "teey_max": 1.695873873873874,
            "k_s": 1.0,
            "k_se": 1.0,
        },
    ]
    for dataset, expected in zip(
        [
            MockEmissionYield.cu_eroded_one(),
            MockEmissionYield.cu_as_received_two(),
            MockEmissionYield.cu_heated_two(),
        ],
        expected_parameters,
    ):
        mock_data_matrix = MockDataMatrix(dataset)
        vaughan_model.find_optimal_parameters(mock_data_matrix)
        found_parameters = {
            name: val.value for name, val in vaughan_model.parameters.items()
        }
        assert expected == found_parameters


class MockDataMatrix:
    """Mock a data matrix with only a TEEY."""

    def __init__(self, emission_data):
        """Set emission yield for 'all' population."""
        self.data_matrix = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
            [emission_data, None, None],
        ]

    def assert_has_all_mandatory_files(self, config) -> None:
        """Skip this check."""
        pass
