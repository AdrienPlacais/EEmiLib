"""
Vaughan
=======

This script showcases:

- How :class:`.model.Vaughan` model can be fitted.
- How different implementations of a same :class:`.Model` are handled.

    .. seealso::
        :class:`.model.FurmanPivi` also has several implementations.

"""

# sphinx_gallery_tags = ["emission yield", "implementation", "Vaughan"]
# sphinx_gallery_thumbnail_number = 1

import matplotlib.pyplot as plt
import numpy as np
from eemilib.data.cu.emission_yield import teey_cu_1_eroded as filepath
from eemilib.emission_data import DataMatrix
from eemilib.loader import PandasLoader
from eemilib.model import Vaughan
from eemilib.plotter import PandasPlotter

# %%
# Load data
# ---------
data_matrix = DataMatrix()
data_matrix.set_files(
    filepath, population="all", emission_data_type="Emission Yield"
)
data_matrix.load_data(PandasLoader())
plotter = PandasPlotter()

# %%
# Basic fitting
# -------------
axes_1 = data_matrix.plot(
    plotter, population="all", emission_data_type="Emission Yield"
)
model_classic = Vaughan()
model_classic.find_optimal_parameters(data_matrix)
model_classic.plot(
    plotter,
    population="all",
    emission_data_type="Emission Yield",
    energies=np.linspace(0, 1000, 1001),
    angles=np.linspace(0, 60, 4),
    axes=axes_1,
)
plt.show()

# %%
# Model implementations
# ---------------------
# Some models can have different implementations. This is in the case for
# :class:`.model.Vaughan` model. By default, we instantiate the model as it is
# defined in :cite:`Vaughan1989`.
#
# But you can find different implementations in the CST and SPARK3D softwares.
# With :class:`.model.Vaughan`, you can select the desired implementation with
# the ``implementation`` keyword:
model_spark = Vaughan(implementation="SPARK3D")
model_cst = Vaughan(implementation="CST")
# %%
# .. tip::
#    The :meth:`.Model.set_implementation` method allows you to change a
#    :class:`.Model` implementation after it has been created.

models = (model_classic, model_spark, model_cst)
for model in models[1:]:
    model.find_optimal_parameters(data_matrix)

# %%
# Plot only at normal incidence to keep the plot readable.
axes_2 = data_matrix.plot(
    plotter, population="all", emission_data_type="Emission Yield"
)
colors = ("black", "grey", "cyan")
linestyles = ("-", ":", "--")
for model, color, ls in zip(models, colors, linestyles):
    model.plot(
        plotter,
        population="all",
        emission_data_type="Emission Yield",
        energies=np.linspace(0, 1000, 1001),
        angles=np.linspace(0, 0, 1),
        axes=axes_2,
        color=color,
        ls=ls,
    )
axes_2.set_xlim(0, 200)
plt.show()
