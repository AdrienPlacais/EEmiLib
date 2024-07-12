"""Define generic utility functions."""

import importlib
import inspect
import os
import pkgutil
from abc import ABCMeta


def get_classes(module_name: str, base_class: ABCMeta) -> dict:
    """In ``module_path``, get every class inheriting from ``class_type``.

    Used by the GUI to dynamically keep track of the :class:`.Loader`,
    :class:`.Model` and :class:`.Plotter` that are implemented.

    """
    classes = {}
    package = __import__(module_name, fromlist=[""])
    for loader, name, is_pkg in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        module = __import__(name, fromlist=[""])
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, base_class) and cls is not base_class:
                classes[name] = module.__name__
    return classes
