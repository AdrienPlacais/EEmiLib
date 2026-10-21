"""
Cached data
===========

This script explains how the :class:`.Model` caches already-calculated electron
emission data.

"""


# sphinx_gallery_tags = ["emission energy", "Maxwellian", "cache"]

from pprint import pprint

import numpy as np

from eemilib.emission_data._data_matrix import ModelledDataMatrix
from eemilib.model import Maxwellian

# %%
# For this example, we create a Maxwellian distribution with arbitrary
# parameters.
parameters_values = {"norm": 1.0, "temperature": 7.5}
model = Maxwellian(parameters_values)

# %%
# The :class:`.Model` stores electron emission data in a
# :class:`.ModelledDataMatrix` object.
cached: ModelledDataMatrix = model._cached_data_matrix
# %%
# For now, it is an empty 4x3 list:
pprint(cached.data_matrix)

# %%
# While being very close to :class:`.MeasuredDataMatrix`, it defines additional
# methods. In particular, :meth:`.ModelledDataMatrix.get_or_compute_data` is a
# version of :meth:`.DataMatrix.get_data` that accepts the arguments that are
# required to compute data. It has a caching functionality: calling it several
# times with the same arguments does not recompute. First calculation fills the
# cache.
my_distribution = model.get_or_compute_data(
    "Emission Energy",
    "SE",
    energy=np.linspace(0, 100, 10001),
    theta=None,
    e_pe=None,
)[0]
# %%
# The distribution is stored:
pprint(cached.data_matrix)

# %%
# Second calculation with the same arguments does not recompute data, it simply
# grabs cached data.
my_second_distribution = model.get_or_compute_data(
    "Emission Energy",
    "SE",
    energy=np.linspace(0, 100, 10001),
    theta=None,
    e_pe=None,
)[0]
# %%
# The new distribution is the same object as the previous one.
print(my_second_distribution is my_distribution)
# %%
# No object was created, cached data is untouched:
pprint(cached.data_matrix)

# %%
# Now let's try to change the method arguments:
my_third_distribution = model.get_or_compute_data(
    "Emission Energy",
    "SE",
    energy=np.linspace(0, 99.999999, 10001),
    theta=None,
    e_pe=None,
)[0]
# %%
# The new distribution is a different object:
print(my_third_distribution is my_distribution)
# %%
# It also replaces the old one:
pprint(cached.data_matrix)
