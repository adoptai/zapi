"""
Example demonstrating LLM API key management with ZAPI.

This shows how to securely provide a single LLM API key per client that will be encrypted
and transmitted to the adopt.ai discovery service.
"""

from zapi import ZAPI, LLMProvider


def main():
    # Example 1: Initialize ZAPI with single LLM key in constructor (Anthropic primary support)
    print("Example 1: ZAPI with single LLM key in constructor (Anthropic primary support)")
    
    # Single key approach - one provider per client instance
    z = ZAPI(
        client_id="YOUR_CLIENT_ID",
        secret="YOUR_SECRET",
        llm_provider="anthropic",  # Primary supported provider
        llm_api_key="sk-ant-your-anthropic-key-here"
    )
    
    print(f"Configured provider: {z.get_llm_provider()}")
    print(f"Has LLM key: {z.has_llm_key()}")
    
    # Launch browser and capture session
    session = z.launch_browser(url="https://app.example.com", headless=False)
    input("Navigate around the app, then press ENTER to continue...")
    
    # Export HAR with encrypted LLM key
    session.dump_logs("example_with_key.har")
    
    # Upload to adopt.ai with encrypted key
    z.upload_har("example_with_key.har")
    
    session.close()
    print("✓ Session completed with encrypted LLM key included\n")
    
    
    # Example 2: Set LLM key after initialization
    print("Example 2: Setting LLM key after initialization")
    
    z2 = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")
    print(f"Initially has key: {z2.has_llm_key()}")
    
    # Add key later - showcasing primary Anthropic support
    z2.set_llm_key("anthropic", "sk-ant-another-key-here")
    
    print(f"After setting key: {z2.has_llm_key()}")
    print(f"Configured provider: {z2.get_llm_provider()}")
    

    # Example 3: Legacy dictionary approach (backward compatibility)
    print("\nExample 3: Legacy dictionary approach (uses first key only)")
    
    z3 = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")
    
    # Legacy method - only first key-value pair is used
    z3.set_llm_keys({
        "anthropic": "sk-ant-legacy-key-here",
        "openai": "sk-ignored-key"  # This will be ignored
    })
    
    print(f"Configured provider: {z3.get_llm_provider()}")  # Only "anthropic"
    print(f"Legacy providers list: {z3.get_llm_providers()}")  # ["anthropic"]
    

    # Example 4: Working without LLM keys (backward compatibility)
    print("\nExample 4: Working without LLM keys (backward compatibility)")
    
    z4 = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")
    print(f"Has LLM key: {z4.has_llm_key()}")
    
    # This will work exactly as before - no encrypted keys sent
    session4 = z4.launch_browser(url="https://app.example.com")
    session4.wait_for(timeout=1000)
    session4.dump_logs("example_no_keys.har")
    z4.upload_har("example_no_keys.har")  # byok_enabled: false
    session4.close()
    print("✓ Session completed without LLM keys (legacy mode)")
    
    
    # Example 5: Show supported providers with support levels
    print("\nExample 5: Supported LLM providers (one key per client)")
    print(f"All supported providers: {list(LLMProvider.get_all_providers())}")
    
    from zapi.providers import get_supported_providers_info, is_primary_provider
    
    providers_info = get_supported_providers_info()
    for provider_name, info in providers_info.items():
        support_level = "🔥 PRIMARY" if is_primary_provider(provider_name) else "📦 Extended"
        print(f"- {info['display_name']}: {support_level} - {info['description']}")
    
    print("\n💡 Single key approach: Each ZAPI client handles one provider's key")
    print("   For multiple providers, create separate ZAPI instances.")
    print("   Anthropic gets full validation, others get basic validation for extensibility.")


if __name__ == "__main__":
    main()