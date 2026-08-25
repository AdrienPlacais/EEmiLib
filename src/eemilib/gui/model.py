"""Define the model related interface in the GUI.

.. todo::
   Find a way to display more info in the `Implementations` dialog.

   - A help button redirecting to the doc?
   - Text/hovering text for each `implementation_choices` entry?

"""

import logging

from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from eemilib.gui.dialogs import SettingsDialog
from eemilib.gui.helper import (
    PARAMETER_ATTR_TO_POS,
    setup_lock_checkbox,
    titled_group,
)
from eemilib.gui.styles import format_number, math_text_label_from_key
from eemilib.model.model import Model
from eemilib.model.parameter import Parameter


def model_configuration() -> tuple[QGroupBox, QTableWidget]:
    """Set the interface related to the model specific parameters.

    Returns
    -------
    QGroupBox
        Holds all the :class:`.Model` parameters logic.
    QTableWidget
        Actual list of :class:`.Parameter`.

    """
    layout = QVBoxLayout()
    group = titled_group("Model configuration", layout)

    headers = list(PARAMETER_ATTR_TO_POS.keys())
    n_cols = len(headers)
    parameters_table = QTableWidget(0, n_cols)
    parameters_table.setHorizontalHeaderLabels(headers)
    parameters_table.setMaximumHeight(1000)
    parameters_table.setMinimumHeight(200)
    parameters_table.setAlternatingRowColors(True)

    header = parameters_table.horizontalHeader()
    for attr, col in PARAMETER_ATTR_TO_POS.items():
        mode = (
            QHeaderView.Stretch
            if attr == "description"
            else QHeaderView.ResizeToContents
        )
        header.setSectionResizeMode(col, mode)

    layout.addWidget(parameters_table)

    group.setLayout(layout)
    return group, parameters_table


def populate_parameters_table_constants(
    parameters_table: QTableWidget, parameters: dict[str, Parameter]
) -> None:
    """Print out the constants of model parameters in dedicated table.

    The :class:`.Parameter` attributes that are written are:
    - :attr:`.Parameter.name`
      - separated into a simple label and unit
    - :attr:`.Parameter.description`
    - :attr:`.Parameter.lower_bound`
    - :attr:`.Parameter.is_locked`

    The method :methd:`.EEmiLibGUI._populate_parameters_table_values` is used
    to print out non-constant parameters, such as :attr:`.Parameter.value`.

    Parameters
    ----------
    parameters_table :
        Table as created by :func:`model_configuration`.
    parameters :
        Model parameters as stored in :attr:`.Model.parameters`.

    """
    parameters_table.setRowCount(0)
    for row, param in enumerate(parameters.values()):
        parameters_table.insertRow(row)

        label, unit = math_text_label_from_key(param.name)
        label.setObjectName(param.name)  # anchors the name to the widget
        parameters_table.setCellWidget(row, 0, label)
        parameters_table.setCellWidget(row, 1, unit)
        description, _ = math_text_label_from_key(param.description)
        parameters_table.setCellWidget(
            row, PARAMETER_ATTR_TO_POS["description"], description
        )

        for attr in ("lower_bound", "upper_bound"):
            col = PARAMETER_ATTR_TO_POS[attr]
            attr_value = getattr(param, attr, None)
            parameters_table.setItem(
                row, col, QTableWidgetItem(str(attr_value))
            )
        col_lock = PARAMETER_ATTR_TO_POS["lock"]
        checkbox_widget = setup_lock_checkbox(param)
        parameters_table.setCellWidget(row, col_lock, checkbox_widget)


def create_evaluation_table() -> QTableWidget:
    """Create the two-column table that displays evaluation results."""
    table = QTableWidget(0, 3)
    table.setHorizontalHeaderLabels(["Metric", "Unit", "Value"])

    header = table.horizontalHeader()
    assert header is not None, "Error when creating header"
    for i in range(3):
        header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setAlternatingRowColors(True)
    return table


def populate_evaluators_table(
    evaluators_table: QTableWidget, evaluations: dict[str, float]
) -> None:
    """Write the contents of ``evaluations`` into the table.

    ``evaluators_table`` is modified in place.

    Parameters
    ----------
    evaluators_table :
        A table with label in first column, units in second, value in third.
        Such a table is created by :func:`create_evaluation_table`.
    evaluations :
        Maps label + units to associated values. Such a dictionnary is returned
        by :meth:`.Model.evaluate`.

    """
    evaluators_table.setRowCount(0)
    for row, (key, value) in enumerate(evaluations.items()):
        evaluators_table.insertRow(row)

        label, unit = math_text_label_from_key(key)
        evaluators_table.setCellWidget(row, 0, label)
        evaluators_table.setCellWidget(row, 1, unit)

        evaluators_table.setItem(
            row, 2, QTableWidgetItem(format_number(value))
        )


class ModelImplementationsDialog(SettingsDialog):
    """Define an interactive window for :class:`.Model` implementations."""

    def __init__(self, parent: QWindow, model: Model) -> None:
        """Instantiate the window and its parameters."""
        super().__init__(
            parent, f"{model.__class__.__name__!s} implementations"
        )
        self._model = model

        self._implementation_dropdowns: dict[str, QComboBox] = {}
        for label, dropdown in self._implementation_selectors():
            self._layout.addWidget(label)
            self._layout.addWidget(dropdown)

        self._finalize()

    def _implementation_selectors(self) -> list[tuple[QLabel, QComboBox]]:
        """Create one dropdown per implementation entry."""
        choices = getattr(
            self._model.__class__, "implementation_choices", None
        )
        if not choices:
            return []

        set_implementation = getattr(self._model, "set_implementation", None)
        if not callable(set_implementation):
            logging.error(
                f"{self._model} defines `implementation_choices` but has no"
                " `set_implementation` method."
            )
            return []

        current = getattr(self._model, "current_implementations", {})

        selectors = []
        for name, options in choices.items():
            label = QLabel(name.replace("_", " ").capitalize())

            dropdown = QComboBox()
            dropdown.addItems(options)
            current_value = current.get(name)
            if current_value:
                dropdown.setCurrentText(current_value)

            self._implementation_dropdowns[name] = dropdown
            selectors.append((label, dropdown))
        return selectors

    def apply(self) -> None:
        """Apply the settings to the :class:`.Model`."""
        set_implementation = getattr(self._model, "set_implementation", None)
        if not callable(set_implementation):
            return
        for name, dropdown in self._implementation_dropdowns.items():
            set_implementation(name, dropdown.currentText())
