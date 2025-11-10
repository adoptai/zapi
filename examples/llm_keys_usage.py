"""
Example demonstrating LLM API key management with ZAPI.

This shows how to securely provide LLM API keys for the 4 main supported providers.
Keys will be encrypted and transmitted to the adopt.ai discovery service.

Supported providers: Anthropic, OpenAI, Google, Groq
"""

from zapi import ZAPI, LLMProvider


def main():
    # Example 1: Initialize ZAPI with single LLM key in constructor (Anthropic primary)
    print("Example 1: ZAPI with single LLM key in constructor (Anthropic primary)")
    
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
    
    # Add key later - showcasing one of the 4 main providers
    z2.set_llm_key("anthropic", "sk-ant-another-key-here")
    
    print(f"After setting key: {z2.has_llm_key()}")
    print(f"Configured provider: {z2.get_llm_provider()}")
    

    # Example 3: Multiple provider support (single provider per client)
    print("\nExample 3: Using different providers (create separate clients)")
    
    # OpenAI example
    z3a = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")
    z3a.set_llm_key("openai", "sk-your-openai-key-here")
    print(f"OpenAI client provider: {z3a.get_llm_provider()}")
    
    # Groq example 
    z3b = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")
    z3b.set_llm_key("groq", "gsk_your-groq-key-here")
    print(f"Groq client provider: {z3b.get_llm_provider()}")
    
    # Google example
    z3c = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")
    z3c.set_llm_key("google", "your-google-api-key-here")
    print(f"Google client provider: {z3c.get_llm_provider()}")
    

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
    
    
    # Example 5: Show all 4 supported providers
    print("\nExample 5: All 4 main supported LLM providers")
    print(f"All supported providers: {list(LLMProvider.get_all_providers())}")
    
    from zapi.providers import get_supported_providers_info, is_primary_provider
    
    providers_info = get_supported_providers_info()
    for provider_name, info in providers_info.items():
        support_level = "🔥 PRIMARY" if is_primary_provider(provider_name) else "⭐ MAIN"
        print(f"- {info['display_name']}: {support_level} - {info['description']}")
    
    print("\n💡 ZAPI supports 4 main providers: Anthropic, OpenAI, Google, Groq")
    print("   Each client handles one provider's key for security and simplicity.")
    print("   All providers have complete validation and optimized integration.")
    
    # Example 6: Demonstrating API key format validation
    print("\nExample 6: API key format validation for each provider")
    
    key_examples = {
        "anthropic": "sk-ant-api03-example-key-here",
        "openai": "sk-your-openai-key-here", 
        "groq": "gsk_your-groq-key-here",
        "google": "your-google-api-key-here"
    }
    
    for provider, example_key in key_examples.items():
        print(f"- {provider.title()}: {example_key[:15]}...")


if __name__ == "__main__":
    main()