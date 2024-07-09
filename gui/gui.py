#!/usr/bin/env python3
import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
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
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulation GUI")

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
        self.loader_dropdown.addItems(
            ["DeesseLoader"]
        )  # Add other loaders as needed
        loader_layout.addWidget(QLabel("Select Loader:"))
        loader_layout.addWidget(self.loader_dropdown)

        self.load_button = QPushButton("Load Data")
        self.load_button.clicked.connect(self.load_data)
        loader_layout.addWidget(self.load_button)

        self.main_layout.addLayout(loader_layout)

    def setup_file_selection_matrix(self):
        # File selection matrix (4x3 grid)
        self.file_matrix_group = QGroupBox("File Selection Matrix")
        self.file_matrix_layout = QGridLayout()

        # Row and column labels
        row_labels = ["SE", "EBE", "IBE", "all"]
        col_labels = ["Emission Yield", "Emission Energy", "Emission Angle"]

        for i, label in enumerate(row_labels):
            self.file_matrix_layout.addWidget(QLabel(label), i + 1, 0)

        for j, label in enumerate(col_labels):
            self.file_matrix_layout.addWidget(QLabel(label), 0, j + 1)

        self.file_lists = [[None for _ in range(3)] for _ in range(4)]
        for i in range(4):
            for j in range(3):
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
        self.model_dropdown.addItems(["Vaughan"])  # Add other models as needed
        model_selection_layout.addWidget(QLabel("Select Model:"))
        model_selection_layout.addWidget(self.model_dropdown)

        self.fit_button = QPushButton("Fit Model")
        self.fit_button.clicked.connect(self.fit_model)
        model_selection_layout.addWidget(self.fit_button)

        self.main_layout.addLayout(model_selection_layout)

    def setup_model_configuration(self):
        # Model configuration group
        self.model_config_group = QGroupBox("Model Configuration")
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
        energy_layout.addWidget(QLabel("First"))
        self.energy_first = QLineEdit()
        energy_layout.addWidget(self.energy_first)
        energy_layout.addWidget(QLabel("Last"))
        self.energy_last = QLineEdit()
        energy_layout.addWidget(self.energy_last)
        energy_layout.addWidget(QLabel("Points"))
        self.energy_points = QLineEdit()
        energy_layout.addWidget(self.energy_points)
        self.energy_angle_layout.addLayout(energy_layout)

        # Angle inputs
        angle_layout = QHBoxLayout()
        angle_layout.addWidget(QLabel("Angle [deg]"))
        angle_layout.addWidget(QLabel("First"))
        self.angle_first = QLineEdit()
        angle_layout.addWidget(self.angle_first)
        angle_layout.addWidget(QLabel("Last"))
        self.angle_last = QLineEdit()
        angle_layout.addWidget(self.angle_last)
        angle_layout.addWidget(QLabel("Points"))
        self.angle_points = QLineEdit()
        angle_layout.addWidget(self.angle_points)
        self.energy_angle_layout.addLayout(angle_layout)

        self.energy_angle_group.setLayout(self.energy_angle_layout)
        self.main_layout.addWidget(self.energy_angle_group)

    def setup_plotter_dropdown(self):
        # Plotter dropdown and Plot buttons
        plotter_layout = QHBoxLayout()
        self.plotter_dropdown = QComboBox()
        self.plotter_dropdown.addItems(
            ["PandasPlotter"]
        )  # Add other plotters as needed
        plotter_layout.addWidget(QLabel("Select Plotter:"))
        plotter_layout.addWidget(self.plotter_dropdown)

        self.plot_measured_button = QPushButton("Plot Measured")
        self.plot_measured_button.clicked.connect(self.plot_measured)
        plotter_layout.addWidget(self.plot_measured_button)

        self.plot_model_button = QPushButton("Plot Model")
        self.plot_model_button.clicked.connect(self.plot_model)
        plotter_layout.addWidget(self.plot_model_button)

        self.main_layout.addLayout(plotter_layout)

    def select_files(self, row, col):
        options = QFileDialog.Options()
        file_names, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "All Files (*);;CSV Files (*.csv)",
            options=options,
        )
        if file_names:
            self.file_lists[row][col].clear()
            self.file_lists[row][col].addItems(file_names)
            # Here you would typically store the file paths in your DataMatrix

    def load_data(self):
        # Implement data loading logic
        print("Loading data...")

    def fit_model(self):
        # Implement model fitting logic
        print("Fitting model...")

    def plot_measured(self):
        # Implement plotting measured data logic
        print("Plotting measured data...")

    def plot_model(self):
        # Implement plotting model data logic
        print("Plotting model data...")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
