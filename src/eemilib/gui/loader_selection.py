"""Define interface related to :class:`.Loader` in GUI."""

import logging

from eemilib.loader.loader import Loader
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class LoaderSettingsDialog(QDialog):
    """Define an interactive window for :class:`.Loader` settings."""

    def __init__(self, parent: QWindow, loader: Loader) -> None:
        """Instantiate the window and its parameters."""
        super().__init__(parent=parent)
        self._loader = loader

        self.setWindowTitle(f"{str(loader.__class__.__name__)} settings")

        self._layout = QVBoxLayout(self)

        self._sep_box: QLineEdit | None = None
        args = self._sep_selector()
        if args is not None:
            label, box = args
            self._layout.addWidget(label)
            self._layout.addWidget(box)
        self._comment_box: QLineEdit | None = None
        args = self._comment_selector()
        if args is not None:
            label, box = args
            self._layout.addWidget(label)
            self._layout.addWidget(box)

        buttons = self._buttons()
        self._layout.addWidget(buttons)

    def _sep_selector(self) -> tuple[QLabel, QLineEdit] | None:
        """Create menu to select column delimiter."""
        sep = getattr(self._loader, "sep", None)
        if sep is None:
            return
        label = QLabel("Column separator")
        sep_box = QLineEdit()
        sep_box.setText(sep)
        self._sep_box = sep_box
        return label, sep_box

    @property
    def selected_sep(self) -> str | None:
        """Return current separator."""
        if not self._sep_box:
            return
        sep = self._sep_box.text().encode("utf-8").decode("unicode-escape")
        return sep

    def _comment_selector(self) -> tuple[QLabel, QLineEdit] | None:
        """Create menu to select comment character."""
        comment = getattr(self._loader, "comment", None)
        if comment is None:
            return
        label = QLabel("Comment character")
        comment_box = QLineEdit()
        comment_box.setText(comment)
        self._comment_box = comment_box
        return label, comment_box

    @property
    def selected_comment(self) -> str | None:
        """Return current comment character."""
        if not self._comment_box:
            return
        comment = (
            self._comment_box.text().encode("utf-8").decode("unicode-escape")
        )
        return comment

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
        if self.selected_sep is not None:
            self._loader.sep = self.selected_sep
        if self.selected_comment is not None:
            self._loader.comment = self.selected_comment
