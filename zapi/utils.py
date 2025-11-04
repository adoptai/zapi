"""Utility functions for ZAPI."""

import os
from typing import Optional, Tuple

try:
    from pydantic import SecretStr
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False
    SecretStr = str  # Fallback to regular string if pydantic not available


def load_llm_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Load LLM credentials from .env file or fallback to code defaults.
    
    Returns:
        Tuple of (provider, api_key) where api_key is properly handled for security
        
    Note:
        Requires pydantic and python-dotenv to be installed for full functionality.
        Falls back gracefully if these packages are not available.
    """
    if not HAS_DOTENV:
        print("⚠️  pydantic/python-dotenv not installed - using fallback credential loading")
        return None, None
    
    # Try to load from .env file
    load_dotenv()
    
    # Check environment variables first
    env_provider = os.getenv("LLM_PROVIDER")
    env_api_key = os.getenv("LLM_API_KEY")
    
    if env_provider and env_api_key:
        print(f"✓ Loaded LLM credentials from .env file (provider: {env_provider})")
        # Return string directly - SecretStr handling is done in demo.py
        return env_provider, env_api_key
    
    print("ℹ️  No LLM credentials found in .env file")
    return None, None