"""Test the helper functions for emission data."""

import numpy as np
import pandas as pd
import pytest

from eemilib.emission_data.helper import trim
from eemilib.loader.loader import EY_col1, EY_colnorm


class TestTrim:
    """Test that trimming works."""

    normal_ey = pd.DataFrame(
        {EY_col1: np.linspace(0.0, 100.0, 11), EY_colnorm: np.random.rand(11)}
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
