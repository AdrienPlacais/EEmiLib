"""Define generic utility functions."""

import inspect
import pkgutil
from abc import ABCMeta
from typing import Any

from eemilib import DOC_URL


def get_classes(module_name: str, base_class: ABCMeta) -> dict[str, str]:
    """In ``module_path``, get every class inheriting from ``class_type``.

    Used by the GUI to dynamically keep track of the :class:`.Loader`,
    :class:`.Model` and :class:`.Plotter` that are implemented.

    Parameters
    ----------
    module_name : str
        The name of a module.
    base_class : ABCMeta
        The mother object that classes should inherit from.

    Returns
    -------
    classes : dict[str, str]
        Keys are the name of the objects inheriting from ``base_class`` found
        in ``module_name``. Values are the path leading to them.

    """
    classes: dict[str, str] = {}
    package = __import__(module_name, fromlist=[""])
    for _, name, _ in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        module = __import__(name, fromlist=[""])
        for name, cls in inspect.getmembers(module, inspect.isclass):
            if issubclass(cls, base_class) and cls is not base_class:
                classes[name] = module.__name__
    return classes


def documentation_url(obj: Any) -> str:
    """Infer the link to the documentation from object path."""
    module = obj.__class__.__module__
    package = module.split(".")[0]
    parts = (DOC_URL, package, module)
    return "/".join(parts) + ".html"
