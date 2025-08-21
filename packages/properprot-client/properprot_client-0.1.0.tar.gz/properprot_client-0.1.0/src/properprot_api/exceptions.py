class APIClientError(Exception):
    """Base exception for API client."""


class APIRequestError(APIClientError):
    """Raised when a request fails (non-2xx)."""
