"""Custom exception classes for ZAPI."""


class ZAPIError(Exception):
    """Base exception class for ZAPI errors."""

    pass


class ZAPIAuthenticationError(ZAPIError):
    """Authentication-related errors."""

    pass


class ZAPIValidationError(ZAPIError):
    """Input validation errors."""

    pass


class ZAPINetworkError(ZAPIError):
    """Network-related errors."""

    pass


# Internal aliases for consistency
AuthError = ZAPIAuthenticationError
NetworkError = ZAPINetworkError
LLMKeyError = ZAPIValidationError
