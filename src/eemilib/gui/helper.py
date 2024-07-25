"""Define functions to be as DRY as possible."""

from abc import ABCMeta
from collections.abc import Callable
from typing import Any

from eemilib.model.parameter import Parameter
from eemilib.util.helper import get_classes
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QFont, QIntValidator
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QWidget,
)


def setup_file_selection_widget(
    select_file_func: Callable,
) -> tuple[QPushButton, QListWidget]:
    """Set the button to load and the list of selected files."""
    button = QPushButton("📂")
    button.setFont(QFont("Segoe UI Emoji", 10))
    button.clicked.connect(select_file_func)

    file_list = QListWidget()
    return button, file_list


def setup_dropdown(
    module_name: str,
    base_class: ABCMeta,
    buttons_args: dict[str, Any],
):
    """Set up interface with a dropdown menu and a button next to it.

    Parameters
    ----------
    module_name : str
        Where the entries of the dropdown will be searched.
    base_class : ABCMeta
        The base class from which dropdown entries should inherit.
    buttons : dict[str, Any]
        Dictionary where the keys are the name of the buttons to add next to
        the dropdown menu, and values the callable that will be called when
        clicking the button.

    Returns
    -------
    classes : dict[str, str]
        Keys are the name of the objects inheriting from ``base_class`` found
        in ``module_name``. Values are the path leading to them.
    layout : QHBoxLayout
        Layout holding together ``dropdown`` and ``button``.
    dropdown : QComboBox
        Dropdown menu holding the keys of ``classes``.
    buttons : list[QPushButton]
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


def setup_linspace_entries(
    label: str,
    max_value: float | None = None,
) -> tuple[QHBoxLayout, QLineEdit, QLineEdit, QLineEdit]:
    """Create an input to call np.linspace."""
    layout = QHBoxLayout()

    layout.addWidget(QLabel(label))

    layout.addWidget(QLabel("first"))
    first = QLineEdit()
    first_validator = QDoubleValidator()
    first_validator.setBottom(0)
    if max_value is not None:
        first_validator.setTop(max_value)
    first.setValidator(first_validator)
    layout.addWidget(first)

    layout.addWidget(QLabel("last"))
    last = QLineEdit()
    last_validator = QDoubleValidator()
    last_validator.setBottom(0)
    if max_value is not None:
        last_validator.setTop(max_value)
    last.setValidator(last_validator)
    layout.addWidget(last)

    layout.addWidget(QLabel("n points"))
    points = QLineEdit()
    points_validator = QIntValidator()
    points_validator.setBottom(0)
    points.setValidator(points_validator)
    layout.addWidget(points)
    return layout, first, last, points


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


# Associate Parameters attributes with their column position
# Note that "name" is the key in the Model.parameters dict rather than the
# Parameter.name attribute (which is not consistent)
PARAMETER_ATTR_TO_POS = {
    "name": 0,
    "unit": 1,
    "value": 2,
    "lower_bound": 3,
    "upper_bound": 4,
    "description": 5,
    "lock": 6,
}

PARAMETER_POS_TO_ATTR = {
    val: key for key, val in PARAMETER_ATTR_TO_POS.items()
}
