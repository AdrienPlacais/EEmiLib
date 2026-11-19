"""Define tests for the export methods of the base loader."""

import pandas as pd
import pytest

from eemilib.loader import CSTLoader


def test_export_emission_yield_not_implemented(
    cst_loader: CSTLoader, tmp_path
) -> None:
    """Check that loaders without export support say so."""
    with pytest.raises(NotImplementedError, match="CSTLoader"):
        cst_loader.export_emission_yield(
            pd.DataFrame(), tmp_path, population="all"
        )


def test_export_emission_energy_distribution_not_implemented(
    cst_loader: CSTLoader, tmp_path
) -> None:
    """Check that loaders without export support say so."""
    with pytest.raises(NotImplementedError, match="CSTLoader"):
        cst_loader.export_emission_energy_distribution(
            pd.DataFrame(), tmp_path, population="all", e_pe=100.0
        )
