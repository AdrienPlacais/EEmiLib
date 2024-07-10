"""EEmiLib (Electron EMIssion Library) holds several electron emission models and offers a simple way to fit the on electron emission data."""

from .emission_data.data_matrix import DataMatrix
from .main import main
from .model.vaughan import Vaughan
from .util.constants import IMPLEMENTED_EMISSION_DATA, IMPLEMENTED_POP
from .util.helper import get_classes
