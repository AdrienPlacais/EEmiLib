"""Define tests for the CST loader."""

import pandas as pd
import pytest


# =============================================================================
# Stainless steel — emission yields
# =============================================================================
def test_load_emission_yields_shape(verified_ss_emission_yields: dict) -> None:
    """Check that all four populations are loaded with two columns."""
    for df in verified_ss_emission_yields.values():
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["Energy [eV]", "0.0 [deg]"]


def test_load_emission_yields_values(
    verified_ss_emission_yields: dict,
) -> None:
    """Redundant with fixture validation, but explicit as its own test."""
    ebe_df = verified_ss_emission_yields["EBE"]
    assert ebe_df["0.0 [deg]"].iloc[2] == pytest.approx(0.48609930276871)


# =============================================================================
# Stainless steel — emission energy distributions
# =============================================================================
def test_load_energy_distributions_shape(
    verified_ss_energy_distributions: dict,
) -> None:
    """Check that all four populations are loaded with two columns and E_PE."""
    for df, e_pe in verified_ss_energy_distributions.values():
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["Energy [eV]", "0.0 [deg]"]
        assert isinstance(e_pe, float)


def test_load_energy_distributions_values(
    verified_ss_energy_distributions: dict,
) -> None:
    """Redundant with fixture validation, but explicit as its own test."""
    se_df, se_e_pe = verified_ss_energy_distributions["SE"]
    assert se_df["0.0 [deg]"].iloc[2] == pytest.approx(0.0076256967149675)
    assert se_e_pe == pytest.approx(100.0)


def test_load_energy_distributions_impact_energy_is_last_energy(
    verified_ss_energy_distributions: dict,
) -> None:
    """Check E_PE is taken as the last emission energy present in the file."""
    for df, e_pe in verified_ss_energy_distributions.values():
        assert e_pe == pytest.approx(df["Energy [eV]"].iloc[-1])


# =============================================================================
# Copper — emission yields
# =============================================================================
def test_load_cu_emission_yields_shape(
    verified_cu_emission_yields: dict,
) -> None:
    """Check that all four populations are loaded with two columns."""
    for df in verified_cu_emission_yields.values():
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["Energy [eV]", "0.0 [deg]"]


def test_load_cu_emission_yields_values(
    verified_cu_emission_yields: dict,
) -> None:
    """Redundant with fixture validation, but explicit as its own test."""
    ebe_df = verified_cu_emission_yields["EBE"]
    assert ebe_df["0.0 [deg]"].iloc[0] == pytest.approx(0.49599999189377)
    assert ebe_df["0.0 [deg]"].iloc[1] == pytest.approx(0.48824268579483)

    se_df = verified_cu_emission_yields["SE"]
    assert se_df["0.0 [deg]"].iloc[1] == pytest.approx(0.019412733614445)


# =============================================================================
# Copper — emission energy distributions
# =============================================================================
def test_load_cu_energy_distributions_shape(
    verified_cu_energy_distributions: dict,
) -> None:
    """Check that all four populations are loaded with two columns and E_PE."""
    for df, e_pe in verified_cu_energy_distributions.values():
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["Energy [eV]", "0.0 [deg]"]
        assert isinstance(e_pe, float)


def test_load_cu_energy_distributions_values(
    verified_cu_energy_distributions: dict,
) -> None:
    """Redundant with fixture validation, but explicit as its own test."""
    se_df, se_e_pe = verified_cu_energy_distributions["SE"]
    assert se_df["0.0 [deg]"].iloc[1] == pytest.approx(0.011950962245464)
    assert se_e_pe == pytest.approx(100.0)


def test_load_cu_energy_distributions_impact_energy_is_last_energy(
    verified_cu_energy_distributions: dict,
) -> None:
    """Check E_PE is taken as the last emission energy present in the file."""
    for df, e_pe in verified_cu_energy_distributions.values():
        assert e_pe == pytest.approx(df["Energy [eV]"].iloc[-1])
