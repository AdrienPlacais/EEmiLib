"""
Emission yield measurements realized at ONERA, Toulouse, France using the
DEESSE test facility from 2018-05-29 to 2018-05-30.

This is an Ag sample that was heated at 200 celsius during 2 hours. It is
called "heated Ag#1" in my PhD :cite:`Placais2021`.

Emission yield at different incidence angles. Can be loaded using
:class:`.loader.DeesseLoader`.

"""

from importlib import resources

files = resources.files(__name__)

teey_ag_1_heated_0deg = files / "cleanAg0_TEEY_29_05_2018_18h02m35s.csv"
teey_ag_1_heated_20deg = files / "cleanAg20_TEEY_30_05_2018_10h18m05s.csv"
teey_ag_1_heated_40deg = files / "cleanAg40_TEEY_30_05_2018_11h05m48s.csv"
teey_ag_1_heated_60deg = files / "cleanAg60_TEEY_30_05_2018_11h54m09s.csv"
teey_ag_1_heated = (
    teey_ag_1_heated_0deg,
    teey_ag_1_heated_20deg,
    teey_ag_1_heated_40deg,
    teey_ag_1_heated_60deg,
)
