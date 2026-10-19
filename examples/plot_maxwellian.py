"""
Maxwellian
==========

This script showcases the basics of loading data and fitting a model.

"""

# sphinx_gallery_tags = ["emission energy", "Maxwellian"]
# sphinx_gallery_thumbnail_number = 2

import matplotlib.pyplot as plt
import numpy as np

from eemilib.data.ag.emission_energy import distrib_70eV
from eemilib.emission_data import MeasuredDataMatrix
from eemilib.loader import PandasLoader
from eemilib.model import Maxwellian
from eemilib.plotter import PandasPlotter

# %%
# We define the path to a file holding an emitted electrons energy
# distribution.
filepath = distrib_70eV

# %%
# Load data
# ---------
# This object will hold all the filepaths and link them to their content
# nature:
measured_data = MeasuredDataMatrix()

# %%
#
# - ``population``: the list of allowed values are defined in
#   :data:`.ImplementedPop`.
# - ``data_type``: allowed values are in
#   :data:`.ImplementedEmissionData`.
#
measured_data.set_files(
    filepath,  # One or several filepaths
    population="all",  # Type of electrons population
    data_type="Emission Energy",  # Nature of emission data
)

# %%
# The :class:`.Loader` will load the ``filepath``. Check
# :class:`.loader.PandasLoader` documentation for the actual expected format,
# but this one should work for most ``CSV``-like files.
loader = PandasLoader(
    sep=",",
    comment="#",  # Columns separator, comments marker
)
# %%
#
# .. seealso::
#    - :class:`.loader.DeesseLoader` shows how :class:`.Loader` can be
#      subclassed for specific needs.
#    - :class:`.loader.CSTLoader` can load files as ``ASCII Export``-ed files
#      from CST software.
#

# %%
# Actually load the data:
measured_data.load_data(loader)
# %%
#
# .. seealso::
#    :meth:`.emission_data.DataMatrix.get_data` to get the loaded data.
#

# %%
# Create a default :class:`.Plotter` object:
plotter = PandasPlotter()

# %%
# Plot the loaded data:
axes_1 = measured_data.plot(
    plotter, population="all", data_type="Emission Energy"
)
plt.show()


# %%
# Fit the model
# -------------
# Create a default :class:`.model.Maxwellian` instance:
model = Maxwellian()

# %%
# Fit it on loaded data:
model.find_optimal_parameters(measured_data)

# %%
# Internally, the :class:`.Model` will store electron emission data in a
# :class:`.ModelledDataMatrix` object. While being very close to
# :class:`.MeasuredDataMatrix`, it defines additional methods. In particular,
# :meth:`.ModelledDataMatrix.get_or_compute_data` is a version of
# :meth:`.DataMatrix.get_data` that accepts the arguments that are required to
# compute data. It has a caching functionality: calling it several times with
# the same arguments does not recompute.

# %%
# Plot
# ----
# We start by re-plotting the experimental data for ``sphinx_gallery``.
#
# For :class:`.Model` plots, we must specify at which energies and angles we
# want data. Here, we select emission energies in
# :math:`[0\,\mathrm{eV},\,50\,\mathrm{eV}]` and only at normal incidence.
axes_2 = measured_data.plot(
    plotter, population="all", data_type="Emission Energy"
)  # Create new Figure from scratch only for ``sphinx_gallery``

axes_2 = model.plot(
    plotter,
    population="SE",
    data_type="Emission Energy",
    energies=np.linspace(0, 50, 201),
    angles=np.linspace(0, 0, 1),
    axes=axes_2,
    color="red",
)
plt.show()
