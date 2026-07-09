r"""Emission yields and emission energy distribution of copper.

Quoting Furman and Pivi :cite:`Furman2002`:

Quoting Furman and Pivi :cite:`Furman2002`:

    The copper data was obtained at CERN from a chemically cleaned
    but not *in situ* vacuum-baked sample [24].
    We have used for our fits data for :math:`\delta(E_0)` in the
    range :math:`0\leq\E_0\leq 1000\,\mathrm{eV}` (Fig. 6), and of
    :math:`\mathrm{d}\delta/\mathrm{d}E` at :math:`E_0=10,\,20` and
    :math:`30\,\mathrm{eV}` (Fig. 7).

- Emission Yields:
  - Normal incidence
  - :math:`0` to :math:`1000\,\mathrm{eV}`
- Energy Distributions:
  - Normal incidence
  - |PE| energy is :math:`100\,\mathrm{eV}`.

Parameters are taken from Tab. 1 and 2 in Furman and Pivi paper
:cite:`Furman2002` (copper). Data generated using CST.

"""

furman_pivi_parameters_values = {
    # =====================================================================
    # Secondary Electrons (or "True Secondaries")
    # =====================================================================
    "normal_e_max_se": 276.8,
    "normal_delta_max": 1.8848,
    "t_1": 0.66,
    "t_2": 0.80,
    "t_3": 0.70,
    "t_4": 1.0,
    "s": 1.54,
    "eps_1": 1.5,
    "eps_2": 1.75,
    "eps_3": 1,
    "eps_4": 3.75,
    "eps_5": 8.5,
    "eps_6": 11.5,
    "eps_7": 2.5,
    "eps_8": 3,
    "eps_9": 2.5,
    "eps_10": 3,
    "p_1": 2.5,
    "p_2": 3.3,
    "p_3": 2.5,
    "p_4": 2.5,
    "p_5": 2.8,
    "p_6": 1.3,
    "p_7": 1.5,
    "p_8": 1.5,
    "p_9": 1.5,
    "p_10": 1.5,
    # =====================================================================
    # Elastically Backscattered Electrons (or "Reflected")
    # =====================================================================
    "normal_e_max_ebe": 0.0,
    "p_1_hat": 0.496,
    "sigma": 2,
    "p_1_inf_ebe": 0.07,
    "W": 60.86,
    "p": 1,
    "e_1": 0.26,
    "e_2": 2.0,
    # =====================================================================
    # Inelastically Backscattered Electrons (or "Rediffused")
    # =====================================================================
    "normal_e_max_ibe": 0.041,
    "p_1_inf_ibe": 0.2,
    "r": 0.104,
    "q": 0.5,
    "r_1": 0.26,
    "r_2": 2.0,
}
