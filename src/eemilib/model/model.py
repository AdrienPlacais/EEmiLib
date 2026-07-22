"""Define the base class for all electron emission models.

.. todo::
    Define all the properties: |EBEEY|, emission energy distributions, etc.

"""

import logging
import math
from abc import ABC, abstractmethod
from collections.abc import Collection
from pprint import pformat
from typing import Any, ClassVar, Literal, cast, overload

import numpy as np
import pandas as pd
from eemilib.core.model_config import ModelConfig
from eemilib.emission_data.data_matrix import DataMatrix, MissingDataError
from eemilib.emission_data.emission_yield import TEEY
from eemilib.emission_data.helper import get_ec1, get_max
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import (
    ImplementedEmissionData,
    ImplementedPop,
    col_energy,
    col_normal,
)
from eemilib.util.helper import documentation_url
from eemilib.util.markdown import E_MAX, EC_1, SIGMA, SIGMA_MAX, tex_math
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
        Tell if the model has a dependency over |PEs| impact energy.
    is_3d :
        Tell if the model has a dependency over |PEs| impact angle.
    is_dielectrics_compatible :
        Tell if the model can take the surface-trapped charges into account.
    initial_parameters :
        List the :class:`.Parameter` kwargs.
    model_config :
        List the files that the model needs to know in order to work.
    implementation_choices :
        Maps each independent implementation axis to its allowed options. Empty
        by default -- models with a single fixed implementation don't need to
        define this.

    """

    emission_data_types: list[ImplementedEmissionData]
    populations: list[ImplementedPop]
    considers_energy: bool
    is_3d: bool
    is_dielectrics_compatible: bool
    initial_parameters: dict[str, dict[str, str | float | bool]]
    model_config: ModelConfig
    implementation_choices: ClassVar[dict[str, tuple[str, ...]]] = {}

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
        #: A :class:`.TypedDict` specific to every :class:`.model.Model`. Keys
        #: are parameters names, values are :class:`.Parameter`.
        self.parameters: Any
        #: Maps each axis name (see :attr:`.Model.implementation_choices`) to the
        #: currently selected option.
        self.current_implementations: dict[str, str] = {}

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
        r"""Compute |TEEY| :math:`\sigma`.

        Under the hood, it calls :meth:`get_data`.

        """
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
        r"""Compute |SEEY| :math:`\delta`.

        Under the hood, it calls :meth:`get_data`.

        """
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
        r"""Compute |SEs| emission energy distribution.

        Under the hood, it calls :meth:`get_data`.

        """
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
        e_pe: float | None = None,
        *args,
        **kwargs,
    ) -> pd.DataFrame | None:
        r"""Return desired data according to current model.

        You should override this method for each :class:`.Model` subclass.
        When desired data is not found, a ``None`` is returned. If you want a
        dummy dataframe instead, call the specific methods for every
        quantity: :meth:`.Model.teey`, :meth:`.Model.seey`,
        :meth:`.Model.se_energy_distribution`.

        Parameters
        ----------
        population :
            Type of population you want data from.
        emission_data_type :
            Desired type of emission data.
        energy :
            According to the emission data type, this argument can mean
            several things:

            - ``"Emission Yield"``: array of |PEs| impact energy in
              :unit:`eV`.
            - ``"Emission Energy"``: array of |EEs| emission energy in
              :unit:`eV`. By convention, if ``e_pe`` is not provided, the
              impact energy of the |PE| is also the last value of ``energy``.

        theta :
            Array of |PE| electrons impact angle in :unit:`\degrees`.
        e_pe :
            Energy of |PEs| in :unit:`eV`, if applicable.
        args :
            Other arguments passed to model functions.
        kwargs :
            Other arguments passed to model functions.

        Returns
        -------
            ``None`` if data is not modelled. Otherwise, a dataframe where
            the first column is called ``"Energy [eV]"`` and holds energy.
            Data is stored in the following columns, called ``"0.0 [deg]"``,
            ``"20.0 [deg]"`` (according to the values of ``theta``). The
            only column guaranteed to be present is the normal incidence
            one.

        """
        return None

    @abstractmethod
    def find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        """Find the best parameters for the current model."""

    @overload
    def plot[T](
        self,
        plotter: Plotter,
        population: ImplementedPop | Collection[ImplementedPop],
        emission_data_type: ImplementedEmissionData,
        energies: NDArray[np.float64],
        angles: NDArray[np.float64],
        axes: T | None = None,
        group_by_pe: Literal[False] = False,
        e_pes: float | None = None,
        **kwargs,
    ) -> T | None: ...

    @overload
    def plot[T](
        self,
        plotter: Plotter,
        population: ImplementedPop | Collection[ImplementedPop],
        emission_data_type: Literal["Emission Energy"],
        energies: NDArray[np.float64],
        angles: NDArray[np.float64],
        axes: dict[float, T] | None = None,
        group_by_pe: Literal[True] = True,
        e_pes: Collection[float] | None = None,
        **kwargs,
    ) -> dict[float, T]: ...

    def plot[T](
        self,
        plotter: Plotter,
        population: ImplementedPop | Collection[ImplementedPop],
        emission_data_type: ImplementedEmissionData,
        energies: NDArray[np.float64],
        angles: NDArray[np.float64],
        axes: T | dict[float, T] | None = None,
        group_by_pe: bool = False,
        e_pes: float | Collection[float] | None = None,
        grid: bool = True,
        **kwargs,
    ) -> T | dict[float, T] | None:
        """Plot model predictions using ``plotter``.

        This method is an orchestrator: it decides which underlying routine
        handles the request, and delegates the actual plotting to
        :meth:`_plot_single` (single-axes case) or :meth:`_plot_grouped_by_pe`
        (``group_by_pe=True`` case).

        Parameters
        ----------
        plotter :
            Object realizing the plot.
        population :
            One or several populations to plot.
        emission_data_type :
            Type of data to plot.
        energies :
            Energies at which the model is evaluated.
        angles :
            Angles at which the model is evaluated.
        axes :
            Axes to re-use if given. A plain ``T`` in the default case; a
            ``dict[float, T]`` keyed by impact energy when ``group_by_pe=True``.
        group_by_pe :
            Only supported for ``emission_data_type == "Emission Energy"``. If
            ``True``, one axes is created (or re-used) per impact energy,
            instead of a single shared axes.
        e_pes :
            |PE| energy/energies. In the single-axes case
            (``group_by_pe=False``), a single ``float`` (or ``None``). In the
            grouped case (``group_by_pe=True``), one or several impact
            energies to plot at, only used when ``axes`` is not given (nothing
            to infer impact energies from otherwise). If ``axes`` is given,
            its keys are used instead and ``e_pes`` is ignored.
        kwargs :
            Other keyword arguments passed to the underlying plotting routine.

        Returns
        -------
            Created axes object (or ``dict`` of axes if ``group_by_pe=True``),
            can be empty if no plot was created.

        """
        if not group_by_pe:
            if isinstance(axes, dict):
                logging.error(
                    "Given axes is a dictionary, but should be a singles Axes "
                    "instance or `None`. A dictionary is expected only when "
                    "`group_by_pe=True`. Setting `axes=None` and trying to "
                    f"continue... Given axes was:\n{pformat(axes)}"
                )
                axes = None
            e_pe = cast(float | None, e_pes)
            return self._plot_single(
                plotter,
                population,
                emission_data_type,
                energies,
                angles,
                axes=cast(T | None, axes),
                e_pe=e_pe,
                grid=grid,
                **kwargs,
            )

        if emission_data_type != "Emission Energy":
            raise ValueError(
                "`group_by_pe=True` is only supported for `emission_data_type="
                "'Emission Energy'`."
            )

        e_pes_collection: Collection[float] | None
        if e_pes is None:
            e_pes_collection = None
        elif isinstance(e_pes, (int, float)):
            e_pes_collection = (float(e_pes),)
        else:
            e_pes_collection = e_pes

        return self._plot_grouped_by_pe(
            plotter,
            population,
            energies,
            angles,
            axes=cast(dict[float, T] | None, axes),
            e_pes=e_pes_collection,
            grid=grid,
            **kwargs,
        )

    def _plot_single[T](
        self,
        plotter: Plotter,
        population: ImplementedPop | Collection[ImplementedPop],
        emission_data_type: ImplementedEmissionData,
        energies: NDArray[np.float64],
        angles: NDArray[np.float64],
        axes: T | None = None,
        e_pe: float | None = None,
        grid: bool = True,
        **kwargs,
    ) -> T | None:
        """Plot model predictions on a single shared axes.

        Parameters
        ----------
        plotter :
            Object realizing the plot.
        population :
            One or several populations to plot.
        emission_data_type :
            Type of data to plot.
        energies :
            Energies at which the model is evaluated.
        angles :
            Angles at which the model is evaluated.
        axes :
            Axes to re-use if given.
        e_pe :
            Impact energy, only used when ``emission_data_type == "Emission
            Energy"``.
        grid :
            Whether grid should appear.
        kwargs :
            Other keyword arguments passed to the underlying plotting routine.

        Return
        ------
            Created axes object, can be ``None`` if no plot was created.

        """
        if isinstance(population, Collection) and not isinstance(
            population, str
        ):
            for pop in population:
                axes = self._plot_single(
                    plotter,
                    pop,
                    emission_data_type,
                    energies,
                    angles,
                    axes=axes,
                    e_pe=e_pe,
                    grid=grid,
                    **kwargs,
                )
            return axes

        data = self.get_data(
            population=population,
            emission_data_type=emission_data_type,
            energy=energies,
            theta=angles,
            e_pe=e_pe,
        )
        if data is None:
            logging.info(
                f"No model data for {population = } and "
                f"{emission_data_type = }. Skipping this plot."
            )
            return axes

        return plotter.plot(
            emission_data_type=emission_data_type,
            df=data,
            axes=axes,
            population=population,
            e_pe=e_pe,
            grid=grid,
            is_model=True,
            **kwargs,
        )

    def _plot_grouped_by_pe[T](
        self,
        plotter: Plotter,
        population: ImplementedPop | Collection[ImplementedPop],
        energies: NDArray[np.float64],
        angles: NDArray[np.float64],
        axes: dict[float, T] | None = None,
        e_pes: Collection[float] | None = None,
        grid: bool = True,
        **kwargs,
    ) -> dict[float, T]:
        """
        Plot ``"Emission Energy"`` model predictions, one axes per |PE| energy.

        If ``axes`` is given, its keys determine which impact energies to plot
        at (and their axes are re-used). Otherwise, ``e_pes`` must be given.

        Parameters
        ----------
        plotter :
            Object realizing the plot.
        population :
            One or several populations to plot.
        energies :
            Energies at which the model is evaluated.
        angles :
            Angles at which the model is evaluated.
        axes :
            Existing ``e_pe``-keyed axes to re-use, if any. If ``e_pes`` is
            given, these energies will be used rather than ``axes`` keys.
        e_pes :
            Impact energies to plot at. Required if ``axes`` is not given.
        grid :
            Whether grid should be plotted.
        kwargs :
            Other keyword arguments passed to the underlying plotting routine.

        Return
        ------
            Axes, keyed by impact energy.

        """
        axes = axes or {}
        e_pes = e_pes or list(axes.keys())

        if not e_pes:
            raise ValueError(
                "You must provide either `axes` (to plot at its existing "
                "impact energies) or `e_pes` (to plot at new impact energies)."
            )

        for e_pe in e_pes:
            axes[e_pe] = self._plot_single(
                plotter,
                population=population,
                emission_data_type="Emission Energy",
                energies=energies,
                angles=angles,
                axes=axes.get(e_pe),
                e_pe=e_pe,
                grid=grid,
                **kwargs,
            )
        return axes

    def set_parameter_value(self, name: str, value: Any) -> None:
        """Give the parameter named ``name`` the value ``value``."""
        if name not in self.parameters:
            logging.warning(
                f"{name = } is not defined for {self}. Skipping... "
            )
            return
        self.parameters[name].value = value

    def reset_parameter_value(self, name: str) -> None:
        """Reset a parameter value to its default.

        Default is defined in ``initial_parameters``.

        """
        if name not in self.parameters:
            logging.warning(
                f"{name = } is not defined for {self}. Skipping... "
            )
            return
        if name not in self.initial_parameters:
            logging.warning(
                f"{name = } has not initial value for {self}. Skipping... "
            )
            return
        value = float(self.initial_parameters[name]["value"])
        self.parameters[name].value = value

    def set_parameters_values(self, values: dict[str, Any]) -> None:
        """Set multiple parameter values."""
        for name, value in values.items():
            self.set_parameter_value(name, value)

    def reset_parameters_values(self, *names: str) -> None:
        """Reset multiple parameter values."""
        for name in names:
            self.reset_parameter_value(name)

    def set_implementation(self, name: str, value: str) -> None:
        """Update one implementation axis.

        Subclasses defining :attr:`implementation_choices` must override
        this to apply the effect of switching ``name`` to ``value``.

        """
        raise NotImplementedError

    def evaluate(
        self,
        data_matrix: DataMatrix,
        *args,
        evaluations: dict[str, float] | None = None,
        **kwargs,
    ) -> dict[str, float]:
        """Evaluate the precision of the model w.r.t. given data.

        For now, the only evaluations are |TEEY| or |SEEY| criterions proposed
        by Fil et al. :cite:`Fil2016a,Fil2020`.

        Parameters
        ----------
        data_matrix :
            Holds all measured electron emission data.
        evaluations :
            Maps names of quality criterions with their actual value. If given,
            it will be preserved and additional evaluations may be added.

        Returns
        -------
        dict[str, float]
            Maps names of quality criterions with their actual value.

        """
        if evaluations is None:
            evaluations = {}
        if "Emission Yield" in self.emission_data_types and (
            "all" in self.populations or "SE" in self.populations
        ):
            evaluations.update(self._evaluate_for_teey_models(data_matrix))

        if len(evaluations) == 0:
            logging.info(
                f"No evaluation was defined for {self.__class__.__name__}"
            )
        return evaluations

    def _evaluate_for_teey_models(
        self, data_matrix: DataMatrix
    ) -> dict[str, float]:
        """Evaluate a |TEEY| model with N. Fil criterions.

        Ref: :cite:`Fil2016a,Fil2020`.

        """
        evaluations = self._main_teey_parameters()

        try:
            teey = data_matrix.teey
        except MissingDataError:
            logging.error("TEEY is mandatory in order to perform evaluations.")
            return evaluations

        evaluations.update(
            {
                rf"Relative error over {tex_math(EC_1)} [\%]": self._error_ec1(
                    teey
                ),
                f"{tex_math(SIGMA)} deviation between {tex_math(EC_1)} and "
                rf"{tex_math(E_MAX)} [\%]": self._error_teey(teey),
            }
        )
        return evaluations

    def _main_teey_parameters(self) -> dict[str, float]:
        r"""Compute main TEEY parameters.

        In particular: $E_{c1}$, $E_{max}$, $\sigma_{max}$.

        """
        energy = np.linspace(0, 1e3, 10001, dtype=np.float64)
        theta = np.array([0.0])
        teey = self.teey(energy, theta)

        e_c1 = get_ec1(teey)
        e_max, sigma_max = get_max(teey)
        return {
            f"Modelled {tex_math(EC_1)} [eV]": e_c1,
            f"Modelled {tex_math(E_MAX)} [eV]": e_max,
            f"Modelled {tex_math(SIGMA_MAX)}": sigma_max,
        }

    def _error_ec1(self, emission_yield: TEEY) -> float:
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

    def _error_teey(self, emission_yield: TEEY) -> float:
        """Compute |TEEY| relative error between $E_{c1}$ and $E_{max}$.

        Returned value is in :unit:`%`.

        """
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

        error = 100.0 * np.std((measured_teey - modelled_teey), ddof=1.0)
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
    out_dict = {
        col_energy: energy,
        **{f"{the} [deg]": out[:, j] for j, the in enumerate(theta)},
    }
    return pd.DataFrame(out_dict)
