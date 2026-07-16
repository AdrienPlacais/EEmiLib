"""Define the ABC for the :class:`Loader`."""

from abc import ABC, abstractmethod
from collections.abc import Collection
from typing import Sequence

import pandas as pd
from eemilib.loader.helper import DataPath
from eemilib.util.constants import ImplementedPop
from eemilib.util.helper import documentation_url


class Loader(ABC):
    """Define the base class for loading various electron emission files."""

    def __init__(self) -> None:
        """Instantiate the object."""
        self.doc_url = documentation_url(self)
        #: Column separator. Not mandatory, but must be called ``sep`` in order
        #: to be recognized by the Parameters in the GUI.
        self.sep: str
        #: Comment character. Not mandatory, but must be called ``comment`` in
        #: order to be recognized by the Parameters in the GUI.
        self.comment: str

    @abstractmethod
    def load_emission_yield(
        self,
        filepath: DataPath | Collection[DataPath],
        *args,
        population: ImplementedPop | None = None,
        **kwargs,
    ) -> pd.DataFrame:
        """Load the given electron emission yield file."""

    @abstractmethod
    def load_emission_energy_distribution(
        self,
        *filepaths: DataPath,
        population: ImplementedPop | None = None,
        e_pes: Sequence[float] | None = None,
        **kwargs,
    ) -> dict[DataPath, tuple[pd.DataFrame, float | None]]:
        """Load the given electron emission energy distribution files.

        We expect several files at normal incidence, with different |PEs|
        energy, and a single ``population``. We also try to load the energy of
        |PEs| from file metadata.

        Parameters
        ----------
        filepaths :
            Path to files holding data under study, corresponding to several
            |PE| energies.
        population :
            Nature of measured electrons. Will generally be ``"all"``, but can
            be left to ``None`` as all loaders do not necessarily use it.
        e_pes :
            |PEs| energies, if the loader cannot find them in the given files.
            Must have the same length as ``filepaths``.

        Returns
        -------
            For every filepath:

            - A pandas dataframe holding the data. Has a ``Energy [eV]`` column
              holding emitted electrons energy. And one or several columns
              ``theta [deg]``, where ``theta`` is the value of the incidence
              angle and content is corresponding emission energy distribution.
            - Energy of |PEs| in :unit:`eV`. If not found in the file comments,
              it will be inferred from the position of the |EBEs| peak.

        """

    @abstractmethod
    def load_emission_angle_distribution(
        self, filepath: DataPath | Collection[DataPath], *args, **kwargs
    ) -> pd.DataFrame:
        """Load the given electron emission angle distribution file."""
