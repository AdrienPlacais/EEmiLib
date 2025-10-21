"""Define an object to store an emission angle distribution."""

from pathlib import Path
from typing import Self

import pandas as pd
from eemilib.emission_data.emission_data import EmissionData
from eemilib.loader.loader import Loader
from eemilib.util.constants import ImplementedPop


class EmissionAngleDistribution(EmissionData):
    """An emission angle distribution."""

    def __init__(
        self,
        population: ImplementedPop,
        data: pd.DataFrame,
    ) -> None:
        """Instantiate the data.

        Parameters
        ----------
        population :
            The concerned population of electrons.
        data :
            Structure holding the data. Must have an ``Angle [deg]`` column
            holding PEs angle. And one or several columns ``theta [deg]``,
            where `theta` is the value of the incidence angle and content is
            corresponding emission angle.

        """
        super().__init__(population, data)
        raise NotImplementedError

    @classmethod
    def from_filepath(
        cls,
        population: ImplementedPop,
        loader: Loader,
        *filepath: str | Path,
    ) -> Self:
        """Instantiate the data from files.

        Parameters
        ----------
        loader :
            The object that will load the data.
        population :
            The concerned population of electrons.
        *filepath :
            Path(s) to file holding data under study.

        """
        data = loader.load_emission_angle_distribution(*filepath)
        return cls(population, data)

    @property
    def label(self) -> str:
        """Print nature of data (markdown)."""
        raise NotImplementedError
