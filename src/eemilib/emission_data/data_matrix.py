"""Store the filepaths entered by user.

.. todo::
    Methods to reset filepaths/data

"""

import logging
from collections.abc import Collection, Sequence
from typing import Literal, cast, overload

from eemilib.core.model_config import ModelConfig
from eemilib.emission_data.emission_angle_distribution import (
    EmissionAngleDistribution,
)
from eemilib.emission_data.emission_data import EmissionData
from eemilib.emission_data.emission_energy_distribution import (
    EMISSION_ENERGIES_BY_POP,
    AllEmissionEnergyDistribution,
    EBEEmissionEnergyDistribution,
    IBEEmissionEnergyDistribution,
    SEEmissionEnergyDistribution,
)
from eemilib.emission_data.emission_yield import EmissionYield
from eemilib.loader.helper import DataPath
from eemilib.loader.loader import Loader
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import (
    IMPLEMENTED_EMISSION_DATA,
    IMPLEMENTED_POP,
    ImplementedEmissionData,
    ImplementedPop,
)
from eemilib.util.helper import flatten

pop_to_row = {pop: i for i, pop in enumerate(IMPLEMENTED_POP)}
row_to_pop = {val: key for key, val in pop_to_row.items()}

emission_data_type_to_col = {
    data_type: j for j, data_type in enumerate(IMPLEMENTED_EMISSION_DATA)
}
col_to_emission_data_type = {
    val: key for key, val in emission_data_type_to_col.items()
}

n_rows = len(IMPLEMENTED_POP)
n_cols = len(IMPLEMENTED_EMISSION_DATA)


class MissingDataError(ValueError):
    """Error raised when data is missing from :class:`.DataMatrix`."""


class DataMatrix:
    """Store all the input files and corresp data in a single object."""

    def __init__(self) -> None:
        """Instantiate the object."""
        self.files_matrix: list[list[list[DataPath]]]
        self.files_matrix = [
            [[] for _ in range(n_cols)] for _ in range(n_rows)
        ]

        self.data_matrix: list[
            list[None | EmissionData | Collection[EmissionData]]
        ]
        self.data_matrix = [
            [None for _ in range(n_cols)] for _ in range(n_rows)
        ]

    def _natures_to_indexes(
        self,
        population_type: ImplementedPop,
        emission_data_type: ImplementedEmissionData,
    ) -> tuple[int, int]:
        """Give the desired indexes."""
        return (
            pop_to_row[population_type],
            emission_data_type_to_col[emission_data_type],
        )

    def _indexes_to_natures(
        self, row: int, col: int
    ) -> tuple[ImplementedPop, ImplementedEmissionData]:
        """Give the desired natures."""
        population_type = row_to_pop[row]
        assert population_type in IMPLEMENTED_POP
        emission_data_type = col_to_emission_data_type[col]
        assert emission_data_type in IMPLEMENTED_EMISSION_DATA
        return population_type, emission_data_type

    @overload
    def set_files(
        self,
        files: DataPath | Collection[DataPath],
        row: int,
        col: int,
        population: None = None,
        emission_data_type: None = None,
    ) -> None: ...

    @overload
    def set_files(
        self,
        files: DataPath | Collection[DataPath],
        row: None = None,
        col: None = None,
        *,
        population: ImplementedPop,
        emission_data_type: ImplementedEmissionData,
    ) -> None: ...

    def set_files(
        self,
        files: DataPath | Collection[DataPath],
        row: int | None = None,
        col: int | None = None,
        population: ImplementedPop | None = None,
        emission_data_type: ImplementedEmissionData | None = None,
    ) -> None:
        """Set the file(s) by index or name."""
        if population and emission_data_type:
            row, col = self._natures_to_indexes(
                population_type=population,
                emission_data_type=emission_data_type,
            )

        if row is None or col is None:
            raise ValueError(
                "You need to provide row and col, or population and "
                f"emission_data_type.\n{row = }, {col = }, {population = },"
                f"{emission_data_type = }"
            )

        if isinstance(files, DataPath):
            self.files_matrix[row][col] = [files]
        else:
            self.files_matrix[row][col] = list(files)

    @overload
    def set_data(
        self,
        emission_data: EmissionData | Collection[EmissionData],
        row: int,
        col: int,
        population: None,
        emission_data_type: None,
    ) -> None: ...

    @overload
    def set_data(
        self,
        emission_data: EmissionYield | Collection[EmissionYield],
        row: None,
        col: None,
        population: ImplementedPop,
        emission_data_type: Literal["Emission Yield"],
    ) -> None: ...

    @overload
    def set_data(
        self,
        emission_data: (
            SEEmissionEnergyDistribution
            | Collection[SEEmissionEnergyDistribution]
        ),
        row: None,
        col: None,
        population: Literal["SE"],
        emission_data_type: Literal["Emission Energy"],
    ) -> None: ...

    @overload
    def set_data(
        self,
        emission_data: (
            EBEEmissionEnergyDistribution
            | Collection[EBEEmissionEnergyDistribution]
        ),
        row: None,
        col: None,
        population: Literal["EBE"],
        emission_data_type: Literal["Emission Energy"],
    ) -> None: ...

    @overload
    def set_data(
        self,
        emission_data: (
            IBEEmissionEnergyDistribution
            | Collection[IBEEmissionEnergyDistribution]
        ),
        row: None,
        col: None,
        population: Literal["IBE"],
        emission_data_type: Literal["Emission Energy"],
    ) -> None: ...
    @overload
    def set_data(
        self,
        emission_data: (
            AllEmissionEnergyDistribution
            | Collection[AllEmissionEnergyDistribution]
        ),
        row: None,
        col: None,
        population: Literal["all"],
        emission_data_type: Literal["Emission Energy"],
    ) -> None: ...

    @overload
    def set_data(
        self,
        emission_data: (
            EmissionAngleDistribution | Collection[EmissionAngleDistribution]
        ),
        row: None,
        col: None,
        population: ImplementedPop,
        emission_data_type: Literal["Emission Angle"],
    ) -> None: ...

    def set_data(
        self,
        emission_data: EmissionData | Collection[EmissionData],
        row: int | None = None,
        col: int | None = None,
        population: ImplementedPop | None = None,
        emission_data_type: ImplementedEmissionData | None = None,
    ) -> None:
        """Set the data by index or name.

        .. todo::
           ``population`` is already known if emission_data is given.
           ``emission_data_type`` could be known if emission_data is given.

        """
        if population and emission_data_type:
            row, col = self._natures_to_indexes(
                population_type=population,
                emission_data_type=emission_data_type,
            )

        if row is None or col is None:
            raise ValueError(
                "You need to provide row and col, or population and "
                f"emission_data_type.\n{row = }, {col = }, {population = },"
                f"{emission_data_type = }"
            )

        self.data_matrix[row][col] = emission_data

    @overload
    def get_files(
        self, row: int, col: int, population: None, emission_data_type: None
    ) -> list[DataPath]: ...

    @overload
    def get_files(
        self,
        row: None,
        col: None,
        population: ImplementedPop,
        emission_data_type: ImplementedEmissionData,
    ) -> list[DataPath]: ...

    def get_files(
        self,
        row: int | None = None,
        col: int | None = None,
        population: ImplementedPop | None = None,
        emission_data_type: ImplementedEmissionData | None = None,
    ) -> list[DataPath]:
        """Get the file(s) by index or name."""
        if population and emission_data_type:
            row, col = self._natures_to_indexes(
                population_type=population,
                emission_data_type=emission_data_type,
            )

        if row is None or col is None:
            raise ValueError(
                "You need to provide row and col, or population and "
                f"emission_data_type.\n{row = }, {col = }, {population = },"
                f"{emission_data_type = }"
            )

        return self.files_matrix[row][col]

    @overload
    def get_data(
        self,
        row: int,
        col: int,
        population: None = None,
        emission_data_type: None = None,
    ) -> None | EmissionData | Sequence[EmissionData]: ...

    @overload
    def get_data(
        self,
        row: None = None,
        col: None = None,
        *,
        population: ImplementedPop,
        emission_data_type: Literal["Emission Yield"],
    ) -> None | EmissionYield | Sequence[EmissionYield]: ...

    @overload
    def get_data(
        self,
        row: None = None,
        col: None = None,
        *,
        population: Literal["SE"],
        emission_data_type: Literal["Emission Energy"],
    ) -> Sequence[SEEmissionEnergyDistribution]: ...

    @overload
    def get_data(
        self,
        row: None = None,
        col: None = None,
        *,
        population: Literal["EBE"],
        emission_data_type: Literal["Emission Energy"],
    ) -> Sequence[EBEEmissionEnergyDistribution]: ...

    @overload
    def get_data(
        self,
        row: None = None,
        col: None = None,
        *,
        population: Literal["IBE"],
        emission_data_type: Literal["Emission Energy"],
    ) -> Sequence[IBEEmissionEnergyDistribution]: ...

    @overload
    def get_data(
        self,
        row: None = None,
        col: None = None,
        *,
        population: Literal["all"],
        emission_data_type: Literal["Emission Energy"],
    ) -> Sequence[AllEmissionEnergyDistribution]: ...

    @overload
    def get_data(
        self,
        row: None = None,
        col: None = None,
        *,
        population: ImplementedPop,
        emission_data_type: Literal["Emission Angle"],
    ) -> (
        None | EmissionAngleDistribution | Sequence[EmissionAngleDistribution]
    ): ...

    @overload
    def get_data(
        self,
        row: None = None,
        col: None = None,
        population: None = None,
        emission_data_type: None = None,
    ) -> Sequence[EmissionData]: ...

    @overload
    def get_data(
        self,
        row: None = None,
        col: None = None,
        *,
        population: ImplementedPop,
        emission_data_type: None = None,
    ) -> Sequence[EmissionData]: ...

    @overload
    def get_data(
        self,
        row: None = None,
        col: None = None,
        *,
        population: None = None,
        emission_data_type: ImplementedEmissionData,
    ) -> Sequence[EmissionData]: ...

    def get_data(
        self,
        row: int | None = None,
        col: int | None = None,
        population: ImplementedPop | None = None,
        emission_data_type: ImplementedEmissionData | None = None,
    ) -> None | EmissionData | Sequence[EmissionData]:
        """Get the file(s) by index or name.

        You can provide ``row`` and ``col`` directly.

        Alternatively, provide ``population`` and ``emission_data_type``. If
        ``population`` is not given, return valid data corresponding to all
        populations. If ``emission_data_type`` is not given, return valid
        data corresponding to all emission data.

        Parameters
        ----------
        row :
            Row index in data matrix.
        col :
            Column index in data matrix.
        population :
            Population type.
        emission_data_type :
            Emission data type.

        Returns
        -------
            Desired data; if the specified data does not exists, a ``None`` is
            returned without any error message. ``"EmissionEnergyDistribution``
            behave differently: a list is always returned, and is empty if no
            data was found.

        """
        if population and emission_data_type:
            row, col = self._natures_to_indexes(
                population_type=population,
                emission_data_type=emission_data_type,
            )
        if population and emission_data_type is None:
            single_pop_data = [
                self.get_data(
                    population=population, emission_data_type=data_type
                )
                for data_type in IMPLEMENTED_EMISSION_DATA
            ]
            return cast(
                list[EmissionData],
                [d for d in flatten(single_pop_data) if d is not None],
            )

        if emission_data_type and population is None:
            emission_data = [
                self.get_data(
                    population=pop, emission_data_type=emission_data_type
                )
                for pop in IMPLEMENTED_POP
            ]
            return cast(
                list[EmissionData],
                [d for d in flatten(emission_data) if d is not None],
            )

        if row is None and col is None:
            all_data = [
                [
                    self.get_data(population=pop, emission_data_type=data_type)
                    for pop in IMPLEMENTED_POP
                ]
                for data_type in IMPLEMENTED_EMISSION_DATA
            ]
            return cast(
                list[EmissionData],
                [d for d in flatten(all_data) if d is not None],
            )

        if row is None or col is None:
            raise ValueError(
                "You need to provide row and col, or population and "
                f"emission_data_type.\n{row = }, {col = }, {population = },"
                f"{emission_data_type = }"
            )

        stored = self.data_matrix[row][col]
        if stored is None:
            return []
        if isinstance(stored, EmissionData):
            return [stored]
        return list(stored)

    def load_data(
        self,
        loader: Loader,
        e_pes_emission_energies: (
            dict[ImplementedPop, Sequence[float]] | None
        ) = None,
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

        """
        for pop in IMPLEMENTED_POP:
            for data_type in IMPLEMENTED_EMISSION_DATA:
                filepaths = self.get_files(
                    population=pop, emission_data_type=data_type
                )  # type: ignore

                if not filepaths:
                    continue

                emission_data = None
                if data_type == "Emission Yield":
                    emission_data = EmissionYield.from_filepath(
                        loader, *filepaths, population=pop
                    )

                elif data_type == "Emission Energy":
                    emission_data = list(
                        EMISSION_ENERGIES_BY_POP[pop].from_filepaths(
                            loader,
                            *filepaths,
                            population=pop,
                            e_pes=(
                                e_pes_emission_energies[pop]
                                if e_pes_emission_energies
                                else None
                            ),
                        )
                    )

                elif data_type == "Emission Angle":
                    emission_data = EmissionAngleDistribution.from_filepath(
                        loader, *filepaths, population=pop
                    )

                if emission_data:
                    self.set_data(
                        emission_data,
                        population=pop,
                        emission_data_type=data_type,
                    )  # type: ignore

    def has_all_mandatory_files(self, model_config: ModelConfig) -> bool:
        """Tell if files defined by :attr:`.Model.model_config` are set."""
        for emission_data_type, corresponding_attribute in zip(
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
                        f"{mandatory_population = } not in "
                        f"{IMPLEMENTED_POP = }"
                    )
                    return False

                filepath = self.get_files(
                    population=mandatory_population,
                    emission_data_type=emission_data_type,
                )  # type: ignore
                if filepath is None:
                    logging.error(
                        f"You must define a {emission_data_type} filepath for"
                        f" population {mandatory_population}"
                    )
                    return False

                data_object = self.get_data(
                    population=mandatory_population,
                    emission_data_type=emission_data_type,
                )  # type: ignore
                if data_object is None:
                    logging.error(
                        f"You must load {emission_data_type} filepath for "
                        f"population {mandatory_population}"
                    )
                    return False
        return True

    def plot[T](
        self,
        plotter: Plotter,
        population: ImplementedPop | Collection[ImplementedPop],
        emission_data_type: ImplementedEmissionData,
        axes: T | None = None,
        **kwargs,
    ) -> T | None:
        """Plot desired measured data using ``plotter``.

        This method uses :meth:`.DataMatrix.get_data` to get the
        :class:`.EmissionData` instance matching ``population`` and
        ``emission_data_type``. Then it calls the :meth:`.EmissionData.plot`
        method.

        Parameters
        ----------
        plotter :
            Object realizing the plot. We transfer it to the
            :meth:`.EmissionData.plot` method.
        population :
            One or several populations to plot. If several are given, we simply
            recursively call this method.
        emission_data_type :
            Type of data to plot.
        axes :
            Axes to re-use if given.
        kwargs :
            Other keyword arguments passed to the :meth:`.EmissionData.plot`
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
                    plotter, pop, emission_data_type, axes=axes, **kwargs
                )
            return axes

        emission_data = self.get_data(
            population=population, emission_data_type=emission_data_type
        )

        if emission_data is None:
            logging.info(
                f"No measurement found for {population = } and "
                f"{emission_data_type = }. Skipping this plot."
            )
            return axes

        if isinstance(emission_data, EmissionData):
            emission_data = (emission_data,)

        for data in emission_data:
            axes = data.plot(
                plotter, axes=axes, population=population, **kwargs
            )
        return axes

    @property
    def teey(self) -> EmissionYield:
        """Return the |TEEY| directly."""
        emission_yield = self.data_matrix[3][0]
        if emission_yield is None:
            raise MissingDataError
        assert isinstance(
            emission_yield, EmissionYield
        ), f"Incorrect type for emission_yield: {type(emission_yield)}"
        assert emission_yield.population == "all"
        return emission_yield

    @property
    def seey(self) -> EmissionYield:
        """Return the |SEEY| directly."""
        emission_yield = self.data_matrix[0][0]
        if emission_yield is None:
            raise MissingDataError
        assert isinstance(
            emission_yield, EmissionYield
        ), f"Incorrect type for emission_yield: {type(emission_yield)}"
        assert emission_yield.population == "SE"
        return emission_yield

    @property
    def se_energy_distribution(self) -> SEEmissionEnergyDistribution:
        """Return the energy distribution of |SEs|."""
        distrib = self.get_data(
            population="SE", emission_data_type="Emission Energy"
        )
        if distrib is None:
            raise MissingDataError
        if isinstance(distrib, SEEmissionEnergyDistribution):
            return distrib
        raise ValueError("Several Energy distributions not handled.")

    @property
    def all_energy_distribution(self) -> AllEmissionEnergyDistribution:
        """Return the energy distribution of all emitted electrons."""
        distrib = self.get_data(
            population="all", emission_data_type="Emission Energy"
        )
        if distrib is None:
            raise MissingDataError
        if isinstance(distrib, AllEmissionEnergyDistribution):
            return distrib
        raise ValueError("Several Energy distributions not handled.")
