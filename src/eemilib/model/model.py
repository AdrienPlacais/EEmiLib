"""Define the base class for all electron emission models.

.. todo::
    Define all the properties: EBEEY, emission energy distributions, etc.

"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import Any

import numpy as np
import pandas as pd
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.model.model_config import ModelConfig
from eemilib.model.parameter import Parameter
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import ImplementedEmissionData, ImplementedPop
from eemilib.util.helper import documentation_url


class Model(ABC):
    """Define the base electron emission model.

    Parameters
    ----------
    considers_energy : bool
        Tell if the model has a dependency over PEs impact energy.
    is_3d : bool
        Tell if the model has a dependency over PEs impact angle.
    is_dielectrics_compatible : bool
        Tell if the model can take the surface-trapped charges into account.
    initial_parameters : dict[str, dict[str, str | float | bool]]
        List the :class:`.Parameter` kwargs.
    model_config : ModelConfig
        List the files that the model needs to know in order to work.

    """

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
        parameters_values : dict[str, Any] | None, optional
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
                f"     - {kwargs.get('unit', '')}",
                f"     - :math:`{kwargs.get('value', '')}`",
                f"     - {kwargs.get('description', '')}",
            ]
            doc_lines += doc
        return "\n".join(doc_lines)

    def teey(
        self, energy: np.ndarray, theta: np.ndarray, *args, **kwargs
    ) -> pd.DataFrame:
        r"""Compute TEEY :math:`\sigma`."""
        return _default_ey(energy, theta)

    def seey(
        self, energy: np.ndarray, theta: np.ndarray, *args, **kwargs
    ) -> pd.DataFrame:
        r"""Compute SEEY :math:`\delta`."""
        return _default_ey(energy, theta)

    @abstractmethod
    def find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        """Find the best parameters for the current model."""

    def plot[
        T
    ](
        self,
        plotter: Plotter,
        population: ImplementedPop | Collection[ImplementedPop],
        emission_data_type: ImplementedEmissionData,
        energies: np.ndarray,
        angles: np.ndarray,
        axes: T | None = None,
        grid: bool = True,
        **kwargs,
    ) -> T:
        """Plot desired modelled data."""
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
        if population != "all":
            raise NotImplementedError
        if emission_data_type != "Emission Yield":
            raise NotImplementedError

        emission_yield = self.teey(energies, angles)
        axes = plotter.plot_emission_yield(
            emission_yield, axes=axes, ls="--", grid=grid, **kwargs
        )
        assert axes is not None
        return axes

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


def _default_ey(energy: np.ndarray, theta: np.ndarray) -> pd.DataFrame:
    """Return a null array with proper shape."""
    n_energy = len(energy)
    n_theta = len(theta)
    out = np.zeros((n_energy, n_theta))
    out_dict = {f"{the} [deg]": out[:, j] for the, j in enumerate(theta)}
    out_dict["Energy [eV]"] = energy
    return pd.DataFrame(out_dict)
