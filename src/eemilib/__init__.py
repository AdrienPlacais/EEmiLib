"""
EEmiLib (Electron EMIssion Library) holds several electron emission models and
offers a simple way to fit the on electron emission data.

"""

import importlib.metadata

from eemilib.util.log_manager import set_up_logging

DOC_URL = "https://adrienplacais.github.io/EEmiLib/"
__version__ = importlib.metadata.version("eemilib")

set_up_logging("EEmiLib")
