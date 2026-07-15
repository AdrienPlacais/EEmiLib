"""Define uniform markdown display."""

MAX = r"\mathrm{max}"
MIN = r"\mathrm{min}"
LOW = r"\mathrm{low}"
SE = r"\mathrm{SE}"
EBE = r"\mathrm{EBE}"
IBE = r"\mathrm{IBE}"

SEEY = r"\delta"
EBEEY = r"\eta_e"
IBEEY = r"\eta_i"
TEEY = r"\sigma"

DELTA_E_TR = r"\Delta E_{tr}"
DIFFUSION_LENGTH = "d"
EC_1 = r"E_{\mathrm{c,\,1}}"
EC_2 = r"E_{\mathrm{c,\,2}}"
ESCAPE_PROBABILITY = "S"
EXCITATION_ENERGY = r"\xi"
E_0 = r"E_0"
E_MAX = rf"E_{MAX}"
K_S = "k_s"
K_SE = "k_{se}"
NORM = "k"
POWER_LAW_EXPONENT = "n"
POWER_LAW_SCALE = "A"
SIGMA_LOW = f"{TEEY}_{LOW}"
SIGMA_MAX = f"{TEEY}_{MAX}"
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
DELTA_MAX = rf"{SEEY}_{MAX}"
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
ETA_E_MAX = r"\eta_{e,\," + MAX + "}"
ETA_E_MAX_FP = r"\hat P_{1,\," + BS + "}"
ETA_E_MIN = r"\eta_{e,\," + MIN + "}"
ETA_E_MIN_FP = r"P_{1,\," + BS + r"}\left( \infty \right)"
SIGMA = rf"\sigma_{BS}"
W = "W"
P = "p"
E1 = "e_1"
E2 = "e_2"

# IBE
E_IBE = rf"E_{IBE}"
E_IBE_FP = rf"\hat E_{RD}"
ETA_I_MAX = r"\eta_{i,\," + MAX + "}"
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
