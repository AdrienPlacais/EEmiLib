"""
Furman and Pivi
===============

This script showcases:

- How :class:`.model.FurmanPivi` model can be fitted.

"""

# sphinx_gallery_tags = ["emission yield", "emission energy", "implementation", "Furman and Pivi"]

import matplotlib.pyplot as plt
import numpy as np

from eemilib.data.ag.emission_energy import distribs
from eemilib.data.ag.emission_yield import teey_ag_1_heated_pd
from eemilib.emission_data import DataMatrix
from eemilib.loader import PandasLoader
from eemilib.model import FurmanPivi
from eemilib.plotter import PandasPlotter

# %%
# Create useful objects first
# ---------------------------
data_matrix = DataMatrix()
loader = PandasLoader()
plotter = PandasPlotter()
model = FurmanPivi()

# %%
# Load data
# ---------
# We will set both |TEEY| and emission energy distributions. In this particular
# case, the energy distributions will be rescaled so that their integral match
# the |TEEY| at the corresponding |PE| energy.
# This could be de-activated by setting
# ``rescale_energy_distributions_to_yield`` to ``False``, but would mess up
# our fitting.
data_matrix.set_files(
    teey_ag_1_heated_pd, data_type="Emission Yield", population="all"
)
data_matrix.set_files(distribs, data_type="Emission Energy", population="all")
data_matrix.load_data(
    loader,
    rescale_energy_distributions_to_yield=True,  # Un-necessary, this is the default value anyway
)

# %%
# Fit the model
# -------------
# This operation can take a little bit of time...
model.find_optimal_parameters(data_matrix)

# %%
# Now let's verify that the model is consistent with experimental data!
#
# .. note::
#    By specifying ``energies=None``, we force the :class:`.Model` to be
#    calculated on the same energies as the loaded data.
axes_yield = data_matrix.plot(
    plotter, population="all", data_type="Emission Yield"
)
axes_yield = model.plot(
    plotter,
    population=["SE", "EBE", "IBE", "all"],
    data_type="Emission Yield",
    energies=None,
    angles=np.linspace(0, 60, 4),
    axes=axes_yield,
)

axes_distrib = data_matrix.plot(
    plotter, population="all", data_type="Emission Energy", group_by_pe=True
)
axes_distrib = model.plot(
    plotter,
    population=["SE", "EBE", "IBE", "all"],
    data_type="Emission Energy",
    energies=None,
    angles=np.linspace(0, 0, 1),
    axes=axes_distrib,
    group_by_pe=True,
)

plt.show()
