class IDriveE2Error(Exception):
    """Base error for IDrive e2 client."""


class InvalidAuth(IDriveE2Error):
    """Raised when credentials are invalid."""


class CannotConnect(IDriveE2Error):
    """Raised when the service is unreachable or returns a bad response."""
