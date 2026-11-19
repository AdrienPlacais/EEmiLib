"""Define tests for the pandas loader."""

from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from eemilib.loader import PandasLoader
from eemilib.loader.helper import read_comments


@pytest.fixture
def pandas_loader() -> PandasLoader:
    """Instantiate a loader with default separator and comment character."""
    return PandasLoader()


@pytest.fixture
def yield_df() -> pd.DataFrame:
    """Create a small emission yield with two incidence angles."""
    return pd.DataFrame(
        {
            "Energy [eV]": [0.0, 10.0, 20.0],
            "0.0 [deg]": [0.1, 0.5, 0.9],
            "20.0 [deg]": [0.2, 0.6, 1.0],
        }
    )


@pytest.fixture
def distribution_df() -> pd.DataFrame:
    """Create a small normal-incidence emission energy distribution."""
    return pd.DataFrame(
        {"Energy [eV]": [0.0, 0.2, 0.4], "0.0 [deg]": [0.0, 0.01, 0.02]}
    )


def test_export_emission_yield_filename(
    pandas_loader: PandasLoader, yield_df: pd.DataFrame, tmp_path: Path
) -> None:
    """Check the name of the exported file."""
    path = pandas_loader.export_emission_yield(
        yield_df, tmp_path, "test", population="SE"
    )
    assert path == tmp_path / "test_emission_yield_SE.csv"
    assert path.is_file()


def test_export_emission_yield_round_trip(
    pandas_loader: PandasLoader, yield_df: pd.DataFrame, tmp_path: Path
) -> None:
    """Check that an exported emission yield can be loaded back."""
    path = pandas_loader.export_emission_yield(
        yield_df, tmp_path, population="all"
    )
    assert_frame_equal(pandas_loader.load_emission_yield(path), yield_df)


def test_export_emission_yield_creates_folder(
    pandas_loader: PandasLoader, yield_df: pd.DataFrame, tmp_path: Path
) -> None:
    """Check that a missing folder is created."""
    path = pandas_loader.export_emission_yield(
        yield_df, tmp_path / "a" / "b", population="all"
    )
    assert path.is_file()


def test_export_emission_yield_comments(
    pandas_loader: PandasLoader, yield_df: pd.DataFrame, tmp_path: Path
) -> None:
    """Check that comments are written at the start of the file."""
    path = pandas_loader.export_emission_yield(
        yield_df, tmp_path, population="all", comments=["first", "second"]
    )
    assert read_comments(path) == [" first", " second"]
    assert_frame_equal(pandas_loader.load_emission_yield(path), yield_df)


def test_export_emission_yield_keeps_one_backup(
    pandas_loader: PandasLoader, yield_df: pd.DataFrame, tmp_path: Path
) -> None:
    """Check that the previous file becomes ``.bak``, replacing older ones."""
    exported = [yield_df * i for i in (1.0, 2.0, 3.0)]
    exported = [
        df.assign(**{"Energy [eV]": yield_df["Energy [eV]"]})
        for df in exported
    ]
    path = None
    for df in exported:
        path = pandas_loader.export_emission_yield(
            df, tmp_path, population="all"
        )
    assert path is not None

    backup = path.with_name(path.name + ".bak")
    assert_frame_equal(pandas_loader.load_emission_yield(path), exported[2])
    assert_frame_equal(pandas_loader.load_emission_yield(backup), exported[1])
    assert len(list(tmp_path.iterdir())) == 2


def test_export_emission_energy_distribution_filename(
    pandas_loader: PandasLoader, distribution_df: pd.DataFrame, tmp_path: Path
) -> None:
    """Check that the PE energy is appended to the file name."""
    path = pandas_loader.export_emission_energy_distribution(
        distribution_df, tmp_path, "test", population="all", e_pe=100.0
    )
    assert path == tmp_path / "test_emission_energy_all_100eV.csv"


def test_export_emission_energy_distribution_round_trip(
    pandas_loader: PandasLoader, distribution_df: pd.DataFrame, tmp_path: Path
) -> None:
    """Check that data and PE energy are loaded back, comments included."""
    path = pandas_loader.export_emission_energy_distribution(
        distribution_df,
        tmp_path,
        population="all",
        e_pe=12.5,
        comments=["some metadata"],
    )
    loaded, e_pe = pandas_loader.load_emission_energy_distribution(path)[path]
    assert_frame_equal(loaded, distribution_df)
    assert e_pe == pytest.approx(12.5)
    assert read_comments(path)[2:] == [" some metadata"]


def test_export_emission_energy_distribution_rejects_several_angles(
    pandas_loader: PandasLoader, yield_df: pd.DataFrame, tmp_path: Path
) -> None:
    """Check that a file the loader could not read back is not written."""
    with pytest.raises(ValueError, match="two columns"):
        pandas_loader.export_emission_energy_distribution(
            yield_df, tmp_path, population="all", e_pe=100.0
        )
    assert not list(tmp_path.iterdir())
