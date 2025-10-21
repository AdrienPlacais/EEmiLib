"""Define some helper functions."""

import logging
from collections.abc import Sequence

from eemilib.util.constants import (
    ImplementedEmissionData,
    ImplementedPop,
    col_energy,
    md_energy_distrib,
    md_ey,
)


def explicit_column_names(
    columns: Sequence[str],
    population: ImplementedPop | None = None,
    emission_data_type: ImplementedEmissionData | None = None,
) -> dict[str, str]:
    """Explicit column names for the plot.

    This is used to have clearer legends in the plot.

    Parameters
    ----------
    columns :
        Columns of the data frame to be plotted.
    population :
        Type of emitted electrons in data frame.
    emission_data_type :
        Type of data stored in data frame.

    Returns
    -------
    dict[str, str]
        Mapping to easily rename the data frame.

    """
    if population is None:
        logging.info(
            "Cannot explicit column names as population kwargs was not given."
            " Keeping original."
        )
        return {col: col for col in columns}

    if emission_data_type == "Emission Yield":
        explicit = {
            col: (
                f"{md_ey[population]} @{col}"
                if col != col_energy
                else "PEs energy [eV]"
            )
            for col in columns
        }
        return explicit

    if emission_data_type == "Emission Energy":
        explicit = {
            col: (
                f"{md_energy_distrib[population]} @{col}"
                if col != col_energy
                else col_energy
            )
            for col in columns
        }
        return explicit

    logging.info(
        f"Explicit column names not implemented for {emission_data_type = }. "
        "Keeping original."
    )
    return {col: col for col in columns}
