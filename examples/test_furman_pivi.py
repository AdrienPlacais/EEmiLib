"""


==========

This script showcases the basics of loading data and fitting a model.

"""

import logging

import matplotlib.pyplot as plt
import numpy as np
from eemilib.data.ag.emission_energy import distribs
from eemilib.data.ag.emission_yield import teey_ag_1_heated_pd
from eemilib.emission_data import DataMatrix
from eemilib.loader import PandasLoader
from eemilib.model import FurmanPivi
from eemilib.plotter import PandasPlotter

mylog = logging.getLogger()
myconsolehandler = mylog.handlers[0]
myconsolehandler.setLevel(logging.DEBUG)
logging.getLogger("matplotlib.font_manager").disabled = True

data_matrix = DataMatrix()
loader = PandasLoader()
plotter = PandasPlotter()
model = FurmanPivi()

data_matrix.set_files(
    teey_ag_1_heated_pd, population="all", data_type="Emission Yield"
)
data_matrix.set_files(distribs, population="all", data_type="Emission Energy")
data_matrix.load_data(loader)

axes_distrib = data_matrix.plot(
    plotter, population="all", data_type="Emission Energy", group_by_pe=True
)
axes_yield = data_matrix.plot(
    plotter, population="all", data_type="Emission Yield"
)

model.find_optimal_parameters(data_matrix)

axes_distrib = model.plot(
    plotter,
    population=["SE", "EBE", "IBE", "all"],
    data_type="Emission Energy",
    energies=None,
    angles=np.linspace(0, 0, 1),
    axes=axes_distrib,
    group_by_pe=True,
)

axes_yield = model.plot(
    plotter,
    population=["SE", "EBE", "IBE", "all"],
    data_type="Emission Yield",
    energies=None,
    angles=np.linspace(0, 60, 4),
    axes=axes_yield,
)
plt.show()
