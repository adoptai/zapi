#!/usr/bin/env python
"""ZAPI Demo Script"""
from zapi import ZAPI
from zapi import load_llm_credentials


def main():
    client_id = "CLIENT_ID"
    secret = "SECRET_KEY"
    url = "URL"
    output_file = "OUTPUT_FILE.har"
    
    # Load LLM credentials securely from .env or fallback to code
    llm_provider, llm_api_key = load_llm_credentials()
    
    try:
        # Initialize ZAPI with optional LLM key for enhanced discovery
        if llm_provider and llm_api_key:
            print(f"Initializing ZAPI with BYOK - {llm_provider} for enhanced API discovery...")
            z = ZAPI(
                client_id=client_id, 
                secret=secret, 
                llm_provider=llm_provider,
                llm_api_key=llm_api_key  # Use the API key directly
            )
            print(f"Configured LLM provider: {z.get_llm_provider()}")
        else:
            print("Initializing ZAPI without LLM keys...")
            z = ZAPI(client_id=client_id, secret=secret)
        
        session = z.launch_browser(url=url, headless=False)
        input("Press ENTER when done navigating...")
        session.dump_logs(output_file)
        z.upload_har(output_file)
        # print the decrypted LLM key 
        # print(f"Decrypted LLM key: {z.get_decrypted_llm_key()}")
        session.close()
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())