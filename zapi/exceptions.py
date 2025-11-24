"""Custom exception classes for ZAPI."""


class ZapiException(Exception):
    """Base exception for all ZAPI errors."""
    pass


class AuthException(ZapiException):
    """Raised for authentication-related errors."""
    pass


class LLMKeyException(ZapiException):
    """Raised for LLM key-related errors."""
    pass


class NetworkException(ZapiException):
    """Raised for network-related errors."""
    pass