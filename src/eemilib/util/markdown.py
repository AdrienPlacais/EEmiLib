"""Define uniform markdown display."""

MAX = r"\mathrm{max}"
LOW = r"\mathrm{low}"

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


def rst_math(key: str) -> str:
    """Transform string to rst math env."""
    return f":math:`{key}`"


def tex_math(key: str) -> str:
    """Transform string to tex math env."""
    return f"${key}$"
