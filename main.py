"""Define a generic worflow."""

from pathlib import Path

import numpy as np

from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.emission_data.emission_yield import EmissionYield
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
    data_matrix.set_files_by_name(filepaths, "all", "Emission Yield")

    # Dropdown menu to select loader
    loader = DeesseLoader()

    # "Load" button
    data_matrix.load_data(loader)

    # =========================================================================
    # Second horizontal screen portion: several tabs with different models
    # =========================================================================
    model = Vaughan
    data_matrix.assert_has_all_mandatory_files(model.model_config)

    # To change
    emission_yield = data_matrix.data_matrix[3][0]
    assert isinstance(emission_yield, EmissionYield)
    model_instance = model()
    # Should take full `DataMatrix` as input
    model_instance.find_optimal_parameters(emission_yield)

    # =========================================================================
    # A third horizontal screen portion, or with the files
    # =========================================================================
    plotter = PandasPlotter()
    axes = plotter.plot_emission_yield_data(emission_yield)
    energies = np.linspace(0, 1000, 1001)
    angles = np.linspace(0, 60, 4)
    plotter.plot_emission_yield_model(
        model_instance, energies, angles, axes=axes
    )

    return emission_yield, model


if __name__ == "__main__":
    emission_yield, model = main()
