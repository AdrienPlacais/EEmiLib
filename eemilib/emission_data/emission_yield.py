"""Define an object to store an emission yield."""

from pathlib import Path
from typing import Literal, Self

import pandas as pd

from eemilib.emission_data.emission_data import EmissionData
from eemilib.loader.loader import Loader


class EmissionYield(EmissionData):
    """An emission yield."""

    def __init__(
        self,
        population: Literal["SE", "EBE", "IBE", "all"],
        data: pd.DataFrame,
    ) -> None:
        """Instantiate the data.

        Parameters
        ----------
        population : Literal["SE", "EBE", "IBE", "all"]
            The concerned population of electrons.
        data : pd.DataFrame
            Structure holding the data. Must have a ``Energy (eV)`` column
            holding PEs energy. And one or several columns ``theta [deg]``,
            where `theta` is the value of the incidence angle and content is
            corresponding emission yield.

        """
        super().__init__(population, data)

    @classmethod
    def from_filepath(
        cls,
        population: Literal["SE", "EBE", "IBE", "all"],
        loader: Loader,
        *filepath: str | Path,
    ) -> Self:
        """Instantiate the data from files.

        Parameters
        ----------
        loader : Loader
            The object that will load the data.
        population : Literal["SE", "EBE", "IBE", "all"]
            The concerned population of electrons.
        *filepath : str | Path
            Path(s) to file holding data under study.

        """
        data = loader.load_emission_yield(*filepath)
        return cls(population, data)
