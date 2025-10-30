"""Define the model related interface in the GUI."""

import logging

from eemilib.gui.helper import PARAMETER_ATTR_TO_POS
from eemilib.model.model import Model
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QLabel,
    QTableWidget,
    QVBoxLayout,
)


def model_configuration() -> tuple[QGroupBox, QTableWidget]:
    """Set the interface related to the model specific parameters."""
    group = QGroupBox("Model configuration")
    layout = QVBoxLayout()

    headers = list(PARAMETER_ATTR_TO_POS.keys())
    n_cols = len(headers)
    model_table = QTableWidget(0, n_cols)
    model_table.setHorizontalHeaderLabels(headers)
    model_table.setMaximumHeight(1000)
    model_table.setMinimumHeight(200)
    layout.addWidget(model_table)

    group.setLayout(layout)
    return group, model_table


class ModelSettingsDialog(QDialog):
    """Define an interactive window for :class:`.Model` settings."""

    def __init__(self, parent: QWindow, model: Model) -> None:
        """Instantiate the window and its parameters."""
        super().__init__(parent=parent)
        self._model = model

        self.setWindowTitle(f"{str(model.__class__.__name__)} settings")

        self._layout = QVBoxLayout(self)

        self._implementation_dropdown: QComboBox | None = None
        args = self._implementation_selector()
        if args is not None:
            label, dropdown = args
            self._layout.addWidget(label)
            self._layout.addWidget(dropdown)

        buttons = self._buttons()
        self._layout.addWidget(buttons)

    def _implementation_selector(self) -> tuple[QLabel, QComboBox] | None:
        """Create implementation selection dropdown menu."""
        implementations = getattr(
            self._model.__class__, "implementations", None
        )
        if not implementations:
            return

        current = getattr(self._model, "current_implementation", None)
        if not current:
            logging.error(
                f"{self._model} has no `current_implementation` attribute. Delete its "
                "`implementations` attribute, or set a `current_implementation`."
            )
            return

        set_implementation = getattr(self._model, "set_implementation", None)
        if not set_implementation:
            logging.error(
                f"{self._model} has no `set_implementation` method. Delete its "
                "`implementations` attribute, or set a `set_implementation`."
            )
            return

        label = QLabel("Implementation")

        implementation_dropdown = QComboBox()
        implementation_dropdown.addItems(implementations)
        implementation_dropdown.setCurrentText(current)

        self._implementation_dropdown = implementation_dropdown
        return label, implementation_dropdown

    @property
    def selected_implementation(self) -> str | None:
        """Return current implementation."""
        if not self._implementation_dropdown:
            return
        return self._implementation_dropdown.currentText()

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
        if self.selected_implementation:
            set_implementation = getattr(
                self._model, "set_implementation", None
            )
            if callable(set_implementation):
                set_implementation(self.selected_implementation)
