r"""Emission yields and emission energy distribution of stainless steel.

Quoting Furman and Pivi :cite:`Furman2002`:

*The stainless steel data were obtained from a sample of SLAC standard 304
rolled sheet chemically etched and passivated but not conditioned [21, 29].*

- Emission Yields:
  - Normal incidence
  - :math:`0` to :math:`1000\,\mathrm{eV}`
- Energy Distributions:
  - Normal incidence
  - |PE| energy is :math:`100\,\mathrm{eV}`.

Parameters are taken from Tab. 1 and 2 in Furman and Pivi paper
:cite:`Furman2002` (stainless steel). Data generated using CST.

Note
----
These settings are the default in CST when selecting PEC.

"""

furman_pivi_parameters_values = {
    # =====================================================================
    # Secondary Electrons (or "True Secondaries")
    # =====================================================================
    "normal_e_max_se": 310.0,
    "normal_delta_max": 1.22,
    "t_1": 0.66,
    "t_2": 0.80,
    "t_3": 0.70,
    "t_4": 1.0,
    "s": 1.813,
    "eps_1": 3.9,
    "eps_2": 6.2,
    "eps_3": 13.0,
    "eps_4": 8.8,
    "eps_5": 6.25,
    "eps_6": 2.25,
    "eps_7": 9.20,
    "eps_8": 5.3,
    "eps_9": 17.8,
    "eps_10": 10.0,
    "p_1": 1.6,
    "p_2": 2.0,
    "p_3": 1.8,
    "p_4": 4.7,
    "p_5": 1.8,
    "p_6": 2.4,
    "p_7": 1.8,
    "p_8": 1.8,
    "p_9": 2.3,
    "p_10": 1.8,
    # =====================================================================
    # Elastically Backscattered Electrons (or "Reflected")
    # =====================================================================
    "normal_e_max_ebe": 0.0,
    "p_1_hat": 0.5,
    "sigma": 1.9,
    "p_1_inf_ebe": 0.07,
    "W": 100.0,
    "p": 0.9,
    "e_1": 0.26,
    "e_2": 2.0,
    # =====================================================================
    # Inelastically Backscattered Electrons (or "Rediffused")
    # =====================================================================
    "normal_e_max_ibe": 40.0,
    "p_1_inf_ibe": 0.74,
    "r": 1.0,
    "q": 0.4,
    "r_1": 0.26,
    "r_2": 2.0,
}
