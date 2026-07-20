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
    e_pe: float | None = None,
    is_model: bool = False,
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
    e_pe :
        Energy of |PEs| in :unit:`eV`, if applicable.
    is_model :
        If data is modelled.

    Returns
    -------
        Mapping to easily rename the data frame.

    """
    if population is None:
        logging.info(
            "Cannot explicit column names as population kwargs was not given."
            " Keeping original."
        )
        return {col: col for col in columns}

    explicit = {}
    for col in columns:
        if col == col_energy:
            explicit[col] = col
            continue

        if is_model:
            modelled = "Modelled"
        else:
            modelled = ""

        if emission_data_type == "Emission Yield":
            _types_of_data = md_ey
            pe = ""
        elif emission_data_type == "Emission Energy":
            _types_of_data = md_energy_distrib
            pe = f"${e_pe}" + r"\,\mathrm{eV}$" if e_pe is not None else ""
        else:
            raise ValueError(
                "Plotting implemented for Emission Yield and Emission Energy only."
            )

        type_of_data = _types_of_data[population]
        _angles = col.split()
        angle = f"@${_angles[0]}" + r"\,\mathrm{" + _angles[1][1:-1] + r"}$"

        info = (key for key in (modelled, type_of_data, angle, pe) if key)
        explicit[col] = " ".join(info)
    return explicit
