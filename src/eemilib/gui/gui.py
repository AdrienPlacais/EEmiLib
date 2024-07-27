#!/usr/bin/env python3
"""Define a GUI.

.. todo::
    Export/Import settings

.. todo::
    logging module

.. todo::
    Add measurables at bottom

.. todo::
    Help buttons

"""
import importlib
import sys
from abc import ABCMeta
from types import ModuleType
from typing import Literal

import numpy as np
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.gui.file_selection import file_selection_matrix
from eemilib.gui.helper import (
    PARAMETER_ATTR_TO_POS,
    PARAMETER_POS_TO_ATTR,
    setup_dropdown,
    setup_linspace_entries,
    setup_lock_checkbox,
    to_plot_checkboxes,
)
from eemilib.gui.model_selection import model_configuration
from eemilib.model.model_config import ModelConfig
from eemilib.util.constants import (
    IMPLEMENTED_EMISSION_DATA,
    IMPLEMENTED_POP,
    ImplementedEmissionData,
    ImplementedPop,
)
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QLineEdit,
    QListWidget,
    QMainWindow,
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

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        self.file_lists = self.setup_file_selection_matrix()

        self.loader_classes, self.loader_dropdown = (
            self.setup_loader_dropdown()
        )

        self.model_classes: dict[str, str]
        self.model_dropdown: QComboBox
        self.setup_model_dropdown()

        self.model_table = self.setup_model_configuration()
        self.setup_energy_angle_inputs()
        self.setup_plotter_dropdown()

        # Call the methods called by the model_dropdown index change
        self._setup_model()
        self._deactivate_unnecessary_file_widgets()

    # =========================================================================
    # File selection
    # =========================================================================
    def setup_file_selection_matrix(self) -> list[list[None | QListWidget]]:
        """Create the 4 * 3 matrix to select the files to load."""
        file_matrix_group, file_lists = file_selection_matrix(self)
        self.main_layout.addWidget(file_matrix_group)
        return file_lists

    def _deactivate_unnecessary_file_widgets(self) -> None:
        """Grey out the files not needed by current model."""
        model = self._dropdown_to_class("model")()
        if not isinstance(model, Model):
            return
        config: ModelConfig = model.model_config

        # Get required file types for each population type
        required_files = {
            "Emission Yield": config.emission_yield_files,
            "Emission Energy": config.emission_energy_files,
            "Emission Angle": config.emission_angle_files,
        }

        for i, pop in enumerate(IMPLEMENTED_POP):
            for j, data_type in enumerate(IMPLEMENTED_EMISSION_DATA):
                is_required = pop in required_files.get(data_type, [])
                self._set_list_widget_state(self.file_lists[i][j], is_required)

    # =========================================================================
    # Load files
    # =========================================================================
    def setup_loader_dropdown(self) -> tuple[
        dict[str, str],
        QComboBox,
    ]:
        """Set the :class:`.Loader` related interface."""
        classes, layout, dropdown, _ = setup_dropdown(
            module_name="eemilib.loader",
            base_class=Loader,
            buttons_args={"Load data": self.load_data},
        )
        # self.load_button = buttons[0]
        self.main_layout.addLayout(layout)
        return classes, dropdown

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

    # =========================================================================
    # Model
    # =========================================================================
    def setup_model_dropdown(self) -> None:
        """Set the :class:`.Model` related interface.

        Assign the :attr:`model_classes` and :attr:`model_dropdown`.

        """
        classes, layout, dropdown, _ = setup_dropdown(
            module_name="eemilib.model",
            base_class=Model,
            buttons_args={"Fit!": self.fit_model},
        )
        self.model_classes = classes
        self.model_dropdown = dropdown
        dropdown.currentIndexChanged.connect(self._setup_model)
        dropdown.currentIndexChanged.connect(
            self._deactivate_unnecessary_file_widgets
        )
        # self.fit_button = buttons[0]
        self.main_layout.addLayout(layout)
        return

    def setup_model_configuration(self) -> QTableWidget:
        """Set the interface related to the model specific parameters."""
        group, model_table = model_configuration()
        self.main_layout.addWidget(group)

        return model_table

    def _setup_model(self) -> None:
        """Instantiate :class:`.Model` when it is selected in dropdown menu."""
        self.model = self._dropdown_to_class("model")()
        self._populate_parameters_table_constants()
        self.model_table.itemChanged.connect(
            self._update_parameter_value_from_table
        )

    def _populate_parameters_table_constants(self) -> None:
        """Print out the model parameters in dedicated table."""
        self.model_table.setRowCount(0)

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

    # =========================================================================
    # Plot
    # =========================================================================
    def setup_energy_angle_inputs(self) -> None:
        """Set the energy and angle inputs for the model plot."""
        self.energy_angle_group = QGroupBox(
            "PEs energy and angle range (model plot)"
        )
        self.energy_angle_layout = QVBoxLayout()

        quantities = ("energy", "angle")
        labels = ("Energy [eV]", "Angle [deg]")
        initial_values = ((0.0, 500.0, 501), (0.0, 60.0, 4))
        max_values = (None, 90.0)
        for qty, label, initial, max_val in zip(
            quantities, labels, initial_values, max_values
        ):
            layout, first, last, points = setup_linspace_entries(
                label,
                initial_values=initial,
                max_value=max_val,
            )
            self.energy_angle_layout.addLayout(layout)

            for attr, attr_name in zip(
                (first, last, points), ("first", "last", "points")
            ):
                setattr(self, "_".join((qty, attr_name)), attr)

        self.energy_angle_group.setLayout(self.energy_angle_layout)
        self.main_layout.addWidget(self.energy_angle_group)

    def _set_up_data_to_plot_checkboxes(self) -> None:
        """Add checkbox to select which data should be plotted."""
        layout, checkboxes = to_plot_checkboxes(
            "Data to plot:",
            IMPLEMENTED_EMISSION_DATA,
            several_can_be_checked=False,
        )
        self.main_layout.addLayout(layout)
        self.data_checkboxes = checkboxes

    def _set_up_population_to_plot_checkboxes(self) -> None:
        """Add checkbox to select which population should be plotted."""
        layout, checkboxes = to_plot_checkboxes(
            "Population to plot:",
            IMPLEMENTED_POP,
            several_can_be_checked=True,
        )
        self.main_layout.addLayout(layout)
        self.population_checkboxes = checkboxes

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
                "New figure": lambda _: setattr(self, "axes", None),
            },
        )
        self.plotter_classes = classes
        self.main_layout.addLayout(layout)
        self.plotter_dropdown = dropdown
        self.plot_measured_button = buttons[0]
        self.plot_model_button = buttons[1]

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

    # =========================================================================
    # Helper
    # =========================================================================
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

    def _set_list_widget_state(
        self, widget: QListWidget, enabled: bool
    ) -> None:
        """Enable or disable a QListWidget based on ``enabled``."""
        if enabled:
            widget.setStyleSheet("background-color: white;")
            widget.setEnabled(True)
            return
        widget.setStyleSheet("background-color: lightgray;")
        widget.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    print(f"{IMPLEMENTED_POP = }")
    main()
