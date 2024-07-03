"""Define the base object that will store emission data."""
from abc import abstractmethod
from pathlib import Path
from typing import Literal, Self

import pandas as pd

from eemilib.loader.loader import Loader


class EmissionData(pd.DataFrame):
    """A yield, energy distribution or angular distribution."""

    def __init__(self,
                 population: Literal["SE", "EBE", "IBE", "all"],
                 data: pd.DataFrame,
                 ) -> None:
        """Instantiate the data.

        Parameters
        ----------
        population : Literal["SE", "EBE", "IBE", "all"]
            The concerned population of electrons.
        data : pd.DataFrame
            Structure holding the data. Column headers as well as units must
            follow specications (see subclasses documentation).

        """
        super().__init__(data)
        self.population = population

    @abstractmethod
    @classmethod
    def from_filepath( cls, population: Literal["SE", "EBE", "IBE", "all"], loader: Loader, *filepath: str | Path) -> Self:
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


class EmissionYield(EmissionData):
    """An emission yield."""

    def __init__(self, population: Literal["SE", "EBE", "IBE", "all"], data: pd.DataFrame) -> None:
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
                 *filepath: str | Path
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
