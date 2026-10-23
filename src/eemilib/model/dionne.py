r"""Create the Dionne model, to compute |SEEY|.

This is a physical model developed by Dionne :cite:`Lye1957,Dionne1973,
Dionne1975`.

.. todo::
   Handle the different implementations like :class:`~eemilib.model.FurmanPivi`
   does.

.. todo::
   Test suite for this model.

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
from collections.abc import Callable
from typing import Any, ClassVar, Literal, TypedDict, cast

import numpy as np
import pandas as pd
from numpy.typing import NDArray

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

#: Models for the energy loss of |PEs| in the material. See
#: :func:`.dionne.range_func` for more information.
EnergyLossModel = Literal["Power law", "CSDA", "Inguimbert"]
ENERGY_LOSS_MODELS = ("Power law", "CSDA", "Inguimbert")


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
            "description": (
                "Energy required to excite a secondary electron in the "
                "material."
            ),
            "is_locked": True,
        },
        "diffusion_length": {
            "markdown": DIFFUSION_LENGTH,
            "unit": "nm",
            "value": 2.0,
            "lower_bound": 0.0,
            "description": (
                "Typical length between two interactions of the SE with the "
                "material. Related to elastic and inelastic mean free paths."
            ),
        },
        "escape_probability": {
            "markdown": ESCAPE_PROBABILITY,
            "unit": "1",
            "value": 0.5,
            "lower_bound": 0.0,
            "upper_bound": 1.0,
            "description": "Probability for the SE to escape the material.",
        },
        "power_law_scale": {
            "markdown": POWER_LAW_SCALE,
            "unit": "1",
            "value": 1.0,
            "lower_bound": 0.0,
            "description": "Scale factor in the power law energy loss model.",
        },
        "power_law_exponent": {
            "markdown": POWER_LAW_EXPONENT,
            "unit": "1",
            "value": 1.2,
            "lower_bound": 1.0,
            "description": "Exponent in the power law energy loss model.",
        },
    }
    implementation_choices: ClassVar[dict[str, tuple[str, ...]]] = {
        "Energy Loss Model": ENERGY_LOSS_MODELS
    }
    _url_doc_override = "manual/models/dionne"

    def __init__(
        self,
        parameters_values: dict[str, Any] | None = None,
        energy_loss_model: EnergyLossModel = "Power law",
    ) -> None:
        r"""Instantiate the object.

        Parameters
        ----------
        parameters_values :
            Contains name of parameters and associated value. If provided, will
            override the default values set in ``initial_parameters``.
        energy_loss_model :
            Model for the energy loss of PEs in the material. Only ``"Power
            law"`` is implemented for now. Check documentation of
            :func:`.dionne.range_func` for more info.

        """
        for parameters_kwargs in self.initial_parameters.values():
            self.add_original_notation(parameters_kwargs, "Dionne")
        super().__init__(parameters_values)
        self.parameters = cast(DionneParameters, self.parameters)
        self._energy_loss_model: EnergyLossModel = energy_loss_model
        self._range_func: RangeFunc
        self.set_implementation("Energy loss model", energy_loss_model)

    def set_implementation(self, name: str, value: str) -> None:
        r"""Update one implementation axis.

        Parameters
        ----------
        name :
            Name of the implementation axis. Currently, only ``"Energy loss
            model"`` is accepted.
        value :
            New value for the energy loss model.

        """
        if name == "Energy loss model":
            if value not in ENERGY_LOSS_MODELS:
                logging.error(
                    f"Unknown value for {name}: {value}.\nAllowed values: "
                    f"{ENERGY_LOSS_MODELS}"
                )
                return

            self._range_func = _set_range_function(value)
            self.current_implementations["Energy loss model"] = value
            return

        logging.error(f"Unknown implementation axis {name = } for Dionne.")

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
        out = np.zeros(len(energy))

        for i, ene in enumerate(energy):
            out[i] = dionne_func(
                ene, range_func=self._range_func, **self.parameters
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
                emission_yield.energies, range_func=self._range_func, **kwargs
            )
            return measured - predicted

        keys = (
            "excitation_energy",
            "diffusion_length",
            "escape_probability",
            "power_law_scale",  # FIXME: Only for Power law
            "power_law_exponent",  # FIXME: Only for Power law
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
# Range functions
# =============================================================================
RangeFunc = Callable[
    [NDArray[np.float64] | float], NDArray[np.float64] | float
]


def power_law_range(
    ene: float | NDArray[np.float64],
    *,
    power_law_scale: Parameter | float,
    power_law_exponent: Parameter | float,
    **kwargs,
) -> float | NDArray[np.float64]:
    r"""Compute penetration depth of |PE|.

    We make the assumption that |PE| looses its energy following a power law or
    Thomson-Whiddington model :cite:`Whiddington1914`.

    .. math::
       R = \frac{E^n}{A\cdot n}

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


def csda_range(
    ene: float | NDArray[np.float64], **kwargs
) -> float | NDArray[np.float64]:
    r"""Compute penetration depth of |PE|.

    We make the assumption that |PE| looses its energy following a continuous
    energy loss. This is *Continuous Slowing-Down Approximation* (CSDA)
    :cite:`Young1956`, which may be better suited than power low at low
    energies.

       .. math::
          \frac{\mathrm{d}E}{\mathrm{d}x} = - E / R

    .. note::
       CSDA may also be incorrect at low-energies, were range is almost
       constant. See Ref. :cite:`Inguimbert2017,Inguimbert2017a` for an
       alternative model.

    Parameters
    ----------
    ene :
        |PEs| energy in :unit:`eV`.
    kwargs :
        For future model implementations.

    Returns
    -------
        Corresponding ranges in :unit:`nm`.

    """
    raise NotImplementedError


def inguimbert_range(
    ene: float | NDArray[np.float64], **kwargs
) -> float | NDArray[np.float64]:
    r"""Compute penetration depth of |PE|.

    We make the assumption that |PE| looses its energy following Inguimbert
    proposition :cite:`Inguimbert2017,Inguimbert2017a`.

    Parameters
    ----------
    ene :
        |PEs| energy in :unit:`eV`.
    kwargs :
        For future model implementations.

    Returns
    -------
        Corresponding ranges in :unit:`nm`.

    """
    raise NotImplementedError


def _set_range_function(model: EnergyLossModel = "Power law") -> RangeFunc:
    """Set the function that computes the range.

    This let you choose between three range function models.

    Parameters
    ----------
    model :
        Name of the model to use.

    Return
    ------
        A function that takes in the energy in :unit:`eV`, model parameters,
        and returns the corresponding range(s) in :unit:`nm`.

    """
    if model == "Power law":
        return power_law_range

    if model == "CSDA":
        return csda_range

    if model == "Inguimbert":
        raise NotImplementedError

    logging.error(f"{model = } does not exist, falling back on power law.")
    return power_law_range


# =============================================================================
# Dionne model
# =============================================================================
def dionne_func(
    ene: float | NDArray[np.float64],
    excitation_energy: Parameter | float,
    diffusion_length: Parameter | float,
    escape_probability: Parameter | float,
    range_func: RangeFunc,
    **parameters,
) -> float | NDArray[np.float64]:
    r"""Compute the |SEEY| for incident energy E.

    The |SEEY| is given by:

    .. math::
       \delta = G \cdot T \cdot S

    where :math:`G` is the mean number of |SEs| generated by the |PE|.
    :math:`T` is their probability to reach the surface. :math:`S` is their
    probability to cross the surface.

    """
    R = range_func(ene, **parameters)
    G = generation(ene, R, excitation_energy)
    T = transport(R, diffusion_length)
    S = escape_probability
    return G * T * S


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


def transport(
    range: float | NDArray[np.float64], diffusion_length: Parameter | float
) -> float | NDArray[np.float64]:
    r"""Compute the transport term.

    This is the probability for a generated secondary electron to reach the
    sample surface.

    .. math::
       T = d\left(1-\mathrm{e}^{-R/d}\right)

    Parameters
    ----------
    range :
        |PE| range in :unit:`nm`.
    diffusion_length :
        Typical length between two interactions between the |SE| and the
        material, in :unit:`nm`.

    Returns
    -------
        Probabiliy for a |SE| to reach the surface.

    """
    return diffusion_length * (1 - np.exp(-range / diffusion_length))


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += Dionne._generate_parameter_docs()
