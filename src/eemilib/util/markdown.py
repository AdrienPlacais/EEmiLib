"""Define uniform markdown display."""

MAX = r"\mathrm{max}"
LOW = r"\mathrm{low}"
SE = r"\mathrm{SE}"
EBE = r"\mathrm{EBE}"
IBE = r"\mathrm{IBE}"

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
SIGMA = r"\sigma"
SIGMA_LOW = f"{SIGMA}_{LOW}"
SIGMA_MAX = f"{SIGMA}_{MAX}"
TEMPERATURE = "T"
W_F = "W_f"


# =============================================================================
# Furman
# =============================================================================
# Notations
BS = r"\mathrm{bs}"
RD = r"\mathrm{rd}"
TS = r"\mathrm{ts}"

# SE
DELTA_MAX = rf"\delta_{MAX}"
DELTA_MAX_FP = rf"\hat \delta_{TS}"
NORMAL_E_MAX_SE = "E_{" + rf"{MAX},\,{SE}" + "}"
NORMAL_E_MAX_SE_FP = rf"\hat E_{TS}"
S = "s"
T1 = "t_1"
T2 = "t_2"
T3 = "t_3"
T4 = "t_4"

# EBE
NORMAL_E_MAX_EBE = "E_{" + rf"{MAX},\,{EBE}" + "}"
P1_HAT = r"\hat P_{1,\," + BS + "}"
P1_INF_EBE = r"P_{1,\," + BS + r"}\left( \infty \right)"
SIGMA = r"\sigma_\mathrm{bs}"
W = "W"
P = "p"
E1 = "e_1"
E2 = "e_2"

# IBE
NORMAL_E_MAX_IBE = "E_{" + rf"{MAX},\,{IBE}" + "}"
P1_INF_IBE = r"P_{1,\," + RD + r"}\left( \infty \right)"
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
