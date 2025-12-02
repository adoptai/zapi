"""
ZAPI - Zero-Config API Intelligence

An open-source library that automatically discovers, understands,
and prepares APIs for LLM and agent workflows.
"""

from .auth import AuthMode
from .constants import BASE_URL
from .core import ZAPI
from .encryption import LLMKeyEncryption
from .exceptions import ZAPIAuthenticationError, ZAPIError, ZAPINetworkError, ZAPIValidationError
from .har_processing import (
    HarProcessingError,
    HarProcessor,
    HarStats,
    analyze_har_file,
)
from .providers import LLMProvider
from .session import BrowserInitializationError, BrowserNavigationError, BrowserSession, BrowserSessionError
from .utils import (
    interactive_chat,
    load_llm_credentials,
)

__version__ = "0.1.0"
__all__ = [
    "ZAPI",
    "BrowserSession",
    "AuthMode",
    "LLMProvider",
    "LLMKeyEncryption",
    "load_llm_credentials",
    # HAR processing
    "HarProcessor",
    "HarStats",
    "analyze_har_file",
    "interactive_chat",
    # Exception classes
    "ZAPIError",
    "ZAPIAuthenticationError",
    "ZAPIValidationError",
    "ZAPINetworkError",
    "BrowserSessionError",
    "BrowserNavigationError",
    "BrowserInitializationError",
    "HarProcessingError",
    "BASE_URL",
]
