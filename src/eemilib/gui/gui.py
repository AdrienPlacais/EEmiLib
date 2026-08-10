#!/usr/bin/env python3
"""Define a GUI.

.. todo::
    Export/Import settings

.. todo::
    Add description at and of parameters
    Dynamic boxes for Parameters?

.. todo::
    Allow ``None`` for energies, so that measurements energies are picked up.
    Ideas:

    - Checkbox "Use energies from measurements".
    - Clicking it greys out the ``energies`` linspace definition.
    - This checkbox is greyed out/unclickable if no data was plotted,
      *i.e.* if current `Axes` contains no `Line2D`.

.. todo::
   Switch to ``@property`` for the dropdowns values?

.. todo::
   Integrate the `dropdown.currentIndexChanged` logic to the `setup_dropdown`
   helper?

.. todo::
   Make plot tab draggable so we can have model values and plot side by side.

.. todo::
   Make model plot update on parameter value change (``Sync`` checkbox).

"""

import importlib
import logging
import sys
from abc import ABCMeta
from collections.abc import Callable
from types import ModuleType
from typing import Literal, cast

import numpy as np
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHeaderView,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from eemilib.core.model_config import ModelConfig
from eemilib.emission_data import DataMatrix
from eemilib.emission_data.emission_data import EmissionData
from eemilib.gui.file_selection import file_selection_matrix
from eemilib.gui.helper import (
    PARAMETER_ATTR_TO_POS,
    PARAMETER_POS_TO_ATTR,
    set_dropdown_value,
    set_help_button_action,
    setup_dropdown,
    setup_linspace_entries,
    setup_lock_checkbox,
    to_plot_checkboxes,
)
from eemilib.gui.loader_selection import LoaderSettingsDialog
from eemilib.gui.model_selection import (
    ModelImplementationsDialog,
    model_configuration,
)
from eemilib.gui.plot_canvas import TabbedPlotArea
from eemilib.gui.styles import (
    TITLE_STYLE,
    format_number,
    math_text_label_from_key,
)
from eemilib.loader.loader import Loader
from eemilib.model.model import Model
from eemilib.plotter.plotter import Plotter
from eemilib.util.constants import (
    IMPLEMENTED_EMISSION_DATA,
    IMPLEMENTED_POP,
    ImplementedEmissionData,
    ImplementedPop,
)
from eemilib.util.helper import flatten

DROPDOWNS = ("Loader", "Model", "Plotter")
Dropdowns = Literal["Loader", "Model", "Plotter"]


class MainWindow(QMainWindow):
    """GUI."""

    #: Whether selecting Model in dropdown should automatically fill the
    #: appropriate data to plot checkbox.
    autofill_data_to_plot = True
    #: Whether selecting Model in dropdown should automatically fill the
    #: appropriate emission data checkbox.
    autofill_nature_to_plot = True
    #: Whether loading data should automatically fill the energy/angle ranges
    #: with their maximum values.
    autofill_plotting_ranges = True

    def __init__(
        self,
        default_model: str = "Vaughan",
        default_loader: str = "PandasLoader",
        default_plotter: str = "GUIPandasPlotter",
    ) -> None:
        """Create the GUI."""
        self._defaults: dict[Dropdowns, str] = {
            "Model": default_model,
            "Loader": default_loader,
            "Plotter": default_plotter,
        }
        # EEmiLib attributes
        self.data_matrix = DataMatrix()
        self.model: Model
        self.loader: Loader
        self.plotter: Plotter

        super().__init__()
        self.setWindowTitle("EEmiLib")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self._data_model_tab = QWidget()
        self._data_model_layout = QVBoxLayout(self._data_model_tab)
        self.tab_widget.addTab(self._data_model_tab, "Data && Model")

        self._plot_tab = QWidget()
        self._plot_layout = QVBoxLayout(self._plot_tab)
        self.tab_widget.addTab(self._plot_tab, "Plot")

        # Tab 1: Data & Model
        self.file_lists = self._setup_file_selection_matrix()

        self.dropdowns: dict[str, QComboBox] = {}

        self.loader_classes: dict[str, str]
        self.loader_help_button: QPushButton
        self._setup_loader_dropdown()

        self.model_table = self._setup_model_configuration()
        self.model_classes: dict[str, str]
        self.model_class: ABCMeta
        self.model_help_button: QPushButton
        self._setup_model_dropdown()

        self.evaluations: dict[str, float]
        self.evaluators_group: QGroupBox
        self.evaluators_table: QTableWidget
        self.force_reevaluation_button: QPushButton
        self._setup_model_evaluation()

        # Tab 2: Plot
        self.plot_area = TabbedPlotArea()
        self._plot_layout.addWidget(self.plot_area)

        self.energy_angle_group: QGroupBox
        self.energy_angle_layout: QVBoxLayout
        self.last_energy_widget: QLineEdit
        self.last_theta_widget: QLineEdit
        self.n_theta_widget: QLineEdit
        self._setup_energy_angle_inputs()

        self.plotter_classes: dict[str, str]
        self.plot_measured_button: QPushButton
        self.plot_model_button: QPushButton
        self.data_checkboxes: list[QRadioButton]
        self.population_checkboxes: list[QCheckBox]
        self._setup_plotter_dropdowns()

        # Call the methods called by the model_dropdown index change
        self._set_default_dropdown()

    # =========================================================================
    # Tab 1 - File selection
    # =========================================================================
    def _setup_file_selection_matrix(self) -> list[list[None | QListWidget]]:
        """Create the 4 * 3 matrix to select the files to load."""
        file_matrix_group, file_lists = file_selection_matrix(self)
        self._data_model_layout.addWidget(file_matrix_group)
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
    # Tab 1 - Load files
    # =========================================================================
    def _setup_loader_dropdown(self) -> None:
        """Set the :class:`.Loader` related interface."""
        settings_label, settings_action = self._setup_loader_settings_dialog()
        setup = setup_dropdown(
            module_name="eemilib.loader",
            base_class=Loader,
            buttons_args={
                "Help": lambda _: logging.info("Help not set."),
                "Load data": self.load_data,
                settings_label: settings_action,
            },
        )
        self.loader_classes = setup.classes
        setup.dropdown.currentIndexChanged.connect(self._setup_loader)
        _ = setup.dropdown.setCurrentText
        self.dropdowns["Loader"] = setup.dropdown
        self.loader_help_button = setup.buttons[0]
        self._data_model_layout.addLayout(setup.layout)

    def _setup_loader(self) -> None:
        """Set up new loader whenever the dropdown menu is changed."""
        self.loader = self._dropdown_to_class("Loader")()
        set_help_button_action(self.loader_help_button, self.loader)

    def _setup_loader_settings_dialog(self) -> tuple[str, Callable]:
        """Give arguments to setup the loader setttings button."""
        settings_label = "⚙️ Settings"

        def settings_action() -> int:
            code = LoaderSettingsDialog(self, self.loader).exec()
            return code

        return settings_label, settings_action

    def load_data(self) -> None:
        """Load all the files set in GUI."""
        for i, pop in enumerate(IMPLEMENTED_POP):
            for j, data in enumerate(IMPLEMENTED_EMISSION_DATA):
                file_list_widget = self.file_lists[i][j]
                if file_list_widget is not None:
                    file_names = [
                        file_list_widget.item(k).text()
                        for k in range(file_list_widget.count())
                    ]
                    self.data_matrix.set_files(
                        file_names, data_type=data, population=pop
                    )

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
    # Tab 1 - Model
    # =========================================================================
    def _setup_model_dropdown(self) -> None:
        """Set the :class:`.Model` related interface.

        Assign the ``model_classes`` and ``model_dropdown``.

        """
        settings_label, settings_action = (
            self._setup_model_implementations_dialog()
        )
        setup = setup_dropdown(
            module_name="eemilib.model",
            base_class=Model,
            buttons_args={
                "Help": lambda _: logging.info("Help not set"),
                "Fit!": (self.fit_model, self._fill_evaluations_display),
                settings_label: settings_action,
            },
        )
        self.model_classes = setup.classes
        self.dropdowns["Model"] = setup.dropdown
        setup.dropdown.currentIndexChanged.connect(self._setup_model)
        setup.dropdown.currentIndexChanged.connect(
            self._deactivate_unnecessary_file_widgets
        )
        setup.dropdown.currentIndexChanged.connect(
            self._fill_plot_nature_and_population
        )
        setup.dropdown.currentIndexChanged.connect(
            self._populate_parameters_table_values
        )

        self.model_help_button = setup.buttons[0]
        self._data_model_layout.addLayout(setup.layout)

    def _setup_model_implementations_dialog(self) -> tuple[str, Callable]:
        """Give arguments to setup the model setttings button."""
        settings_label = "⚙️ Implementations"

        def settings_action() -> int:
            code = ModelImplementationsDialog(self, self.model).exec()
            self._populate_parameters_table_values()
            self._populate_parameters_table_constants()
            return code

        return settings_label, settings_action

    def _setup_model_configuration(self) -> QTableWidget:
        """Set the interface related to the model specific parameters."""
        group, model_table = model_configuration()
        self._data_model_layout.addWidget(group)
        return model_table

    def _setup_model(self) -> None:
        """Instantiate :class:`.Model` when it is selected in dropdown menu."""
        self.model_class = self._dropdown_to_class("Model")
        self.model = self.model_class()

        set_help_button_action(self.model_help_button, self.model)

        self._populate_parameters_table_constants()
        self.model_table.itemChanged.connect(
            self._update_parameter_value_from_table
        )

    def _populate_parameters_table_constants(self) -> None:
        """Print out the model parameters in dedicated table."""
        self.model_table.setRowCount(0)
        for row, param in enumerate(self.model.parameters.values()):
            self.model_table.insertRow(row)

            label, unit = math_text_label_from_key(param.name)
            label.setObjectName(param.name)  # anchors the name to the widget
            self.model_table.setCellWidget(row, 0, label)
            self.model_table.setCellWidget(row, 1, unit)
            description, _ = math_text_label_from_key(param.description)
            self.model_table.setCellWidget(
                row, PARAMETER_ATTR_TO_POS["description"], description
            )

            for attr in ("lower_bound", "upper_bound"):
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

        name = self.model_table.cellWidget(row, 0).objectName()
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

    # =========================================================================
    # Tab 1 - Model evaluation
    # =========================================================================
    def _setup_model_evaluation(self) -> None:
        """Set up display of model evaluators."""
        self.evaluators_group = QGroupBox("Model evaluations")
        self.evaluators_group.setStyleSheet(TITLE_STYLE)
        self.evaluators_layout = QVBoxLayout()

        self.evaluators_table = self._create_evaluators_table()
        self.evaluators_layout.addWidget(self.evaluators_table)

        self.force_reevaluation_button = self._set_reevaluation_button()
        self.evaluators_layout.addWidget(self.force_reevaluation_button)

        self.evaluators_group.setLayout(self.evaluators_layout)
        self._data_model_layout.addWidget(self.evaluators_group)

    def _create_evaluators_table(self) -> QTableWidget:
        """Create the two-column table that displays evaluation results."""
        table = QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(["Metric", "Unit", "Value"])

        for i in range(3):
            table.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeToContents
            )
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setAlternatingRowColors(True)
        return table

    def _set_reevaluation_button(self) -> QPushButton:
        """Create and return the 'Re-evaluate' button."""
        button = QPushButton("Re-evaluate")
        button.clicked.connect(self._fill_evaluations_display)
        return button

    def _fill_evaluations_display(self) -> None:
        """Fill the evaluations display with the last model."""
        if not hasattr(self, "model") or not self.model:
            logging.info("Please select a model before evaluating.")
            return
        if not hasattr(self, "data_matrix") or not self.data_matrix:
            logging.info("Please load data before evaluating.")
            return
        self._evaluate_model()
        self._populate_evaluators_table()

    def _evaluate_model(self) -> None:
        """Evaluate model and save resulting dict in ``self.evaluations``."""
        self.evaluations = self.model.evaluate(self.data_matrix)

    def _populate_evaluators_table(self) -> None:
        """Write the contents of ``self.evaluations`` into the table."""
        self.evaluators_table.setRowCount(0)
        for row, (key, value) in enumerate(self.evaluations.items()):
            self.evaluators_table.insertRow(row)

            label, unit = math_text_label_from_key(key)
            self.evaluators_table.setCellWidget(row, 0, label)
            self.evaluators_table.setCellWidget(row, 1, unit)

            self.evaluators_table.setItem(
                row, 2, QTableWidgetItem(format_number(value))
            )

    # =========================================================================
    # Tab 2 - Plot
    # =========================================================================
    def _fill_plot_nature_and_population(self) -> None:
        """Check emission data type and population.

        When model is updated, check the ``Data to plot`` and ``Population to
        plot`` checkboxes in the ``Plot`` tab that are concerned by current
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

        data_type_to_plot = model.data_types[0]
        if self.autofill_data_to_plot:
            index = IMPLEMENTED_EMISSION_DATA.index(data_type_to_plot)
            self.data_checkboxes[index].setChecked(True)

        if self.autofill_nature_to_plot:
            pop_to_plot = set(
                model.model_config.mandatory_populations(
                    data_type=data_type_to_plot
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

    def _setup_energy_angle_inputs(self) -> None:
        """Set the energy and angle inputs for the model plot."""
        self.energy_angle_group = QGroupBox("Plot configuration")
        self.energy_angle_group.setStyleSheet(TITLE_STYLE)
        self.energy_angle_layout = QVBoxLayout()
        quantities = ("energy", "angle")
        labels = ("Energy [eV]", "Angle [deg]")
        initial_values = ((0.0, 500.0, 501), (0.0, 60.0, 4))
        max_values = (None, 90.0)
        for qty, label, initial, max_val in zip(
            quantities, labels, initial_values, max_values
        ):
            setup = setup_linspace_entries(
                label, initial_values=initial, max_value=max_val
            )
            self.energy_angle_layout.addLayout(setup.layout)
            if qty == ("energy"):
                self.last_energy_widget = setup.last
            elif qty == ("angle"):
                self.last_theta_widget = setup.last
                self.n_theta_widget = setup.n_points
            for attr, attr_name in zip(
                (setup.first, setup.last, setup.n_points),
                ("first", "last", "points"),
            ):
                setattr(self, f"{qty}_{attr_name}", attr)

        self.energy_angle_group.setLayout(self.energy_angle_layout)
        self._plot_layout.addWidget(self.energy_angle_group)

    def _setup_plotter_dropdowns(self) -> None:
        """Set the :class:`.Plotter` related interface."""
        self._set_up_data_to_plot_checkboxes()
        self._set_up_population_to_plot_checkboxes()

        setup = setup_dropdown(
            module_name="eemilib.plotter",
            base_class=Plotter,
            buttons_args={
                "Plot file": self.plot_measured,
                "Plot modelled data": self.plot_model,
                "Clear figure": lambda _: self.plot_area.clear(),
            },
        )
        self.plotter_classes = setup.classes
        setup.dropdown.currentIndexChanged.connect(self._setup_plotter)
        self.dropdowns["Plotter"] = setup.dropdown
        self.plot_measured_button = setup.buttons[0]
        self.plot_model_button = setup.buttons[1]
        self._plot_layout.addLayout(setup.layout)

    def _setup_plotter(self) -> None:
        """Set up new plotter when the dropdown menu is changed."""
        self.plotter = self._dropdown_to_class("Plotter")()

    def _set_up_data_to_plot_checkboxes(self) -> None:
        """Add checkbox to select which data should be plotted."""
        layout, checkboxes = to_plot_checkboxes(
            "Data to plot:",
            IMPLEMENTED_EMISSION_DATA,
            several_can_be_checked=False,
        )
        self._plot_layout.addLayout(layout)
        self.data_checkboxes = checkboxes

    def _set_up_population_to_plot_checkboxes(self) -> None:
        """Add checkbox to select which population should be plotted."""
        layout, checkboxes = to_plot_checkboxes(
            "Population to plot:", IMPLEMENTED_POP, several_can_be_checked=True
        )
        self._plot_layout.addLayout(layout)
        self.population_checkboxes = checkboxes

    def plot_measured(self) -> None:
        """Plot the desired data, as imported."""
        success_pop, populations = self._get_populations_to_plot()
        if not success_pop:
            return
        cast(list[ImplementedPop], populations)
        success_data, data_type = self._get_data_type_to_plot()
        if not success_data:
            return
        cast(ImplementedEmissionData, data_type)

        group_by_pe = data_type == "Emission Energy"
        if group_by_pe:
            axes_by_pe = {
                e_pe: self.plot_area.axes_for(e_pe)
                for e_pe in self._known_impact_energies()
            }
            self.data_matrix.plot(
                self.plotter,
                population=populations,
                data_type=data_type,
                axes=axes_by_pe,
                group_by_pe=True,
            )
            self.plot_area.refresh()
        else:
            axes = self.plot_area.axes_for(None)
            self.data_matrix.plot(
                self.plotter,
                population=populations,
                data_type=data_type,
                axes=axes,
            )
            self.plot_area.refresh(None)

    def plot_model(self) -> None:
        """Plot the desired data, as modelled."""
        success_pop, populations = self._get_populations_to_plot()
        if not success_pop:
            return
        success_data, data_type = self._get_data_type_to_plot()
        if not success_data:
            return
        success_ene, energies = self._gen_linspace("energy")
        if not success_ene:
            return
        success_angle, angles = self._gen_linspace("angle")
        if not success_angle:
            return

        group_by_pe = data_type == "Emission Energy"
        if group_by_pe:
            axes_by_pe = {
                e_pe: self.plot_area.axes_for(e_pe)
                for e_pe in self._known_impact_energies()
            }
            self.model.plot(
                self.plotter,
                population=populations,
                data_type=data_type,
                energies=energies,
                angles=angles,
                axes=axes_by_pe,
                group_by_pe=True,
            )
            self.plot_area.refresh()
        else:
            axes = self.plot_area.axes_for(None)
            self.model.plot(
                self.plotter,
                population=populations,
                data_type=data_type,
                energies=energies,
                angles=angles,
                axes=axes,
            )
            self.plot_area.refresh(None)

    def _get_data_type_to_plot(
        self,
    ) -> tuple[bool, ImplementedEmissionData | None]:
        """Read input to determine the emission data type to plot."""
        data_type = [
            IMPLEMENTED_EMISSION_DATA[i]
            for i, checked in enumerate(self.data_checkboxes)
            if checked.isChecked()
        ]
        if len(data_type) == 0:
            logging.error("Please provide a type of data to plot.")
            return False, None
        return True, data_type[0]

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
            line_name = f"{variable}_{box}"
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
                "Model is not set, cannot fill energy/angle plotting ranges."
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

        data = list(
            cast(
                list[EmissionData],
                flatten(
                    [
                        data_matrix.get_data(data_type, IMPLEMENTED_POP)
                        for data_type in model.data_types
                    ]
                ),
            )
        )

        if not data:
            logging.debug(
                "No valid data, cannot fill energy/angle plotting ranges."
            )
            return

        e_maxi = max([max(d.energies) for d in data])
        if e_maxi is not None and not np.isnan(e_maxi):
            logging.debug(f"Setting {e_maxi = }")
            self.last_energy_widget.setText(str(e_maxi))

        theta_maxi = 0.0
        n_theta = 1
        for d in data:
            _theta_max = max(d.angles)
            if _theta_max < theta_maxi:
                continue
            theta_maxi = _theta_max
            n_theta = len(d.angles)
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

        module_names_to_paths = f"{name.lower()}_classes"
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

    def _known_impact_energies(self) -> list[float]:
        """List loaded impact energies."""
        distribs = self.data_matrix.get_data(
            "Emission Energy", IMPLEMENTED_POP
        )
        impacts = {d.e_pe for d in distribs}
        return sorted(impacts)

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


def main() -> None:
    """Build the GUI interface."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
