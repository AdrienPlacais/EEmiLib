"""Define the base class for all electron emission models.

.. todo::
    Define all the properties: EBEEY, emission energy distributions, etc.

"""

import logging
import math
from abc import ABC, abstractmethod
from collections.abc import Collection
from pprint import pformat
from typing import Any

import numpy as np
import pandas as pd
from eemilib.core.model_config import ModelConfig
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.emission_data.emission_yield import EmissionYield
from eemilib.model.parameter import Parameter
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import (
    ImplementedEmissionData,
    ImplementedPop,
    col_energy,
    col_normal,
)
from eemilib.util.helper import documentation_url
from numpy.typing import NDArray


class Model(ABC):
    """Define the base electron emission model.

    Parameters
    ----------
    emission_data_types :
        Types of modelled data.
    populations :
        Modelled populations.
    considers_energy :
        Tell if the model has a dependency over PEs impact energy.
    is_3d :
        Tell if the model has a dependency over PEs impact angle.
    is_dielectrics_compatible :
        Tell if the model can take the surface-trapped charges into account.
    initial_parameters :
        List the :class:`.Parameter` kwargs.
    model_config :
        List the files that the model needs to know in order to work.

    """

    emission_data_types: list[ImplementedEmissionData]
    populations: list[ImplementedPop]
    considers_energy: bool
    is_3d: bool
    is_dielectrics_compatible: bool
    initial_parameters: dict[str, dict[str, str | float | bool]]

    model_config: ModelConfig

    def __init__(
        self, *args, parameters_values: dict[str, Any] | None = None, **kwargs
    ) -> None:
        """Instantiate the object.

        Parameters
        ----------
        parameters_values :
            Contains name of parameters and associated value. If provided, will
            override the default values set in ``initial_parameters``.

        """
        self.doc_url = documentation_url(self, **kwargs)
        self.parameters: dict[str, Parameter]

    @classmethod
    def _generate_parameter_docs(cls) -> str:
        """Generate documentation for the :class:`.Parameter`."""
        doc_lines = [
            "",
            "Model parameters",
            "================",
            "",
            ".. list-table::",
            "   :widths: 5 10 5 5 65",
            "   :header-rows: 1",
            "",
            "   * - Parameter",
            "     - Name",
            "     - Unit",
            "     - Initial",
            "     - Description",
        ]
        for name, kwargs in cls.initial_parameters.items():
            doc = [
                f"   * - :math:`{kwargs.get('markdown', '')}`",
                f"     - {name}",
                f"     - :unit:`{kwargs.get('unit', '')}`",
                f"     - :math:`{kwargs.get('value', '')}`",
                f"     - {kwargs.get('description', '')}",
            ]
            doc_lines += doc
        return "\n".join(doc_lines)

    def teey(
        self,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        *args,
        **kwargs,
    ) -> pd.DataFrame:
        r"""Compute TEEY :math:`\sigma`."""
        teey = self.get_data(
            "all",
            "Emission Yield",
            energy=energy,
            theta=theta,
            *args,
            **kwargs,
        )
        if teey is not None:
            return teey
        logging.warning("No TEEY data found, returning dummy.")
        return _dummy_df(energy, theta)

    def seey(
        self,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        *args,
        **kwargs,
    ) -> pd.DataFrame:
        r"""Compute SEEY :math:`\delta`."""
        seey = self.get_data(
            "SE", "Emission Yield", energy=energy, theta=theta, *args, **kwargs
        )
        if seey is not None:
            return seey
        logging.warning("No SEEY data found, returning dummy.")
        return _dummy_df(energy, theta)

    def se_energy_distribution(
        self,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        *args,
        **kwargs,
    ) -> pd.DataFrame:
        r"""Compute SEs emission energy distribution."""
        se_distrib = self.get_data(
            "SE",
            "Emission Energy",
            energy=energy,
            theta=theta,
            *args,
            **kwargs,
        )
        if se_distrib is not None:
            return se_distrib
        logging.warning(
            "No SE energy distribution data found, returning dummy."
        )
        return _dummy_df(energy, theta)

    def get_data(
        self,
        population: ImplementedPop,
        emission_data_type: ImplementedEmissionData,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        *args,
        **kwargs,
    ) -> pd.DataFrame | None:
        """Return desired data according to current model.

        You should override this method for each :class:`.Model` subclass.
        When desired data is not found, a ``None`` is returned. If you want a
        dummy dataframe instead, call the specific methods for every quantity:
        :meth:`.Model.teey`, :meth:`.Model.seey`,
        :meth:`.Model.se_energy_distribution`.

        """
        return None

    @abstractmethod
    def find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        """Find the best parameters for the current model."""

    def plot[T](
        self,
        plotter: Plotter,
        population: ImplementedPop | Collection[ImplementedPop],
        emission_data_type: ImplementedEmissionData,
        energies: NDArray[np.float64],
        angles: NDArray[np.float64],
        axes: T | None = None,
        grid: bool = True,
        **kwargs,
    ) -> T | None:
        """Plot desired modelled data using ``plotter``.

        This method uses :meth:`.Model.get_data` to compute the modelled data
        matching ``population`` and ``emission_data_type``. Then it calls the
        :meth:`.Model.plot` method.

        Parameters
        ----------
        plotter :
            Object realizing the plot. We transfer it to the
            :meth:`.Model.plot` method.
        population :
            One or several populations to plot. If several are given, we simply
            recursively call this method.
        emission_data_type :
            Type of data to plot.
        energies :
            Energies in :unit:`eV` for which model should be plotted.
        angles :
            Angles in :unit:`deg` for which model should be plotted.
        axes :
            Axes to re-use if given.
        grid :
            If grid should be plotted.
        kwargs :
            Other keyword arguments passed to the :meth:`.Model.plot`
            method.

        Returns
        -------
            Created axes object, or ``None`` if no plot was created.

        """
        if isinstance(population, Collection) and not isinstance(
            population, str
        ):
            for pop in population:
                axes = self.plot(
                    plotter,
                    pop,
                    emission_data_type,
                    energies,
                    angles,
                    axes=axes,
                    grid=grid,
                    **kwargs,
                )
            return axes

        to_plot = self.get_data(
            population=population,
            emission_data_type=emission_data_type,
            energy=energies,
            theta=angles,
        )
        if to_plot is None:
            logging.info(
                f"No modelled data found for {population = } and "
                f"{emission_data_type = }. Skipping this plot."
            )
            return axes

        if emission_data_type == "Emission Yield":
            return plotter.plot_emission_yield(
                to_plot,
                axes=axes,
                ls="--",
                grid=grid,
                population=population,
                **kwargs,
            )
        if emission_data_type == "Emission Energy":
            return plotter.plot_emission_energy_distribution(
                to_plot,
                axes=axes,
                ls="--",
                grid=grid,
                population=population,
                **kwargs,
            )
        raise NotImplementedError

    def set_parameter_value(self, name: str, value: Any) -> None:
        """Give the parameter named ``name`` the value ``value``."""
        if name not in self.parameters:
            logging.warning(
                f"{name = } is not defined for {self}. Skipping... "
            )
            return
        self.parameters[name].value = value

    def set_parameters_values(self, values: dict[str, Any]) -> None:
        """Set multiple parameter values."""
        for name, value in values.items():
            self.set_parameter_value(name, value)

    def evaluate(
        self, data_matrix: DataMatrix, *args, **kwargs
    ) -> dict[str, float]:
        """Evaluate the precision of the model w.r.t. given data."""
        raise NotImplementedError

    def _evaluate_for_teey_models(
        self, data_matrix: DataMatrix
    ) -> dict[str, float]:
        """Evaluate a TEEY model with N. Fil criterions.

        Ref: :cite:`Fil2016a,Fil2020`

        """
        emission_yield = data_matrix.teey
        errors = {
            r"Relative error over $E_{c1}$ [%]": self._error_ec1(
                emission_yield
            ),
            r"$\sigma$ deviation between $E_{c1}$ and $E_{max}$ [%]": self._error_teey(
                emission_yield
            ),
        }
        return errors

    def _error_ec1(self, emission_yield: EmissionYield) -> float:
        """Compute relative error over first crossover energy in :unit:`%`."""
        measured_ec1 = emission_yield.e_c1
        energy = np.linspace(0, 1.5 * measured_ec1, 10001, dtype=np.float64)
        theta = np.array([0.0])
        teey = self.teey(energy, theta)

        idx_ec1 = (teey[col_normal] - 1.0).abs().idxmin()
        model_ec1 = energy[idx_ec1]

        std = math.sqrt((measured_ec1 - model_ec1) ** 2)
        error = 100.0 * std / measured_ec1
        return float(error)

    def _error_teey(self, emission_yield: EmissionYield) -> float:
        """Compute TEEY relative error between E_c1 and E_max in :unit:`%`."""
        min_energy = emission_yield.e_c1
        max_energy = emission_yield.e_max
        df = emission_yield.data
        mask = (df[col_energy] >= min_energy) & (df[col_energy] <= max_energy)

        measured_teey = df.loc[mask, col_normal].to_numpy()
        measured_energy = df.loc[mask, col_energy].to_numpy()
        angles = np.array([0.0])
        modelled_teey = self.teey(measured_energy, angles)[
            col_normal
        ].to_numpy()

        error = 100.0 * np.std(measured_teey - modelled_teey, ddof=1.0)
        return float(error)

    def display_parameters(self) -> None:
        """Display the parameters and their values in a nice looking way."""
        if not hasattr(self, "parameters"):
            logging.info("`parameters` attribute was not set.")

        msg = {
            f"{key:>20}": str(param) for key, param in self.parameters.items()
        }
        logging.info("Parameters values:\n" + pformat(msg))


def _dummy_df(
    energy: NDArray[np.float64], theta: NDArray[np.float64]
) -> pd.DataFrame:
    """Return a null array with proper shape."""
    n_energy = len(energy)
    n_theta = len(theta)
    out = np.zeros((n_energy, n_theta))
    out_dict = {f"{the} [deg]": out[:, j] for the, j in enumerate(theta)}
    out_dict["Energy [eV]"] = energy
    return pd.DataFrame(out_dict)
