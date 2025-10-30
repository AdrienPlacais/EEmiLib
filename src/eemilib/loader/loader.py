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
        #: Column separator. Not mandatory, but must be called ``sep`` in order
        #: to be recognized by the Parameters in the GUI.
        self.sep: str
        #: Comment character. Not mandatory, but must be called ``comment`` in
        #: order to be recognized by the Parameters in the GUI.
        self.comment: str

    @abstractmethod
    def load_emission_yield(
        self,
        filepath: str | Path | Collection[str] | Collection[Path],
        *args,
        **kwargs,
    ) -> pd.DataFrame:
        """Load the given electron emission yield file."""

    @abstractmethod
    def load_emission_energy_distribution(
        self,
        filepath: str | Path | Collection[str] | Collection[Path],
        *args,
        **kwargs,
    ) -> tuple[pd.DataFrame, float | None]:
        """Load the given electron emission energy distribution file.

        Should also try to load the energy of primary electrons from file
        metadata. If not possible, :class:`.EmissionEnergyDistribution` will
        try to infer it from the position of the |EBEs| peak.

        """

    @abstractmethod
    def load_emission_angle_distribution(
        self,
        filepath: str | Path | Collection[str] | Collection[Path],
        *args,
        **kwargs,
    ) -> pd.DataFrame:
        """Load the given electron emission angle distribution file."""
