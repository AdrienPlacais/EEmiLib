#!/usr/bin/env python3
"""Define a GUI.

.. todo::
    Export/Import settings

.. todo::
    Add description at and of parameters
    Dynamic boxes for Parameters?

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
from numpy.typing import NDArray
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
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
    LinspaceEntries,
    set_dropdown_value,
    set_help_button_action,
    setup_dropdown,
    setup_linspace_entries,
    titled_group,
    to_plot_checkboxes,
)
from eemilib.gui.loader_selection import LoaderSettingsDialog
from eemilib.gui.model import (
    ModelImplementationsDialog,
    create_evaluation_table,
    model_configuration,
    populate_evaluators_table,
    populate_parameters_table_constants,
)
from eemilib.gui.plot_canvas import TabbedPlotArea
from eemilib.gui.styles import format_number
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


class EEmiLibGUI(QMainWindow):
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

        #: Holds all widgets of first tab
        self.data_model_layout: QVBoxLayout
        #: Holds all widgets of second tab
        self.plot_layout: QVBoxLayout
        self._setup_main_structure()

        #: Maps a dropdown name to the actual ``QComboBox`` widget.
        self.dropdowns: dict[str, QComboBox] = {}

        # Tab 1: Data & Model
        self.file_lists: list[list[None | QListWidget]]
        self._setup_file_selection_matrix()

        #: Maps implemented loader names to their actual import path.
        self.loader_classes: dict[str, str]
        #: Opens current :class:`.Loader` documentation.
        self.loader_help_button: QPushButton
        self._setup_loader_dropdown()

        #: Store the :class:`.Parameters` logic for the :class:`.Model`.
        self.parameters_table: QTableWidget
        self._setup_model_configuration()

        #: Maps implemented model names to their actual import path.
        self.model_classes: dict[str, str]
        #: Opens current :class:`.Model` documentation.
        self.model_help_button: QPushButton
        self._setup_model_dropdown()

        #: Widget holding evaluator names and values.
        self.evaluators_table: QTableWidget
        self._setup_model_evaluation()

        # Tab 2: Plot
        #: Stores the current figure(s).
        self.plot_area: TabbedPlotArea
        self._setup_plot_area()

        #: Store whether measurements are currently plotted.
        self._measurements_are_plotted: bool = False

        #: Holds all widgets related to the energy linspace
        self.energy: LinspaceEntries
        #: Holds all widgets related to the angle linspace
        self.angle: LinspaceEntries
        #: Check this to make the ``Model`` plots use the same energies as
        #: the measurements
        self.use_measured_energies_checkbox: QCheckBox
        self._setup_energy_angle_inputs()

        #: Maps implemented :class:`.Plotter` names with their actual import
        #: paths.
        self.plotter_classes: dict[str, str]
        #: Let user select which type of data should be plotted.
        self.data_checkboxes: list[QRadioButton]
        #: Let user select which kind of electron population should be plotted.
        self.population_checkboxes: list[QCheckBox]
        self._setup_plotter_dropdowns()

        # Call the methods called by the model_dropdown index change
        self._set_default_dropdown()

    @property
    def measurements_are_plotted(self) -> bool:
        """Tell if measurements are currenty plotted."""
        return self._measurements_are_plotted

    @measurements_are_plotted.setter
    def measurements_are_plotted(self, value: bool) -> None:
        """Update flag value, and also the checkbox "Use measured energies".

        Used by the "Plot model" and the "Clear figure" buttons.

        """
        self._measurements_are_plotted = value
        checkbox = getattr(self, "use_measured_energies_checkbox", None)
        if checkbox is None:
            logging.error(
                "Checkbox 'use_measured_energies_checkbox' not created yet. "
                "May cause problems later."
            )
            return
        self.refresh_use_measured_energies_availability()

    # =========================================================================
    # Main tabs organization
    # =========================================================================
    def _setup_main_structure(self) -> None:
        """Organize the GUI into tabs.

        1. First tab holds:
            i. A :class:`.DataMatrix`;
            ii. :class:`.Model` parameters.
        2. Second tab holds:
            i. The :class:`.Plotter` parameters.

        Sets :attr:`data_model_layout` and :attr:`plot_layout`.

        """
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        tab = QTabWidget()
        main_layout.addWidget(tab)

        data_model_tab = QWidget()
        self.data_model_layout = QVBoxLayout(data_model_tab)
        tab.addTab(data_model_tab, "Data && Model")

        plot_tab = QWidget()
        self.plot_layout = QVBoxLayout(plot_tab)
        tab.addTab(plot_tab, "Plot")

    # =========================================================================
    # Tab 1 - File selection
    # =========================================================================
    def _setup_file_selection_matrix(self) -> None:
        """Create the 4 * 3 matrix to select the files to load.

        1. Create the widgets
           - ``file_matrix_group``, delegated to
             :func:`.file_selection_matrix`.
           - :attr:`file_lists`, delegated to :func:`.file_selection_matrix`.
        2. Wire the signals
           - Delegated to :func:`.file_selection_matrix`.
        3. Create the layout
           - :attr:`data_model_layout`, already created
           - :func:`file_selection_matrix` also creates a ``QGridLayout``
             internally.
        4. Call the `addWidget` and `addLayout` methods
           - The `addWidget` related to :attr:`file_lists` are handled by
             :func:`.file_selection_matrix`!

        """
        file_matrix_group, self.file_lists = file_selection_matrix(self)
        self.data_model_layout.addWidget(file_matrix_group)

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
        """Set the :class:`.Loader` dropdown.

        1. Create the widgets
           - :attr:`loader_help_button`, delegated to :func:`.setup_dropdown`.
           - The widgets associating :class:`.Loader` names to the instances
             are created, wired, added directly within :func:`setup_dropdown`.
        2. Wire the signals
           - Delegated to :func:`.setup_dropdown`.
           - Some wiring is also done at the end of the  method.
        3. Create the layout
           - already created: `data_model_layout`
           - A `QHBoxLayout` is returned by :func:`.setup_dropdown`
        4. Call the `addWidget` and `addLayout` methods
           - :func:`.setup_dropdown` already adds its widgets to the layout in
             the returned :class:`.DropdownSetup`.
           - Add the final layout from :func:`.setup_dropdown` to the
             :attr:`data_model_layout`.

        Also sets the :attr:`loader_classes` dictionary.

        """
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
        self.loader_help_button = setup.buttons[0]
        self.dropdowns["Loader"] = setup.dropdown
        self.loader_classes = setup.classes

        setup.dropdown.currentIndexChanged.connect(
            self._instantiate_a_new_loader
        )
        # FIXME: I believe the line below is just here to init the dropdown.
        # But we already have the :meth:`_set_default_dropdown` called at the
        # end of ``__init__`` 🤔
        _ = setup.dropdown.setCurrentText

        self.data_model_layout.addLayout(setup.layout)

    def _instantiate_a_new_loader(self) -> None:
        """Set up new loader whenever the dropdown menu is changed."""
        self.loader = self._dropdown_to_class("Loader")()
        set_help_button_action(self.loader_help_button, self.loader)

    def _setup_loader_settings_dialog(self) -> tuple[str, Callable]:
        """Give arguments to setup the loader settings button."""
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
    def _setup_model_configuration(self) -> None:
        """Orchestrate :class:`.Model` :class:`.Parameter` related interfaces.

        1. Create the widgets
           - :attr:`.parameters_table`, delegated to
             :func:`model_configuration`.
        2. Wire the signals
           - delegated to :func:`model_configuration`
        3. Create the layout
           - already created: `data_model_layout`
        4. Call the `addWidget` and `addLayout` methods

        """
        model_group, self.parameters_table = model_configuration()
        self.data_model_layout.addWidget(model_group)

    def _setup_model_dropdown(self) -> None:
        """Set the :class:`.Model` dropdown.

        1. Create the widgets
           - :attr:`model_help_button`. Delegated to :func:`.setup_dropdown`.
           - ``model_dropdown``, added to :attr:`dropdowns`. Delegated to
             :func:`.setup_dropdown`.
        2. Wire the signals
           - Delegated to :func:`.setup_dropdown`.
           - Some wiring is also done at the end of the  method.
        3. Create the layout
           - already created: `data_model_layout`
           - A `QHBoxLayout` is returned by :func:`.setup_dropdown`
        4. Call the `addWidget` and `addLayout` methods
           - :func:`.setup_dropdown` already adds its widgets to the layout in
             the returned :class:`.DropdownSetup`.
           - Add the final layout from :func:`.setup_dropdown` to the
             :attr:`data_model_layout`.

        Also, it sets the :attr:`model_classes` dictionary.

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
        self.model_help_button = setup.buttons[0]
        self.dropdowns["Model"] = setup.dropdown
        self.model_classes = setup.classes

        setup.dropdown.currentIndexChanged.connect(
            self._instantiate_a_new_model
        )
        setup.dropdown.currentIndexChanged.connect(
            self._deactivate_unnecessary_file_widgets
        )
        setup.dropdown.currentIndexChanged.connect(
            self._autofill_plot_data_type_and_population
        )
        setup.dropdown.currentIndexChanged.connect(
            self._populate_parameters_table_values
        )

        self.data_model_layout.addLayout(setup.layout)

    def _setup_model_implementations_dialog(self) -> tuple[str, Callable]:
        """Give arguments to setup the model setttings button."""
        settings_label = "⚙️ Implementations"

        def settings_action() -> int:
            code = ModelImplementationsDialog(self, self.model).exec()
            self._populate_parameters_table_values()
            populate_parameters_table_constants(
                self.parameters_table, self.model.parameters
            )
            return code

        return settings_label, settings_action

    def _instantiate_a_new_model(self) -> None:
        """Instantiate :class:`.Model` when it is selected in dropdown menu."""
        self.model = self._dropdown_to_class("Model")()

        set_help_button_action(self.model_help_button, self.model)

        populate_parameters_table_constants(
            self.parameters_table, self.model.parameters
        )
        self.parameters_table.itemChanged.connect(
            self._update_parameter_value_from_table
        )

    def _update_parameter_value_from_table(
        self, item: QTableWidgetItem
    ) -> None:
        """Update :class:`.Parameter` value based on user input in table."""
        row, col = item.row(), item.column()
        updatable_attr = ("value", "lower_bound", "upper_bound")
        attr = PARAMETER_POS_TO_ATTR[col]
        if attr not in updatable_attr:
            return

        name = self.parameters_table.cellWidget(row, 0).objectName()
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
        """Print out the :attr:`.Parameter.value` in the dedicated tab.

        This method needs dynamic access to :attr:`model`, so it is not defined
        as a function like :func:`.populate_parameters_table_constants`.

        """
        for row, param in enumerate(self.model.parameters.values()):
            for attr in ("value",):
                col = PARAMETER_ATTR_TO_POS[attr]
                attr_value = getattr(param, attr, None)
                self.parameters_table.setItem(
                    row, col, QTableWidgetItem(str(attr_value))
                )

        for i, param in enumerate(self.model.parameters.values()):
            self.parameters_table.setItem(
                i, 2, QTableWidgetItem(format_number(param.value))
            )

    # =========================================================================
    # Tab 1 - Model evaluation
    # =========================================================================
    def _setup_model_evaluation(self) -> None:
        """Create the display of the model evaluations.

        Sets :attr:`evaluators_table`.

        """
        layout = QVBoxLayout()
        group = titled_group("Model evaluations", layout)

        self.evaluators_table = create_evaluation_table()
        layout.addWidget(self.evaluators_table)

        reevaluate_button = QPushButton("Re-evaluate")
        reevaluate_button.clicked.connect(self._fill_evaluations_display)
        layout.addWidget(reevaluate_button)

        self.data_model_layout.addWidget(group)

    def _fill_evaluations_display(self) -> None:
        """Fill the evaluations display with the last model."""
        if not hasattr(self, "model") or not self.model:
            logging.info("Please select a model before evaluating.")
            return
        if not hasattr(self, "data_matrix") or not self.data_matrix:
            logging.info("Please load data before evaluating.")
            return
        evaluations = self.model.evaluate(self.data_matrix)
        populate_evaluators_table(self.evaluators_table, evaluations)

    # =========================================================================
    # Tab 2 - Plot
    # =========================================================================
    def _setup_plot_area(self) -> None:
        """Create the tabbed canvas area.

        Sets :attr:`plot_area`.

        """
        self.plot_area = TabbedPlotArea()
        self.plot_layout.addWidget(self.plot_area)

    def _autofill_plot_data_type_and_population(self) -> None:
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
        """Set the energy and angle inputs for the model plot.

        Sets :attr:`energy`, :attr:`angle`, :attr:`use_measured_energies_checkbox`.

        """
        layout = QVBoxLayout()
        group = titled_group("Plot configuration", layout)

        self.energy = setup_linspace_entries(
            "Energy [eV]", initial_values=(0.0, 500.0, 501)
        )
        layout.addLayout(self.energy.layout)

        self.use_measured_energies_checkbox = (
            self._create_use_measured_energies_checkbox()
        )
        layout.addWidget(self.use_measured_energies_checkbox)

        self.angle = setup_linspace_entries(
            "Angle [deg]", initial_values=(0.0, 60.0, 4), max_value=90.0
        )
        layout.addLayout(self.angle.layout)

        self.plot_layout.addWidget(group)

    def _create_use_measured_energies_checkbox(self) -> QCheckBox:
        """Set checkbox making :meth:`.Model.plot` use ener from measurements.

        Behavior:
        - Greyed out if no measurements plotted (rely on
          :attr:`.measurements_are_plotted`)
        - When checked, the :meth:`.Model.plot` is called with
          ``energies=None`` so that min/max energies are taken from currently
          drawn axes.

        """

        def _on_use_measured_energies_toggled(checked: bool) -> None:
            """Grey out energy linspace inputs."""
            for widg in (
                self.energy.first,
                self.energy.last,
                self.energy.n_points,
            ):
                widg.setEnabled(not checked)

        checkbox = QCheckBox("Use energies from measurements")
        checkbox.setEnabled(self.measurements_are_plotted)
        checkbox.toggled.connect(_on_use_measured_energies_toggled)
        return checkbox

    def refresh_use_measured_energies_availability(self) -> None:
        """Re-sync the checkbox state with :attr:`.measurements_are_plotted`.

        Call this every time :attr:`.measurements_are_plotted` changes.

        """
        checkbox = self.use_measured_energies_checkbox
        checkbox.setEnabled(self.measurements_are_plotted)
        if not self.measurements_are_plotted and checkbox.isChecked():
            checkbox.setChecked(False)

    def _get_energies_for_model_plot(self) -> NDArray[np.float64] | None:
        """Get proper energies for :meth:`.Model.plot`.

        - If the :attr:`.use_measured_energies_checkbox` is checked, we return
          ``None`` and :meth:`.Model.plot` will take energies  from the given
          ``Axes``.
        - If unchecked, we create a linspace from the energy linspace inputs.

        """
        checkbox = self.use_measured_energies_checkbox
        if checkbox.isChecked():
            return

        success, linspace = self._gen_linspace("energy")
        if not success:
            logging.warning(
                "An error was raised trying to generate the linspace. "
                "Continue with a default energies array."
            )
        return linspace

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
                "Clear figure": self._clear_figure_action,
            },
        )
        self.plotter_classes = setup.classes
        setup.dropdown.currentIndexChanged.connect(self._setup_plotter)
        self.dropdowns["Plotter"] = setup.dropdown
        self.plot_layout.addLayout(setup.layout)

    def _clear_figure_action(self) -> None:
        """Clean the figure and the ``is/are_plotted`` flag(s)."""
        self.plot_area.clear()
        self.measurements_are_plotted = False

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
        self.plot_layout.addLayout(layout)
        self.data_checkboxes = checkboxes

    def _set_up_population_to_plot_checkboxes(self) -> None:
        """Add checkbox to select which population should be plotted."""
        layout, checkboxes = to_plot_checkboxes(
            "Population to plot:", IMPLEMENTED_POP, several_can_be_checked=True
        )
        self.plot_layout.addLayout(layout)
        self.population_checkboxes = checkboxes

    def plot_measured(self) -> None:
        """Plot the desired data, as imported."""
        success_pop, populations = self._get_populations_to_plot()
        if not success_pop:
            return
        cast(list[ImplementedPop], populations)
        data_type = self._get_data_type_to_plot()
        if data_type is None:
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

        self.measurements_are_plotted = True
        return

    def plot_model(self) -> None:
        """Plot the desired data, as modelled."""
        success_pop, populations = self._get_populations_to_plot()
        if not success_pop:
            return
        data_type = self._get_data_type_to_plot()
        if data_type is None:
            return
        energies = self._get_energies_for_model_plot()
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

        return

    def _get_data_type_to_plot(self) -> ImplementedEmissionData | None:
        """Read input to determine the emission data type to plot."""
        data_type: list[ImplementedEmissionData] = [
            IMPLEMENTED_EMISSION_DATA[i]
            for i, checked in enumerate(self.data_checkboxes)
            if checked.isChecked()
        ]
        if len(data_type) == 0:
            logging.error("Please provide a type of data to plot.")
            return None
        return data_type[0]

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
    ) -> tuple[bool, NDArray[np.float64]]:
        """Take the desired input, check validity, create array of values."""
        success = True
        linspace_args = []
        linspace: LinspaceEntries | None = getattr(self, variable)
        if linspace is None:
            raise ValueError(
                f"The LinspaceEntries named {variable} was not found."
            )

        for line_name in ("first", "last", "n_points"):
            widget = getattr(linspace, line_name, None)
            if widget is None:
                logging.error(f"The attribute {line_name} is not defined.")
                success = False
                continue

            assert isinstance(widget, QLineEdit)
            value = widget.displayText()
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
            self.energy.last.setText(str(e_maxi))

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
            self.angle.last.setText(str(theta_maxi))
            logging.debug(f"Setting {n_theta = }")
            self.angle.n_points.setText(str(n_theta))

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
    window = EEmiLibGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
