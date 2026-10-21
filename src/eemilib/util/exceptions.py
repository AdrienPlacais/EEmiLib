"""Gather the EEmiLib exceptions."""


class NotImplementedPopulationError(NotImplementedError):
    """Error raised when the desired population does not exists."""


class NotImplementedEmissionDataTypeError(NotImplementedError):
    """Error raised when a not implemented data type is asked.

    Raised when ``data_type = "Emission Angle"``.

    """


class MissingDataError(ValueError):
    """Error raised when data is missing."""


class MissingNormalEmissionYieldError(MissingDataError):
    """Error raised when emission yield at normal incidence would be needed."""
