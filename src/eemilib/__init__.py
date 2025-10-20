"""
EEmiLib (Electron EMIssion Library) holds several electron emission models and
offers a simple way to fit the on electron emission data.

"""

import importlib.metadata
from importlib import resources

from eemilib.util.log_manager import set_up_logging

DOC_URL = "https://eemilib.readthedocs.io/en/latest"
__version__ = importlib.metadata.version("eemilib")

teey_cu = resources.files("eemilib.data.cu.emission_yield")
emission_energy_ag = resources.files("eemilib.data.ag.emission_energy")

set_up_logging("EEmiLib")
