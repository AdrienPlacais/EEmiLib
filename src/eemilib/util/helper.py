"""Define generic utility functions."""

import importlib
import inspect
import os
import pkgutil
from abc import ABCMeta


def get_classes(module_path: str, base_class: ABCMeta) -> list[str]:
    """In ``module_path``, get every class inheriting from ``class_type``.

    Used by the GUI to dynamically keep track of the :class:`.Loader`,
    :class:`.Model` and :class:`.Plotter` that are implemented.

    """
    base_module = importlib.import_module(module_path)
    class_list = []
    for _, module_name, is_pkg in pkgutil.iter_modules(
        [os.path.dirname(base_module.__file__)]
    ):
        if is_pkg:
            continue
        full_module_name = f"{module_path}.{module_name}"
        try:
            imported_module = importlib.import_module(full_module_name)
        except ImportError as e:
            print(f"Error importing {full_module_name}: {e}")
            continue

        for name, obj in inspect.getmembers(imported_module, inspect.isclass):
            if issubclass(obj, base_class) and obj is not base_class:
                class_list.append(name)
    return class_list
