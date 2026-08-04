"""Define a model parameter."""

import logging

import numpy as np


class Parameter:
    """An electron emission model parameter.

    Actual parameter value is stored in :attr:`.value`, but you can perform
    most float operations directly on the instance:

    .. code-block:: python

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

    #: This tricky ass attribute tells numpy to always defer to Python's
    #: operator protocol (our own __radd__, __rmul__, etc.) instead of trying
    #: to coerce this object into an array first. Without this, expressions
    #: like ``ndarray + parameter`` can silently produce object-dtype arrays
    #: instead of float64 ones. This is not an immediate problem, but we cannot
    #: use these kind of arrays in a function like np.exp.
    __array_ufunc__ = None

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
        if not isinstance(value, (float, int)):
            if isinstance(value, np.ndarray) and len(value) == 1:
                value = float(value[0])
            else:
                raise ValueError(f"Trying to set unsupported {value = }")
        if self._value == value:
            logging.debug(f"{self.name:<52}: is already {value}.")
        else:
            debug = (
                f"{self.name:<52}: updating {self._value:<35} -> {value:<35}"
            )
            if abs(value - self.lower_bound) < 0.5 * self._tol:
                debug += " new value very close to lower bound "
            if abs(value - self.upper_bound) < 0.5 * self._tol:
                debug += " new value very close to upper bound "
            logging.debug(debug)
        self._value = value

    @property
    def lower_bound(self) -> float:
        """Give the current lower bound of the parameter.

        - If the parameter is not locked, we return the user-defined value
          stored in :attr:`.self._lower_bound`.
        - If it is locked, we return a lower bound that is :attr:`self._tol`
          lower than currently store value.
          - Exception : if the user-defined :attr:`._lower_bound` is exactly
            ``0.0``, we suppose that the value should stay positive. We update
            the returned lower bound accordingly.

        """
        if self.is_locked:
            bound = min(self.value - self._tol, self.value + self._tol)
            if self._lower_bound != 0.0 or abs(bound) >= self._tol:
                return bound
            # _lower_bound is exactly 0.0, and calculated bound is very close
            # to 0: we enforce lower bound to 0.0 to avoid negative values
            return 0.0
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
