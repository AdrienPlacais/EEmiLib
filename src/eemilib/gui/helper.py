"""Define functions to be as DRY as possible."""

import logging
from abc import ABCMeta
from collections.abc import Collection
from functools import partial
from typing import Any, Literal, overload

from eemilib.model.parameter import Parameter
from eemilib.util.helper import get_classes
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QWidget,
)


def setup_dropdown(
    module_name: str,
    base_class: ABCMeta,
    buttons_args: dict[str, Any],
) -> tuple[dict[str, str], QHBoxLayout, QComboBox, list[QPushButton]]:
    """Set up interface with a dropdown menu and a button next to it.

    Parameters
    ----------
    module_name :
        Where the entries of the dropdown will be searched.
    base_class :
        The base class from which dropdown entries should inherit.
    buttons :
        Dictionary where the keys are the name of the buttons to add next to
        the dropdown menu, and values the callable that will be called when
        clicking the button.

    Returns
    -------
    dict[str, str]
        Keys are the name of the objects inheriting from ``base_class`` found
        in ``module_name``. Values are the path leading to them.
    QHBoxLayout
        Layout holding together ``dropdown`` and ``button``.
    QComboBox
        Dropdown menu holding the keys of ``classes``.
    list[QPushButton]
        The buttons next to the dropdown menu.

    """
    classes = get_classes(module_name, base_class)

    layout = QHBoxLayout()

    dropdown = QComboBox()
    dropdown.addItems(classes.keys())
    layout.addWidget(QLabel(f"Select {base_class.__name__}:"))
    layout.addWidget(dropdown)

    buttons = []
    for name, action in buttons_args.items():
        button = QPushButton(name)
        button.clicked.connect(action)
        layout.addWidget(button)
        buttons.append(button)

    return classes, layout, dropdown, buttons


def set_dropdown_value(
    dropdown: QComboBox, value: str | ABCMeta | None
) -> None:
    """Set a ``dropdown`` to desired value.

    Parameters
    ----------
    dropdown :
        Dropdown object.
    value :
        Name of class or class object you want to select in the dropdown. If
        unset, we do not do anything.
    allowed_values :
        Dict used for the ``dropdown`` creation; links name of class objects
        to their import path.

    """
    if value is None:
        return
    if isinstance(value, ABCMeta):
        value = value.__name__
    index = dropdown.findText(value)
    if index == -1:
        logging.info(f"{value = } not found in {dropdown = } items.")
        return
    dropdown.setCurrentIndex(index)


def setup_linspace_entries(
    label: str,
    initial_values: tuple[float, float, int],
    max_value: float | None = None,
) -> tuple[QHBoxLayout, QLineEdit, QLineEdit, QLineEdit]:
    """Create an input to call np.linspace."""
    layout = QHBoxLayout()
    layout.addWidget(QLabel(label))

    widgets: list[QWidget] = []
    for label, is_int, x_0, x_max in zip(
        ("first", "last", "n_points"),
        (False, False, True),
        initial_values,
        (max_value, max_value, None),
    ):
        layout.addWidget(QLabel(label))
        widgets.append(w := _linspace_entry(is_int, x_0=x_0, x_max=x_max))
        layout.addWidget(w)

    return layout, widgets[0], widgets[1], widgets[2]


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


def setup_lock_checkbox(
    parameter: Parameter,
) -> QWidget:
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


def format_number(value: int | float) -> str:
    """Format the given number.

    Parameters
    ----------
    value :
        Number to format.

    """
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


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
}

#: Maps column position in list of parameters to the corresponding Parameter
#: attribute
PARAMETER_POS_TO_ATTR = {
    val: key for key, val in PARAMETER_ATTR_TO_POS.items()
}
