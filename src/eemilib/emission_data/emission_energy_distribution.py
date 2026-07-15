"""Define an object to store an emission energy distribution."""

from typing import Self

import pandas as pd
from eemilib.emission_data.emission_data import EmissionData
from eemilib.loader.helper import DataPath
from eemilib.loader.loader import Loader
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import (
    ImplementedPop,
    col_energy,
    col_normal,
    md_energy_distrib,
)


class EmissionEnergyDistribution(EmissionData):
    """An emission energy distribution."""

    def __init__(
        self,
        population: ImplementedPop,
        data: pd.DataFrame,
        e_pe: float | None = None,
        norm: float | None = None,
    ) -> None:
        """Instantiate the data.

        Parameters
        ----------
        population :
            The concerned population of electrons.
        data :
            Structure holding the data. Must have a ``Energy (eV)`` column
            holding ``population`` energy. And one or several columns
            ``theta [deg]``, where ``theta`` is the value of the incidence
            angle and content is corresponding emission energy.
        e_pe :
            Energy of primary electrons in :unit:`eV`.
        norm :
            To specify re-normalization constant. If not provided, we try to
            set the maximum of |SEs| to unity. Provide ``1.0`` to avoid any
            normalization.

        """
        super().__init__(population, data)
        self.energies = data[col_energy].to_numpy()
        self.angles = [
            float(col.split()[0]) for col in data.columns if col != col_energy
        ]

        #: Energy of peak distribution in :unit:`eV`.
        self.e_peak: float
        _, self.e_peak = self._peak

        #: Energy of |PEs| in :unit:`eV`. If this information is not found in
        #: the file header, we suppose it is the maximum of the input energy
        #: array.
        self.e_pe = e_pe if e_pe else float(self.data[col_energy].max())

        #: Re-normalization factor of distribution.
        self.norm = norm
        if self.norm:
            self.normalize()

    @classmethod
    def from_filepath(
        cls,
        loader: Loader,
        *filepath: DataPath,
        population: ImplementedPop,
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
        data, e_pe = loader.load_emission_energy_distribution(*filepath)
        return cls(population, data, e_pe=e_pe)

    @property
    def label(self) -> str:
        """Print nature of data (markdown)."""
        return md_energy_distrib[self.population]

    def plot[T](
        self,
        plotter: Plotter,
        *args,
        lw: float | None = 0.0,
        marker: str | None = "+",
        axes: T | None = None,
        grid: bool = True,
        population: ImplementedPop | None = None,
        **kwargs,
    ) -> T:
        """Plot the contained data using plotter.

        This wrapper simply calls the
        :meth:`.Plotter.plot_emission_energy_distribution` method.
        method.

        """
        return plotter.plot_emission_energy_distribution(
            df=self.data,
            *args,
            axes=axes,
            lw=lw,
            marker=marker,
            grid=grid,
            label=self.label,
            population=population,
            is_model=False,
            **kwargs,
        )

    def normalize(self) -> None:
        """Normalize the distribution by :attr:`norm`."""
        if self.norm is None:
            raise ValueError("Cannot normalize if norm is None")
        data_columns = [c for c in self.data.columns if c != col_energy]
        self.data[data_columns] /= self.norm

    @property
    def _se_ebe_limit(self) -> int:
        """Arbitrary index limit between |SEs| and |EBEs|."""
        return int(self._n_points / 4)

    @property
    def _peak(self) -> tuple[int, float]:
        """Find maximum of PDF.

        Returns
        -------
        int
            Index of maximum value.
        float
            Position of the peak in :unit:`eV`.

        """
        i = self.data[col_normal].argmax()
        e_peak = self.data.at[i, col_energy]
        return int(i), float(e_peak)


class SEEmissionEnergyDistribution(EmissionEnergyDistribution):
    """Emission energy distribution of |SEs|."""

    def __init__(
        self,
        data: pd.DataFrame,
        e_pe: float | None = None,
        norm: float | None = None,
    ) -> None:
        super().__init__(population="SE", data=data, e_pe=e_pe, norm=norm)

    @classmethod
    def from_filepath(
        cls,
        loader: Loader,
        *filepath: DataPath,
        population: ImplementedPop = "SE",
    ) -> Self:
        """Instantiate the data from files.

        Parameters
        ----------
        loader :
            The object that will load the data.
        *filepath :
            Path(s) to file holding data under study.
        population :
            The concerned population of electrons.

        """
        return super().from_filepath(loader, *filepath, population=population)


class EBEEmissionEnergyDistribution(EmissionEnergyDistribution):
    """Emission energy distribution of |EBEs|."""

    def __init__(
        self,
        data: pd.DataFrame,
        e_pe: float | None = None,
        norm: float | None = None,
    ) -> None:
        super().__init__(population="EBE", data=data, e_pe=e_pe, norm=norm)

    @classmethod
    def from_filepath(
        cls,
        loader: Loader,
        *filepath: DataPath,
        population: ImplementedPop = "EBE",
    ) -> Self:
        """Instantiate the data from files.

        Parameters
        ----------
        loader :
            The object that will load the data.
        *filepath :
            Path(s) to file holding data under study.
        population :
            The concerned population of electrons.

        """
        return super().from_filepath(loader, *filepath, population=population)


class IBEEmissionEnergyDistribution(EmissionEnergyDistribution):
    """Emission energy distribution of |EBEs|."""

    def __init__(
        self,
        data: pd.DataFrame,
        e_pe: float | None = None,
        norm: float | None = None,
    ) -> None:
        super().__init__(population="IBE", data=data, e_pe=e_pe, norm=norm)

    @classmethod
    def from_filepath(
        cls,
        loader: Loader,
        *filepath: DataPath,
        population: ImplementedPop = "IBE",
    ) -> Self:
        """Instantiate the data from files.

        Parameters
        ----------
        loader :
            The object that will load the data.
        *filepath :
            Path(s) to file holding data under study.
        population :
            The concerned population of electrons.

        """
        return super().from_filepath(loader, *filepath, population=population)


class AllEmissionEnergyDistribution(EmissionEnergyDistribution):
    """Emission energy distribution of all populations."""

    def __init__(
        self,
        data: pd.DataFrame,
        e_pe: float | None = None,
        norm: float | None = None,
    ) -> None:
        super().__init__(population="all", data=data, e_pe=e_pe, norm=norm)
        #: Energy at the maximum of |SEs| in :unit:`eV`.
        self.e_peak_se: float
        _, self.e_peak_se = self._SE_peak
        #: Energy at the maximum of |EBEs| in :unit:`eV`.
        self.e_peak_ebe: float
        #: Position of |EBE| peak.
        self.i_peak_ebe: int
        self.i_peak_ebe, self.e_peak_ebe = self._EBE_peak

    @classmethod
    def from_filepath(
        cls,
        loader: Loader,
        *filepath: DataPath,
        population: ImplementedPop = "all",
    ) -> Self:
        """Instantiate the data from files.

        Parameters
        ----------
        loader :
            The object that will load the data.
        *filepath :
            Path(s) to file holding data under study.
        population :
            The concerned population of electrons.

        """
        return super().from_filepath(loader, *filepath, population=population)

    @property
    def _SE_peak(self) -> tuple[int, float]:
        """Find the |SEs| maximum."""
        i = self.data[: self._se_ebe_limit][col_normal].argmax()
        e_peak_se = self.data.at[i, col_energy]
        return int(i), float(e_peak_se)

    @property
    def _EBE_peak(self) -> tuple[int, float]:
        """Find the position of the |EBE| peak."""
        i = (
            self.data[self._se_ebe_limit :][col_normal].argmax()
            + self._se_ebe_limit
        )
        e_peak_ebe = self.data.at[i, col_energy]
        return int(i), float(e_peak_ebe)


#: Maps populations to their appropriate :class:`.EmissionEnergyDistribution`
#: subclass.
EMISSION_ENERGIES_BY_POP: dict[
    ImplementedPop, type[EmissionEnergyDistribution]
] = {
    "SE": SEEmissionEnergyDistribution,
    "EBE": EBEEmissionEnergyDistribution,
    "IBE": IBEEmissionEnergyDistribution,
    "all": AllEmissionEnergyDistribution,
}
