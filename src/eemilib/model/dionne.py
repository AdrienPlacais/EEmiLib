r"""Create the Dionne model, to compute |SEEY|.

This is a physical model developed by Dionne :cite:`Lye1957,Dionne1973,
Dionne1975`.

"""

# work_function :
#     Material work function in :unit:`eV`. This parameter is mandatory
#     in order to set the value of :math:`\xi`. More information in
#     :func:`.dionne.generation` documentation.
# if work_function is None:
#     logging.warning(
#         "The work function is mandatory to set the value of the "
#         "excitation energy. Please set excitation energy manually "
#         "before proceeding to the fit."
#     )

import logging
from typing import Any, ClassVar, Literal, TypedDict, cast

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from scipy.integrate import quad_vec
from scipy.special import expn

from eemilib.core.model_config import ModelConfig
from eemilib.emission_data import DataMatrix
from eemilib.model.model import Model
from eemilib.model.parameter import Parameter
from eemilib.util.constants import (
    COL_ENERGY,
    ImplementedEmissionData,
    ImplementedPop,
)
from eemilib.util.markdown import (
    DIFFUSION_LENGTH,
    ESCAPE_PROBABILITY,
    EXCITATION_ENERGY,
    POWER_LAW_EXPONENT,
    POWER_LAW_SCALE,
)

#: Models for the energy loss of |PEs| in the material.
EnergyLoss = Literal["Power law", "Constant loss"]
ENERGY_LOSS = ("Power law", "Constant loss")

#: Models for scattering of secondaries
Scattering = Literal["1D", "3D"]
SCATTERING = ("1D", "3D")


class DionneParameters(TypedDict):
    """Parameters for :class:`.Dionne`."""

    excitation_energy: Parameter
    diffusion_length: Parameter
    escape_probability: Parameter
    power_law_scale: Parameter
    power_law_exponent: Parameter


class Dionne(Model):
    """Define the Dionne model :cite:`Lye1957,Dionne1973,Dionne1975`."""

    data_types = ("Emission Yield",)
    populations = ("SE",)
    considers_energy = True
    is_3d = False
    is_dielectrics_compatible = False
    model_config = ModelConfig(
        emission_yields=("SE",), emission_energies=(), emission_angles=()
    )
    initial_parameters: ClassVar[dict[str, dict[str, str | float | bool]]] = {
        "excitation_energy": {
            "markdown": EXCITATION_ENERGY,
            "unit": "eV",
            "value": 4.6,
            "lower_bound": 0.0,
            "upper_bound": 30.0,
            "description": (
                "Energy required to excite a secondary electron in the "
                "material."
            ),
            "is_locked": True,
            "original_notation": r"\xi",
        },
        "diffusion_length": {
            "markdown": DIFFUSION_LENGTH,
            "unit": "nm",
            "value": 2.0,
            "lower_bound": 0.0,
            "upper_bound": 20.0,
            "description": (
                "Typical length between two interactions of the SE with the "
                "material. Related to elastic and inelastic mean free paths."
            ),
            "original_notation": r"1/\alpha",
        },
        "escape_probability": {
            "markdown": ESCAPE_PROBABILITY,
            "unit": "1",
            "value": 0.5,
            "lower_bound": 0.0,
            "upper_bound": 1.0,
            "description": "Probability for the SE to escape the material.",
            "original_notation": "B",
        },
        "power_law_scale": {
            "markdown": POWER_LAW_SCALE,
            "unit": "1",
            "value": 1.0,
            "lower_bound": 0.0,
            "upper_bound": 50.0,
            "description": "Scale factor in the power law energy loss model.",
        },
        "power_law_exponent": {
            "markdown": POWER_LAW_EXPONENT,
            "unit": "1",
            "value": 1.2,
            "lower_bound": 1.0,
            "upper_bound": 5.0,
            "description": "Exponent in the power law energy loss model.",
        },
    }
    implementation_choices: ClassVar[dict[str, tuple[str, ...]]] = {
        "energy_loss": ENERGY_LOSS,
        "secondary_scattering": SCATTERING,
    }
    _url_doc_override = "manual/models/dionne"

    def __init__(
        self,
        parameters_values: dict[str, Any] | None = None,
        energy_loss: EnergyLoss = "Constant loss",
        secondary_scattering: Scattering = "1D",
    ) -> None:
        r"""Instantiate the object.

        Parameters
        ----------
        parameters_values :
            Contains name of parameters and associated value. If provided, will
            override the default values set in ``initial_parameters``.
        energy_loss :
            Model for the energy loss of PEs in the material, *cf* Eqs (16) and
            (26) in Ref. :cite:`Dionne1973`.
        secondary_scattering :
            Whether |SEs| propagate through the surface in 1D or 3D, *cf* Eqs
            (3) and (10) in Ref. :cite:`Dionne1973`.

        """
        for parameters_kwargs in self.initial_parameters.values():
            self.add_original_notation(parameters_kwargs, "Dionne")
        super().__init__(parameters_values)
        self.parameters = cast(DionneParameters, self.parameters)

        self._energy_loss: EnergyLoss
        self._secondary_scattering: Scattering
        self.set_implementation("energy_loss", energy_loss)
        self.set_implementation("secondary_scattering", secondary_scattering)

    def set_implementation(self, name: str, value: str) -> None:
        r"""Update one implementation axis.

        Parameters
        ----------
        name :
            Name of the implementation axis. ``"energy_loss"`` or
            ``"secondary_scattering"``.
        value :
            New value.

        """
        choices = self.implementation_choices.get(name)
        if choices is None:
            logging.error(f"Unknown implementation axis {name = } for Dionne.")
            return
        if value not in choices:
            logging.error(
                f"Unknown value for {name}: {value}.\nAllowed: {choices}"
            )
            return
        setattr(self, f"_{name}", value)
        self.current_implementations[name] = value

    def compute_data(
        self,
        data_type: ImplementedEmissionData,
        population: ImplementedPop,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        *args,
        **kwargs,
    ) -> pd.DataFrame | None:
        """Return desired data according to current model.

        Will return a dataframe only if the |TEEY| is asked.

        """
        if population != "SE" or data_type != "Emission Yield":
            return super().compute_data(
                data_type, population, energy, theta, *args, **kwargs
            )

        out = dionne_func(
            energy,
            energy_loss=self._energy_loss,
            scattering=self._secondary_scattering,
            **self.parameters,
        )

        out_dict = {
            COL_ENERGY: energy,
            **{f"{the} [deg]": out for the in theta},
        }
        return pd.DataFrame(out_dict)

    def _find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        """Extract main |SEEY| curve parameters from measure."""
        emission_yield = data_matrix.seey
        assert emission_yield.population == "SE"

        def _residue(kwargs: dict[str, float]) -> NDArray[np.float64]:
            measured = emission_yield.normal_data
            predicted = dionne_func(
                emission_yield.energies,
                energy_loss=self._energy_loss,
                scattering=self._secondary_scattering,
                **kwargs,
            )
            return measured - predicted

        keys = (
            "excitation_energy",
            "diffusion_length",
            "escape_probability",
            "power_law_scale",
            "power_law_exponent",
        )
        self._fit(keys, _residue)

    def evaluate(
        self, data_matrix: DataMatrix | None = None
    ) -> dict[str, float]:
        """Evaluate the quality of the model using Fil criterions.

        Fil criterions :cite:`Fil2016a,Fil2020` are adapted to |TEEY| models.

        """
        return self._evaluate_for_teey_models(
            self._resolve_data_matrix(data_matrix)
        )


# =============================================================================
# |PEs| penetration
# =============================================================================
def generation(
    ene: float | NDArray[np.float64],
    range: float | NDArray[np.float64],
    excitation_energy: Parameter | float,
    atol: float = 1e-12,
) -> float | NDArray[np.float64]:
    r"""Compute the generation term.

    This is the probability for an incident electron with an energy ``ene`` to
    generate a secondary electron.

    .. math::
       G = \frac{1}{R}\frac{E}{\xi}

    This is obtained by integrating the average number of |SEs| produced per
    |PE| of energy :math:`E`, in a layer of thickness :math:`\mathrm{d}x` at
    depth :math:`x` denoted :math:`n(x, E)\mathrm{d}x`, with the hypothesis
    that :math:`n(x,E)` is proportional to the average energy loss per unit
    path length.

    Parameters
    ----------
    ene :
        |PEs| energy in :unit:`eV`.
    range :
        Corresponding ranges in :unit:`nm`.
    excitation_energy :
        Energy required to excite a secondary electron in the material in
        :unit:`eV`.
    atol :
        Absolute tolerance to reject ranges too close to 0.

    Returns
    -------
        Probabiliy for an electron to generate secondary electrons.

    """
    ene = np.asarray(ene, dtype=np.float64)
    range = np.asarray(range, dtype=np.float64)
    valid = ~np.isclose(range, 0, atol=atol)

    result = np.zeros_like(range, dtype=float)
    result[valid] = ene[valid] / (range[valid] * excitation_energy)

    if np.isscalar(ene) and np.isscalar(range):
        return float(result)

    return result


def power_law_range(
    ene: float | NDArray[np.float64],
    *,
    power_law_scale: Parameter | float,
    power_law_exponent: Parameter | float,
    **kwargs,
) -> float | NDArray[np.float64]:
    r"""Compute penetration depth of |PE|.

    We make the assumption that |PE| looses its energy following a power law or
    Thomson-Whiddington model :cite:`Whiddington1914`:

    .. math::
       \frac{\mathrm{d}e}{\mathrm{d}x} = - \frac{A}{e^{n-1}}

    where :math:`A` is the power law scale, :math:`n>1` the power law
    exponent, :math:`E` the impact energy. Integrating this over the full |PE|
    path gives:

    .. math::
       R = \frac{E^n}{A\cdot n}

    This is Eq.~(13) in Dionne paper :cite:`Dionne1973`.

    .. note::
       It was shown that it was not adapted at low energies.

    Parameters
    ----------
    ene :
        |PEs| energy in :unit:`eV`.
    power_law_scale :
        Power law parameter :math:`A`.
    power_law_exponent :
        Power law parameter :math:`n`.
    kwargs :
        For future model implementations.

    Returns
    -------
        Corresponding ranges in :unit:`nm`.

    """
    return ene**power_law_exponent / (power_law_scale * power_law_exponent)


# =============================================================================
# |SEs| transport functions
# =============================================================================
def _escape_profile(
    x: NDArray[np.float64],
    diffusion_length: Parameter | float,
    scattering: Scattering,
) -> NDArray[np.float64]:
    r"""Give the shape of the |SE| escape probability.

    This is :math:`f(x)/S` in Eqs. (3) and (10) of :cite:`Dionne1973`:

    .. math::
       \mathrm{e}^{-x/d} \quad \text{(1D)}, \qquad
       \frac{1}{2} E_2(x/d) \quad \text{(3D)}

    where :math:`E_n(z) = \int_1^\infty \mathrm{e}^{-zt} t^{-n}\,
    \mathrm{d}t` is the generalized exponential integral.

    Parameters
    ----------
    x :
        Emission depth of the |SE| in :unit:`nm`.
    diffusion_length :
        Typical length between two interactions of the |SE| with the
        material, in :unit:`nm`.
    scattering :
        Model for |SE| transport.

    """
    t = x / diffusion_length
    if scattering == "1D":
        return np.exp(-t)
    return 0.5 * expn(2, t)


def transport_constant_loss(
    range: float | NDArray[np.float64],
    diffusion_length: Parameter | float,
    scattering: Scattering = "1D",
) -> float | NDArray[np.float64]:
    r"""Compute the transport term for a constant energy loss.

    This is the probability, times a length, for a generated |SE| to reach the
    surface. In 1D, Eq. (26) of :cite:`Dionne1973`:

    .. math::
       T = d\left(1 - \mathrm{e}^{-R/d}\right)

    In 3D, Eq. (29):

    .. math::
       T = \frac{d}{4}\left(1 - 2 E_3(R/d)\right)

    Parameters
    ----------
    range :
        |PE| range :math:`R` in :unit:`nm`.
    diffusion_length :
        Diffusion length :math:`d` in :unit:`nm`.
    scattering :
        Model for |SE| transport.

    """
    d = float(diffusion_length)
    if scattering == "1D":
        return d * (1.0 - np.exp(-range / d))
    return 0.25 * d * (1.0 - 2.0 * expn(3, range / d))


def transport_power_law(
    range: NDArray[np.float64],
    power_law_exponent: Parameter | float,
    diffusion_length: Parameter | float,
    scattering: Scattering = "1D",
) -> NDArray[np.float64]:
    r"""Compute the transport term for a power law energy loss.

    Eqs. (16) and (20) of :cite:`Dionne1973`. The substitution
    :math:`x = R(1 - w^n)` removes the integrable singularity at
    :math:`x = R`:

    .. math::
       T = R \int_0^1 \frac{f(R(1 - w^n))}{S}\,\mathrm{d}w

    Parameters
    ----------
    range :
        |PE| range :math:`R` in :unit:`nm`.
    power_law_exponent :
        Exponent :math:`n` of the power law.
    diffusion_length :
        Diffusion length :math:`d` in :unit:`nm`.
    scattering :
        Model for |SE| transport.

    """
    n = float(power_law_exponent)
    d = float(diffusion_length)

    def integrand(w: float) -> NDArray[np.float64]:
        return _escape_profile(range * (1.0 - w**n), d, scattering)

    mean_escape, _ = quad_vec(integrand, 0.0, 1.0)
    return range * mean_escape


# =============================================================================
# Dionne model
# =============================================================================
def dionne_func(
    ene: float | NDArray[np.float64],
    excitation_energy: Parameter | float,
    diffusion_length: Parameter | float,
    escape_probability: Parameter | float,
    power_law_scale: Parameter | float,
    power_law_exponent: Parameter | float,
    energy_loss: EnergyLoss = "Constant loss",
    scattering: Scattering = "1D",
    **parameters,
) -> float | NDArray[np.float64]:
    r"""Compute the |SEEY| for incident energy E.

    The |SEEY| is given by:

    .. math::
       \delta = G \cdot T \cdot S

    where :math:`G` is the mean number of |SEs| generated by the |PE|.
    :math:`T` is their probability to reach the surface. :math:`S` is their
    probability to cross the surface.

    Parameters
    ----------
    ene :
        |PEs| energy in :unit:`eV`.
    excitation_energy :
        Energy required to excite a secondary electron in the material.
    diffusion_length :
        Typical length between two interactions of the SE with the material.
        Related to elastic and inelastic mean free paths.
    escape_probability :
        Probability for the SE to escape the material.
    power_law_scale :
        Scale factor in the power law energy loss model.
    power_law_exponent :
        Exponent in the power law energy loss model.
    energy_loss :
        ``"Constant loss"``: :math:`\delta = G \cdot T \cdot S`, where
        :math:`G` is the mean number of |SEs| generated by the |PE|, :math:`T`
        their probability to reach the surface, :math:`S` their probability to
        cross it. ``"Power law"``: numerical integration of Eq. (16)/(20).
    scattering :
        Scattering model for the SEs.
    parameters :
        Additional unused parameters.

    """
    ene = np.atleast_1d(np.asarray(ene, dtype=np.float64))
    R = power_law_range(
        ene,
        power_law_scale=power_law_scale,
        power_law_exponent=power_law_exponent,
    )
    G = generation(ene, R, excitation_energy)
    if energy_loss == "Constant loss":
        T = transport_constant_loss(R, diffusion_length, scattering)
    elif energy_loss == "Power law":
        T = transport_power_law(
            R, power_law_exponent, diffusion_length, scattering
        )
    else:
        raise ValueError(f"Unknown {energy_loss = }")
    S = escape_probability
    return G * T * S


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += Dionne._generate_parameter_docs()
