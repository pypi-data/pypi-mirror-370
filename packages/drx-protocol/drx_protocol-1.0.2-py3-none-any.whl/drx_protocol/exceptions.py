"""Drx exceptions."""


class DrxError(Exception):
    """Base DrX error class"""


class ApiError(DrxError):
    """Raised when API returns an error code"""


class MessageIdError(DrxError):
    """Raised when the received message id does not match the send message id"""


class UnexpectedPayload(DrxError):
    """Raised when the payload is mallformed"""


class InvalidParameter(DrxError):
    """Raised when a function is called with invalid parameters"""


class LicenseInvalidError(DrxError):
    """Raised when an API call returns credentials issue"""


class DrxConnectionError(DrxError):
    """Wraps around connection errors for API calls"""


class DrxTimeoutError(DrxError):
    """Wraps around asyncio.TimeoutError for API calls"""
