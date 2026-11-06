"""Gather the EEmiLib exceptions."""

from collections.abc import Sequence


class NotImplementedPopulationError(NotImplementedError):
    """Error raised when the desired population does not exists."""


class NotImplementedEmissionDataTypeError(NotImplementedError):
    """Error raised when a not implemented data type is asked.

    Raised when ``data_type = "Emission Angle"``.

    """


class MissingDataError(ValueError):
    """Error raised when data is missing.

    It can happen either because a :class:`.DataMatrix` does not hold required
    data, or because no :class:`.DataMatrix` could be found.

    """

    def __init__(
        self, message: str = "", *, missing: Sequence[tuple[str, str]] = ()
    ) -> None:
        """Init error with optional list of missing data."""
        self.missing = tuple(missing)
        if self.missing:
            details = ", ".join(
                f"{data_type} ({pop})" for data_type, pop in self.missing
            )
            message = f"{message} Missing: {details}.".strip()
        super().__init__(message)


class MissingNormalEmissionYieldError(MissingDataError):
    """Error raised when emission yield at normal incidence would be needed."""
