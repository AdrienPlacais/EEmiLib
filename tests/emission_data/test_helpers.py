"""Test the helper functions for emission data."""

import numpy as np
import pandas as pd
from eemilib.emission_data.helper import resample, trim
from eemilib.util.constants import col_energy, col_normal


class TestTrim:
    """Test that trimming works."""

    normal_ey = pd.DataFrame(
        {
            col_energy: np.linspace(0.0, 100.0, 11),
            col_normal: np.random.rand(11),
        }
    )

    def test_no_trim(self) -> None:
        """Test no trimming."""
        expected = self.normal_ey
        returned = trim(self.normal_ey)
        assert np.array_equal(expected, returned)

    def test_low_trim(self) -> None:
        """Test lower trimming."""
        expected = self.normal_ey.iloc[2:]
        returned = trim(self.normal_ey, min_e=20)
        assert np.array_equal(expected, returned)

    def test_upp_trim(self) -> None:
        """Test upper trimming."""
        expected = self.normal_ey.iloc[:-2]
        returned = trim(self.normal_ey, max_e=80)
        assert np.array_equal(expected, returned)

    def test_both_trim(self) -> None:
        """Test both trimming."""
        expected = self.normal_ey.iloc[3:-3]
        returned = trim(self.normal_ey, min_e=30, max_e=70)
        assert np.array_equal(expected, returned)


class TestResample:
    """Test that resampling emission yield works."""

    def _generate_fake_ey(self, n_points: int) -> pd.DataFrame:
        """Generate a generic emission yield."""
        assert n_points % 2 == 1
        half = int((n_points + 1) / 2)
        fake_ey = pd.DataFrame(
            {
                col_energy: np.linspace(0, 200, n_points),
                col_normal: np.hstack(
                    (
                        np.linspace(0.5, 2.5, half),
                        np.linspace(2.5, 0.5, half)[1:],
                    )
                ),
            }
        )
        return fake_ey

    def test_resample(self) -> None:
        """Test resampling the emission yield."""
        n_orig, n_resample = 11, 15
        expected = self._generate_fake_ey(n_resample)
        original = self._generate_fake_ey(n_orig)
        returned = resample(original, n_resample)
        print(returned - expected)
        assert np.allclose(returned, expected, atol=1e-15)
