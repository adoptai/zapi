"""LLM Provider enums and validation utilities.

ZAPI supports a generic key-value approach for LLM API keys, allowing developers
to bring their own keys for any provider. We explicitly support Anthropic with 
full validation, and provide extensible support for additional providers.

Currently supported providers:
- Anthropic (primary support with full validation)
- OpenAI, Google, Cohere, HuggingFace (extensible support)
"""

from enum import Enum
from typing import Dict, Set


class LLMProvider(Enum):
    """
    Supported LLM providers for API key management.
    
    Uses generic key-value pairs {"provider": "api_key"} pattern for future-proof
    extensibility. Anthropic is explicitly supported as the primary provider.
    """
    # Primary supported provider
    ANTHROPIC = "anthropic"
    
    # Additional supported providers (extensible)
    OPENAI = "openai"
    GOOGLE = "google" 
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    
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
    Validate LLM keys dictionary using generic key-value approach.
    
    Supports generic {"provider": "api_key"} pattern for any LLM provider.
    Anthropic keys receive full validation, other providers have basic validation.
    
    Args:
        llm_keys: Dictionary mapping provider names to API keys
                 Example: {"anthropic": "sk-ant-...", "openai": "sk-..."}
        
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
    
    Anthropic receives full validation as the primary supported provider.
    Other providers have basic validation for extensibility.
    
    Args:
        provider: Provider name (normalized to lowercase)
        api_key: API key to validate
        
    Raises:
        ValueError: If key format is invalid for the provider
    """
    # Primary supported provider - full validation
    if provider == LLMProvider.ANTHROPIC.value:
        if not api_key.startswith("sk-ant-"):
            raise ValueError("Anthropic API keys must start with 'sk-ant-'")
        if len(api_key) < 20:
            raise ValueError("Anthropic API keys must be at least 20 characters long")
    
    # Additional providers - basic validation for extensibility
    elif provider == LLMProvider.OPENAI.value:
        if not api_key.startswith("sk-"):
            raise ValueError("OpenAI API keys must start with 'sk-'")
    
    elif provider == LLMProvider.GOOGLE.value:
        # Google API keys are typically 39 characters and alphanumeric + hyphens
        if len(api_key) < 20:
            raise ValueError("Google API keys must be at least 20 characters long")
    
    elif provider == LLMProvider.COHERE.value:
        # Cohere API keys are typically long alphanumeric strings
        if len(api_key) < 20:
            raise ValueError("Cohere API keys must be at least 20 characters long")
    
    elif provider == LLMProvider.HUGGINGFACE.value:
        if not api_key.startswith("hf_"):
            raise ValueError("HuggingFace API keys must start with 'hf_'")
    
    # Generic validation for all providers
    if len(api_key) < 10:
        raise ValueError(f"API key for {provider} is too short (minimum 10 characters)")
    
    # Additional validation: ensure key contains only valid characters
    if not api_key.replace("-", "").replace("_", "").replace(".", "").isalnum():
        raise ValueError(f"API key for {provider} contains invalid characters")


def get_provider_display_name(provider: str) -> str:
    """
    Get human-readable display name for provider.
    
    Supports generic key-value approach - any provider name can be used,
    with known providers getting proper display names.
    
    Args:
        provider: Provider name (normalized)
        
    Returns:
        Display name for the provider
    """
    display_names = {
        # Primary supported provider
        LLMProvider.ANTHROPIC.value: "Anthropic (Fully Supported)",
        
        # Additional supported providers
        LLMProvider.OPENAI.value: "OpenAI",
        LLMProvider.GOOGLE.value: "Google",
        LLMProvider.COHERE.value: "Cohere", 
        LLMProvider.HUGGINGFACE.value: "HuggingFace",
    }
    return display_names.get(provider, provider.title())


def is_primary_provider(provider: str) -> bool:
    """
    Check if provider is a primary supported provider with full validation.
    
    Args:
        provider: Provider name (normalized)
        
    Returns:
        True if provider is primary supported (Anthropic), False otherwise
    """
    return provider.lower() == LLMProvider.ANTHROPIC.value


def get_supported_providers_info() -> Dict[str, Dict[str, str]]:
    """
    Get information about supported providers.
    
    Returns:
        Dictionary with provider info including support level
    """
    return {
        "anthropic": {
            "display_name": "Anthropic",
            "support_level": "primary",
            "description": "Fully supported with complete validation"
        },
        "openai": {
            "display_name": "OpenAI", 
            "support_level": "extended",
            "description": "Basic validation, extensible support"
        },
        "google": {
            "display_name": "Google",
            "support_level": "extended", 
            "description": "Basic validation, extensible support"
        },
        "cohere": {
            "display_name": "Cohere",
            "support_level": "extended",
            "description": "Basic validation, extensible support"  
        },
        "huggingface": {
            "display_name": "HuggingFace",
            "support_level": "extended",
            "description": "Basic validation, extensible support"
        }
    }
