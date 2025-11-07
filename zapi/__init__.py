"""
ZAPI - Zero-Config API Intelligence

An open-source library that automatically discovers, understands, 
and prepares APIs for LLM and agent workflows.
"""

from .core import (
    ZAPI, 
    ZAPIError, 
    ZAPIAuthenticationError, 
    ZAPIValidationError, 
    ZAPINetworkError
)
from .session import (
    BrowserSession,
    BrowserSessionError,
    BrowserNavigationError,
    BrowserInitializationError
)
from .auth import AuthMode
from .providers import LLMProvider
from .encryption import LLMKeyEncryption
from .utils import load_llm_credentials
from .har_processing import (
    HarProcessor,
    HarStats,
    HarProcessingError,
    analyze_har_file,
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
    # Exception classes
    "ZAPIError",
    "ZAPIAuthenticationError", 
    "ZAPIValidationError",
    "ZAPINetworkError",
    "BrowserSessionError",
    "BrowserNavigationError", 
    "BrowserInitializationError",
    "HarProcessingError"
]

