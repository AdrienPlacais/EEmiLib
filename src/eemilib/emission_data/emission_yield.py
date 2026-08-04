"""Define an object to store an emission yield."""

import logging
from collections.abc import Callable
from pathlib import Path
from re import L
from typing import Self

import numpy as np
import pandas as pd
from eemilib.emission_data.emission_data import EmissionData, MissingDataError
from eemilib.emission_data.helper import (
    get_crossover_energies,
    get_emax_eymax,
    resample,
)
from eemilib.loader.helper import DataPath
from eemilib.loader.loader import Loader
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import (
    ImplementedPop,
    col_energy,
    col_normal,
    md_ey,
)
from numpy.typing import NDArray


class MissingNormalEmissionYieldError(MissingDataError):
    """Error raised when emission yield at normal incidence would be needed."""


class EmissionYield(EmissionData):
    """An emission yield."""

    population: ImplementedPop

    def __init__(self, data: pd.DataFrame) -> None:
        """Instantiate the data.

        Parameters
        ----------
        data :
            Structure holding the data. Must have an ``Energy (eV)`` column
            holding |PEs| energy. And one or several columns ``theta [deg]``,
            where ``theta`` is the value of the incidence angle and content is
            corresponding emission yield.

        """
        super().__init__(self.population, data)
        self.energies = data[col_energy].to_numpy()
        self.angles = [
            float(col.split()[0]) for col in data.columns if col != col_energy
        ]

    @classmethod
    def _from_filepath(
        cls, loader: Loader, *filepath: DataPath, population: ImplementedPop
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
        if population != cls.population:
            logging.warning(
                f"{cls.__name__} always represents population {cls.population}"
                f", but {population = } was given. The returned object will "
                f"still hold {cls.population} data; the mismatched argument is"
                " ignored."
            )
        data = loader.load_emission_yield(*filepath, population=cls.population)
        return cls(data=data)

    @classmethod
    def from_filepaths(
        cls, loader: Loader, *filepath: DataPath, population: ImplementedPop
    ) -> list[Self]:
        return [
            cls._from_filepath(loader, fp, population=population)
            for fp in filepath
        ]

    @property
    def label(self) -> str:
        """Print nature of data (markdown)."""
        return md_ey[self.population]

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

        This wrapper simply calls the :meth:`.Plotter.plot_emission_yield`
        method.

        """
        return plotter.plot_emission_yield(
            df=self.data,
            *args,
            axes=axes,
            marker=marker,
            grid=grid,
            label=self.label,
            population=population,
            is_model=False,
            **kwargs,
        )


class SEEY(EmissionYield):
    """|SEEY|.

    In addition to the other emission yields, has characteristic points:
    cross-over energies, maximum yield, energy at maximum yield.

    """

    population = "SE"

    def __init__(self, data: pd.DataFrame) -> None:
        """Compute characteristic parameters."""
        super().__init__(data)

        #: Energy at the maximum emission yield in :unit:`eV`.
        self.e_max: float
        #: Maximum emission yield.
        self.ey_max: float
        #: First cross-over energy in :unit:`eV`.
        self.e_c1: float
        #: Second cross-over energy in :unit:`eV`.
        self.e_c2: float | None
        self.e_max, self.ey_max, self.e_c1, self.e_c2 = self._parameters(
            n_resample=1000
        )

    def _parameters(
        self, n_resample: int = -1
    ) -> tuple[float, float, float, float | None]:
        """Compute the characteristics of the emission yield."""
        if 0.0 not in self.angles:
            raise MissingNormalEmissionYieldError(
                "We need normal incidence measurements to compute "
                "characteristic points."
            )

        normal_ey = self.data[[col_energy, col_normal]]
        assert isinstance(normal_ey, pd.DataFrame)
        normal_ey = resample(normal_ey, n_resample)

        e_max, sigma_max = self._get_maximum_ey(normal_ey)
        e_c1, e_c2 = self._get_crossovers(normal_ey, e_max)
        return e_max, sigma_max, e_c1, e_c2

    def _get_maximum_ey(
        self, normal_ey: pd.DataFrame, tol_energy: float = 10.0
    ) -> tuple[float, float]:
        r"""Get the position and value of max emission yield.

        Parameters
        ----------
        normal_ey :
            Holds energy of |PEs| as well as emission yield at nominal incidence.
        tol_energy :
            If the :math:`E_{max}` is too close to the maximum |PE| energy, an
            warning is raised; tolerance is ``tol_energy``.

        Returns
        -------
            :math:`E_{max}` and :math:`\sigma_{max}`.
        """
        e_max, sigma_max = get_emax_eymax(normal_ey)
        if abs(e_max - self.energies[-1]) < tol_energy:
            logging.warning(
                "E_max is very close to the last measured energy. Maybe "
                "maximum emission yield was not reached?"
            )
        return e_max, sigma_max

    def _get_crossovers(
        self,
        normal_ey: pd.DataFrame,
        e_max: float,
        min_e: float = 10.0,
        tol_ey: float = 0.01,
    ) -> tuple[float, float | None]:
        """Compute first and second crossover energies.

        Parameters
        ----------
        normal_ey :
            Holds energy of |PEs| as well as emission yield at nominal incidence.
        e_max :
            Energy of maximum emission yield. Used to discriminate
            :math:`E_{c1}` from :math:`E_{c2}`.
        min_e :
            Energy under which :math:`E_{c1}` is not searched. It is useful if
            emission yield data comes from a model which sets the emission
            yield to unity at very low energies (eg some implementations of
            Vaughan).
        tol_ey :
            It the emission yield is too far from unity at crossover energy, a
            warning is raised. Tolerance is ``tol_ey``.

        Returns
        -------
        tuple[float, float | None]
            First and second crossover energies.

        """
        (ec1, ey_ec1), (ec2, ey_ec2) = get_crossover_energies(
            normal_ey, e_max, min_e
        )
        if abs(ey_ec1 - 1.0) > tol_ey:
            logging.warning(
                f"The emission yield at first crossover energy is {ey_ec1}, "
                "which is far from unity. Keeping it anyway."
            )

        if abs(ey_ec2 - 1.0) > tol_ey:
            logging.info(
                f"The emission yield at second crossover energy is {ey_ec2}, "
                "which is far from unity. Maybe its energy lies outside of the"
                " measurement range. Setting E_c2 = None."
            )
            ec2 = None

        return ec1, ec2


class EBEEY(EmissionYield):
    """|EBEEY|."""

    population = "EBE"


class IBEEY(EmissionYield):
    """|IBEEY|."""

    population = "IBE"


class TEEY(SEEY):
    """|TEEY|.

    Inherits from :class:`SEEY` to keep the same characteristic points:
    cross-over energies, maximum yield, energy at maximum yield.

    """

    population = "all"

    def decompose(
        self,
        se_shape: Callable[[NDArray[np.float64]], NDArray[np.float64]],
        ebe_shape: Callable[[NDArray[np.float64]], NDArray[np.float64]],
        ibe_shape: Callable[[NDArray[np.float64]], NDArray[np.float64]],
    ) -> tuple[SEEY, EBEEY, IBEEY]:
        r"""Split the measured |TEEY| into |SEEY|/|EBEEY|/|IBEEY| shares.

        At normal incidence, and at each impact energy :math:`E`, the measured
        total yield is split proportionally to each population's expected shape
        at that energy:

        .. math::
            \hat\delta_\mathrm{pop}(E) = \sigma_\mathrm{measured}(E) \times
            \frac{\mathrm{shape}_\mathrm{pop}(E)}
            {\mathrm{shape}_\mathrm{SE}(E) + \mathrm{shape}_\mathrm{EBE}(E) +
            \mathrm{shape}_\mathrm{IBE}(E)}

        This is a soft decomposition (fractional weights, not a hard cutoff),
        mirroring :meth:`.AllEmissionEnergyDistribution.decompose`. Only the
        normal-incidence column is considered; oblique-incidence fitting is a
        separate, later step (angular parameters are independent of the
        normal-incidence ones).

        Parameters
        ----------
        se_shape :
            Function returning the expected (unnormalized) |SEEY| at the given
            impact energies. Must already be bound to the relevant parameters
            (e.g. via :func:`functools.partial` applied to
            :func:`.furman_pivi.se.seey`).
        ebe_shape :
            Same as ``se_shape``, for |EBEEY| (e.g. bound
            :func:`.furman_pivi.ebe.ebeey`).
        ibe_shape :
            Same as ``se_shape``, for |IBEEY| (e.g. bound
            :func:`.furman_pivi.ibe.ibeey`).

        Return
        ------
            The |SEEY|, |EBEEY|, |IBEEY| shares of this |TEEY|, at normal
            incidence.

        """
        energies = np.asarray(self.energies, dtype=np.float64)

        shapes = {
            "SE": se_shape(energies),
            "EBE": ebe_shape(energies),
            "IBE": ibe_shape(energies),
        }
        total_shape = sum(shapes.values())
        has_signal = total_shape > 0
        weights = {
            pop: np.where(has_signal, shape / total_shape, 0.0)
            for pop, shape in shapes.items()
        }

        measured = self.data[col_normal].to_numpy()
        split_data = {
            pop: pd.DataFrame(
                {col_energy: energies, col_normal: measured * weight}
            )
            for pop, weight in weights.items()
        }

        return (
            SEEY(split_data["SE"]),
            EBEEY(split_data["EBE"]),
            IBEEY(split_data["IBE"]),
        )


#: Maps populations to their appropriate :class:`.EmissionYield`
#: subclass.
EMISSION_YIELDS_BY_POP: dict[ImplementedPop, type[EmissionYield]] = {
    "SE": SEEY,
    "EBE": EBEEY,
    "IBE": IBEEY,
    "all": TEEY,
}
