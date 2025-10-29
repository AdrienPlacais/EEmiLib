r"""Create the Dionne model, to compute SEEY.

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

from functools import partial
from typing import Any, Literal, TypedDict

import numpy as np
import pandas as pd
from eemilib.core.model_config import ModelConfig
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.model.model import Model
from eemilib.model.parameter import Parameter
from eemilib.util.constants import (
    ImplementedEmissionData,
    ImplementedPop,
    col_energy,
    col_normal,
)
from numpy.typing import NDArray
from scipy.optimize import Bounds, least_squares

#: Models for the energy loss of PEs in the material. See
#: :func:`.dionne.range_func` for more information.
EnergyLossModel = Literal["Power law", "CSDA", "Inguimbert"]
ENERGY_LOSS_MODELS = ("Power law", "CSDA", "Inguimbert")


class DionneParameters(TypedDict):
    excitation_energy: Parameter
    diffusion_length: Parameter
    escape_probability: Parameter
    power_law_scale: Parameter
    power_law_exponent: Parameter


class Dionne(Model):
    """Define the Dionne model :cite:`Lye1957,Dionne1973,Dionne1975`."""

    emission_data_types = ["Emission Yield"]
    populations = ["SE"]
    considers_energy = True
    is_3d = False
    is_dielectrics_compatible = False
    model_config = ModelConfig(
        emission_yield_files=("SE",),
        emission_energy_files=(),
        emission_angle_files=(),
    )
    initial_parameters = {
        "excitation_energy": {
            "markdown": r"\xi",
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
            "markdown": "d",
            "unit": "nm",
            "value": 2.0,
            "lower_bound": 0.0,
            "description": (
                "Typical length between two interactions of the SE with the "
                "material. Related to elastic and inelastic mean free paths."
            ),
        },
        "escape_probability": {
            "markdown": "S",
            "unit": "1",
            "value": 0.5,
            "lower_bound": 0.0,
            "upper_bound": 1.0,
            "description": "Probability for the SE to escape the material.",
        },
        "power_law_scale": {
            "markdown": r"A",
            "unit": "1",
            "value": 1.0,
            "lower_bound": 0.0,
            "description": "Scale factor in the power law energy loss model.",
        },
        "power_law_exponent": {
            "markdown": r"n",
            "unit": "1",
            "value": 1.2,
            "lower_bound": 1.0,
            "description": "Exponent in the power law energy loss model.",
        },
    }

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
        super().__init__(url_doc_override="manual/models/dionne")
        self._energy_loss_model: EnergyLossModel = energy_loss_model
        self.parameters: DionneParameters = {  # type: ignore
            name: Parameter(**kwargs)  # type: ignore
            for name, kwargs in self.initial_parameters.items()
        }
        self._generate_parameter_docs()
        if parameters_values is not None:
            self.set_parameters_values(parameters_values)

        self._func = dionne_func

    def get_data(
        self,
        population: ImplementedPop,
        emission_data_type: ImplementedEmissionData,
        energy: NDArray[np.float64],
        theta: NDArray[np.float64],
        *args,
        **kwargs,
    ) -> pd.DataFrame | None:
        """Return desired data according to current model.

        Will return a dataframe only if the TEEY is asked.

        """
        if population != "SE" or emission_data_type != "Emission Yield":
            return super().get_data(
                population=population,
                emission_data_type=emission_data_type,
                energy=energy,
                theta=theta,
                *args,
                **kwargs,
            )
        out = np.zeros(len(energy))

        for i, ene in enumerate(energy):
            out[i] = self._func(ene, **self.parameters)

        out_dict = {col_normal: out, col_energy: energy}
        return pd.DataFrame(out_dict)

    def find_optimal_parameters(
        self, data_matrix: DataMatrix, **kwargs
    ) -> None:
        """Extract main SEEY curve parameters from measure."""
        if not data_matrix.has_all_mandatory_files(self.model_config):
            raise ValueError("Files are not all provided.")

        emission_yield = data_matrix.seey
        assert emission_yield.population == "SE"

        # Not very robust, but should be same order as in `_residue` func
        keys = (
            "excitation_energy",
            "diffusion_length",
            "escape_probability",
            "power_law_scale",
            "power_law_exponent",
        )
        params = [self.parameters[k] for k in keys]
        x0 = [param.value for param in params]
        bounds = Bounds(
            np.array([param.lower_bound for param in params]),
            np.array([param.upper_bound for param in params]),
        )
        fun = partial(_residue, energy_loss_model=self._energy_loss_model)

        lsq = least_squares(
            fun=_residue,
            x0=x0,
            bounds=bounds,
            args=(
                emission_yield.data[col_energy].to_numpy(),
                emission_yield.data[col_normal].to_numpy(),
            ),
        )

        optimized_values = {k: v for k, v in zip(keys, lsq.x, strict=True)}
        self.set_parameters_values(optimized_values)

    def evaluate(self, data_matrix: DataMatrix) -> dict[str, float]:
        """Evaluate the quality of the model using Fil criterions.

        Fil criterions :cite:`Fil2016a,Fil2020` are adapted to TEEY models.

        """
        return self._evaluate_for_teey_models(data_matrix)


def dionne_func(
    ene: float | NDArray[np.float64],
    excitation_energy: Parameter | float,
    diffusion_length: Parameter | float,
    escape_probability: Parameter | float,
    energy_loss_model: EnergyLossModel = "Power law",
    power_law_scale: Parameter | float | None = None,
    power_law_exponent: Parameter | float | None = None,
    **parameters,
) -> float | NDArray[np.float64]:
    r"""Compute the SEEY for incident energy E.

    The SEEY is given by:

    .. math::
       \delta = G \cdot T \cdot S

    where :math:`G` is the mean number of SEs generated by the PE. :math:`T` is
    their probability to reach the surface. :math:`S` is their probability to
    cross the surface.

    """
    R = range_func(
        ene,
        energy_loss_model=energy_loss_model,
        power_law_scale=power_law_scale,
        power_law_exponent=power_law_exponent,
        **parameters,
    )
    G = generation(ene, R, excitation_energy)
    T = transport(R, diffusion_length)
    S = (
        escape_probability.value
        if isinstance(escape_probability, Parameter)
        else escape_probability
    )
    return G * T * S


def range_func(
    ene: float | NDArray[np.float64],
    energy_loss_model: EnergyLossModel = "Power law",
    power_law_scale: Parameter | float | None = None,
    power_law_exponent: Parameter | float | None = None,
    **kwargs,
) -> float | NDArray[np.float64]:
    r"""Compute penetration depth of PE.

    We make the assumption that PE looses its energy following a power law or
    Thomson-Whiddington model :cite:`Whiddington1914`.

    .. math::
       R = \frac{E^n}{A\cdot n}

    .. note::
       This is currently the only model that is implemented. However, it was
       shown that it was not adapted at low energies. *Continuous Slowing-Down
       Approximation* (CSDA) :cite:`Young1956` may be better suited:

       .. math::
          \frac{\mathrm{d}E}{\mathrm{d}x} = - E / R

       CSDA may also be incorrect at low-energies, were range is almost
       constant. See Ref. :cite:`Inguimbert2017,Inguimbert2017a` for an
       alternative model.

    Parameters
    ----------
    ene :
        PEs energy in :unit:`eV`.
    energy_loss_model :
        Model for the energy loss of PEs along their path. Currently, the
        power law is the only one that is implememnted.
    power_law_scale :
        Power law parameter :math:`A`.
    power_law_exponent :
        Power law parameter :math:`n`.
    kwargs :
        For future model implementations.

    Returns
    -------
    float | NDArray[np.float64]
        Corresponding ranges in :unit:`nm`.

    """
    if energy_loss_model != "Power law":
        raise NotImplementedError(
            "The only PE energy loss model is the power law."
        )
    if not power_law_scale:
        raise RuntimeError("Power law model needs `A` parameter.")
    if not power_law_exponent:
        raise RuntimeError("Power law model needs `n` parameter.")
    n_value = (
        power_law_exponent.value
        if isinstance(power_law_exponent, Parameter)
        else power_law_exponent
    )
    A_value = (
        power_law_scale.value
        if isinstance(power_law_scale, Parameter)
        else power_law_scale
    )
    return ene**n_value / (A_value * n_value)


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
        PEs energy in :unit:`eV`.
    range :
        Corresponding ranges in :unit:`nm`.
    excitation_energy :
        Energy required to excite a secondary electron in the material in
        :unit:`eV`.

    Returns
    -------
    float | NDArray[np.float64]
        Probabiliy for an electron to generate secondary electrons.

    """
    xi_value = (
        excitation_energy.value
        if isinstance(excitation_energy, Parameter)
        else excitation_energy
    )
    ene = np.asarray(ene, dtype=np.float64)
    range = np.asarray(range, dtype=np.float64)
    valid = ~np.isclose(range, 0, atol=atol)

    result = np.zeros_like(range, dtype=float)
    result[valid] = ene[valid] / (range[valid] * xi_value)

    if np.isscalar(ene) and np.isscalar(range):
        return float(result)

    return result


def transport(
    range: float | NDArray[np.float64],
    diffusion_length: Parameter | float,
) -> float | NDArray[np.float64]:
    r"""Compute the transport term.

    This is the probability for a generated secondary electron to reach the
    sample surface.

    .. math::
       T = d\left(1-\mathrm{e}^{-R/d}\right)

    Parameters
    ----------
    range :
        PE range in :unit:`nm`.
    diffusion_length :
        Typical length between two interactions between the SE and the
        material, in :unit:`nm`.

    Returns
    -------
    float | NDArray[np.float64]
        Probabiliy for a SE to reach the surface.

    """
    d_value = (
        diffusion_length.value
        if isinstance(diffusion_length, Parameter)
        else diffusion_length
    )
    return d_value * (1 - np.exp(-range / d_value))


def _residue(
    x: tuple[float, float, float, float, float],
    ene: NDArray[np.float64],
    measured: NDArray[np.float64],
) -> NDArray[np.float64]:
    modelled = dionne_func(
        ene=ene,
        excitation_energy=x[0],
        diffusion_length=x[1],
        escape_probability=x[2],
        power_law_scale=x[3],
        power_law_exponent=x[4],
        energy_loss_model="Power law",
    )
    assert isinstance(modelled, np.ndarray)
    return modelled - measured


# Append dynamically generated docs to the module docstring
if __doc__ is None:
    __doc__ = ""
__doc__ += Dionne._generate_parameter_docs()
