"""Define an object holding dropdown-related together.

In particular, class-selection dropdowns.

"""

import importlib
import logging
from abc import ABCMeta
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Literal

from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton

from eemilib.util.helper import get_classes

DROPDOWNS = ("Loader", "Model", "Plotter")
Dropdowns = Literal["Loader", "Model", "Plotter"]


@dataclass
class DropdownEntry:
    """Everything the GUI needs to track for one dropdown menu."""

    #: Actual dropdown object.
    dropdown: QComboBox
    #: Maps displayed class names to their import path.
    classes: dict[str, str]
    #: Layout holding the dropdown and its buttons.
    layout: QHBoxLayout
    #: Buttons next to the dropdown, in creation order.
    buttons: list[QPushButton]

    def selected_class(self) -> ABCMeta:
        """Resolve the currently selected class."""
        selected = self.dropdown.currentText()
        module_path = self.classes[selected]
        module: ModuleType = importlib.import_module(module_path)
        return getattr(module, selected)


def setup_dropdown(
    module_name: str, base_class: ABCMeta, buttons_args: dict[str, Any]
) -> DropdownEntry:
    """Set up interface with a dropdown menu and buttons next to it.

    Parameters
    ----------
    module_name :
        Where the entries of the dropdown will be searched.
    base_class :
        The base class from which dropdown entries should inherit.
    buttons_args :
        Dictionary where the keys are the name of the buttons to add next to
        the dropdown menu, and values the callable that will be called when
        clicking the button. Several callables can be provided as a list or
        tuple.

    Returns
    -------
        Everything the caller needs to track for this dropdown.

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
        if not hasattr(action, "__iter__"):
            action = (action,)
        for a in action:
            button.clicked.connect(a)
        layout.addWidget(button)
        buttons.append(button)

    return DropdownEntry(
        dropdown=dropdown, classes=classes, layout=layout, buttons=buttons
    )


def set_dropdown_value(
    entry: DropdownEntry, value: str | ABCMeta | None
) -> None:
    """Set a dropdown to the desired value.

    Parameters
    ----------
    entry :
        The dropdown entry to update.
    value :
        Name of class or class object you want to select in the dropdown. If
        unset, we do not do anything.

    """
    if value is None:
        return
    if isinstance(value, ABCMeta):
        value = value.__name__
    dropdown = entry.dropdown
    index = dropdown.findText(value)
    if index == -1:
        logging.info(f"{value = } not found in {dropdown = } items.")
        return
    current_index = dropdown.currentIndex()
    if current_index != index:
        dropdown.setCurrentIndex(index)
    else:
        dropdown.currentIndexChanged.emit(index)
