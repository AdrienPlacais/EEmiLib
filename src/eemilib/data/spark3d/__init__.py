"""Make available ECSS TEEY, as exported by SPARK3D."""

from importlib import resources

files = resources.files(__name__)

ecss_al = files / "aluminium_ecss.txt"
ecss_al_parameters_values = {
    "E_c1": 17,
    "E_max": 276,
    "teey_low": 0.8,
    "teey_max": 2.92,
    "E_0": 8,
}

ecss_ag = files / "silver_ecss.txt"
ecss_ag_parameters_values = {
    "E_c1": 20,
    "E_max": 315,
    "teey_low": 0.8,
    "teey_max": 2.34,
}

ecss_cu = files / "copper_ecss.txt"
ecss_cu_parameters_values = {
    "E_c1": 19,
    "E_max": 232,
    "teey_low": 0.8,
    "teey_max": 2.48,
}
