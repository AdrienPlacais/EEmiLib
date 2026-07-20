"""

Chung and Everhart example
==========================

This script showcases how :class:`.model.ChungEverhart` model can be fitted.

In this example, the fit is performed over several energy distributions with
different |PE| impact energies.

"""

# sphinx_gallery_tags = ["emission energy", "group_by_pe", "ChungEverhart"]

import matplotlib.pyplot as plt
import numpy as np
from eemilib.data.ag.emission_energy import distrib_70eV, distrib_100eV
from eemilib.emission_data import DataMatrix
from eemilib.loader import PandasLoader
from eemilib.model import ChungEverhart
from eemilib.plotter import PandasPlotter

# %%
# In order to avoid creating too many images, we perform this study only for
# |PE| energies of :math:`70\,\mathrm{eV}` and :math:`100\,\mathrm{eV}`.
filepaths = (distrib_70eV, distrib_100eV)

# %%
# We associate the filepaths from :mod:`eemilib.data.ag.emission_energy` to
# the emission energy distribution of |EEs|.
data_matrix = DataMatrix()
data_matrix.set_files(
    filepaths, population="all", emission_data_type="Emission Energy"
)

# %%
# We create a :class:`.Loader` that supports these files and load the data:
loader = PandasLoader()
data_matrix.load_data(loader)

# %%
# Create a default :class:`.Plotter` object:
plotter = PandasPlotter()

# %%
# We set ``group_by_pe=True`` to create one plot per energy distribution file,
# *i.e.* one per |PE| impact energy:
axes_1 = data_matrix.plot(
    plotter,
    population="all",
    emission_data_type="Emission Energy",
    group_by_pe=True,
)
plt.show()

# %%
# Note that the returned object is not a simple `list` of `Axes`, but a `dict`
# associating every |PE| energy to an `Axes`:
__import__("pprint").pprint(axes_1)

# %%
# Create a default :class:`.model.ChungEverhart` instance, and find the
# :math:`W_f` parameter that works best for all given energies:
model = ChungEverhart()
model.find_optimal_parameters(data_matrix)

# %%
# Plot the modelled emission energy, re-using the previous ``axes``:
axes_2 = data_matrix.plot(
    plotter,
    population="all",
    emission_data_type="Emission Energy",
    group_by_pe=True,
)  # Create new Figure from scratch only for ``sphinx_gallery``
_ = model.plot(
    plotter,
    population="SE",
    emission_data_type="Emission Energy",
    energies=np.linspace(0, 50, 201),
    angles=np.linspace(0, 0, 1),
    axes=axes_2,
    group_by_pe=True,
)
plt.show()

# %%
# .. note::
#    When ``e_pes`` is given, like in the next example, these energies are used
#    for the :class:`.Model` plot.
#    ``axes`` is then optional.
#
axes_3 = data_matrix.plot(
    plotter,
    population="all",
    emission_data_type="Emission Energy",
    group_by_pe=True,
)  # Create new Figure from scratch only for ``sphinx_gallery``
_ = model.plot(
    plotter,
    population="SE",
    emission_data_type="Emission Energy",
    energies=np.linspace(0, 50, 201),
    angles=np.linspace(0, 0, 1),
    axes=axes_3,
    e_pes=[50, 70],
    group_by_pe=True,
)
plt.show()
