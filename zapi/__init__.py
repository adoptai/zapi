"""
ZAPI - Zero-Config API Intelligence

An open-source library that automatically discovers, understands, 
and prepares APIs for LLM and agent workflows.
"""

from .core import ZAPI
from .session import BrowserSession
from .auth import AuthMode
from .providers import LLMProvider
from .encryption import LLMKeyEncryption
from .utils import load_llm_credentials

__version__ = "0.1.0"
__all__ = [
    "ZAPI", 
    "BrowserSession", 
    "AuthMode",
    "LLMProvider",
    "LLMKeyEncryption",
    "load_llm_credentials"
]

