"""Define the ABC for the :class:`Loader`."""

from abc import ABC, abstractmethod
from collections.abc import Collection
from pathlib import Path

import pandas as pd
from eemilib.util.helper import documentation_url

paths = Path | str


class Loader(ABC):
    """Define the base class for loading various electron emission files."""

    def __init__(self) -> None:
        """Instantiate the object."""
        self.doc_url = documentation_url(self)

    @abstractmethod
    def load_emission_yield(
        self, filepath: str | Path | Collection[str] | Collection[Path]
    ) -> pd.DataFrame:
        """Load the given electron emission yield file."""

    @abstractmethod
    def load_emission_energy_distribution(
        self, filepath: str | Path | Collection[str] | Collection[Path]
    ) -> pd.DataFrame:
        """Load the given electron emission energy distribution file."""

    @abstractmethod
    def load_emission_angle_distribution(
        self, filepath: str | Path | Collection[str] | Collection[Path]
    ) -> pd.DataFrame:
        """Load the given electron emission angle distribution file."""
