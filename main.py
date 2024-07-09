"""Define a generic worflow."""

from pathlib import Path

import numpy as np

from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.loader.deesse_loader import DeesseLoader
from eemilib.model.vaughan import Vaughan
from eemilib.plotter.pandas import PandasPlotter


def main():
    base_folder = Path(
        "/home/placais/Documents/Simulation/python/eemilib/data/deesse/"
    )
    filepaths = (
        base_folder / "cleanAg0_TEEY_29_05_2018_18h02m35s.csv",
        base_folder / "cleanAg20_TEEY_30_05_2018_10h18m05s.csv",
        base_folder / "cleanAg40_TEEY_30_05_2018_11h05m48s.csv",
        base_folder / "cleanAg60_TEEY_30_05_2018_11h54m09s.csv",
    )

    # =========================================================================
    # First horizontal screen portion: first tab
    # =========================================================================
    data_matrix = DataMatrix()
    data_matrix.set_files(
        filepaths, population="all", emission_data_type="Emission Yield"
    )

    # Dropdown menu. Possible values are modules in eemilib.loader, deriving
    # from Loader
    loader = DeesseLoader()

    # "Load" button
    data_matrix.load_data(loader)

    # =========================================================================
    # Second horizontal screen portion: several tabs with different models
    # =========================================================================
    # A dropdown menu. Possible values are modules in eemilib.model, deriving
    # from Model
    model = Vaughan()

    # The "Fit!" button
    model.find_optimal_parameters(data_matrix)

    # =========================================================================
    # A third horizontal screen portion, or with the files
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
    return


if __name__ == "__main__":
    main()
