import os
import sys

import eemilib
import sphinx

project = "EEmiLib"
copyright = "2025, Adrien Plaçais"
author = "Adrien Plaçais"
version = eemilib.__version__
release = version

# -- General configuration ---------------------------------------------------
# Add the _ext/ folder so that Sphinx can find it
sys.path.append(os.path.abspath("./_ext"))

extensions = [
    "myst_parser",
    "nbsphinx",
    "sphinx.ext.autodoc",  # include doc from docstrings
    "sphinx.ext.intersphinx",  # interlink with other docs, such as numpy
    "sphinx.ext.napoleon",  # handle numpy style
    "sphinx.ext.todo",  # allow use of TODO
    "sphinx_rtd_theme",  # ReadTheDocs theme
    "sphinxcontrib.bibtex",
    "unit_role",
]

autodoc_default_options = {
    "member-order": "bysource",
    "members": True,
    "private-members": True,
    "special-members": "__init__, __post_init__, __str__",
    "undoc-members": True,
}

add_module_names = False
default_role = "literal"
todo_include_todos = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
bibtex_bibfiles = ["references.bib"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_sidebars = {
    "**": [
        "versions.html",
    ],
}

# -- Check that there is no broken link --------------------------------------
nitpicky = True
nitpick_ignore = [
    ("py:class", "PyQt5.QtWidgets.QCheckBox"),
    ("py:class", "PyQt5.QtWidgets.QComboBox"),
    ("py:class", "PyQt5.QtWidgets.QGroupBox"),
    ("py:class", "PyQt5.QtWidgets.QHBoxLayout"),
    ("py:class", "PyQt5.QtWidgets.QLineEdit"),
    ("py:class", "PyQt5.QtWidgets.QListWidget"),
    ("py:class", "PyQt5.QtWidgets.QMainWindow"),
    ("py:class", "PyQt5.QtWidgets.QPushButton"),
    ("py:class", "PyQt5.QtWidgets.QRadioButton"),
    ("py:class", "PyQt5.QtWidgets.QTableWidget"),
    ("py:class", "PyQt5.QtWidgets.QTableWidgetItem"),
    ("py:class", "PyQt5.QtWidgets.QWidget"),
    ("py:class", "T"),
    ("py:class", "optional"),
    ("py:class", "numpy.float64"),
    # Dirty fix
    ("py:class", "ImplementedEmissionData"),
    ("py:class", "ImplementedPop"),
]
intersphinx_mapping = {
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
    "python": ("https://docs.python.org/3", None),
    "PyQt5": (
        "https://www.riverbankcomputing.com/static/Docs/PyQt5/",
        None,
    ),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
}

rst_prolog = """
.. |axplot| replace:: :meth:`matplotlib.axes.Axes.plot`
.. |dfplot| replace:: :meth:`pandas.DataFrame.plot`

"""

# Parameters for sphinx-autodoc-typehints
always_document_param_types = True
always_use_bars_union = True
typehints_defaults = "comma"

# MyST parser to include markdown files
myst_gfm_only = True  # interpret markdown with github styling
#
# -- bug fixes ---------------------------------------------------------------
# fix following warning:
# <unknown>:1: warning: py:class reference target not found: pathlib._local.path [ref.class]
# note that a patch is provided by sphinx 8.2, but nbsphinx 0.9.7 requires
# sphinx<8.2
# associated issue:
# https://github.com/sphinx-doc/sphinx/issues/13178
if sys.version_info[:2] >= (3, 13) and sphinx.version_info[:2] < (8, 2):  # type: ignore
    import pathlib

    from sphinx.util.typing import _INVALID_BUILTIN_CLASSES

    _INVALID_BUILTIN_CLASSES[pathlib.Path] = "pathlib.Path"  # type: ignore
    nitpick_ignore.append(("py:class", "pathlib._local.Path"))
