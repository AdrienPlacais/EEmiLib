"""Define tests for the Furman and Pivi model.

.. todo::
   Emission energy distributions

"""

import numpy as np
import pandas as pd
import pytest
from eemilib.data import fp_copper as cu
from eemilib.data import fp_stainless_steel as ss
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.emission_data.emission_data import EmissionData
from eemilib.emission_data.emission_yield import EmissionYield
from eemilib.model import FurmanPivi
from eemilib.util.constants import ImplementedPop
from pandas.testing import assert_frame_equal


@pytest.fixture
def furman_pivi_model() -> FurmanPivi:
    """Create a default instance of :class:`.FurmanPivi` model."""
    return FurmanPivi()


@pytest.fixture
def furman_pivi_ss() -> FurmanPivi:
    """Create an instance with the stainless steel parameters.

    By default, the parameters already have these values. But we hard-write
    them in case default parameters change.

    """
    return FurmanPivi(parameters_values=ss.furman_pivi_parameters_values)


@pytest.fixture
def furman_pivi_cu() -> FurmanPivi:
    """Create an instance with the Cu parameters."""
    return FurmanPivi(parameters_values=cu.furman_pivi_parameters_values)


class MockDataMatrix(DataMatrix):
    """Mock a data matrix with emission yields for all populations."""

    def __init__(
        self,
        seey: EmissionData,
        ebeey: EmissionData,
        ibeey: EmissionData,
        teey: EmissionData,
    ) -> None:
        """Set emission yield for |SEs|, |EBEs|, |IBEs|."""
        self.data_matrix = [
            [seey, None, None],
            [ebeey, None, None],
            [ibeey, None, None],
            [teey, None, None],
        ]

    def has_all_mandatory_files(self, *args, **kwargs) -> bool:
        """Skip this check."""
        return True


def _mock_data_matrix_from_yields(yields: dict) -> MockDataMatrix:
    """Build a :class:`MockDataMatrix` from a dict of loaded yield DataFrames."""
    seey = EmissionYield(population="SE", data=yields["SE"])
    ebeey = EmissionYield(population="EBE", data=yields["EBE"])
    ibeey = EmissionYield(population="IBE", data=yields["IBE"])
    teey = EmissionYield(population="all", data=yields["all"])
    return MockDataMatrix(seey=seey, ebeey=ebeey, ibeey=ibeey, teey=teey)


@pytest.fixture
def emission_data_ss(verified_ss_emission_yields: dict) -> MockDataMatrix:
    """Instantiate SS exported with CST, via the verified loader fixture."""
    return _mock_data_matrix_from_yields(verified_ss_emission_yields)


@pytest.fixture
def emission_data_cu(verified_cu_emission_yields: dict) -> MockDataMatrix:
    """Instantiate Cu exported with CST, via the verified loader fixture."""
    return _mock_data_matrix_from_yields(verified_cu_emission_yields)


def test_initial_parameters(furman_pivi_model: FurmanPivi) -> None:
    """Check that the mandatory parameters are defined."""
    expected_parameters = {
        "normal_e_max_se",
        "normal_delta_max",
        "t_1",
        "t_2",
        "t_3",
        "t_4",
        "s",
        "eps_1",
        "eps_2",
        "eps_3",
        "eps_4",
        "eps_5",
        "eps_6",
        "eps_7",
        "eps_8",
        "eps_9",
        "eps_10",
        "p_1",
        "p_2",
        "p_3",
        "p_4",
        "p_5",
        "p_6",
        "p_7",
        "p_8",
        "p_9",
        "p_10",
        "normal_e_max_ebe",
        "p_1_hat",
        "sigma",
        "p_1_inf_ebe",
        "W",
        "p",
        "e_1",
        "e_2",
        "normal_e_max_ibe",
        "p_1_inf_ibe",
        "r",
        "q",
        "r_1",
        "r_2",
    }
    assert (
        set(furman_pivi_model.initial_parameters.keys()) == expected_parameters
    )


@pytest.mark.parametrize("population", ["SE", "EBE", "IBE", "all"])
def test_emission_yields_output_shape(
    furman_pivi_model: FurmanPivi, population: ImplementedPop
) -> None:
    """Check that all emission yield arrays have proper shape."""
    energy = np.linspace(0, 100, 5, dtype=np.float64)
    theta = np.linspace(0, 80, 3, dtype=np.float64)
    result = furman_pivi_model.get_data(
        population=population,
        emission_data_type="Emission Yield",
        energy=energy,
        theta=theta,
    )
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (5, 4)  # 3 theta columns + 1 energy column


@pytest.mark.parametrize(
    "material, model_fixture, data_fixture",
    [
        pytest.param(
            "SS", "furman_pivi_ss", "emission_data_ss", id="Stainless steel"
        ),
        pytest.param("Cu", "furman_pivi_cu", "emission_data_cu", id="Copper"),
    ],
)
@pytest.mark.parametrize(
    "population",
    [
        pytest.param("SE", id="SEEY"),
        pytest.param("EBE", id="EBEEY"),
        pytest.param("IBE", id="IBEEY"),
        pytest.param("all", id="TEEY"),
    ],
)
def test_emission_yields_values(
    request: pytest.FixtureRequest,
    material: str,
    model_fixture: str,
    data_fixture: str,
    population: ImplementedPop,
) -> None:
    """Check that our implementation gives same EY as CST, for SS and Cu."""
    model: FurmanPivi = request.getfixturevalue(model_fixture)
    data_matrix: MockDataMatrix = request.getfixturevalue(data_fixture)

    expected = data_matrix.get_data(
        population=population, emission_data_type="Emission Yield"
    )
    assert isinstance(expected, EmissionYield)
    energy = np.array(expected.energies)
    theta = np.array(expected.angles)

    calculated = model.get_data(
        population=population,
        emission_data_type="Emission Yield",
        energy=energy,
        theta=theta,
    )

    assert_frame_equal(expected.data, calculated, atol=1e-1)


@pytest.mark.xfail
def test_find_optimal_parameters(
    furman_pivi_model_for_pec_cst: FurmanPivi,
    pec_cst: MockDataMatrix,
    population: ImplementedPop,
) -> None:
    raise NotImplementedError
