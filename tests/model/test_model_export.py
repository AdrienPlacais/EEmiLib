"""Define tests for :meth:`.Model.export`."""

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from eemilib.emission_data import DataMatrix
from eemilib.emission_data.emission_energy_distribution import (
    AllEmissionEnergyDistribution,
)
from eemilib.loader import CSTLoader, PandasLoader
from eemilib.loader.helper import read_comments
from eemilib.model import FurmanPivi
from eemilib.util.constants import COL_ENERGY, COL_NORMAL


@pytest.fixture
def model() -> FurmanPivi:
    """Create a default instance of :class:`.FurmanPivi`."""
    return FurmanPivi()


@pytest.fixture
def loader() -> PandasLoader:
    """Instantiate a loader with default separator and comment character."""
    return PandasLoader()


def test_export_returns_written_files(
    model: FurmanPivi, loader: PandasLoader, tmp_path: Path
) -> None:
    """Check that returned paths are exactly the files on disk."""
    paths = model.export(
        loader, tmp_path, e_pes=[10.0, 50.0], energy=np.linspace(0, 100, 11)
    )
    assert len(paths) > 0
    assert set(paths) == set(tmp_path.iterdir())


def test_export_emission_yield_filenames(
    model: FurmanPivi, loader: PandasLoader, tmp_path: Path
) -> None:
    """Check that one file per population is written."""
    model.export(loader, tmp_path, "test", data_types=["Emission Yield"])
    expected = {f"test_emission_yield_{pop}.csv" for pop in model.populations}
    assert {p.name for p in tmp_path.iterdir()} == expected


def test_export_emission_yield_round_trip(
    model: FurmanPivi, loader: PandasLoader, tmp_path: Path
) -> None:
    """Check that exported yields are loaded back as modelled."""
    energy = np.linspace(0, 100, 11)
    theta = np.array([0.0, 30.0])
    model.export(
        loader,
        tmp_path,
        data_types=["Emission Yield"],
        populations=["all"],
        energy=energy,
        theta=theta,
    )
    loaded = loader.load_emission_yield(
        tmp_path / "eemilib_emission_yield_all.csv"
    )
    assert_frame_equal(loaded, model.teey(energy, theta))


def test_export_energy_distribution_filenames_and_trim(
    model: FurmanPivi, loader: PandasLoader, tmp_path: Path
) -> None:
    """Check file names, PE energies, and that data stops at the PE energy."""
    model.export(
        loader,
        tmp_path,
        data_types=["Emission Energy"],
        populations=["all"],
        energy=np.linspace(0, 100, 101),
        e_pes=[10, 50],
    )
    for e_pe in (10, 50):
        path = tmp_path / f"eemilib_emission_energy_all_{e_pe}eV.csv"
        loaded, loaded_e_pe = loader.load_emission_energy_distribution(path)[
            path
        ]
        assert loaded_e_pe == pytest.approx(e_pe)
        assert loaded[COL_ENERGY].iloc[-1] == pytest.approx(e_pe)
        assert list(loaded.columns) == [COL_ENERGY, COL_NORMAL]


def test_export_energy_distribution_warns_on_oblique_theta(
    model: FurmanPivi,
    loader: PandasLoader,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Check that only normal incidence is exported, with a warning."""
    with caplog.at_level(logging.WARNING):
        paths = model.export(
            loader,
            tmp_path,
            data_types=["Emission Energy"],
            populations=["all"],
            theta=np.array([0.0, 30.0]),
            e_pes=[50.0],
        )
    assert "normal incidence" in caplog.text
    loaded, _ = loader.load_emission_energy_distribution(paths[0])[paths[0]]
    assert list(loaded.columns) == [COL_ENERGY, COL_NORMAL]


def test_export_energy_distribution_default_e_pes(
    model: FurmanPivi,
    loader: PandasLoader,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Check the fallback on default PE energies, with a warning."""
    with caplog.at_level(logging.WARNING):
        paths = model.export(
            loader,
            tmp_path,
            data_types=["Emission Energy"],
            populations=["all"],
        )
    assert "default" in caplog.text
    assert len(paths) == 6


def test_export_energy_distribution_e_pes_from_reference(
    model: FurmanPivi, loader: PandasLoader, tmp_path: Path
) -> None:
    """Check that PE energies are taken from the reference data."""
    measured = pd.DataFrame(
        {COL_ENERGY: np.linspace(0, 30, 31), COL_NORMAL: np.ones(31)}
    )
    reference = DataMatrix()
    reference.set_data(
        AllEmissionEnergyDistribution(measured, e_pe=30.0, norm=1.0)
    )
    model.set_reference_data(reference)

    paths = model.export(
        loader, tmp_path, data_types=["Emission Energy"], populations=["all"]
    )
    assert [p.name for p in paths] == ["eemilib_emission_energy_all_30eV.csv"]


def test_export_default_comments(
    model: FurmanPivi, loader: PandasLoader, tmp_path: Path
) -> None:
    """Check that class name and parameters are written by default."""
    paths = model.export(
        loader, tmp_path, data_types=["Emission Yield"], populations=["all"]
    )
    comments = read_comments(paths[0])
    assert comments[0] == " FurmanPivi data"
    assert len(comments) == 1 + len(model.parameters)
    assert any(line.strip().startswith("t_1") for line in comments)


def test_export_custom_comments(
    model: FurmanPivi, loader: PandasLoader, tmp_path: Path
) -> None:
    """Check that given comments replace the default ones."""
    paths = model.export(
        loader,
        tmp_path,
        data_types=["Emission Yield"],
        populations=["all"],
        comments=["custom"],
    )
    assert read_comments(paths[0]) == [" custom"]


def test_export_unsupported_loader(
    model: FurmanPivi, cst_loader: CSTLoader, tmp_path: Path
) -> None:
    """Check that a loader without export support raises."""
    with pytest.raises(NotImplementedError):
        model.export(cst_loader, tmp_path, data_types=["Emission Yield"])
