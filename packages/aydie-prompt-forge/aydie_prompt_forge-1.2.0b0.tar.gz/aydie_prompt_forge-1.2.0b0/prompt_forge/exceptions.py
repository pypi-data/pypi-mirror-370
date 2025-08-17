class AydieException(Exception):
    """
    Base exception class for all errors raised by the prompt-forge library.

    This is the root exception for the Aydie brand of tools. Catching this
    will catch all custom errors defined in this library.
    """
    pass

class InvalidPromptFileError(AydieException, ValueError):
    """ 
    Raised when the prompt repository file is malformed.

    This can be due to incorrect YAML syntax, missing required fields
    (like 'id' or 'template'), or a structure that doesn't match the
    expected format (e.g., not a list of dictionaries).

    Inherits from both AydieException and ValueError for more flexible
    exception handling.
    """
    pass


class PromptNotFoundError(AydieException, KeyError):
    """
    Raised when a requested prompt ID is not found in the repository.

    Inherits from both AydieException and KeyError.
    """
    pass