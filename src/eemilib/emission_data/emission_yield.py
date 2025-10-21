"""Define an object to store an emission yield."""

import logging
from pathlib import Path
from typing import Self

import pandas as pd
from eemilib.emission_data.emission_data import EmissionData
from eemilib.emission_data.helper import (
    get_crossover_energies,
    get_emax_eymax,
    resample,
)
from eemilib.loader.loader import Loader
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import (
    ImplementedPop,
    col_energy,
    col_normal,
    md_ey,
)


class EmissionYield(EmissionData):
    """An emission yield."""

    def __init__(self, population: ImplementedPop, data: pd.DataFrame) -> None:
        """Instantiate the data.

        Parameters
        ----------
        population :
            The concerned population of electrons.
        data :
            Structure holding the data. Must have an ``Energy (eV)`` column
            holding PEs energy. And one or several columns ``theta [deg]``,
            where ``theta`` is the value of the incidence angle and content is
            corresponding emission yield.

        """
        super().__init__(population, data)
        self.energies = data[col_energy].to_numpy()
        self.angles = [
            float(col.split()[0]) for col in data.columns if col != col_energy
        ]
        #: Energy at the maximum emission yield in :unit:`eV`. Not defined for
        #: BEs.
        self.e_max: float
        #: Maximum emission yield. Not defined for BEs.
        self.ey_max: float
        #: First cross-over enrergy in :unit:`eV`. Not defined for BEs.
        self.e_c1: float
        #: Second cross-over enrergy in :unit:`eV`. Not defined for BEs.
        self.e_c2: float | None
        if self.population in ("SE", "all"):
            self.e_max, self.ey_max, self.e_c1, self.e_c2 = self._parameters(
                n_resample=1000
            )

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
        data = loader.load_emission_yield(*filepath)
        return cls(population, data)

    @property
    def label(self) -> str:
        """Print nature of data (markdown)."""
        return md_ey[self.population]

    def _parameters(
        self,
        n_resample: int = -1,
    ) -> tuple[float, float, float, float | None]:
        """Compute the characteristics of the emission yield."""
        assert 0.0 in self.angles, "Need the normal incidence measurements."

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
            Holds energy of PEs as well as emission yield at nominal incidence.
        tol_energy :
            If the :math:`E_{max}` is too close to the maximum PE energy, an
            warning is raised; tolerance is ``tol_energy``. The default value
            is 10 eV.

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
            Holds energy of PEs as well as emission yield at nominal incidence.
        e_max :
            Energy of maximum emission yield. Used to discriminate
            :math:`E_{c1}` from :math:`E_{c2}`.
        min_e :
            Energy under which :math:`E_{c1}` is not searched. It is useful if
            emission yield data comes from a model which sets the emission
            yield to unity at very low energies (eg some implementations of
            Vaughan). The default value is 10 eV.
        tol_ey :
            It the emission yield is too far from unity at crossover energy, a
            warning is raised. Tolerance is ``tol_ey``. The default value is
            ``0.01``.

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

        This wrapper simply calls the :meth:`.Plotter.plot_emission_yield`
        method.

        """
        return plotter.plot_emission_yield(
            df=self.data,
            *args,
            axes=axes,
            lw=lw,
            marker=marker,
            grid=grid,
            label=self.label,
            population=population,
            **kwargs,
        )
