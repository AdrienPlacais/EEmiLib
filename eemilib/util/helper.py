"""Define generic utility functions."""

import importlib
import inspect
import pkgutil
from abc import ABCMeta


def get_classes(package_path: str, class_type: ABCMeta) -> list[str]:
    """In ``package_path``, get every class inheriting from ``class_type``.

    Used by the GUI to dynamically keep track of the :class:`.Loader`,
    :class:`.Model` and :class:`.Plotter` that are implemented.

    """
    model_classes = []
    for _, module_name, _ in pkgutil.iter_modules([package_path]):
        module = importlib.import_module(
            f"{package_path.replace('/', '.')}.{module_name}"
        )
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, class_type) and obj is not class_type:
                model_classes.append(name)
    return model_classes
