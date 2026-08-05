"""Define tests for the Furman and Pivi model.

.. todo::
   Emission angle distributions

"""

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from eemilib.data import fp_copper, fp_stainless_steel
from eemilib.emission_data import DataMatrix
from eemilib.emission_data.emission_energy_distribution import (
    EMISSION_ENERGIES_BY_POP,
    AllEmissionEnergyDistribution,
    EBEEmissionEnergyDistribution,
    IBEEmissionEnergyDistribution,
    SEEmissionEnergyDistribution,
)
from eemilib.emission_data.emission_yield import (
    EBEEY,
    IBEEY,
    SEEY,
    TEEY,
    EmissionYield,
)
from eemilib.model import FurmanPivi
from eemilib.util.constants import ImplementedPop


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
    return FurmanPivi(
        parameters_values=fp_stainless_steel.furman_pivi_parameters_values,
        distribution="Binomial",
        normalization="penetrated",
    )


@pytest.fixture
def furman_pivi_cu() -> FurmanPivi:
    """Create an instance with the Cu parameters."""
    return FurmanPivi(
        parameters_values=fp_copper.furman_pivi_parameters_values,
        distribution="Binomial",
        normalization="penetrated",
    )


class MockDataMatrix(DataMatrix):
    """Mock a data matrix with emission yields and/or energy distributions."""

    def __init__(
        self,
        seey: SEEY | None = None,
        ebeey: EBEEY | None = None,
        ibeey: IBEEY | None = None,
        teey: TEEY | None = None,
        se_pdf: SEEmissionEnergyDistribution | None = None,
        ebe_pdf: EBEEmissionEnergyDistribution | None = None,
        ibe_pdf: IBEEmissionEnergyDistribution | None = None,
        all_pdf: AllEmissionEnergyDistribution | None = None,
    ) -> None:
        """Set emission yield and/or energy distribution for all populations."""
        self.data_matrix = [
            [seey, [se_pdf] if se_pdf else se_pdf, None],
            [ebeey, [ebe_pdf] if ebe_pdf else ebe_pdf, None],
            [ibeey, [ibe_pdf] if ibe_pdf else ibe_pdf, None],
            [teey, [all_pdf] if all_pdf else all_pdf, None],
        ]

    def has_all_mandatory_files(self, *args, **kwargs) -> bool:
        """Skip this check."""
        return True


def _mock_data_matrix_from_yields(yields: dict) -> MockDataMatrix:
    """Build a :class:`MockDataMatrix` from a dict of loaded yield DataFrames."""
    seey = SEEY(data=yields["SE"])
    ebeey = EBEEY(data=yields["EBE"])
    ibeey = IBEEY(data=yields["IBE"])
    teey = TEEY(data=yields["all"])
    return MockDataMatrix(seey=seey, ebeey=ebeey, ibeey=ibeey, teey=teey)


def _mock_data_matrix_from_energy_distributions(
    distributions: dict,
) -> MockDataMatrix:
    """Build a :class:`MockDataMatrix` from loaded (df, e_pe) distribution pairs."""
    se_df, se_e_pe = distributions["SE"]
    ebe_df, ebe_e_pe = distributions["EBE"]
    ibe_df, ibe_e_pe = distributions["IBE"]
    all_df, all_e_pe = distributions["all"]

    se_pdf = SEEmissionEnergyDistribution(data=se_df, e_pe=se_e_pe, norm=1.0)
    ebe_pdf = EBEEmissionEnergyDistribution(
        data=ebe_df, e_pe=ebe_e_pe, norm=1.0
    )
    ibe_pdf = IBEEmissionEnergyDistribution(
        data=ibe_df, e_pe=ibe_e_pe, norm=1.0
    )
    all_pdf = AllEmissionEnergyDistribution(
        data=all_df, e_pe=all_e_pe, norm=1.0
    )
    return MockDataMatrix(
        se_pdf=se_pdf, ebe_pdf=ebe_pdf, ibe_pdf=ibe_pdf, all_pdf=all_pdf
    )


@pytest.fixture
def emission_data_ss(verified_ss_emission_yields: dict) -> MockDataMatrix:
    """Instantiate SS yields exported with CST, via the verified loader fixture."""
    return _mock_data_matrix_from_yields(verified_ss_emission_yields)


@pytest.fixture
def emission_data_cu(verified_cu_emission_yields: dict) -> MockDataMatrix:
    """Instantiate Cu yields exported with CST, via the verified loader fixture."""
    return _mock_data_matrix_from_yields(verified_cu_emission_yields)


@pytest.fixture
def energy_distrib_data_ss(
    verified_ss_energy_distributions: dict,
) -> MockDataMatrix:
    """Instantiate SS energy distributions, via the verified loader fixture."""
    return _mock_data_matrix_from_energy_distributions(
        verified_ss_energy_distributions
    )


@pytest.fixture
def energy_distrib_data_cu(
    verified_cu_energy_distributions: dict,
) -> MockDataMatrix:
    """Instantiate Cu energy distributions, via the verified loader fixture."""
    return _mock_data_matrix_from_energy_distributions(
        verified_cu_energy_distributions
    )


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
        "eta_e_max",
        "sigma",
        "eta_e_min",
        "W",
        "p",
        "e_1",
        "e_2",
        "e_ibe",
        "eta_i_max",
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
        data_type="Emission Yield",
        energy=energy,
        theta=theta,
    )
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (5, 4)  # 3 theta columns + 1 energy column


@pytest.mark.parametrize(
    "model_fixture, data_fixture",
    [
        pytest.param(
            "furman_pivi_ss", "emission_data_ss", id="Stainless steel"
        ),
        pytest.param("furman_pivi_cu", "emission_data_cu", id="Copper"),
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
    model_fixture: str,
    data_fixture: str,
    population: ImplementedPop,
) -> None:
    """Check that our implementation gives same EY as CST, for SS and Cu."""
    model: FurmanPivi = request.getfixturevalue(model_fixture)
    data_matrix: MockDataMatrix = request.getfixturevalue(data_fixture)

    expected = data_matrix.get_data("Emission Yield", population)[0]
    assert isinstance(expected, EmissionYield)
    energy = np.array(expected.energies)
    theta = np.array(expected.angles)

    calculated = model.get_data(
        population=population,
        data_type="Emission Yield",
        energy=energy,
        theta=theta,
    )

    assert_frame_equal(expected.data, calculated)


@pytest.mark.parametrize(
    "model_fixture, data_fixture",
    [
        pytest.param(
            "furman_pivi_ss", "energy_distrib_data_ss", id="Stainless steel"
        ),
        pytest.param("furman_pivi_cu", "energy_distrib_data_cu", id="Copper"),
    ],
)
@pytest.mark.parametrize(
    "population",
    [
        pytest.param("SE", id="SE energy distribution"),
        pytest.param("EBE", id="EBE energy distribution"),
        pytest.param("IBE", id="IBE energy distribution"),
        pytest.param("all", id="Overall energy distribution"),
    ],
)
def test_energy_distribution_values(
    request: pytest.FixtureRequest,
    model_fixture: str,
    data_fixture: str,
    population: ImplementedPop,
) -> None:
    """Check that our implementation gives same spectrum as CST, for SS and Cu.

    Both ``expected`` and ``calculated`` are wrapped in
    :class:`.EmissionEnergyDistribution` before comparison, since this class
    normalizes ``data`` in its constructor; comparing raw model output
    against already-normalized CST data would otherwise fail on scale alone.

    """
    model: FurmanPivi = request.getfixturevalue(model_fixture)
    data_matrix: MockDataMatrix = request.getfixturevalue(data_fixture)

    expected = data_matrix.get_data("Emission Energy", population)[0]
    emission_energies = np.array(expected.energies)
    theta = np.array(expected.angles)

    calculated_df = model.get_data(
        population=population,
        data_type="Emission Energy",
        energy=emission_energies,
        theta=theta,
        impact_energy=expected.e_pe,
    )
    assert isinstance(calculated_df, pd.DataFrame)
    calculated = EMISSION_ENERGIES_BY_POP[population](
        data=calculated_df, e_pe=expected.e_pe, norm=1.0
    )

    assert_frame_equal(expected.data, calculated.data)


@pytest.mark.xfail
def test_find_optimal_parameters(
    furman_pivi_model_for_pec_cst: FurmanPivi,
    pec_cst: MockDataMatrix,
    population: ImplementedPop,
) -> None:
    raise NotImplementedError
