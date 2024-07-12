#!/usr/bin/env python3
"""Define a GUI."""
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
        self.loader_dropdown = QComboBox()
        self.loader_dropdown.addItems(get_classes("eemilib.loader", Loader))
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
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(get_classes("eemilib.model", Model))
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
        self.plotter_dropdown = QComboBox()
        self.plotter_dropdown.addItems(
            get_classes("eemilib.plotter", Plotter)
        )  # Add other plotters as needed
        plotter_layout.addWidget(QLabel("Select Plotter:"))
        plotter_layout.addWidget(self.plotter_dropdown)

        self.plot_measured_button = QPushButton("Plot file")
        self.plot_measured_button.clicked.connect(self.plot_measured)
        plotter_layout.addWidget(self.plot_measured_button)

        self.plot_model_button = QPushButton("Plot model")
        self.plot_model_button.clicked.connect(self.plot_model)
        plotter_layout.addWidget(self.plot_model_button)

        # Add checkboxes and plotter layout to the main layout
        self.main_layout.addLayout(data_plot_layout)
        self.main_layout.addLayout(population_plot_layout)
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
            self.data_matrix.set_files(file_names, row=row, col=col)

    def load_data(self) -> None:
        """Load all the files set in GUI."""
        print("Loading data...")
        # if loader is None:
        #     print("missing arg")
        #     return
        # self.data_matrix.load_data(loader)
        # print("Data loaded!")

    def fit_model(self):
        # Implement model fitting logic
        print("Fitting model...")

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
