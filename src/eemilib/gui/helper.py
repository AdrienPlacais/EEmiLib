"""Define functions to be as DRY as possible."""

import logging
from collections.abc import Collection
from functools import partial
from typing import Any, Literal, NamedTuple, overload

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QWidget,
)

from eemilib.gui.styles import TITLE_STYLE
from eemilib.model.parameter import Parameter


class LinspaceEntries(NamedTuple):
    """Named values returned by ``setup_linspace_entries``."""

    #: Row title
    label: QLabel
    #: Start of the linspace
    first: QWidget
    #: End of the linspace
    last: QWidget
    #: Number of linspace points
    n_points: QWidget
    #: When checked, values are taken from measurements; the entries above
    #: are greyed out
    use_measured: QCheckBox


def setup_linspace_entries(
    label: str,
    initial_values: tuple[float, float, int],
    max_value: float | None = None,
    use_measured_text: str = "Match measurements",
) -> LinspaceEntries:
    """Create the widgets of an input to call np.linspace."""
    widgets = [
        _linspace_entry(is_int, x_0=x_0, x_max=x_max)
        for is_int, x_0, x_max in zip(
            (False, False, True), initial_values, (max_value, max_value, None)
        )
    ]

    use_measured = QCheckBox(use_measured_text)
    use_measured.setEnabled(False)

    def grey_out_entries(checked: bool) -> None:
        for widget in widgets:
            widget.setEnabled(not checked)

    use_measured.toggled.connect(grey_out_entries)

    return LinspaceEntries(QLabel(label), *widgets, use_measured)


def add_linspace_row(
    grid: QGridLayout, row: int, entries: LinspaceEntries
) -> None:
    """Place ``entries`` on a row of ``grid``, with the sub-labels."""
    grid.addWidget(entries.label, row, 0)
    for i, (name, widget) in enumerate(
        (
            ("first", entries.first),
            ("last", entries.last),
            ("n_points", entries.n_points),
        )
    ):
        grid.addWidget(QLabel(name), row, 1 + 2 * i)
        grid.addWidget(widget, row, 2 + 2 * i)
    grid.addWidget(entries.use_measured, row, 7)


def _linspace_entry(
    is_int: bool, x_0: float, x_min: int = 0, x_max: float | None = None
) -> QWidget:
    """Create widget for a single linspace entry."""
    validator = QDoubleValidator()
    validator.setBottom(x_min)
    if is_int:
        validator = QIntValidator()
    if x_max is not None:
        validator.setTop(int(x_max))

    entry = QLineEdit()
    entry.setValidator(validator)
    entry.setText(str(x_0))
    return entry


def setup_lock_checkbox(parameter: Parameter) -> QWidget:
    """Create the checkbox for the Lock button."""
    checkbox = QCheckBox()
    checkbox.setChecked(parameter.is_locked)
    checkbox.stateChanged.connect(
        lambda state, param=parameter: _toggle_lock(state, param)
    )

    checkbox_widget = QWidget()
    layout = QHBoxLayout(checkbox_widget)
    layout.addWidget(checkbox)
    layout.setAlignment(Qt.AlignCenter)
    layout.setContentsMargins(0, 0, 0, 0)
    checkbox_widget.setLayout(layout)
    return checkbox_widget


def _toggle_lock(state: Any, parameter: Parameter) -> None:
    """Activate/deactivate lock."""
    if state == Qt.Checked:
        parameter.lock()
        return
    parameter.unlock()


@overload
def to_plot_checkboxes(
    label: str,
    boxes_labels: Collection[str],
    *,
    several_can_be_checked: Literal[False],
) -> tuple[QHBoxLayout, list[QRadioButton]]: ...


@overload
def to_plot_checkboxes(
    label: str,
    boxes_labels: Collection[str],
    *,
    several_can_be_checked: Literal[True],
) -> tuple[QHBoxLayout, list[QCheckBox]]: ...


def to_plot_checkboxes(
    label: str,
    boxes_labels: Collection[str],
    *,
    several_can_be_checked: bool = False,
) -> tuple[QHBoxLayout, list[QRadioButton] | list[QCheckBox]]:
    """Create several check boxes next to each other."""
    checkbox_constructor = QCheckBox
    if not several_can_be_checked:
        checkbox_constructor = QRadioButton
    checkboxes = [checkbox_constructor(x) for x in boxes_labels]

    layout = QHBoxLayout()
    layout.addWidget(QLabel(label))
    for checkbox in checkboxes:
        layout.addWidget(checkbox)

    return layout, checkboxes


def set_help_button_action(button: QPushButton, obj: Any) -> None:
    """Update the link of the provided help button."""
    button.clicked.disconnect()
    this_help = partial(_open_help, obj=obj)
    button.clicked.connect(this_help)


def _open_help(obj: Any) -> None:
    """Open the ``doc_url`` attribute of given object."""
    url = getattr(obj, "doc_url", None)
    if not isinstance(url, str):
        logging.warning(f"No valid URL found for {obj = }")
        return
    QDesktopServices.openUrl(QUrl(url))


def titled_group(title: str, layout: QLayout) -> QGroupBox:
    """Add a standard `QGroupBox` to the given layout."""
    group = QGroupBox(title)
    group.setStyleSheet(TITLE_STYLE)
    group.setLayout(layout)
    return group


# Associate Parameters attributes with their column position
# Note that "name" is the key in the Model.parameters dict rather than the
# Parameter.name attribute (which is not consistent)
PARAMETER_ATTR_TO_POS = {
    "name": 0,
    "unit": 1,
    "value": 2,
    "lower_bound": 3,
    "upper_bound": 4,
    "lock": 5,
    "description": 6,
}

#: Maps column position in list of parameters to the corresponding Parameter
#: attribute
PARAMETER_POS_TO_ATTR = {
    val: key for key, val in PARAMETER_ATTR_TO_POS.items()
}
