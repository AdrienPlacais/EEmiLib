"""Define ``QDialog`` subclasses."""

from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout


class SettingsDialog(QDialog):
    """Base class for a simple settings dialog with OK/Cancel buttons.

    Subclasses should, in their own ``__init__``, add their specific
    widgets to :attr:`_layout` and then call :meth:`_finalize` last, so the
    OK/Cancel row appears at the bottom. They must also override
    :meth:`apply`.

    """

    def __init__(self, parent: QWindow, title: str) -> None:
        """Instantiate the window."""
        super().__init__(parent=parent)
        self.setWindowTitle(title)
        self._layout = QVBoxLayout(self)

    def _finalize(self) -> None:
        """Add the OK/Cancel row. Call once, after adding other widgets."""
        self._layout.addWidget(self._buttons())

    def _buttons(self) -> QDialogButtonBox:
        """Create OK/Cancel buttons."""
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButtons(
                QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            )
        )

        def on_ok() -> None:
            self.apply()
            self.accept()

        buttons.accepted.connect(on_ok)
        buttons.rejected.connect(self.reject)
        return buttons

    def apply(self) -> None:
        """Apply the settings. Subclasses must override."""
        raise NotImplementedError
