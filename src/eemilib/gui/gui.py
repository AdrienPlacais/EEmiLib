#!/usr/bin/env python3
"""Define a GUI."""
import importlib
import inspect
import sys

from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.loader.loader import Loader
from eemilib.model.model import Model
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import IMPLEMENTED_EMISSION_DATA, IMPLEMENTED_POP
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

    def __init__(self):
        # EEmiLib attributes
        self.data_matrix = DataMatrix()

        super().__init__()
        self.setWindowTitle("EEmiLib GUI")

        # GUI attributes
        self.file_lists: list[list[None | QListWidget]]

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.main_layout = QVBoxLayout(self.central_widget)

        # Add components
        self.setup_loader_dropdown()
        self.setup_file_selection_matrix()
        self.setup_model_selection()
        self.setup_model_configuration()
        self.setup_energy_angle_inputs()
        self.setup_plotter_dropdown()

    def setup_loader_dropdown(self):
        # Loader dropdown and Load Data button
        loader_layout = QHBoxLayout()
        self.loader_classes = get_classes("eemilib.loader", Loader)
        self.loader_dropdown = QComboBox()
        self.loader_dropdown.addItems(self.loader_classes.keys())
        loader_layout.addWidget(QLabel("Select Loader:"))
        loader_layout.addWidget(self.loader_dropdown)

        self.load_button = QPushButton("Load data")
        self.load_button.clicked.connect(self.load_data)
        loader_layout.addWidget(self.load_button)

        self.main_layout.addLayout(loader_layout)

    def setup_file_selection_matrix(self):
        self.file_matrix_group = QGroupBox("Files selection matrix")
        self.file_matrix_layout = QGridLayout()

        # Row and column labels
        row_labels = IMPLEMENTED_POP
        col_labels = IMPLEMENTED_EMISSION_DATA
        n_rows = len(row_labels)
        n_cols = len(col_labels)

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

    def setup_model_selection(self):
        # Model selection dropdown and Fit Model button
        model_selection_layout = QHBoxLayout()
        self.model_classes = get_classes("eemilib.model", Model)
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(self.model_classes.keys())
        model_selection_layout.addWidget(
            QLabel("Select electron emission model:")
        )
        model_selection_layout.addWidget(self.model_dropdown)

        self.fit_button = QPushButton("Fit!")
        self.fit_button.clicked.connect(self.fit_model)
        model_selection_layout.addWidget(self.fit_button)

        self.main_layout.addLayout(model_selection_layout)

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

        # Energy inputs
        energy_layout = QHBoxLayout()
        energy_layout.addWidget(QLabel("Energy [eV]"))
        energy_layout.addWidget(QLabel("first"))
        self.energy_first = QLineEdit()
        energy_layout.addWidget(self.energy_first)
        energy_layout.addWidget(QLabel("last"))
        self.energy_last = QLineEdit()
        energy_layout.addWidget(self.energy_last)
        energy_layout.addWidget(QLabel("n points"))
        self.energy_points = QLineEdit()
        energy_layout.addWidget(self.energy_points)
        self.energy_angle_layout.addLayout(energy_layout)

        # Angle inputs
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("Angle [deg]"))
        angle_layout.addWidget(QLabel("first"))
        self.angle_first = QLineEdit()
        angle_layout.addWidget(self.angle_first)
        angle_layout.addWidget(QLabel("last"))
        self.angle_last = QLineEdit()
        angle_layout.addWidget(self.angle_last)
        angle_layout.addWidget(QLabel("n points"))
        self.angle_points = QLineEdit()
        angle_layout.addWidget(self.angle_points)
        self.energy_angle_layout.addLayout(angle_layout)

        self.energy_angle_group.setLayout(self.energy_angle_layout)
        self.main_layout.addWidget(self.energy_angle_group)

    def setup_plotter_dropdown(self):
        # Data and Population checkboxes
        data_plot_layout = QHBoxLayout()
        data_plot_layout.addWidget(QLabel("Data to plot:"))
        self.data_checkboxes = []
        for data in IMPLEMENTED_EMISSION_DATA:
            checkbox = QRadioButton(data)
            self.data_checkboxes.append(checkbox)
            data_plot_layout.addWidget(checkbox)

        population_plot_layout = QHBoxLayout()
        population_plot_layout.addWidget(QLabel("Population to plot:"))
        self.population_checkboxes = []
        for pop in IMPLEMENTED_POP:
            checkbox = QCheckBox(pop)
            self.population_checkboxes.append(checkbox)
            population_plot_layout.addWidget(checkbox)

        plotter_layout = QHBoxLayout()
        self.plotter_classes = get_classes("eemilib.plotter", Plotter)
        self.plotter_dropdown = QComboBox()
        self.plotter_dropdown.addItems(self.plotter_classes.keys())
        plotter_layout.addWidget(QLabel("Select Plotter:"))
        plotter_layout.addWidget(self.plotter_dropdown)

        self.plot_measured_button = QPushButton("Plot file")
        self.plot_measured_button.clicked.connect(self.plot_measured)
        plotter_layout.addWidget(self.plot_measured_button)

        self.plot_model_button = QPushButton("Plot model")
        self.plot_model_button.clicked.connect(self.plot_model)
        plotter_layout.addWidget(self.plot_model_button)

        self.main_layout.addLayout(plotter_layout)

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

    def fit_model(self):
        # Implement model fitting logic
        selected_model = self.model_dropdown.currentText()
        module_name = self.model_classes[selected_model]
        model_module = importlib.import_module(module_name)
        model_class = getattr(model_module, selected_model)

        # Instantiate the model with the current data matrix
        model = model_class()
        model.find_optimal_parameters(self.data_matrix)

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
        # Implement plotting measured data logic
        print("Plotting measured data...")

    def plot_model(self):
        # Implement plotting model data logic
        print("Plotting model data...")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    print(f"{IMPLEMENTED_POP = }")
    main()
