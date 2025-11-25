"""Utility functions for ZAPI."""

import json
import os
from typing import Any, Optional

try:
    from dotenv import load_dotenv
    from pydantic import SecretStr

    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False
    SecretStr = str  # Fallback to regular string if pydantic not available


def load_security_headers(headers_file: Optional[str] = None) -> dict[str, str]:
    """
    Load security headers from JSON file.

    Args:
        headers_file: Path to JSON file containing headers. If None, uses
                     'api-headers.json' in the zapi root directory.

    Returns:
        Dictionary of headers to add to API requests
    """
    if headers_file is None:
        # Always use the same fixed location: zapi/api-headers.json
        headers_file = "api-headers.json"

    if not os.path.exists(headers_file):
        print(f"ℹ️  No headers file found at '{headers_file}' - proceeding without authentication headers")
        return {}

    try:
        with open(headers_file) as f:
            data = json.load(f)
            headers = data.get("headers", {})
            if headers:
                print(f"✅ Loaded {len(headers)} security headers from '{headers_file}'")
                # Don't print the actual headers for security
                header_names = list(headers.keys())
                print(f"   Headers: {', '.join(header_names)}")
            else:
                print(f"⚠️  Headers file '{headers_file}' found but contains no headers")
            return headers
    except (OSError, json.JSONDecodeError) as e:
        print(f"⚠️  Error loading headers file '{headers_file}': {e}")
        print("   Proceeding without authentication headers")
        return {}


def load_adopt_credentials() -> tuple[Optional[str], Optional[str]]:
    """
    Load ADOPT credentials from .env file or fallback to code defaults.

    Returns:
        Tuple of (client_id, secret) where values are loaded from environment

    Note:
        Requires python-dotenv to be installed for full functionality.
        Falls back gracefully if these packages are not available.
    """
    if not HAS_DOTENV:
        print("⚠️  python-dotenv not installed - using fallback credential loading")
        return None, None

    # Try to load from .env file
    load_dotenv()

    # Check environment variables first
    env_client_id = os.getenv("ADOPT_CLIENT_ID")
    env_secret = os.getenv("ADOPT_SECRET_KEY")

    if env_client_id and env_secret:
        print("✓ Loaded ADOPT credentials from .env file")
        return env_client_id, env_secret

    print("ℹ️  No ADOPT credentials found in .env file")
    return None, None


def load_llm_credentials() -> tuple[Optional[str], Optional[str], Optional[str]]:
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
        return None, None, None

    # Try to load from .env file
    load_dotenv()

    # Check environment variables first
    env_llm_provider = os.getenv("LLM_PROVIDER")
    env_llm_api_key = os.getenv("LLM_API_KEY")
    env_llm_model_name = os.getenv("LLM_MODEL_NAME")

    if env_llm_provider and env_llm_api_key and env_llm_model_name:
        print(f"✓ Loaded LLM credentials from .env file (provider: {env_llm_provider})")
        # Return string directly - SecretStr handling is done in demo.py
        return env_llm_provider, env_llm_api_key, env_llm_model_name

    print("ℹ️  No LLM credentials found in .env file")
    return None, None, None


def load_zapi_credentials() -> tuple[str, str, str, str, str]:
    """
    Load complete ZAPI credentials (ADOPT + LLM) from environment variables with fallbacks.

    This is a convenience function that combines load_adopt_credentials() and load_llm_credentials()
    with sensible fallback values for development/examples.

    Returns:
        Tuple of (client_id, secret, llm_provider, llm_model_name, llm_api_key)

    Note:
        If environment variables are not found, returns fallback placeholder values
        suitable for examples and development.
    """
    # Load ADOPT credentials securely from .env or fallback to code
    print("🔐 Loading ADOPT credentials...")
    client_id, secret = load_adopt_credentials()

    # Fallback to hardcoded values if not found in .env
    if not client_id or not secret:
        print("⚠️  Using fallback credentials - update your .env file for production")
        client_id = "YOUR_CLIENT_ID"
        secret = "YOUR_SECRET"

    # Load LLM credentials securely from .env or fallback to code
    print("🔐 Loading LLM credentials...")
    llm_provider, llm_api_key, llm_model_name = load_llm_credentials()

    # Fallback to hardcoded values if not found in .env
    if not llm_provider or not llm_api_key or not llm_model_name:
        print("⚠️  Using fallback LLM credentials - update your .env file for production")
        llm_provider = llm_provider or "anthropic"
        llm_model_name = llm_model_name or "claude-3-5-sonnet-20241022"
        llm_api_key = llm_api_key or "YOUR_ANTHROPIC_API_KEY"

    return client_id, secret, llm_provider, llm_model_name, llm_api_key


def set_llm_api_key_env(provider: str, api_key: str) -> None:
    """
    Set the appropriate environment variable for the given LLM provider.

    This is required for LangChain v1.0 to automatically detect and use the API keys.

    Args:
        provider: The LLM provider name ('anthropic' or 'openai')
        api_key: The API key to set in the environment

    Raises:
        ValueError: If the provider is not supported
    """
    if provider == "anthropic":
        os.environ["ANTHROPIC_API_KEY"] = api_key
    elif provider == "openai":
        os.environ["OPENAI_API_KEY"] = api_key
    else:
        raise ValueError(f"Unsupported provider: {provider}. Supported providers: anthropic, openai")


def _safe_get(obj: Any, *keys: str, default: Any = None) -> Any:
    """
    Safely get a value from an object or dict using multiple possible keys.
    Tries object attributes first, then dict keys.

    Args:
        obj: Object or dict to get value from
        *keys: Multiple possible keys/attributes to try
        default: Default value if none found

    Returns:
        First found value or default
    """
    for key in keys:
        if hasattr(obj, key):
            value = getattr(obj, key, None)
            if value is not None:
                return value
        if isinstance(obj, dict) and key in obj:
            value = obj[key]
            if value is not None:
                return value
    return default


def _extract_token_metadata(response: Any) -> Optional[str]:
    """
    Extract token usage metadata from agent response.

    Args:
        response: The response object from the agent

    Returns:
        Formatted token usage string or None if no token info found
    """
    try:
        # Get usage metadata from last message
        if not isinstance(response, dict) or not response.get("messages"):
            return None

        usage = getattr(response["messages"][-1], "usage_metadata", None)
        if not usage:
            return None

        # Extract token values (filtering None values)
        token_info = {
            "input": _safe_get(usage, "input_tokens"),
            "output": _safe_get(usage, "output_tokens"),
            "total": _safe_get(usage, "total_tokens"),
        }
        token_info = {k: v for k, v in token_info.items() if v is not None}

        if not token_info:
            return None

        # Calculate total if missing
        if "total" not in token_info and "input" in token_info and "output" in token_info:
            token_info["total"] = token_info["input"] + token_info["output"]

        # Format output
        labels = {"input": "Input", "output": "Output", "total": "Total"}
        return "Tokens - " + " | ".join(f"{labels[k]}: {token_info[k]}" for k in labels if k in token_info)

    except Exception:
        return None


def interactive_chat(agent: Any, single_shot: bool = False, debug_mode: bool = False) -> None:
    """
    Interactive terminal chat with the agent.

    Args:
        agent: The LangChain agent instance
        single_shot: If True, only accepts one prompt and exits
        debug_mode: If True, shows detailed debug information
    """
    print("\n💬 Interactive Chat Mode")
    print("=" * 25)

    if debug_mode:
        print("🐛 Debug mode: ON")
    print("Type your question and press Enter\n")

    history = []
    first_interaction = True

    while True:
        try:
            # Add divider between questions (except for the first one)
            if not first_interaction:
                print("─" * 60)
                print()

            # Get user input
            user_input = input("You: ").strip()

            # Handle commands
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == "help":
                print("\nAvailable commands:")
                print("- 'exit' or 'quit': Exit the chat")
                print("- 'history': Show conversation history")
                print("- 'debug': Toggle debug mode on/off")
                print("- 'help': Show this help message")
                print("- Any other text: Ask the agent\n")
                continue
            elif user_input.lower() == "debug":
                debug_mode = not debug_mode
                status = "ON" if debug_mode else "OFF"
                print(f"🐛 Debug mode: {status}\n")
                continue
            elif user_input.lower() == "history":
                if history:
                    print("\n📜 Conversation History:")
                    for i, (q, a) in enumerate(history, 1):
                        print(f"{i}. You: {q}")
                        print(f"   Agent: {a[:100]}{'...' if len(a) > 100 else ''}\n")
                else:
                    print("No conversation history yet.\n")
                continue
            elif not user_input:
                continue

            # Process with agent
            print("🤖 Agent: ", end="", flush=True)
            try:
                if debug_mode:
                    print(f"\n🐛 [DEBUG] Sending request: {user_input}")
                    print(f"🐛 [DEBUG] Agent type: {type(agent)}")

                response = agent.invoke({"messages": [{"role": "user", "content": user_input}]})

                if debug_mode:
                    print(f"\n🐛 [DEBUG] Response type: {type(response)}")
                    print(
                        f"🐛 [DEBUG] Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}"
                    )

                    if isinstance(response, dict) and "messages" in response:
                        messages = response["messages"]
                        print(f"🐛 [DEBUG] Messages count: {len(messages)}")
                        for i, msg in enumerate(messages):
                            print(f"🐛 [DEBUG] Message {i}: {type(msg).__name__}")
                            if hasattr(msg, "content"):
                                content_preview = (
                                    str(msg.content)[:100] + "..." if len(str(msg.content)) > 100 else str(msg.content)
                                )
                                print(f"🐛 [DEBUG] Content preview: {content_preview}")
                            if hasattr(msg, "tool_calls") and msg.tool_calls:
                                print(f"🐛 [DEBUG] Tool calls: {[tc['name'] for tc in msg.tool_calls]}")
                    print()

                # Extract response content
                if hasattr(response, "content"):
                    # Handle AIMessage or similar objects with content attribute
                    agent_response = response.content
                elif isinstance(response, dict) and "messages" in response:
                    # Handle dictionary response with messages array - get last AIMessage
                    messages = response["messages"]
                    if messages:
                        last_message = messages[-1]
                        agent_response = last_message.content if hasattr(last_message, "content") else str(last_message)
                    else:
                        agent_response = str(response)
                elif isinstance(response, dict) and "content" in response:
                    # Handle dictionary response with direct content
                    agent_response = response["content"]
                else:
                    # Fallback to string representation
                    agent_response = str(response)

                if debug_mode:
                    print(f"🐛 [DEBUG] Final response length: {len(str(agent_response))} characters")

                print(agent_response)

                # Extract and display token metadata
                token_info = _extract_token_metadata(response)
                if token_info:
                    print(f"\n📊 {token_info}")

                # Add spacing between interactions
                print()

            except Exception as e:
                if debug_mode:
                    import traceback

                    print("\n🐛 [DEBUG] Exception details:")
                    print(f"🐛 [DEBUG] Exception type: {type(e)}")
                    print(f"🐛 [DEBUG] Exception message: {str(e)}")
                    print("🐛 [DEBUG] Traceback:")
                    traceback.print_exc()
                    print()
                print(f"❌ Error: {e}")
                agent_response = f"Error: {e}"
                # Add spacing after error
                print()

            # Store in history
            history.append((user_input, agent_response))

            # Mark that we've had our first interaction
            first_interaction = False

            # Exit if single shot mode
            if single_shot:
                break

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            if single_shot:
                break
