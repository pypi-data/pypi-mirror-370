class AutonomiError(Exception):
    """Base error raised by dweb autonomi wrapper."""


class InvalidAddressError(AutonomiError):
    """Raised when an invalid data address is supplied."""


class NetworkError(AutonomiError):
    """Raised when there is a network/client level error."""


