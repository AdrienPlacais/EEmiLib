"""Define an object to store an emission energy distribution."""

import logging
from abc import abstractmethod
from typing import Callable, Self, Sequence

import numpy as np
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
from numpy.typing import NDArray


class EmissionEnergyDistribution(EmissionData):
    """An emission energy distribution."""

    population: ImplementedPop

    def __init__(
        self,
        data: pd.DataFrame,
        e_pe: float | None = None,
        norm: float | None = None,
    ) -> None:
        """Instantiate the data.

        Parameters
        ----------
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
        super().__init__(self.population, data)
        self.energies = data[col_energy].to_numpy()
        self.angles = [
            float(col.split()[0]) for col in data.columns if col != col_energy
        ]

        #: Peak distribution in :unit:`eV^{-1}`.
        self.peak_value: float
        #: Index of peak.
        self.i_peak: int
        self.i_peak, self.peak_value = self._peak

        #: Energy of |PEs| in :unit:`eV`. If this information is not found in
        #: the file header, we suppose it is the maximum of the input energy
        #: array.
        self.e_pe = e_pe if e_pe else float(self.data[col_energy].max())

        #: Re-normalization factor of distribution.
        self.norm = norm if norm is not None else self._default_norm()
        self.unnormalized_data = self.data
        self.normalize()

    @classmethod
    def _from_filepath(
        cls,
        loader: Loader,
        *filepath: DataPath,
        population: ImplementedPop,
        e_pes: Sequence[float] | float | None = None,
    ) -> Self:
        """Instantiate the data from files.

        Currently unused.

        Parameters
        ----------
        loader :
            The object that will load the data.
        *filepath :
            Path(s) to file holding data under study. Only the first result is
            used; if you have several measurement files, prefer
            :meth:`from_filepaths`.
        population :
            The concerned population of electrons.
        e_pes :
            |PEs| energies, if the loader cannot find them in the given files.
            Must have the same length as ``filepaths``. Can be a single float
            if only file is to be loaded.

        """
        if isinstance(e_pes, (float, int)):
            e_pes = [e_pes]
        if population != cls.population:
            logging.warning(
                f"{cls.__name__} always represents population {cls.population}"
                f", but {population = } was given. The returned object will "
                f"still hold {cls.population} data; the mismatched argument is"
                " ignored."
            )
        results = loader.load_emission_energy_distribution(
            *filepath, population=cls.population, e_pes=e_pes
        )
        if len(results) != 1:
            raise ValueError(
                f"Expected exactly one loaded distribution, got {len(results)}. "
                "Use `from_filepaths` to load several files at once."
            )
        data, e_pe = next(iter(results.values()))
        return cls(data=data, e_pe=e_pe)

    @classmethod
    def from_filepaths(
        cls,
        loader: Loader,
        *filepath: DataPath,
        population: ImplementedPop,
        e_pes: Sequence[float] | None = None,
        norms: Sequence[float | None] | None = None,
    ) -> Sequence[Self]:
        """Instantiate one instance per given file.

        Parameters
        ----------
        loader :
            The object that will load the data.
        *filepath :
            Path(s) to file(s) holding data under study, one measurement per
            file (in particular: taken at different |PEs| energies).
        population :
            The concerned population of electrons.
        e_pes :
            |PEs| energies, if the loader cannot find them in the given files.
            Must have the same length as ``filepaths``.

        Return
        ------
            One instance per successfully loaded file.

        """
        results = loader.load_emission_energy_distribution(
            *filepath, population=cls.population, e_pes=e_pes
        )
        if norms is None:
            norms = [None for _ in results]
        return [cls(data, e_pe=e_pe) for data, e_pe in results.values()]

    @abstractmethod
    def _default_norm(self) -> float:
        """Compute the default normalization constant for this population.

        Subclasses should override this to define population-specific behavior
        (e.g. normalizing by this population's own peak value).

        """

    @property
    def label(self) -> str:
        """Print nature of data (markdown)."""
        return md_energy_distrib[self.population]

    def plot[T](
        self,
        plotter: Plotter,
        *args,
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
            marker=marker,
            grid=grid,
            label=self.label,
            population=population,
            is_model=False,
            e_pe=self.e_pe,
            **kwargs,
        )

    def normalize(self) -> None:
        """Normalize the distribution by :attr:`norm`."""
        if self.norm is None:
            raise ValueError("Cannot normalize if norm is None")
        data_columns = [c for c in self.data.columns if c != col_energy]
        self.data[data_columns] = (
            self.unnormalized_data[data_columns] / self.norm
        )

    @property
    def _se_ebe_limit(self) -> int:
        """Arbitrary index limit between |SEs| and |EBEs|."""
        return int(self._n_points / 4)

    @property
    def _peak(self) -> tuple[int, float]:
        """Find maximum of PDF.

        Returns
        -------
        float
            Index of the peak.
        float
            Value of the peak.

        """
        i = self.data[col_normal].argmax()
        return i, float(self.data.at[i, col_normal])


class SEEmissionEnergyDistribution(EmissionEnergyDistribution):
    """Emission energy distribution of |SEs|."""

    population = "SE"

    def _default_norm(self) -> float:
        """Compute the default normalization constant for this population.

        Subclasses should override this to define population-specific behavior
        (e.g. normalizing by this population's own peak value).

        """
        return self.peak_value


class EBEEmissionEnergyDistribution(EmissionEnergyDistribution):
    """Emission energy distribution of |EBEs|."""

    population = "EBE"

    def _default_norm(self) -> float:
        """Compute the default normalization constant for this population.

        Subclasses should override this to define population-specific behavior
        (e.g. normalizing by this population's own peak value).

        """
        logging.warning(
            "Default norm was not overriden. Returning default value of 1.0"
        )
        return 1.0


class IBEEmissionEnergyDistribution(EmissionEnergyDistribution):
    """Emission energy distribution of |EBEs|."""

    population = "IBE"

    def _default_norm(self) -> float:
        """Compute the default normalization constant for this population.

        Subclasses should override this to define population-specific behavior
        (e.g. normalizing by this population's own peak value).

        """
        logging.warning(
            "Default norm was not overriden. Returning default value of 1.0"
        )
        return 1.0


class AllEmissionEnergyDistribution(EmissionEnergyDistribution):
    """Emission energy distribution of all populations."""

    population = "all"

    def _default_norm(self) -> float:
        return self._SE_peak[1]

    @property
    def _SE_peak(self) -> tuple[int, float]:
        """Find the |SEs| maximum."""
        i = int(self.data[: self._se_ebe_limit][col_normal].argmax())
        return i, float(self.data.at[i, col_normal])

    @property
    def _EBE_peak(self) -> tuple[float, float]:
        """Find the position of the |EBE| peak."""
        raise NotImplementedError("still used?")
        i = (
            self.data[self._se_ebe_limit :][col_normal].argmax()
            + self._se_ebe_limit
        )
        e_peak_ebe = self.data.at[i, col_energy]
        return float(e_peak_ebe), float(self.data.at[i, col_normal])

    def decompose(
        self,
        se_shape: Callable[[NDArray[np.float64]], NDArray[np.float64]],
        ebe_shape: Callable[[NDArray[np.float64]], NDArray[np.float64]],
        ibe_shape: Callable[[NDArray[np.float64]], NDArray[np.float64]],
    ) -> tuple[
        SEEmissionEnergyDistribution,
        EBEEmissionEnergyDistribution,
        IBEEmissionEnergyDistribution,
    ]:
        r"""Split total energy distribution into |SE|/|EBE|/|IBE| shares.

        At each emission energy :math:`E`, the measured total value is split
        proportionally to each population's expected shape at that energy:

        .. math::
            f_\mathrm{pop}(E) = f_\mathrm{all}(E) \times
                    \frac{
                        \mathrm{shape}_\mathrm{pop}(E)
                    }{
                        \mathrm{shape}_\mathrm{SE}(E)
                        + \mathrm{shape}_\mathrm{EBE}(E)
                        + \mathrm{shape}_\mathrm{IBE}(E)
                    }

        This is a soft decomposition (fractional weights, not a hard cutoff): a
        given energy can be mostly SE and partly EBE, for instance.

        Parameters
        ----------
        se_shape :
            Function returning the expected (unnormalized) |SE| shape at the
            given emission energies. Must already be bound to the relevant
            impact energy and incidence angle (e.g. via
            :func:`functools.partial` applied to
            :func:`.se_energy_distribution`).
        ebe_shape :
            Same as ``se_shape``, for |EBEs| (e.g. bound
            :func:`.ebe_energy_distribution`).
        ibe_shape :
            Same as ``se_shape``, for |IBEs| (e.g. bound
            :func:`.ibe_energy_distribution`).

        Return
        ------
            The |SE|, |EBE|, |IBE| shares of ``self``, each as their respective
            :class:`.EmissionEnergyDistribution` subclass. Values are
            constructed with ``norm=1.0`` (no further re-normalization), since
            they are already consistently scaled with ``self``.

        """
        energies = np.array(self.energies)
        e_pe = self.e_pe

        shapes = {
            "SE": se_shape(energies),
            "EBE": ebe_shape(energies),
            "IBE": ibe_shape(energies),
        }
        total_shape = sum(shapes.values())
        has_signal = total_shape > 0
        weights = {
            pop: np.divide(
                shape, total_shape, out=np.zeros_like(shape), where=has_signal
            )
            for pop, shape in shapes.items()
        }

        data_columns = [c for c in self.data.columns if c != col_energy]
        split_data = {
            pop: self.data.assign(
                **{col: self.data[col] * weight for col in data_columns}
            )
            for pop, weight in weights.items()
        }

        return (
            SEEmissionEnergyDistribution(
                split_data["SE"], e_pe=e_pe, norm=1.0
            ),
            EBEEmissionEnergyDistribution(
                split_data["EBE"], e_pe=e_pe, norm=1.0
            ),
            IBEEmissionEnergyDistribution(
                split_data["IBE"], e_pe=e_pe, norm=1.0
            ),
        )


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
