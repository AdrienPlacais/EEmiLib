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

    # Dropdown menu to select loader
    loader = DeesseLoader()

    # "Load" button
    data_matrix.load_data(loader)

    # =========================================================================
    # Second horizontal screen portion: several tabs with different models
    # =========================================================================
    model = Vaughan()

    # The "Fit!" button
    model.find_optimal_parameters(data_matrix)

    # =========================================================================
    # A third horizontal screen portion, or with the files
    # =========================================================================
    plotter = PandasPlotter()
    axes = data_matrix.data_matrix[3][0].plot(plotter)

    energies = np.linspace(0, 1000, 1001)
    angles = np.linspace(0, 60, 4)
    axes = model.plot(
        plotter,
        population="all",
        emission_data_type="Emission Yield",
        energies=energies,
        angles=angles,
        axes=axes,
    )
    return


if __name__ == "__main__":
    main()
