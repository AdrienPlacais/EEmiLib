"""Define a structure to select a :class:`.Model` mandatory files."""

from collections.abc import Collection
from dataclasses import dataclass

from eemilib.util.constants import ImplementedPop


@dataclass
class ModelConfig:
    """Define mandatory files for a :class:`.Model`."""

    emission_yield_files: Collection[ImplementedPop]
    emission_energy_files: Collection[ImplementedPop]
    emission_angle_files: Collection[ImplementedPop]
