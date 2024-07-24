#!/usr/bin/env python3
"""Define a GUI."""
import importlib
import sys
from abc import ABCMeta
from types import ModuleType
from typing import Literal

import numpy as np
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.gui.helper import (
    PARAMETER_ATTR_TO_POS,
    PARAMETER_POS_TO_ATTR,
    setup_dropdown,
    setup_linspace_entries,
    setup_lock_checkbox,
)
from eemilib.util.constants import (
    IMPLEMENTED_EMISSION_DATA,
    IMPLEMENTED_POP,
    ImplementedEmissionData,
    ImplementedPop,
)
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
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
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from eemilib.loader.loader import Loader
from eemilib.model.model import Model
from eemilib.plotter.plotter import Plotter


class MainWindow(QMainWindow):
    """This object holds the GUI."""

    def __init__(self):
        """Create the GUI."""
        # EEmiLib attributes
        self.data_matrix = DataMatrix()
        self.model: Model
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
        self._setup_model()
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

        dropdown.currentIndexChanged.connect(self._setup_model)
        self.model_dropdown = dropdown

        self.fit_button = buttons[0]

    def setup_model_configuration(self) -> None:
        """Set the interface related to the model specific parameters."""
        # Model configuration group
        self.model_config_group = QGroupBox("Model configuration")
        self.model_config_layout = QVBoxLayout()

        self.model_table = QTableWidget(0, 7)
        self.model_table.setHorizontalHeaderLabels(
            list(PARAMETER_ATTR_TO_POS.keys())
        )
        self.model_table.setMaximumHeight(1000)
        self.model_table.setMinimumHeight(200)
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
        self.energy_first.setText(str(0.0))
        self.energy_last = last
        self.energy_last.setText(str(500.0))
        self.energy_points = points
        self.energy_points.setText(str(501))

        layout, first, last, points = setup_linspace_entries(
            "Angle [deg]", max_value=90.0
        )
        self.energy_angle_layout.addLayout(layout)
        self.angle_first = first
        self.angle_first.setText(str(0.0))
        self.angle_last = last
        self.angle_last.setText(str(60.0))
        self.angle_points = points
        self.angle_points.setText(str(4))

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

    def _dropdown_to_class(
        self, attribute: Literal["loader", "plotter", "model"]
    ) -> ABCMeta:
        """Convert dropdown entry to class."""
        dropdown_name = "_".join((attribute, "dropdown"))
        dropdown = getattr(self, dropdown_name, None)
        assert (
            dropdown is not None
        ), f" The dropdown attribute {dropdown_name} is not defined."

        module_names_to_paths = "_".join((attribute, "classes"))
        module_name_to_path = getattr(self, module_names_to_paths, None)
        assert module_name_to_path is not None, (
            f"The dictionary {module_names_to_paths}, linking every module"
            " name to its path, is not defined."
        )

        selected: str = dropdown.currentText()
        module_path: str = module_name_to_path[selected]
        module: ModuleType = importlib.import_module(module_path)
        my_class = getattr(module, selected)
        return my_class

    def load_data(self) -> None:
        """Load all the files set in GUI."""
        loader = self._dropdown_to_class("loader")()

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

    def _setup_model(self) -> None:
        """Instantiate model when it is selected in dropdown menu."""
        self.model = self._dropdown_to_class("model")()
        self._populate_parameters_table_constants()
        self.model_table.itemChanged.connect(
            self._update_parameter_value_from_table
        )

    def _populate_parameters_table_constants(self) -> None:
        """Print out the model parameters in dedicated table."""
        self._clear_parameters_table()

        for row, (name, param) in enumerate(self.model.parameters.items()):
            self.model_table.insertRow(row)

            self.model_table.setItem(row, 0, QTableWidgetItem(name))
            for attr in ("unit", "lower_bound", "upper_bound", "description"):
                col = PARAMETER_ATTR_TO_POS[attr]
                attr_value = getattr(param, attr, None)
                self.model_table.setItem(
                    row, col, QTableWidgetItem(str(attr_value))
                )
            col_lock = PARAMETER_ATTR_TO_POS["lock"]
            checkbox_widget = setup_lock_checkbox(param)
            self.model_table.setCellWidget(row, col_lock, checkbox_widget)

    def fit_model(self) -> None:
        """Perform the fit on the loaded data."""
        if not hasattr(self, "model") or not self.model:
            print("Please select a model before fitting.")
            return
        self.model.find_optimal_parameters(self.data_matrix)
        self._populate_parameters_table_values()

    def _populate_parameters_table_values(self) -> None:
        """Print out the values of the model parameters in dedicated table."""
        for row, param in enumerate(self.model.parameters.values()):
            for attr in ("value",):
                col = PARAMETER_ATTR_TO_POS[attr]
                attr_value = getattr(param, attr, None)
                self.model_table.setItem(
                    row, col, QTableWidgetItem(str(attr_value))
                )

        for i, param in enumerate(self.model.parameters.values()):
            self.model_table.setItem(i, 2, QTableWidgetItem(str(param.value)))

    def _update_parameter_value_from_table(
        self, item: QTableWidgetItem
    ) -> None:
        """Update :class:`.Parameter` value based on user input in table."""
        row, col = item.row(), item.column()
        updatable_attr = ("value", "lower_bound", "upper_bound")
        attr = PARAMETER_POS_TO_ATTR[col]
        if attr not in updatable_attr:
            print("This column cannot be updated.")
            return

        name = self.model_table.item(row, 0).text()
        parameter = self.model.parameters.get(name)

        if parameter:
            try:
                new_value = float(item.text())
                setattr(parameter, attr, new_value)

            except ValueError:
                print(f"Invalid value entered for {name}")
                item.setText(str(parameter.value))

    def plot_measured(self) -> None:
        """Plot the desired data, as imported."""
        plotter = self._dropdown_to_class("plotter")()

        success_pop, populations = self._get_populations_to_plot()
        success_data, emission_data_type = (
            self._get_emission_data_type_to_plot()
        )
        if not (success_pop and success_data):
            return

        self.axes = self.data_matrix.plot(
            plotter,
            population=populations,
            emission_data_type=emission_data_type,
            axes=self.axes,
        )

    def plot_model(self) -> None:
        """Plot the desired data, as modelled."""
        plotter = self._dropdown_to_class("plotter")()

        success_pop, populations = self._get_populations_to_plot()
        success_data, emission_data_type = (
            self._get_emission_data_type_to_plot()
        )
        if not (success_pop and success_data):
            return
        success_ene, energies = self._gen_linspace("energy")
        success_angle, angles = self._gen_linspace("angle")
        if not (success_ene and success_angle):
            return

        self.axes = self.model.plot(
            plotter,
            population=populations,
            emission_data_type=emission_data_type,
            energies=energies,
            angles=angles,
            axes=self.axes,
        )

    def _new_axes(self) -> None:
        """Remove the stored axes to plot on a new one."""
        self.axes = None

    def _clear_parameters_table(self) -> None:
        """Remove entries of the parameters table but not headers."""
        self.model_table.setRowCount(0)

    def _get_emission_data_type_to_plot(
        self,
    ) -> tuple[bool, ImplementedEmissionData]:
        """Read input to determine the emission data type to plot."""
        success = True
        emission_data_type = [
            IMPLEMENTED_EMISSION_DATA[i]
            for i, checked in enumerate(self.data_checkboxes)
            if checked.isChecked()
        ]
        if len(emission_data_type) == 0:
            print("Please provide a type of data to plot.")
            success = False
        return success, emission_data_type[0]

    def _get_populations_to_plot(self) -> tuple[bool, list[ImplementedPop]]:
        """Read input to determine the populations to plot."""
        success = True
        populations = [
            IMPLEMENTED_POP[i]
            for i, checked in enumerate(self.population_checkboxes)
            if checked.isChecked()
        ]
        if len(populations) == 0:
            print("Please provide at least one population to plot.")
            success = False
        return success, populations

    def _gen_linspace(
        self, variable: Literal["energy", "angle"]
    ) -> tuple[bool, np.ndarray]:
        """Take the desired input, check validity, create array of values."""
        success = True
        linspace_args = []
        for box in ("first", "last", "points"):
            line_name = "_".join((variable, box))
            qline_edit = getattr(self, line_name, None)
            if qline_edit is None:
                print(f"The attribute {line_name} is not defined.")
                success = False
                continue

            assert isinstance(qline_edit, QLineEdit)
            value = qline_edit.displayText()
            if not value:
                print(f"You must give a value in {line_name}.")
                success = False
                continue
            linspace_args.append(value)

        if not success:
            return success, np.linspace(0, 10, 11)

        return success, np.linspace(
            float(linspace_args[0]),
            float(linspace_args[1]),
            int(linspace_args[2]),
        )


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    print(f"{IMPLEMENTED_POP = }")
    main()
