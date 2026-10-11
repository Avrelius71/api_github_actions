class ApiError(Exception):
    """Base exception for API client errors."""


class ApiTimeoutError(ApiError):
    """Raised when request timed out."""


class ApiConnectionError(ApiError):
    """Raised when connection to API failed."""
