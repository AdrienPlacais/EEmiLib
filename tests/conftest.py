"""Shared fixtures for loader-dependent tests."""

import pandas as pd
import pytest

from eemilib.data import fp_copper, fp_stainless_steel
from eemilib.data.dummy.emission_energy import maxwellian
from eemilib.data.spark3d import ecss_ag, ecss_al, ecss_cu
from eemilib.loader import CSTLoader, PandasLoader


@pytest.fixture(scope="session")
def cst_loader() -> CSTLoader:
    """Instantiate the CST loader, shared across the test session."""
    return CSTLoader()


@pytest.fixture(scope="session")
def spark3d_loader() -> PandasLoader:
    """Instantiate a loader for SPARK3D-exported data."""
    return PandasLoader(sep="\t")


# =============================================================================
# Stainless steel
# =============================================================================
@pytest.fixture(scope="session")
def verified_ss_emission_yields(cst_loader: CSTLoader) -> dict:
    """Load stainless steel emission yields, validated against known values.

    This fixture is the single point of trust for CST-loaded stainless steel
    yield data. If it fails, every test depending on it errors out
    immediately instead of silently running against broken data.

    """
    yields = cst_loader.load_emission_yields(
        fp_stainless_steel.cst_emission_yields
    )

    expected_keys = {"SE", "EBE", "IBE", "all"}
    assert set(yields.keys()) == expected_keys, (
        f"Expected populations {expected_keys}, got {set(yields.keys())}"
    )

    ebe_df = yields["EBE"]
    assert ebe_df["Energy [eV]"].iloc[0] == 0.0
    assert ebe_df["0.0 [deg]"].iloc[0] == pytest.approx(0.5)
    assert ebe_df["0.0 [deg]"].iloc[1] == pytest.approx(0.49249401688576)

    se_df = yields["SE"]
    assert se_df["0.0 [deg]"].iloc[0] == pytest.approx(0.0)
    assert se_df["0.0 [deg]"].iloc[1] == pytest.approx(0.0087758488953114)

    return yields


@pytest.fixture(scope="session")
def verified_ss_energy_distributions(cst_loader: CSTLoader) -> dict:
    """Load stainless steel energy distributions, validated against known values.

    This fixture is the single point of trust for CST-loaded stainless steel
    energy-distribution data. If it fails, every test depending on it errors
    out immediately instead of silently running against broken data.

    """
    distributions = cst_loader.load_emission_energy_distributions(
        fp_stainless_steel.cst_energy_distributions
    )

    expected_keys = {"SE", "EBE", "IBE", "all"}
    assert set(distributions.keys()) == expected_keys, (
        f"Expected populations {expected_keys}, got {set(distributions.keys())}"
    )

    ebe_df, ebe_e_pe = distributions["EBE"]
    assert ebe_df["Energy [eV]"].iloc[0] == 0.0
    assert ebe_df["0.0 [deg]"].iloc[0] == pytest.approx(0.0)
    assert ebe_e_pe == pytest.approx(100.0)

    se_df, se_e_pe = distributions["SE"]
    assert se_df["0.0 [deg]"].iloc[1] == pytest.approx(0.0041240798309445)
    assert se_e_pe == pytest.approx(100.0)

    return distributions


# =============================================================================
# Copper
# =============================================================================
@pytest.fixture(scope="session")
def verified_cu_emission_yields(cst_loader: CSTLoader) -> dict:
    """Load copper emission yields, validated against known values.

    This fixture is the single point of trust for CST-loaded copper yield
    data. If it fails, every test depending on it errors out immediately
    instead of silently running against broken data.

    """
    yields = cst_loader.load_emission_yields(fp_copper.cst_emission_yields)

    expected_keys = {"SE", "EBE", "IBE", "all"}
    assert set(yields.keys()) == expected_keys, (
        f"Expected populations {expected_keys}, got {set(yields.keys())}"
    )

    ebe_df = yields["EBE"]
    assert ebe_df["Energy [eV]"].iloc[0] == 0.0
    assert ebe_df["0.0 [deg]"].iloc[0] == pytest.approx(0.49599999189377)
    assert ebe_df["0.0 [deg]"].iloc[1] == pytest.approx(0.48824268579483)

    se_df = yields["SE"]
    assert se_df["0.0 [deg]"].iloc[0] == pytest.approx(0.0)
    assert se_df["0.0 [deg]"].iloc[1] == pytest.approx(0.019412733614445)

    return yields


@pytest.fixture(scope="session")
def verified_cu_energy_distributions(cst_loader: CSTLoader) -> dict:
    """Load copper energy distributions, validated against known values.

    This fixture is the single point of trust for CST-loaded copper
    energy-distribution data. If it fails, every test depending on it errors
    out immediately instead of silently running against broken data.

    """
    distributions = cst_loader.load_emission_energy_distributions(
        fp_copper.cst_energy_distributions
    )

    expected_keys = {"SE", "EBE", "IBE", "all"}
    assert set(distributions.keys()) == expected_keys, (
        f"Expected populations {expected_keys}, got {set(distributions.keys())}"
    )

    ebe_df, ebe_e_pe = distributions["EBE"]
    assert ebe_df["Energy [eV]"].iloc[0] == 0.0
    assert ebe_df["0.0 [deg]"].iloc[0] == pytest.approx(0.0)
    assert ebe_e_pe == pytest.approx(100.0)

    se_df, se_e_pe = distributions["SE"]
    assert se_df["0.0 [deg]"].iloc[1] == pytest.approx(0.011950962245464)
    assert se_e_pe == pytest.approx(100.0)

    return distributions


# =============================================================================
# Dummy Maxwellian
# =============================================================================
@pytest.fixture(scope="session")
def verified_maxwellian_distribution(cst_loader: CSTLoader) -> dict:
    """Load dummy energy distributions, validated against known values.

    This fixture is the single point of trust for CST-loaded dummy
    energy-distribution data. If it fails, every test depending on it errors
    out immediately instead of silently running against broken data.

    """
    distributions = cst_loader.load_emission_energy_distributions(maxwellian)

    expected_keys = {"SE"}
    assert set(distributions.keys()) == expected_keys, (
        f"Expected populations {expected_keys}, got {set(distributions.keys())}"
    )

    se_df, se_e_pe = distributions["SE"]
    assert se_df["0.0 [deg]"].iloc[1] == pytest.approx(0.0035416216123849)
    assert se_e_pe == pytest.approx(100.0)

    return distributions


# =============================================================================
# SPARK3D exported data
# =============================================================================
@pytest.fixture(scope="session")
def verified_al_ecss_emission_yields(
    spark3d_loader: CSTLoader,
) -> pd.DataFrame:
    """Load aluminium emission yields, validated against known values."""
    seey = spark3d_loader.load_emission_yield(ecss_al, population="SE")
    assert seey["0.0 [deg]"].iloc[0] == pytest.approx(0.0)
    assert seey["0.0 [deg]"].iloc[5] == pytest.approx(0.729686)
    return seey


@pytest.fixture(scope="session")
def verified_ag_ecss_emission_yields(
    spark3d_loader: CSTLoader,
) -> pd.DataFrame:
    """Load silver emission yields, validated against known values."""
    seey = spark3d_loader.load_emission_yield(ecss_ag, population="SE")
    assert seey["0.0 [deg]"].iloc[0] == pytest.approx(0.0)
    assert seey["0.0 [deg]"].iloc[5] == pytest.approx(0.798212)
    return seey


@pytest.fixture(scope="session")
def verified_cu_ecss_emission_yields(
    spark3d_loader: CSTLoader,
) -> pd.DataFrame:
    """Load copper emission yields, validated cuainst known values."""
    seey = spark3d_loader.load_emission_yield(ecss_cu, population="SE")
    assert seey["0.0 [deg]"].iloc[0] == pytest.approx(0.0)
    assert seey["0.0 [deg]"].iloc[5] == pytest.approx(0.696006)
    return seey
