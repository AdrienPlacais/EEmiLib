"""Define a model parameter."""

import numpy as np


class Parameter:
    """An electron emission model parameter."""

    _tol: float = 1e-10

    def __init__(
        self,
        markdown: str,
        unit: str = "1",
        value: float = 0.0,
        *,
        lower_bound: float = -np.inf,
        upper_bound: float = np.inf,
        description: str = "",
        is_locked: bool = False,
    ) -> None:
        """Instantiate the parameter.

        Parameters
        ----------
        markdown : str
            The name of the parameter, in markdown format.
        unit : str, optional
            The unit of the parameter. The default is ``"1"`` (no unit).
        value : float, optional
            A first value for the parameter. The default is ``0.``.
        lower_bound : float, optional
            A first lower bound for the parameter. The default is ``-np.inf``.
        upper_bound : float, optional
            A first upper bound for the parameter. The default is ``np.inf``.
        description : str, optional
            A description string for the parameter. The default is an empty
            string.

        """
        self.markdown = markdown
        self.unit = unit
        self._value = value
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self.description = description
        self.is_locked = is_locked

    def __repr__(self) -> str:
        """Print out name of parameter and current value."""
        return f"{self.name} ({self.unit}): {self.value} {self.description}"

    @property
    def name(self) -> str:
        """Return markdown name of parameter with its unit."""
        return f"{self.markdown} [{self.unit}]"

    @property
    def value(self) -> float:
        """Give the current value of the parameter."""
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        """Set the value of the parameter."""
        self._value = value
        if not self.is_locked:
            return
        self._set_tiny_bounds()

    @property
    def lower_bound(self) -> float:
        """Give the current lower bound of the parameter."""
        return self._lower_bound

    @lower_bound.setter
    def lower_bound(self, lower_bound: float) -> None:
        """Set the lower bound of the parameter."""
        self._lower_bound = lower_bound
        return

    @property
    def upper_bound(self) -> float:
        """Give the current upper bound of the parameter."""
        return self._upper_bound

    @upper_bound.setter
    def upper_bound(self, upper_bound: float) -> None:
        """Set the upper bound of the parameter."""
        self._upper_bound = upper_bound
        return

    def lock(self) -> None:
        """Set the parameter to its current value."""
        self.is_locked = True
        self._set_tiny_bounds()

    def unlock(self) -> None:
        """Allow parameter to be changed again during optimisation."""
        self.is_locked = False
        self.lower_bound = -np.inf
        self.upper_bound = +np.inf

    def _set_tiny_bounds(self) -> None:
        """Set tiny bounds around :attr:`value`."""
        bound_1, bound_2 = self.value - self._tol, self.value + self._tol
        self.lower_bound = min(bound_1, bound_2)
        self.upper_bound = max(bound_1, bound_2)
