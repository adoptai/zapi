"""LLM Provider enums and validation utilities.

ZAPI supports a generic key-value approach for LLM API keys, allowing developers
to bring their own keys for any provider. We support 4 main providers with 
full validation and optimized integration.

Currently supported providers:
- Anthropic, OpenAI, Google, Groq (main supported providers)
"""

from enum import Enum
from typing import Dict, Set


class LLMProvider(Enum):
    """
    Supported LLM providers for API key management.
    
    ZAPI supports 4 main LLM providers with optimized integration and validation.
    Each provider has specific API key format validation.
    """
    # Main supported providers
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google" 
    GROQ = "groq"
    
    @classmethod
    def get_all_providers(cls) -> Set[str]:
        """Get all supported provider names."""
        return {provider.value for provider in cls}
    
    @classmethod
    def is_valid_provider(cls, provider: str) -> bool:
        """Check if a provider name is valid."""
        return provider.lower() in cls.get_all_providers()


def validate_llm_keys(llm_keys: Dict[str, str]) -> Dict[str, str]:
    """
    Validate LLM keys dictionary for supported providers.
    
    Supports the 4 main LLM providers with specific validation for each.
    
    Args:
        llm_keys: Dictionary mapping provider names to API keys
                 Example: {"anthropic": "sk-ant-...", "openai": "sk-...", "groq": "gsk_..."}
        
    Returns:
        Validated and normalized keys dictionary
        
    Raises:
        ValueError: If keys format is invalid or providers are unsupported
    """
    if not isinstance(llm_keys, dict):
        raise ValueError("llm_keys must be a dictionary")
    
    if not llm_keys:
        raise ValueError("llm_keys cannot be empty")
    
    validated_keys = {}

    supported_providers = ", ".join(LLMProvider.get_all_providers())
    
    for provider, api_key in llm_keys.items():
        # Normalize provider name to lowercase
        provider_normalized = provider.lower()
        
        # Validate provider is supported
        if not LLMProvider.is_valid_provider(provider_normalized):
            raise ValueError(
                f"Unsupported LLM provider: '{provider}'. "
                f"Supported providers: {supported_providers}"
            )
        
        # Validate API key format
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError(f"API key for provider '{provider}' must be a non-empty string")
        
        validated_keys[provider_normalized] = api_key.strip()
    
    return validated_keys


def _validate_key_format(provider: str, api_key: str) -> None:
    """
    Validate API key format for specific providers.
    
    All 4 main providers receive specific validation tailored to their API key formats.
    
    Args:
        provider: Provider name (normalized to lowercase)
        api_key: API key to validate
        
    Raises:
        ValueError: If key format is invalid for the provider
    """
    # Main supported providers - specific validation for each
    if provider == LLMProvider.ANTHROPIC.value:
        if not api_key.startswith("sk-ant-"):
            raise ValueError("Anthropic API keys must start with 'sk-ant-'")
        if len(api_key) < 20:
            raise ValueError("Anthropic API keys must be at least 20 characters long")
    
    elif provider == LLMProvider.OPENAI.value:
        if not api_key.startswith("sk-"):
            raise ValueError("OpenAI API keys must start with 'sk-'")
        if len(api_key) < 20:
            raise ValueError("OpenAI API keys must be at least 20 characters long")
    
    elif provider == LLMProvider.GOOGLE.value:
        # Google API keys are typically 39 characters and alphanumeric + hyphens
        if len(api_key) < 20:
            raise ValueError("Google API keys must be at least 20 characters long")
    
    elif provider == LLMProvider.GROQ.value:
        if not api_key.startswith("gsk_"):
            raise ValueError("Groq API keys must start with 'gsk_'")
        if len(api_key) < 20:
            raise ValueError("Groq API keys must be at least 20 characters long")
    
    # Generic validation for all providers
    if len(api_key) < 10:
        raise ValueError(f"API key for {provider} is too short (minimum 10 characters)")
    
    # Additional validation: ensure key contains only valid characters
    if not api_key.replace("-", "").replace("_", "").replace(".", "").isalnum():
        raise ValueError(f"API key for {provider} contains invalid characters")


def get_provider_display_name(provider: str) -> str:
    """
    Get human-readable display name for provider.
    
    Returns display names for the 4 main supported providers.
    
    Args:
        provider: Provider name (normalized)
        
    Returns:
        Display name for the provider
    """
    display_names = {
        # Main supported providers
        LLMProvider.ANTHROPIC.value: "Anthropic",
        LLMProvider.OPENAI.value: "OpenAI",
        LLMProvider.GOOGLE.value: "Google",
        LLMProvider.GROQ.value: "Groq",
    }
    return display_names.get(provider, provider.title())


def is_primary_provider(provider: str) -> bool:
    """
    Check if provider is the primary supported provider.
    
    Args:
        provider: Provider name (normalized)
        
    Returns:
        True if provider is primary supported (Anthropic), False otherwise
    """
    return provider.lower() == LLMProvider.ANTHROPIC.value


def get_supported_providers_info() -> Dict[str, Dict[str, str]]:
    """
    Get information about the 4 main supported providers.
    
    Returns:
        Dictionary with provider info including support level
    """
    return {
        "anthropic": {
            "display_name": "Anthropic",
            "support_level": "primary",
            "description": "Primary supported provider with complete validation"
        },
        "openai": {
            "display_name": "OpenAI", 
            "support_level": "main",
            "description": "Fully supported with complete validation"
        },
        "google": {
            "display_name": "Google",
            "support_level": "main", 
            "description": "Fully supported with complete validation"
        },
        "groq": {
            "display_name": "Groq",
            "support_level": "main",
            "description": "Fully supported with complete validation"
        }
    }
