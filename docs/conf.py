import os
import sys

import eemilib

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
    "sphinx.ext.autodoc",  # include doc from docstrings
    "sphinx.ext.intersphinx",  # interlink with other docs, such as numpy
    "sphinx.ext.napoleon",  # handle numpy style
    "sphinx_autodoc_typehints",  # exploit Python typing for doc
    "sphinx.ext.todo",  # allow use of TODO
    "sphinx_rtd_theme",  # ReadTheDocs theme
    "sphinxcontrib.bibtex",
    "unit_role",
]

autodoc_default_options = {
    "exclude-members": "_abc_impl",
    "member-order": "bysource",
    "members": True,
    "private-members": True,
    "special-members": "__post_init__, __str__",
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

intersphinx_aliases = {
    "np.float64": "numpy.float64",
    "NDArray": "numpy.typing.NDArray",
}

# -- Parameters for sphinx-autodoc-typehints ----------------------------------
typehints_fully_qualified = False

# Document parameters without documentation. Set it to True to ensure that all
# parameters have their type documented
always_document_param_types = False
# Integrate the doc of the __init__, and in particular it's Parameters section,
# to the class documentation (__init__ doc is hidden)
autoclass_content = "both"

always_use_bars_union = True

typehints_document_rtype = True
typehints_document_rtype_none = True
typehints_use_rtype = True

typehints_defaults = "comma"
simplify_optional_unions = True
typehints_formatter = None

# If set to True, these ones also show the typing in the function signature in
# the doc. Like:
# function(a: float, b: int) -> tuple[float, int]
# instead of:
# function(a, b)
typehints_use_signature = False
typehints_use_signature_return = False

# MyST parser to include markdown files
myst_gfm_only = True  # interpret markdown with github styling
