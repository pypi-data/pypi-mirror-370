"""Exception classes for TRC20 monitoring."""


class TRC20MonitorError(Exception):
    """Base exception for TRC20 monitoring errors."""

    pass


class ConfigurationError(TRC20MonitorError):
    """Raised when there's a configuration error."""

    pass


class ValidationError(TRC20MonitorError):
    """Raised when input validation fails."""

    pass


class APIError(TRC20MonitorError):
    """Raised when API calls fail."""

    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        """Initialize APIError.
        
        Args:
            message: Error message
            status_code: HTTP status code if applicable
            response_text: Raw response text if applicable
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class DatabaseError(TRC20MonitorError):
    """Raised when database operations fail."""

    pass


class NotificationError(TRC20MonitorError):
    """Raised when notification sending fails."""

    pass