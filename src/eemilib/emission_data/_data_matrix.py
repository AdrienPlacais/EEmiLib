"""Store the filepaths entered by user.

.. todo::
    Methods to reset filepaths/data

"""

import logging
from collections.abc import Collection, Sequence
from typing import Literal, cast, overload

import numpy as np

from eemilib.core.model_config import ModelConfig
from eemilib.emission_data.emission_angle_distribution import (
    EmissionAngleDistribution,
)
from eemilib.emission_data.emission_data import EmissionData, MissingDataError
from eemilib.emission_data.emission_energy_distribution import (
    EMISSION_ENERGIES_BY_POP,
    AllEmissionEnergyDistribution,
    EBEEmissionEnergyDistribution,
    IBEEmissionEnergyDistribution,
    SEEmissionEnergyDistribution,
)
from eemilib.emission_data.emission_yield import (
    EBEEY,
    EMISSION_YIELDS_BY_POP,
    IBEEY,
    SEEY,
    TEEY,
    EmissionYield,
)
from eemilib.loader.helper import DataPath
from eemilib.loader.loader import Loader
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import (
    IMPLEMENTED_EMISSION_DATA,
    IMPLEMENTED_POP,
    ImplementedEmissionData,
    ImplementedPop,
)

pop_to_row = {pop: i for i, pop in enumerate(IMPLEMENTED_POP)}
row_to_pop = {val: key for key, val in pop_to_row.items()}

data_type_to_col = {
    data_type: j for j, data_type in enumerate(IMPLEMENTED_EMISSION_DATA)
}
col_to_data_type = {val: key for key, val in data_type_to_col.items()}

n_rows = len(IMPLEMENTED_POP)
n_cols = len(IMPLEMENTED_EMISSION_DATA)


class DataMatrix:
    """Store all the input files and corresp data in a single object."""

    def __init__(self) -> None:
        """Instantiate the object."""
        self.files_matrix: list[list[list[DataPath]]]
        self.files_matrix = [
            [[] for _ in range(n_cols)] for _ in range(n_rows)
        ]

        self.data_matrix: list[list[list[EmissionData]]]
        self.data_matrix = [[[] for _ in range(n_cols)] for _ in range(n_rows)]

    def _natures_to_indexes(
        self, data_type: ImplementedEmissionData, population: ImplementedPop
    ) -> tuple[int, int]:
        """Give the desired indexes."""
        return (pop_to_row[population], data_type_to_col[data_type])

    def _indexes_to_natures(
        self, row: int, col: int
    ) -> tuple[ImplementedPop, ImplementedEmissionData]:
        """Give the desired natures."""
        population_type = row_to_pop[row]
        assert population_type in IMPLEMENTED_POP
        data_type = col_to_data_type[col]
        assert data_type in IMPLEMENTED_EMISSION_DATA
        return population_type, data_type

    def set_files(
        self,
        files: DataPath | Collection[DataPath],
        data_type: ImplementedEmissionData,
        population: ImplementedPop,
    ) -> None:
        """Set the file(s) by index or name."""
        row, col = self._natures_to_indexes(data_type, population)
        if isinstance(files, DataPath):
            self.files_matrix[row][col] = [files]
        else:
            self.files_matrix[row][col] = list(files)

    @overload
    def set_data(
        self,
        emission_data: EmissionYield | Collection[EmissionYield],
        data_type: Literal["Emission Yield"],
        population: ImplementedPop,
    ) -> None: ...

    @overload
    def set_data(
        self,
        emission_data: (
            SEEmissionEnergyDistribution
            | Collection[SEEmissionEnergyDistribution]
        ),
        data_type: Literal["Emission Energy"],
        population: Literal["SE"],
    ) -> None: ...

    @overload
    def set_data(
        self,
        emission_data: (
            EBEEmissionEnergyDistribution
            | Collection[EBEEmissionEnergyDistribution]
        ),
        data_type: Literal["Emission Energy"],
        population: Literal["EBE"],
    ) -> None: ...

    @overload
    def set_data(
        self,
        emission_data: (
            IBEEmissionEnergyDistribution
            | Collection[IBEEmissionEnergyDistribution]
        ),
        data_type: Literal["Emission Energy"],
        population: Literal["all"],
    ) -> None: ...
    @overload
    def set_data(
        self,
        emission_data: (
            AllEmissionEnergyDistribution
            | Collection[AllEmissionEnergyDistribution]
        ),
        data_type: Literal["Emission Energy"],
        population: Literal["all"],
    ) -> None: ...

    @overload
    def set_data(
        self,
        emission_data: (
            EmissionAngleDistribution | Collection[EmissionAngleDistribution]
        ),
        data_type: Literal["Emission Angle"],
        population: ImplementedPop,
    ) -> None: ...

    def set_data(
        self,
        emission_data: EmissionData | Collection[EmissionData],
        data_type: ImplementedEmissionData,
        population: ImplementedPop,
    ) -> None:
        """Set the data by index or name.

        .. todo::
           ``population`` is already known if emission_data is given.
           ``data_type`` could be known if emission_data is given.

        """
        row, col = self._natures_to_indexes(data_type, population)
        if isinstance(emission_data, EmissionData):
            emission_data = [emission_data]
        self.data_matrix[row][col] = list(emission_data)

    def get_files(
        self, data_type: ImplementedEmissionData, population: ImplementedPop
    ) -> list[DataPath]:
        """Get the file(s) by index or name."""
        row, col = self._natures_to_indexes(data_type, population)
        return self.files_matrix[row][col]

    @overload
    def get_data(
        self, data_type: Literal["Emission Yield"], population: Literal["SE"]
    ) -> Sequence[SEEY]: ...

    @overload
    def get_data(
        self, data_type: Literal["Emission Yield"], population: Literal["EBE"]
    ) -> Sequence[EBEEY]: ...

    @overload
    def get_data(
        self, data_type: Literal["Emission Yield"], population: Literal["IBE"]
    ) -> Sequence[IBEEY]: ...

    @overload
    def get_data(
        self, data_type: Literal["Emission Yield"], population: Literal["all"]
    ) -> Sequence[TEEY]: ...

    @overload
    def get_data(
        self, data_type: Literal["Emission Energy"], population: Literal["SE"]
    ) -> Sequence[SEEmissionEnergyDistribution]: ...

    @overload
    def get_data(
        self, data_type: Literal["Emission Energy"], population: Literal["EBE"]
    ) -> Sequence[EBEEmissionEnergyDistribution]: ...

    @overload
    def get_data(
        self, data_type: Literal["Emission Energy"], population: Literal["IBE"]
    ) -> Sequence[IBEEmissionEnergyDistribution]: ...

    @overload
    def get_data(
        self, data_type: Literal["Emission Energy"], population: Literal["all"]
    ) -> Sequence[AllEmissionEnergyDistribution]: ...

    @overload
    def get_data(
        self, data_type: Literal["Emission Angle"], population: ImplementedPop
    ) -> Sequence[EmissionAngleDistribution]: ...

    def get_data(
        self, data_type: ImplementedEmissionData, population: ImplementedPop
    ) -> Sequence[EmissionData]:
        """Get the file(s) by name.

        Parameters
        ----------
        data_type :
            Emission data type.
        population :
            Population type.

        Returns
        -------
            Desired data; if the specified data does not exists, an empty list
            is returned without any error message.

        """
        row, col = self._natures_to_indexes(data_type, population)
        data = self.data_matrix[row][col]
        if data is None:
            return []
        if isinstance(data, EmissionData):
            return [data]
        return data

    def load_data(
        self,
        loader: Loader,
        e_pes_emission_energies: (
            dict[ImplementedPop, Sequence[float]] | None
        ) = None,
        rescale_energy_distributions_to_yield: bool = True,
    ) -> None:
        """Load all filepaths in ``files_matrix``.

        Parameters
        ----------
        loader :
            Actual instance that will load data.
        e_pes_emission_energies :
            Maps emitted electrons populations to their files' |PEs| energies
            in :unit:`eV`. Every value must have the same length as it's
            corresponding file paths. Use it only if the original files do not
            contain this info and/or the :class:`.Loader` cannot infer it.
        rescale_energy_distributions_to_yield :
            Rescale ``"all"`` emission distributions so that their integrals
            match the |TEEY|. Only if emission yield and emission distributions
            for ``"all"`` population are provided.

        """
        for population in IMPLEMENTED_POP:
            for data_type in IMPLEMENTED_EMISSION_DATA:
                filepaths = self.get_files(data_type, population)

                if not filepaths:
                    continue

                emission_data = None
                if data_type == "Emission Yield":
                    emission_data = list(
                        EMISSION_YIELDS_BY_POP[population].from_filepaths(
                            loader, *filepaths, population=population
                        )
                    )

                elif data_type == "Emission Energy":
                    emission_data = list(
                        EMISSION_ENERGIES_BY_POP[population].from_filepaths(
                            loader,
                            *filepaths,
                            population=population,
                            e_pes=(
                                e_pes_emission_energies[population]
                                if e_pes_emission_energies
                                else None
                            ),
                        )
                    )

                elif data_type == "Emission Angle":
                    emission_data = EmissionAngleDistribution.from_filepath(
                        loader, *filepaths, population=population
                    )

                if emission_data:
                    self.set_data(
                        emission_data,
                        data_type=data_type,
                        population=population,
                    )  # type: ignore
        if not rescale_energy_distributions_to_yield:
            return
        teeys = self.get_data("Emission Yield", "all")
        if not teeys:
            return
        distribs = self.get_data("Emission Energy", "all")
        if not distribs:
            return
        logging.info(
            "TEEY and emission energy distribution are provided. Rescaling "
            "distributions so that their integrals match the TEEY. You can "
            "desactivate this with `rescale_energy_distributions_to_yield = "
            "False` in `DataMatrix.load_data`"
        )
        self.rescale_energy_distributions_to_teey()

    def has_all_mandatory_files(self, model_config: ModelConfig) -> bool:
        """Tell if files defined by :attr:`.Model.model_config` are set."""
        for data_type, corresponding_attribute in zip(
            IMPLEMENTED_EMISSION_DATA,
            (
                "emission_yield_files",
                "emission_energy_files",
                "emission_angle_files",
            ),
        ):
            mandatory_populations = getattr(
                model_config, corresponding_attribute
            )

            for mandatory_population in mandatory_populations:
                if mandatory_population not in IMPLEMENTED_POP:
                    logging.error(
                        f"{mandatory_population = } not in {IMPLEMENTED_POP = }"
                    )
                    return False

                filepath = self.get_files(data_type, mandatory_population)
                if filepath is None:
                    logging.error(
                        f"You must define a {data_type} filepath for"
                        f" population {mandatory_population}"
                    )
                    return False

                data_objects = self.get_data(data_type, mandatory_population)
                if not data_objects:
                    logging.error(
                        f"You must load {data_type} filepath for "
                        f"population {mandatory_population}"
                    )
                    return False
        return True

    @overload
    def plot[T](
        self,
        plotter: Plotter,
        population: ImplementedPop | Collection[ImplementedPop],
        data_type: ImplementedEmissionData,
        axes: T | None = None,
        group_by_pe: Literal[False] = False,
        **kwargs,
    ) -> T | None: ...

    @overload
    def plot[T](
        self,
        plotter: Plotter,
        population: ImplementedPop | Collection[ImplementedPop],
        data_type: Literal["Emission Energy"],
        axes: dict[float, T] | None = None,
        group_by_pe: Literal[True] = True,
        **kwargs,
    ) -> dict[float, T]: ...

    def plot[T](
        self,
        plotter: Plotter,
        population: ImplementedPop | Collection[ImplementedPop],
        data_type: ImplementedEmissionData,
        axes: T | dict[float, T] | None = None,
        group_by_pe: bool = False,
        **kwargs,
    ) -> T | dict[float, T] | None:
        """Plot desired measured data using ``plotter``.

        This method is an orchestrator: it decides which underlying routine
        handles the request, and delegates the actual plotting to
        :meth:`.EmissionData.plot` (single-axes case) or
        :meth:`_plot_grouped_by_pe` (``group_by_pe=True`` case).

        Parameters
        ----------
        plotter :
            Object realizing the plot. We transfer it to the
            :meth:`.EmissionData.plot` method.
        population :
            One or several populations to plot. If several are given, we simply
            recursively call this method. They will share the same axes.
        data_type :
            Type of data to plot.
        axes :
            Axes to re-use if given. A plain ``T`` in the default case; a
            ``dict[float, T]`` keyed by impact energy when
            ``group_by_pe=True``.
        group_by_pe :
            Only supported for ``data_type == "Emission Energy"``. If
            ``True``, one axes is created (or re-used) per distinct impact
            energy found in the measurements, instead of sharing a single axes
            for everything.
        kwargs :
            Other keyword arguments passed to the :meth:`.EmissionData.plot`
            method.

        Returns
        -------
            Created axes object (or ``dict`` of axes if ``group_by_pe=True``),
            can be empty if no plot was created.

        """
        if group_by_pe:
            if data_type != "Emission Energy":
                raise ValueError(
                    "`group_by_pe=True` is only supported for "
                    "`data_type='Emission Energy'`."
                )
            return self._plot_grouped_by_pe(
                plotter,
                population,
                axes=cast(dict[float, T] | None, axes),
                **kwargs,
            )

        if isinstance(population, Collection) and not isinstance(
            population, str
        ):
            for pop in population:
                axes = self.plot(plotter, pop, data_type, axes=axes, **kwargs)
            return axes

        emission_data = self.get_data(data_type, population)

        if not emission_data:
            logging.info(
                f"No measurement found for {population = } and "
                f"{data_type = }. Skipping this plot."
            )
            return axes

        if not hasattr(emission_data, "__iter__"):
            raise ValueError(
                "now, emission data should be a possibly empty list"
            )
        for data in emission_data:
            axes = data.plot(
                plotter, axes=axes, population=population, **kwargs
            )
        return axes

    def _plot_grouped_by_pe[T](
        self,
        plotter: Plotter,
        population: ImplementedPop | Collection[ImplementedPop],
        axes: dict[float, T] | None = None,
        **kwargs,
    ) -> dict[float, T]:
        """Plot ``"Emission Energy"`` data, one axes per impact energy.

        Distributions are grouped by their
        :attr:`.EmissionEnergyDistribution.e_pe`; one axes is created (or
        re-used from ``axes``) per distinct value found. If several populations
        are given and share the same ``e_pe``, they are plotted on the same
        axes together.

        Parameters
        ----------
        plotter :
            Object realizing the plot.
        population :
            One or several populations to plot.
        axes :
            Existing ``e_pe``-keyed axes to re-use, if any.
        kwargs :
            Other keyword arguments passed to :meth:`.EmissionData.plot`.

        Return
        ------
            Axes, keyed by impact energy.

        """
        if axes is None:
            axes = {}

        if isinstance(population, Collection) and not isinstance(
            population, str
        ):
            for pop in population:
                axes = self._plot_grouped_by_pe(
                    plotter, pop, axes=axes, **kwargs
                )
            return axes

        emission_data = self.get_data("Emission Energy", population)
        if not emission_data:
            logging.info(
                f"No measurement found for {population = } and "
                '"Emission Energy". Skipping this plot.'
            )
            return axes

        for distrib in emission_data:
            e_pe = distrib.e_pe
            axes[e_pe] = distrib.plot(
                plotter, axes=axes.get(e_pe), population=population, **kwargs
            )
        return axes

    @property
    def teey(self) -> TEEY:
        """Return the |TEEY| directly."""
        emission_yield = self.get_data("Emission Yield", "all")
        if not emission_yield:
            raise MissingDataError
        if len(emission_yield) > 1:
            logging.warning("Several TEEY are stored. Returning first.")
        return emission_yield[0]

    @property
    def seey(self) -> SEEY:
        """Return the |SEEY| directly."""
        emission_yield = self.get_data("Emission Yield", "SE")
        if not emission_yield:
            raise MissingDataError
        if len(emission_yield) > 1:
            logging.warning("Several SEEY are stored. Returning first.")
        return emission_yield[0]

    def rescale_energy_distributions_to_teey(self) -> None:
        r"""Rescale measured energy distributions to match the measured |TEEY|.

        Enforces the physical constraint from Eq. (4)/(50) in
        :cite:`Furman2002`:

        .. math::
           \int_0^{E_0} \frac{d\delta}{dE}\,dE = \delta(E_0)

        Each measured energy distribution's absolute scale is corrected (via a
        single multiplicative factor) so that its integral over emission
        energy matches the independently measured yield at the same impact
        energy. This compensates for per-file calibration drift (e.g.
        inconsistent detector settings across measurement files), by anchoring
        every spectrum to the same, trusted yield measurement.

        """
        teeys = self.get_data("Emission Yield", "all")
        if not teeys:
            raise MissingDataError(
                "Missing TEEY measurement, needed to rescale energy distributions."
            )
        if len(teeys) > 1:
            logging.warning(
                "Several emission yield measurements found; using the first "
                "one to rescale energy distributions."
            )
        ref_teey = teeys[0]
        energies = np.array(ref_teey.energies)

        distributions = self.get_data("Emission Energy", "all")
        for distrib in distributions:
            e_pe = distrib.e_pe
            if not (energies.min() <= e_pe <= energies.max()):
                logging.warning(
                    f"{e_pe = } is outside the measured yield energy range "
                    f"[{energies.min()}, {energies.max()}]; "
                    "skipping rescaling for this distribution."
                )
                continue

            expected_area = float(
                np.interp(e_pe, energies, ref_teey.normal_data)
            )
            distrib.rescale(objective_yield=expected_area, norm=1.0)
