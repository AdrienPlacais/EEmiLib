"""Define tests for the Maxwellian model."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from eemilib import emission_energy_ag
from eemilib.data.dummy.emission_energy import maxwellian_parameters_values
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.emission_data.emission_energy_distribution import (
    AllEmissionEnergyDistribution,
)
from eemilib.loader import PandasLoader
from eemilib.model import Maxwellian
from pandas.testing import assert_frame_equal
from pytest import approx


@pytest.fixture
def maxwellian_model() -> Maxwellian:
    """Create a default instance of :class:`.Maxwellian` model."""
    return Maxwellian()


class MockDataMatrix(DataMatrix):
    """Mock a data matrix with only an energy distribution for |SEs|."""

    def __init__(self, se_pdf: AllEmissionEnergyDistribution) -> None:
        """Set emission energy pdf for 'SEs' population."""
        self.data_matrix = [
            [[], [], []],
            [[], [], []],
            [[], [], []],
            [[], [se_pdf], []],
        ]

    def has_all_mandatory_files(self, *args, **kwargs) -> bool:
        """Skip this check."""
        return True


def _mock_data_matrix_from_energy_distributions(
    distributions: dict,
) -> MockDataMatrix:
    """Build a :class:`MockDataMatrix` from loaded (df, e_pe) distribution pairs."""
    se_df, se_e_pe = distributions["SE"]
    se_pdf = AllEmissionEnergyDistribution(data=se_df, e_pe=se_e_pe)
    return MockDataMatrix(se_pdf=se_pdf)


@pytest.fixture
def energy_distrib_data(
    verified_maxwellian_distribution: dict,
) -> MockDataMatrix:
    """Instantiate dummy energy distributions, via the verified loader fixture."""
    return _mock_data_matrix_from_energy_distributions(
        verified_maxwellian_distribution
    )


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


def test_modelled_maxwellian_agains_cst(
    energy_distrib_data: MockDataMatrix,
) -> None:
    model = Maxwellian(parameters_values=maxwellian_parameters_values)

    data_matrix = energy_distrib_data
    expected = data_matrix.get_data(
        population="all", data_type="Emission Energy"
    )[0]
    emission_energies = np.array(expected.energies)
    theta = np.array(expected.angles)

    calculated_df = model.get_data(
        population="SE",
        data_type="Emission Energy",
        energy=emission_energies,
        theta=theta,
        impact_energy=expected.e_pe,
    )
    assert isinstance(calculated_df, pd.DataFrame)

    calculated = AllEmissionEnergyDistribution(
        data=calculated_df, e_pe=expected.e_pe
    )
    assert_frame_equal(expected.data, calculated.data)


@pytest.mark.parametrize(
    "filepath,expected",
    [
        pytest.param(
            emission_energy_ag / "corrected_cleanAg0_150eV_2018.05.30.csv",
            {"temperature": 3.349073165207961, "norm": 6.920409838552599},
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
        files=(Path(filepath),), population="all", data_type="Emission Energy"
    )
    data_matrix.load_data(PandasLoader())
    model = Maxwellian()
    model.find_optimal_parameters(data_matrix, population="all")
    found_parameters = {
        name: val.value for name, val in model.parameters.items()
    }
    assert found_parameters == approx(expected)
