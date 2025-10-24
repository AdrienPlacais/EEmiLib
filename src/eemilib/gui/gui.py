#!/usr/bin/env python3
"""Define a GUI.

.. todo::
    Export/Import settings

.. todo::
    logging module

.. todo::
    Add measurables at bottom

"""
import importlib
import logging
import sys
from abc import ABCMeta
from types import ModuleType
from typing import Literal

import numpy as np
from eemilib.core.model_config import ModelConfig
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.gui.file_selection import file_selection_matrix
from eemilib.gui.helper import (
    PARAMETER_ATTR_TO_POS,
    PARAMETER_POS_TO_ATTR,
    format_number,
    set_dropdown_value,
    set_help_button_action,
    setup_dropdown,
    setup_linspace_entries,
    setup_lock_checkbox,
    to_plot_checkboxes,
)
from eemilib.gui.model_selection import model_configuration
from eemilib.loader.loader import Loader
from eemilib.model.model import Model
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import (
    IMPLEMENTED_EMISSION_DATA,
    IMPLEMENTED_POP,
    ImplementedEmissionData,
    ImplementedPop,
)
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QGroupBox,
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

DROPDOWNS = ("Loader", "Model", "Plotter")
Dropdowns = Literal["Loader", "Model", "Plotter"]


class MainWindow(QMainWindow):
    """This object holds the GUI."""

    #: If selecting Model in dropdown should automatically fill the appopriate
    #: data to plot checkbox
    autofill_data_to_plot = True
    #: If selecting Model in dropdown should automatically fill the appopriate
    #: emission data checkbox
    autofill_nature_to_plot = True
    #: If loading data should automatically fill the energy/angle ranges with
    #: their maximum values
    autofill_plotting_ranges = True

    def __init__(
        self,
        default_model: str = "Vaughan",
        default_loader: str = "PandasLoader",
        default_plotter: str = "PandasPlotter",
    ) -> None:
        """Create the GUI."""
        self._defaults: dict[Dropdowns, str] = {
            "Model": default_model,
            "Loader": default_loader,
            "Plotter": default_plotter,
        }
        # EEmiLib attributes
        self.data_matrix = DataMatrix()
        self.loader: Loader
        self.model: Model
        self.axes = None

        super().__init__()
        self.setWindowTitle("EEmiLib")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        self.file_lists = self.setup_file_selection_matrix()

        self.dropdowns: dict[str, QComboBox] = {}

        self.loader_classes: dict[str, str]
        self.loader_help_button: QPushButton
        self.setup_loader_dropdown()

        self.model_classes: dict[str, str]
        self.model_help_button: QPushButton
        self.setup_model_dropdown()

        self.model_table = self.setup_model_configuration()
        self.energy_angle_group: QGroupBox
        self.energy_angle_layout: QVBoxLayout
        self.last_energy_widget: QLineEdit
        self.last_theta_widget: QLineEdit
        self.n_theta_widget: QLineEdit
        self.setup_energy_angle_inputs()

        self.plotter_classes: dict[str, str]
        self.plot_measured_button: QPushButton
        self.plot_model_button: QPushButton
        self.data_checkboxes: list[QRadioButton]
        self.population_checkboxes: list[QCheckBox]
        self.setup_plotter_dropdowns()

        # Call the methods called by the model_dropdown index change
        self._set_default_dropdown()

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
        model = self._dropdown_to_class("Model")()
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
    def setup_loader_dropdown(self) -> None:
        """Set the :class:`.Loader` related interface."""
        classes, layout, dropdown, buttons = setup_dropdown(
            module_name="eemilib.loader",
            base_class=Loader,
            buttons_args={
                "Help": lambda _: logging.info("Help not set."),
                "Load data": self.load_data,
            },
        )
        self.loader_classes = classes
        dropdown.currentIndexChanged.connect(self._setup_loader)
        dropdown.setCurrentText
        self.dropdowns["Loader"] = dropdown
        self.loader_help_button = buttons[0]
        self.main_layout.addLayout(layout)
        return

    def _setup_loader(self) -> None:
        """Setup new loader whenever the dropdown menu is changed."""
        self.loader = self._dropdown_to_class("Loader")()
        set_help_button_action(self.loader_help_button, self.loader)

    def load_data(self) -> None:
        """Load all the files set in GUI."""
        for i in range(len(IMPLEMENTED_POP)):
            for j in range(len(IMPLEMENTED_EMISSION_DATA)):
                file_list_widget = self.file_lists[i][j]
                if file_list_widget is not None:
                    file_names = [
                        file_list_widget.item(k).text()
                        for k in range(file_list_widget.count())
                    ]
                    self.data_matrix.set_files(file_names, row=i, col=j)

        try:
            self.data_matrix.load_data(self.loader)
        except Exception as e:
            logging.error(
                "An error was raised during the loading of the data file. "
                "Check that the format of the files is consistent with what "
                f"is expected by the data loader. Error message:\n{e}"
            )

        if self.autofill_plotting_ranges:
            self._fill_plotting_ranges()

    # =========================================================================
    # Model
    # =========================================================================
    def setup_model_dropdown(self) -> None:
        """Set the :class:`.Model` related interface.

        Assign the ``model_classes`` and ``model_dropdown``.

        """
        classes, layout, dropdown, buttons = setup_dropdown(
            module_name="eemilib.model",
            base_class=Model,
            buttons_args={
                "Help": lambda _: logging.info("Help not set"),
                "Fit!": self.fit_model,
            },
        )
        self.model_classes = classes
        self.dropdowns["Model"] = dropdown
        dropdown.currentIndexChanged.connect(self._setup_model)
        dropdown.currentIndexChanged.connect(
            self._deactivate_unnecessary_file_widgets
        )
        dropdown.currentIndexChanged.connect(
            self._fill_plot_nature_and_population
        )

        self.model_help_button = buttons[0]
        self.main_layout.addLayout(layout)
        return

    def setup_model_configuration(self) -> QTableWidget:
        """Set the interface related to the model specific parameters."""
        group, model_table = model_configuration()
        self.main_layout.addWidget(group)

        return model_table

    def _setup_model(self) -> None:
        """Instantiate :class:`.Model` when it is selected in dropdown menu."""
        self.model = self._dropdown_to_class("Model")()

        set_help_button_action(self.model_help_button, self.model)

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
            for attr in ("unit", "lower_bound", "upper_bound"):
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
            return

        name = self.model_table.item(row, 0).text()
        parameter = self.model.parameters.get(name)

        if parameter:
            try:
                new_value = float(item.text())
                setattr(parameter, attr, new_value)

            except ValueError:
                logging.warning(f"Invalid value entered for {name}")
                item.setText(str(parameter.value))

    def fit_model(self) -> None:
        """Perform the fit on the loaded data."""
        if not hasattr(self, "model") or not self.model:
            logging.info("Please select a model before fitting.")
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
            self.model_table.setItem(
                i, 2, QTableWidgetItem(format_number(param.value))
            )

    def _fill_plot_nature_and_population(self) -> None:
        """Check emission data type and population.

        When model is updated, check the ``Data to plot`` and ``Population to
        plot`` checkboxes in the ``Plot`` section that are concerned by current
        model.

        """
        try:
            model = self.model
        except AttributeError as e:
            logging.debug(
                "Model is not set, cannot fill plot nature or population "
                f"checkboxes.\n{e}"
            )
            return

        data_type_to_plot = model.emission_data_types[0]
        if self.autofill_data_to_plot:
            index = IMPLEMENTED_EMISSION_DATA.index(data_type_to_plot)
            self.data_checkboxes[index].setChecked(True)

        if self.autofill_nature_to_plot:
            pop_to_plot = set(
                model.model_config.mandatory_populations(
                    emission_data_type=data_type_to_plot
                )
                + list(model.populations)
            )
            for button, population in zip(
                self.population_checkboxes, IMPLEMENTED_POP, strict=True
            ):
                if population in pop_to_plot:
                    button.setChecked(True)
                    continue
                button.setChecked(False)

    # =========================================================================
    # Plot
    # =========================================================================
    def setup_energy_angle_inputs(self) -> None:
        """Set the energy and angle inputs for the model plot."""
        self.energy_angle_group = QGroupBox(
            "Energy and angle range (used for model plot)"
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
            if qty == ("energy"):
                self.last_energy_widget = last
            elif qty == ("angle"):
                self.last_theta_widget = last
                self.n_theta_widget = points

            for attr, attr_name in zip(
                (first, last, points), ("first", "last", "points")
            ):
                setattr(self, "_".join((qty, attr_name)), attr)

        self.energy_angle_group.setLayout(self.energy_angle_layout)
        self.main_layout.addWidget(self.energy_angle_group)

    def setup_plotter_dropdowns(self) -> None:
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
        self.dropdowns["Plotter"] = dropdown
        self.plot_measured_button = buttons[0]
        self.plot_model_button = buttons[1]

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

    def plot_measured(self) -> None:
        """Plot the desired data, as imported."""
        plotter = self._dropdown_to_class("Plotter")(gui=True)

        success_pop, populations = self._get_populations_to_plot()
        if not success_pop:
            return
        success_data, emission_data_type = (
            self._get_emission_data_type_to_plot()
        )
        if not success_data:
            return

        self.axes = self.data_matrix.plot(
            plotter,
            population=populations,
            emission_data_type=emission_data_type,
            axes=self.axes,
        )

    def plot_model(self) -> None:
        """Plot the desired data, as modelled."""
        plotter = self._dropdown_to_class("Plotter")(gui=True)

        success_pop, populations = self._get_populations_to_plot()
        if not success_pop:
            return
        success_data, emission_data_type = (
            self._get_emission_data_type_to_plot()
        )
        if not success_data:
            return
        success_ene, energies = self._gen_linspace("energy")
        if not success_ene:
            return
        success_angle, angles = self._gen_linspace("angle")
        if not success_angle:
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
    ) -> tuple[bool, ImplementedEmissionData | None]:
        """Read input to determine the emission data type to plot."""
        emission_data_type = [
            IMPLEMENTED_EMISSION_DATA[i]
            for i, checked in enumerate(self.data_checkboxes)
            if checked.isChecked()
        ]
        if len(emission_data_type) == 0:
            logging.error("Please provide a type of data to plot.")
            return False, None
        return True, emission_data_type[0]

    def _get_populations_to_plot(self) -> tuple[bool, list[ImplementedPop]]:
        """Read input to determine the populations to plot."""
        success = True
        populations = [
            IMPLEMENTED_POP[i]
            for i, checked in enumerate(self.population_checkboxes)
            if checked.isChecked()
        ]
        if len(populations) == 0:
            logging.error("Please provide at least one population to plot.")
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
                logging.error(f"The attribute {line_name} is not defined.")
                success = False
                continue

            assert isinstance(qline_edit, QLineEdit)
            value = qline_edit.displayText()
            if not value:
                logging.error(f"You must give a value in {line_name}.")
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

    def _fill_plotting_ranges(self) -> None:
        """Fill energy and angle plotting ranges to match data files values.

        This method is called when the button ``Load`` is pressed.

        """
        try:
            model = self.model
        except AttributeError as e:
            logging.debug(
                "Model is not set, cannot fill energy/angle plotting ranges. "
                f"\n{e}"
            )
            return
        try:
            data_matrix = self.data_matrix
        except AttributeError as e:
            logging.debug(
                "DataMatrix is not set, cannot fill energy/angle plotting "
                f"ranges.\n{e}"
            )
            return

        if not self.autofill_plotting_ranges:
            return
        data_type_to_plot = model.emission_data_types[0]

        data = data_matrix.get_data(emission_data_type=data_type_to_plot)
        if len(data) == 0:
            logging.debug(
                "No valid data, cannot fill energy/angle plotting ranges."
            )
            return
        data_subset = data[0]

        e_maxi = max(data_subset.energies)
        if e_maxi is not None and not np.isnan(e_maxi):
            logging.debug(f"Setting {e_maxi = }")
            self.last_energy_widget.setText(str(e_maxi))

        theta_maxi = max(data_subset.angles)
        n_theta = len(data_subset.angles)
        if theta_maxi is not None and not np.isnan(theta_maxi):
            logging.debug(f"Setting {theta_maxi = }")
            self.last_theta_widget.setText(str(theta_maxi))
            logging.debug(f"Setting {n_theta = }")
            self.n_theta_widget.setText(str(n_theta))

    # =========================================================================
    # Helper
    # =========================================================================
    def _dropdown_to_class(self, name: Dropdowns) -> ABCMeta:
        """Convert dropdown entry to class."""
        dropdown = self.dropdowns.get(name, None)
        assert dropdown is not None, f" The dropdown {name} is not defined."

        module_names_to_paths = "_".join((name.lower(), "classes"))
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

    # =========================================================================
    # Misc
    # =========================================================================
    def _set_default_dropdown(self) -> None:
        """Set dropdowns to their default values.

        We call this method at the end of the GUI initialization rather than
        at the creation of the dropdowns to ensure that every side effects
        is executed.

        """
        for key in DROPDOWNS:
            set_dropdown_value(self.dropdowns[key], self._defaults[key])


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
