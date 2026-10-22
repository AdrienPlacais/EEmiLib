"""Define uniform markdown display."""

# =============================================================================
# Generic
# =============================================================================
from eemilib.util.constants import ImplementedEmissionData, ImplementedPop

MAX = r"\mathrm{max}"
MIN = r"\mathrm{min}"
LOW = r"\mathrm{low}"
SE = r"\mathrm{SE}"
EBE = r"\mathrm{EBE}"
IBE = r"\mathrm{IBE}"
ALL = r"\mathrm{all}"

_SEEY = r"\delta"
_EBEEY = r"\eta_e"
_IBEEY = r"\eta_i"
_TEEY = r"\sigma"

ETA_E_MAX = r"\eta_{e,\," + MAX + "}"
ETA_E_MIN = r"\eta_{e,\," + MIN + "}"
ETA_I_MAX = r"\eta_{i,\," + MAX + "}"
DELTA_MAX = rf"{_SEEY}_{MAX}"
SIGMA_LOW = f"{_TEEY}_{LOW}"
SIGMA_MAX = f"{_TEEY}_{MAX}"

EC_1 = r"E_{\mathrm{c,\,1}}"
EC_2 = r"E_{\mathrm{c,\,2}}"
E_MAX = rf"E_{MAX}"

EY_LABELS: dict[ImplementedPop, str] = {
    "SE": rf"SEEY ${_SEEY}$",
    "EBE": rf"EBEEY ${_EBEEY}$",
    "IBE": rf"IBEEY ${_IBEEY}$",
    "all": rf"TEEY ${_TEEY}$",
}
ENE_DISTRIB_LABELS: dict[ImplementedPop, str] = {
    "SE": rf"$f_{SE}$",
    "EBE": rf"$f_{EBE}$",
    "IBE": rf"$f_{IBE}$",
    "all": rf"$f_{ALL}$",
}
#: y-label in plots for the different emission data type.
DATA_TYPE_LABELS: dict[ImplementedEmissionData, str] = {
    "Emission Yield": "Emission Yield",
    "Emission Energy": r"Emission Energy Distribution [$\mathrm{eV}^{-1}$]",
    "Emission Angle": "Emission Angle Distribution",
}

# =============================================================================
# Vaughan
# =============================================================================
DELTA_E_TR = r"\Delta E_{tr}"
E_0 = r"E_0"
K_S = "k_s"
K_SE = "k_{se}"

# =============================================================================
# Dionne
# =============================================================================
DIFFUSION_LENGTH = "d"
POWER_LAW_EXPONENT = "n"
POWER_LAW_SCALE = "A"
ESCAPE_PROBABILITY = "S"
EXCITATION_ENERGY = r"\xi"

# =============================================================================
# Chung Everhart, Maxwellian
# =============================================================================
NORM = "k"
TEMPERATURE = "T"
W_F = "W_f"

# =============================================================================
# Furman
# =============================================================================
# Notations
BS = r"\mathrm{e}"  # 'bs' in CST, 'e' in Furman and Pivi paper
RD = r"\mathrm{r}"  # 'rd' in CST, 'r' in Furman and Pivi paper
TS = r"\mathrm{ts}"

# SE
DELTA_MAX_FP = rf"\hat \delta_{TS}"
NORMAL_E_MAX_SE = "E_{" + rf"{MAX},\,{SE}" + "}"
NORMAL_E_MAX_SE_FP = rf"\hat E_{TS}"
S = "s"
T1 = "t_1"
T2 = "t_2"
T3 = "t_3"
T4 = "t_4"
EPS_1 = r"\epsilon_1"
EPS_2 = r"\epsilon_2"
EPS_3 = r"\epsilon_3"
EPS_4 = r"\epsilon_4"
EPS_5 = r"\epsilon_5"
EPS_6 = r"\epsilon_6"
EPS_7 = r"\epsilon_7"
EPS_8 = r"\epsilon_8"
EPS_9 = r"\epsilon_9"
EPS_10 = r"\epsilon_{10}"
P_1 = "p_1"
P_2 = "p_2"
P_3 = "p_3"
P_4 = "p_4"
P_5 = "p_5"
P_6 = "p_6"
P_7 = "p_7"
P_8 = "p_8"
P_9 = "p_9"
P_10 = "p_{10}"

# EBE
NORMAL_E_MAX_EBE = "E_{" + rf"{MAX},\,{EBE}" + "}"
NORMAL_E_MAX_EBE_FP = r"\hat E_e"
ETA_E_MAX_FP = r"\hat P_{1,\," + BS + "}"
ETA_E_MIN_FP = r"P_{1,\," + BS + r"}\left( \infty \right)"
SIGMA = rf"\sigma_{BS}"
W = "W"
P = "p"
E1 = "e_1"
E2 = "e_2"

# IBE
E_IBE = rf"E_{IBE}"
E_IBE_FP = rf"\hat E_{RD}"
ETA_I_MAX_FP = r"P_{1,\," + RD + r"}(\infty)"
R = "r"
Q = "q"
R1 = "r_1"
R2 = "r_2"


def rst_math(key: str) -> str:
    """Transform string to rst math env."""
    return f":math:`{key}`"


def tex_math(key: str) -> str:
    """Transform string to tex math env."""
    return f"${key}$"
