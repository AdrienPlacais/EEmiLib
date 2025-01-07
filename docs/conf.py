import eemilib

project = "EEmiLib"
copyright = "2024, Adrien Plaçais"
author = "Adrien Plaçais"
version = eemilib.__version__
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinxcontrib.bibtex",
    "sphinx.ext.napoleon",  # handle numpy style
    "sphinx.ext.autodoc",
    "sphinx_rtd_theme",  # ReadTheDocs theme
    "myst_parser",  # still useful?
    "sphinx.ext.todo",  # allow use of TODO
    # "sphinx.ext.viewcode",
    "nbsphinx",
]
bibtex_bibfiles = ["references.bib"]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": True,
    "special-members": "__init__, __post_init__",
}

add_module_names = False
default_role = "literal"
todo_include_todos = True
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "display_version": True,
}
html_static_path = ["_static"]
