"""Define interface related to :class:`.Loader` in GUI."""

from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QCheckBox, QLabel, QLineEdit

from eemilib.gui.dialogs import SettingsDialog
from eemilib.loader.loader import Loader


def _unescape(text: str) -> str:
    r"""Interpret escape sequences typed by the user (e.g. ``\\t``)."""
    return text.encode("utf-8").decode("unicode-escape")


class LoaderSettingsDialog(SettingsDialog):
    """Define an interactive window for :class:`.Loader` settings."""

    def __init__(self, parent: QWindow, loader: Loader) -> None:
        """Instantiate the window and its parameters."""
        super().__init__(parent, f"{loader.__class__.__name__!s} settings")
        self._loader = loader

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

        self._gui = parent
        self._rescale_checkbox = QCheckBox(
            "Rescale energy distributions to TEEY"
        )
        self._rescale_checkbox.setChecked(
            parent.rescale_energy_distributions_to_yield
        )
        self._rescale_checkbox.setToolTip(
            "When both a TEEY and an 'all' emission energy distribution are "
            "loaded, scale each distribution so that its integral equals the "
            "TEEY at the same impact energy.\n"
            "Required by FurmanPivi. The other models predict an SE peak of 1, "
            "so their curves will not match the measurements' scale on the "
            "plot (the fit is not affected).\n"
            "Takes effect the next time you press 'Load data'."
        )
        self._layout.addWidget(self._rescale_checkbox)
        self._finalize()

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
        return _unescape(self._sep_box.text())

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
        return _unescape(self._comment_box.text())

    def apply(self) -> None:
        """Apply the settings to the :class:`.Model`."""
        if self.selected_sep is not None:
            self._loader.sep = self.selected_sep
        if self.selected_comment is not None:
            self._loader.comment = self.selected_comment
        self._gui.rescale_energy_distributions_to_yield = (
            self._rescale_checkbox.isChecked()
        )
