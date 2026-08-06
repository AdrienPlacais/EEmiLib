"""Provide Cu data.

This set of data is available online :cite:`Placais2020b`. Please use this
reference if you use it in your work.

It corresponds to the two Cu samples I used in my PhD :cite:`Placais2021`.

This data can be loaded with :class:`.pandas_loader.PandasLoader`.

"""

from importlib import resources

files = resources.files(__name__)

teey_cu_1_eroded = files / "measured_TEEY_Cu_1_eroded.csv"
teey_cu_1_heated = files / "measured_TEEY_Cu_1_heated.csv"
teey_cu_2_as_received = files / "measured_TEEY_Cu_2_as-received.csv"
teey_cu_2_eroded = files / "measured_TEEY_Cu_2_eroded.csv"
teey_cu_2_heated = files / "measured_TEEY_Cu_2_heated.csv"
