"""Define an object to store an emission energy distribution."""

import logging
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
            Re-normalization constant. If not provided, defaults to
            :meth:`_default_norm`, which each subclass defines according to its
            own population. Pass ``1.0`` explicitly to disable normalization.

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
        self.norm = norm if norm is not None else self._default_norm()
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

    def _default_norm(self) -> float:
        """Compute the default normalization constant for this population.

        Subclasses should override this to define population-specific behavior
        (e.g. normalizing by this population's own peak value).

        """
        logging.warning(
            "Default norm was not overriden. Returning default value of 1.0"
        )
        return 1.0

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
    def _peak(self) -> tuple[float, float]:
        """Find maximum of PDF.

        Returns
        -------
        float
            Position of the peak in :unit:`eV`.
        float
            Value of the peak.

        """
        i = self.data[col_normal].argmax()
        e_peak = self.data.at[i, col_energy]
        return float(e_peak), float(self.data.at[i, col_normal])


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
        if population != "SE":
            logging.warning(
                f"{cls.__name__} always represents population 'SE', but "
                f"{population = } was given. The returned object will still "
                "hold 'SE' data; the mismatched argument is ignored."
            )
        data, e_pe = loader.load_emission_energy_distribution(*filepath)
        return cls(data, e_pe=e_pe)

    def _default_norm(self) -> float:
        """Compute the default normalization constant for this population.

        Subclasses should override this to define population-specific behavior
        (e.g. normalizing by this population's own peak value).

        """
        return self._peak[1]


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
        if population != "EBE":
            logging.warning(
                f"{cls.__name__} always represents population 'EBE', but "
                f"{population = } was given. The returned object will still "
                "hold 'EBE' data; the mismatched argument is ignored."
            )
        data, e_pe = loader.load_emission_energy_distribution(*filepath)
        return cls(data, e_pe=e_pe)


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
        if population != "IBE":
            logging.warning(
                f"{cls.__name__} always represents population 'IBE', but "
                f"{population = } was given. The returned object will still "
                "hold 'IBE' data; the mismatched argument is ignored."
            )
        data, e_pe = loader.load_emission_energy_distribution(*filepath)
        return cls(data, e_pe=e_pe)


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
        self.e_peak_se, _ = self._SE_peak
        #: Energy at the maximum of |EBEs| in :unit:`eV`.
        self.e_peak_ebe: float
        #: Position of |EBE| peak.
        self.e_peak_ebe, _ = self._EBE_peak

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
        if population != "all":
            logging.warning(
                f"{cls.__name__} always represents population 'all', but "
                f"{population = } was given. The returned object will still "
                "hold 'all' data; the mismatched argument is ignored."
            )
        data, e_pe = loader.load_emission_energy_distribution(*filepath)
        return cls(data, e_pe=e_pe)

    def _default_norm(self) -> float:
        return self._SE_peak[1]

    @property
    def _SE_peak(self) -> tuple[float, float]:
        """Find the |SEs| maximum."""
        i = self.data[: self._se_ebe_limit][col_normal].argmax()
        e_peak_se = self.data.at[i, col_energy]
        return float(e_peak_se), float(self.data.at[i, col_normal])

    @property
    def _EBE_peak(self) -> tuple[float, float]:
        """Find the position of the |EBE| peak."""
        i = (
            self.data[self._se_ebe_limit :][col_normal].argmax()
            + self._se_ebe_limit
        )
        e_peak_ebe = self.data.at[i, col_energy]
        return float(e_peak_ebe), float(self.data.at[i, col_normal])


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
