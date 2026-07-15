"""Define the model related interface in the GUI.

.. todo::
   Find a way to display more info in the `Implementations` dialog.

   - A help button redirecting to the doc?
   - Text/hovering text for each `implementation_choices` entry?

"""

import logging

from eemilib.gui.helper import PARAMETER_ATTR_TO_POS
from eemilib.gui.styles import TITLE_STYLE
from eemilib.model.model import Model
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QVBoxLayout,
)


def model_configuration() -> tuple[QGroupBox, QTableWidget]:
    """Set the interface related to the model specific parameters."""
    group = QGroupBox("Model configuration")
    group.setStyleSheet(TITLE_STYLE)
    layout = QVBoxLayout()

    headers = list(PARAMETER_ATTR_TO_POS.keys())
    n_cols = len(headers)
    model_table = QTableWidget(0, n_cols)
    model_table.setHorizontalHeaderLabels(headers)
    model_table.setMaximumHeight(1000)
    model_table.setMinimumHeight(200)
    model_table.setAlternatingRowColors(True)

    header = model_table.horizontalHeader()
    for attr, col in PARAMETER_ATTR_TO_POS.items():
        mode = (
            QHeaderView.Stretch
            if attr == "description"
            else QHeaderView.ResizeToContents
        )
        header.setSectionResizeMode(col, mode)

    layout.addWidget(model_table)

    group.setLayout(layout)
    return group, model_table


class ModelImplementationsDialog(QDialog):
    """Define an interactive window for :class:`.Model` implementations."""

    def __init__(self, parent: QWindow, model: Model) -> None:
        """Instantiate the window and its parameters."""
        super().__init__(parent=parent)
        self._model = model

        self.setWindowTitle(f"{str(model.__class__.__name__)} implementations")

        self._layout = QVBoxLayout(self)

        self._implementation_dropdowns: dict[str, QComboBox] = {}
        for label, dropdown in self._implementation_selectors():
            self._layout.addWidget(label)
            self._layout.addWidget(dropdown)

        buttons = self._buttons()
        self._layout.addWidget(buttons)

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

    def _buttons(self) -> QDialogButtonBox:
        """Create OK/Cancel buttons."""
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButtons(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
        )

        def on_ok():
            self.apply()
            self.accept()

        buttons.accepted.connect(on_ok)
        buttons.rejected.connect(self.reject)
        return buttons

    def apply(self) -> None:
        """Apply the settings to the :class:`.Model`."""
        set_implementation = getattr(self._model, "set_implementation", None)
        if not callable(set_implementation):
            return
        for name, dropdown in self._implementation_dropdowns.items():
            set_implementation(name, dropdown.currentText())
