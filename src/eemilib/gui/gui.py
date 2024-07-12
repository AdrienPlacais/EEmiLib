#!/usr/bin/env python3
"""Define a GUI."""
import importlib
import inspect
import sys

from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.gui.helper import setup_dropdown, setup_linspace_entries
from eemilib.loader.loader import Loader
from eemilib.model.model import Model
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import (
    IMPLEMENTED_EMISSION_DATA,
    IMPLEMENTED_POP,
    ImplementedEmissionData,
    ImplementedPop,
)
from eemilib.util.helper import get_classes
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """This object holds the GUI."""

    def __init__(self):
        """Create the GUI."""
        # EEmiLib attributes
        self.data_matrix = DataMatrix()
        self.axes = None

        super().__init__()
        self.setWindowTitle("EEmiLib GUI")

        # GUI attributes
        self.file_lists: list[list[None | QListWidget]]

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        self.setup_file_selection_matrix()
        self.setup_loader_dropdown()
        self.setup_model_dropdown()
        self.setup_model_configuration()
        self.setup_energy_angle_inputs()
        self.setup_plotter_dropdown()

    def setup_file_selection_matrix(self) -> None:
        """Create the 4 * 3 matrix to select the files to load."""
        self.file_matrix_group = QGroupBox("Files selection matrix")
        self.file_matrix_layout = QGridLayout()

        row_labels, col_labels = IMPLEMENTED_POP, IMPLEMENTED_EMISSION_DATA
        n_rows, n_cols = len(row_labels), len(col_labels)

        for i, label in enumerate(row_labels):
            self.file_matrix_layout.addWidget(QLabel(label), i + 1, 0)

        for j, label in enumerate(col_labels):
            self.file_matrix_layout.addWidget(QLabel(label), 0, j + 1)

        self.file_lists = [
            [None for _ in range(n_cols)] for _ in range(n_rows)
        ]
        for i in range(n_rows):
            for j in range(n_cols):
                cell_layout = QHBoxLayout()
                button = QPushButton("📂")
                button.setFont(QFont("Segoe UI Emoji", 10))
                button.clicked.connect(
                    lambda _, x=i, y=j: self.select_files(x, y)
                )
                cell_layout.addWidget(button)
                file_list = QListWidget()
                cell_layout.addWidget(file_list)
                self.file_matrix_layout.addLayout(cell_layout, i + 1, j + 1)
                self.file_lists[i][j] = file_list

        self.file_matrix_group.setLayout(self.file_matrix_layout)
        self.main_layout.addWidget(self.file_matrix_group)

    def setup_loader_dropdown(self) -> None:
        """Set the :class:`.Loader` related interface."""
        classes, layout, dropdown, buttons = setup_dropdown(
            module_name="eemilib.loader",
            base_class=Loader,
            buttons_args={"Load data": self.load_data},
        )
        self.loader_classes = classes
        self.main_layout.addLayout(layout)
        self.loader_dropdown = dropdown
        self.load_button = buttons[0]

    def setup_model_dropdown(self) -> None:
        """Set the :class:`.Model` related interface."""
        classes, layout, dropdown, buttons = setup_dropdown(
            module_name="eemilib.model",
            base_class=Model,
            buttons_args={"Fit!": self.fit_model},
        )
        self.model_classes = classes
        self.main_layout.addLayout(layout)
        self.model_dropdown = dropdown
        self.fit_button = buttons[0]

    def setup_model_configuration(self):
        # Model configuration group
        self.model_config_group = QGroupBox("Model configuration")
        self.model_config_layout = QVBoxLayout()

        self.model_table = QTableWidget(0, 6)
        self.model_table.setHorizontalHeaderLabels(
            [
                "Parameter",
                "Unit",
                "Value",
                "Lower Bound",
                "Upper Bound",
                "Lock",
            ]
        )
        self.model_config_layout.addWidget(self.model_table)

        self.model_config_group.setLayout(self.model_config_layout)
        self.main_layout.addWidget(self.model_config_group)

    def setup_energy_angle_inputs(self):
        # Energy and Angle input fields
        self.energy_angle_group = QGroupBox(
            "PEs energy and angle range (model plot)"
        )
        self.energy_angle_layout = QVBoxLayout()

        layout, first, last, points = setup_linspace_entries("Energy [eV]")
        self.energy_angle_layout.addLayout(layout)
        self.energy_first = first
        self.energy_last = last
        self.energy_points = points

        layout, first, last, points = setup_linspace_entries("Angle [deg]")
        self.energy_angle_layout.addLayout(layout)
        self.angle_first = first
        self.angle_last = last
        self.angle_points = points

        self.energy_angle_group.setLayout(self.energy_angle_layout)
        self.main_layout.addWidget(self.energy_angle_group)

    def _set_up_data_to_plot_checkboxes(self) -> None:
        """Add checkbox to select which data should be plotted."""
        data_plot_layout = QHBoxLayout()
        data_plot_layout.addWidget(QLabel("Data to plot:"))
        self.data_checkboxes = []
        for data in IMPLEMENTED_EMISSION_DATA:
            checkbox = QRadioButton(data)
            self.data_checkboxes.append(checkbox)
            data_plot_layout.addWidget(checkbox)
        self.main_layout.addLayout(data_plot_layout)

    def _set_up_population_to_plot_checkboxes(self) -> None:
        """Add checkbox to select which population should be plotted."""
        population_plot_layout = QHBoxLayout()
        population_plot_layout.addWidget(QLabel("Population to plot:"))
        self.population_checkboxes: list[QCheckBox] = []
        for pop in IMPLEMENTED_POP:
            checkbox = QCheckBox(pop)
            self.population_checkboxes.append(checkbox)
            population_plot_layout.addWidget(checkbox)
        self.main_layout.addLayout(population_plot_layout)

    def setup_plotter_dropdown(self) -> None:
        """Set the :class:`.Plotter` related interface."""
        self._set_up_data_to_plot_checkboxes()
        self._set_up_population_to_plot_checkboxes()

        classes, layout, dropdown, buttons = setup_dropdown(
            module_name="eemilib.plotter",
            base_class=Plotter,
            buttons_args={
                "Plot file": self.plot_measured,
                "Plot model": self.plot_model,
                "New figure": self._new_axes,
            },
        )
        self.plotter_classes = classes
        self.main_layout.addLayout(layout)
        self.plotter_dropdown = dropdown
        self.plot_measured_button = buttons[0]
        self.plot_model_button = buttons[1]

    def select_files(self, row: int, col: int) -> None:
        options = QFileDialog.Options()
        file_names, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "All Files (*);;CSV Files (*.csv)",
            options=options,
        )
        if file_names:
            current_file_lists = self.file_lists[row][col]
            assert current_file_lists is not None
            current_file_lists.clear()
            current_file_lists.addItems(file_names)
            # self.data_matrix.set_files(file_names, row=row, col=col)

    def load_data(self) -> None:
        """Load all the files set in GUI."""
        selected_loader = self.loader_dropdown.currentText()
        module_name = self.loader_classes[selected_loader]
        loader_module = importlib.import_module(module_name)
        loader_class = getattr(loader_module, selected_loader)

        loader = loader_class()

        for i in range(len(IMPLEMENTED_POP)):
            for j in range(len(IMPLEMENTED_EMISSION_DATA)):
                file_list_widget = self.file_lists[i][j]
                if file_list_widget is not None:
                    file_names = [
                        file_list_widget.item(k).text()
                        for k in range(file_list_widget.count())
                    ]
                    self.data_matrix.set_files(file_names, row=i, col=j)

        self.data_matrix.load_data(loader)
        print("Data loaded!")

    def fit_model(self) -> None:
        """Perform the fit on the loaded data."""
        selected_model = self.model_dropdown.currentText()
        module_name = self.model_classes[selected_model]
        model_module = importlib.import_module(module_name)
        model_class = getattr(model_module, selected_model)

        # Instantiate the model with the current data matrix
        model = model_class()
        model.find_optimal_parameters(self.data_matrix)
        optimal_parameters = model.parameters

        # Read parameters from the GUI and set them in the model
        # params = {}
        # for row in range(self.model_table.rowCount()):
        #     param_name = self.model_table.item(row, 0).text()
        #     param_value = float(self.model_table.item(row, 2).text())
        #     params[param_name] = param_value
        #
        # model.set_parameters(params)
        #
        # # Fit the model
        # model.fit()

        print("Model fitted successfully!")

    def plot_measured(self):
        """Plot the desired data, as imported."""
        selected_plotter: str = self.plotter_dropdown.currentText()
        plotter_module_name: str = self.plotter_classes[selected_plotter]
        plotter_module = importlib.import_module(plotter_module_name)
        plotter_class = getattr(plotter_module, selected_plotter)
        plotter = plotter_class()

        populations = [
            IMPLEMENTED_POP[i]
            for i, checked in enumerate(self.population_checkboxes)
            if checked.isChecked()
        ]
        if len(populations) == 0:
            print("Please provide at least one population to plot.")
            return
        emission_data_type = "Emission Yield"
        self.axes = self.data_matrix.plot(
            plotter,
            population=populations,
            emission_data_type=emission_data_type,
            axes=self.axes,
        )

    def plot_model(self) -> None:
        pass

    def _new_axes(self) -> None:
        """Remove the stored axes to plot on a new one."""
        self.axes = None


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    print(f"{IMPLEMENTED_POP = }")
    main()
