"""Different exceptions pertaining to pyaims."""


class PyaimsError(Exception):
    """A general Pyaims exception."""


class InvalidSpeciesInput(PyaimsError):
    """Exception raised if an error occurs when creating species' defaults."""


class AimsParseError(PyaimsError):
    """Exception raised if an error occurs when parsing an Aims output file."""
