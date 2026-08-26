"""Gather the EEmiLib exceptions."""


class NotImplementedPopulationError(NotImplementedError):
    """Error raised when the desired population does not exists."""


class MissingDataError(ValueError):
    """Error raised when data is missing."""


class MissingNormalEmissionYieldError(MissingDataError):
    """Error raised when emission yield at normal incidence would be needed."""
