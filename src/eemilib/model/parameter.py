"""Define a model parameter."""

import numpy as np


class Parameter:
    """An electron emission model parameter.

    Actual parameter value is stored in :attr:`.value`, but you can perform
    most float operations directly on the instance:

    .. codeblock:: python

       param: Parameter(...)

       # Valid operations:
       param + 5
       param ** 3
       5 - param
       param <= 10
       10 < param
       # ...

       # ===========================================
       # This one is the only one to be unsupported:
       param == 210
       # ===========================================

    """

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
        markdown :
            The name of the parameter, in markdown format.
        unit :
            The unit of the parameter.
        value :
            A first value for the parameter.
        lower_bound :
            A first lower bound for the parameter.
        upper_bound :
            A first upper bound for the parameter.
        description :
            A description string for the parameter.
        is_locked :
            Forces the parameters to a certain value, which will not be
            modified by EEmiLib.

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

    def __str__(self) -> str:
        """Return name of parameter, its value and its unit."""
        return f"{self.value:.3f} [{self.unit}]"

    def __float__(self) -> float:
        """Allow ``float(self)`` to return stored value.

        Most libraries will vall ``float(parameter_instance)`` when
        encountering object.

        """
        return self.value

    def __add__(self, other) -> float:
        """Allow ``self + other`` operation."""
        return self.value + other

    def __radd__(self, other):
        """Allow ``other + self `` operation."""
        return other + self.value

    def __sub__(self, other):
        """Allow ``self - other`` operation."""
        return self.value - other

    def __rsub__(self, other):
        """Allow ``other - self `` operation."""
        return other - self.value

    def __mul__(self, other):
        """Allow ``self * other`` operation."""
        return self.value * other

    def __rmul__(self, other):
        """Allow ``other * self `` operation."""
        return other * self.value

    def __truediv__(self, other):
        """Allow ``self / other`` operation."""
        return self.value / other

    def __rtruediv__(self, other):
        """Allow ``other / self `` operation."""
        return other / self.value

    def __pow__(self, other):
        """Allow ``self ** other`` operation."""
        return self.value**other

    def __rpow__(self, other):
        """Allow ``other ** self `` operation."""
        return other**self.value

    def __neg__(self) -> float:
        """Allow ``-self`` operation."""
        return -self.value

    def __abs__(self) -> float:
        """Allow ``abs(self)`` operation."""
        return abs(self.value)

    def __lt__(self, other):
        """Allow ``self < other`` operation."""
        return self.value < other

    def __rlt__(self, other):
        """Allow ``other < self `` operation."""
        return other < self.value

    def __le__(self, other):
        """Allow ``self <= other`` operation."""
        return self.value <= other

    def __rle__(self, other):
        """Allow ``other <= self `` operation."""
        return other <= self.value

    def __gt__(self, other):
        """Allow ``self > other`` operation."""
        return self.value > other

    def __rgt__(self, other):
        """Allow ``other > self `` operation."""
        return other > self.value

    def __ge__(self, other):
        """Allow ``self >= other`` operation."""
        return self.value >= other

    def __rge__(self, other):
        """Allow ``other >= self `` operation."""
        return other >= self.value

    @property
    def name(self) -> str:
        """Return markdown name of parameter with its unit."""
        return f"${self.markdown}$ [{self.unit}]"

    @property
    def value(self) -> float:
        """Give the current value of the parameter."""
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        """Set the value of the parameter."""
        self._value = value

    @property
    def lower_bound(self) -> float:
        """Give the current lower bound of the parameter."""
        if self.is_locked:
            return min(self.value - self._tol, self.value + self._tol)
        return self._lower_bound

    @lower_bound.setter
    def lower_bound(self, lower_bound: float) -> None:
        """Set the lower bound of the parameter."""
        self._lower_bound = lower_bound
        return

    @property
    def upper_bound(self) -> float:
        """Give the current upper bound of the parameter."""
        if self.is_locked:
            return max(self.value - self._tol, self.value + self._tol)
        return self._upper_bound

    @upper_bound.setter
    def upper_bound(self, upper_bound: float) -> None:
        """Set the upper bound of the parameter."""
        self._upper_bound = upper_bound
        return

    def lock(self) -> None:
        """Set the parameter to its current value."""
        if self.is_locked:
            return
        self.is_locked = True

    def unlock(self) -> None:
        """Allow parameter to be changed again during optimisation."""
        if not self.is_locked:
            return
        self.is_locked = False
