"""Define a generic worflow."""

from pathlib import Path

import numpy as np
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.loader.pandas_loader import PandasLoader
from eemilib.model.vaughan import Vaughan
from eemilib.plotter.pandas import PandasPlotter


def main() -> None:
    """Define the simple basic workflow to adapt as GUI."""
    filepath = Path("../../data/example_copper/measured_TEEY_Cu_1_eroded.txt")
    filepaths = (filepath,)

    # =========================================================================
    # Horizontal screen portion 1 of 3
    # =========================================================================
    data_matrix = DataMatrix()

    # A matrix with 4 rows, 3 cols. You click on a cell, a window opens and you
    # select the file(s) to open.
    data_matrix.set_files(
        filepaths,
        row=3,
        col=0,
    )

    # Dropdown menu. Possible values are modules in eemilib.loader, deriving
    # from Loader
    loader = PandasLoader()

    # "Load" button
    data_matrix.load_data(loader)

    # =========================================================================
    # Horizontal screen portion 2 of 3
    # =========================================================================
    # A dropdown menu. Possible values are modules in eemilib.model, deriving
    # from Model
    model = Vaughan()

    # A matrix with 6 columns, n rows
    # There is one row per (key, value) pair in Model.parameters attribute
    # The list of columns is:
    # 0: parameter.markdown
    # 1: parameter.unit
    # 2: parameter.value (editable, editing it updates parameter.value parameter)
    # 3: parameter.lower_bound (editable, editing it updates parameter.lower_bound parameter)
    # 4: parameter.upper_bound (editable, editing it updates parameter.upper_bound parameter)
    # 5: a "lock" checkbox. checking it calls the parameter.lock method. unchecking it calls the paramer.unlock method

    # The "Fit!" button, at the bottom
    model.find_optimal_parameters(data_matrix)
    # It will update the values of model.parameters[key].value, so the matrix
    # above should be updated too

    # =========================================================================
    # Horizontal screen, portion 3 of 3
    # =========================================================================
    # A dropdown menu. Possible values are modules in eemilib.plotter, deriving
    # from Plotter
    plotter = PandasPlotter()

    # Cases to tick (several values possible); the possible values are in the
    # tuple constants.ImplementedPop
    population = "all"
    # Case to tick (one value possible); the possible values are in
    # constants.ImplementedEmissionData
    emission_data_type = "Emission Yield"

    # The "Plot measured" button
    axes = data_matrix.plot(
        plotter, population=population, emission_data_type=emission_data_type
    )

    # Energy [eV]: (here start, stop, nstep boxes)
    e_start = 0
    e_end = 1000
    n_e = 1001

    # Angles [deg]: (here start, stop, nstep boxes)
    theta_start = 0
    theta_end = 60
    n_theta = 4

    # The "Plot model" button
    axes = model.plot(
        plotter,
        population=population,
        emission_data_type=emission_data_type,
        energies=np.linspace(e_start, e_end, n_e),
        angles=np.linspace(theta_start, theta_end, n_theta),
        axes=axes,
    )

    # Evaluate
    evaluations = model.evaluate(data_matrix)
    print(evaluations)
    return


if __name__ == "__main__":
    main()
