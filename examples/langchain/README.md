# ZAPI LangChain Integration

This example demonstrates how to use ZAPI with LangChain to automatically convert your documented APIs into LangChain tools.

## Quick Start

### 1. Basic Usage (Recommended)

```python
from langchain.agents import create_agent
from zapi import ZAPI, interactive_chat

# Initialize ZAPI and create agent
z = ZAPI()

# Get ZAPI tools automatically
agent = create_agent(
    z.get_llm_model_name(),
    z.get_zapi_tools(),  # Simple one-liner to get all tools
    system_prompt="You are a helpful assistant with access to APIs."
)

# Start interactive chat
interactive_chat(agent)
```

### 2. Run the Demo

```bash
python demo.py
```

## Optional: Custom API Authentication Headers

If your APIs require custom authentication headers, you can provide them via a JSON file.

### Create API Headers File

Create a file named `api-headers.json` in the `zapi/` root directory:

```json
{
  "headers": {
    "Authorization": "Bearer your-api-token-here",
    "X-API-Key": "your-api-key-here",
    "X-Client-ID": "your-client-id-here"
  }
}
```

### Header Examples

**Bearer Token Authentication:**
```json
{
  "headers": {
    "Authorization": "Bearer sk_live_abc123..."
  }
}
```

**API Key Authentication:**
```json
{
  "headers": {
    "X-API-Key": "your_api_key_here",
    "X-Client-ID": "your_client_id"
  }
}
```

**Custom Headers:**
```json
{
  "headers": {
    "X-Custom-Auth": "custom_value",
    "X-Organization": "org_123",
    "X-Tenant": "tenant_456"
  }
}
```

## Usage

```python
from zapi import ZAPI

z = ZAPI()
tools = z.get_zapi_tools()  # Automatically loads api-headers.json if it exists
```

That's it! The `get_zapi_tools()` method automatically:
- Fetches your documented APIs from ZAPI platform
- Loads authentication headers from `api-headers.json` (if present)
- Converts APIs into LangChain-compatible tools

## Creating an Agent

ZAPI works seamlessly with LangChain's agent framework. Here's the complete flow:

```python
from langchain.agents import create_agent
from zapi import ZAPI, interactive_chat

# 1. Initialize ZAPI
z = ZAPI()

# 2. Create agent with ZAPI tools
agent = create_agent(
    z.get_llm_model_name(),      # Gets the LLM model (e.g., "claude-3-5-sonnet-20241022")
    z.get_zapi_tools(),           # Gets all your documented APIs as tools
    system_prompt="You are a helpful assistant with access to APIs."
)

# 3. Start chatting!
interactive_chat(agent)
```

### What happens here?

- **`z.get_llm_model_name()`**: Returns the LLM model name configured in your ZAPI credentials
- **`z.get_zapi_tools()`**: Fetches and converts your APIs into LangChain tools
- **`create_agent()`**: Creates a LangChain agent that can use your APIs
- **`interactive_chat()`**: Starts an interactive terminal chat session with the agent

The agent will automatically:
- Understand when to call your APIs based on user queries
- Extract parameters from natural language
- Execute API calls through ZAPI
- Present results in a conversational format

## Security Notes

- **Never commit your actual API keys to version control**
- Add `api-headers.json` to your `.gitignore` file
- Use environment-specific headers files for different environments
- The tool will show which headers are loaded but won't display their values for security

## What ZAPI Does

1. **Fetches Documented APIs**: Retrieves all APIs you've documented in ZAPI platform
2. **Converts to LangChain Tools**: Automatically creates LangChain tools with proper schemas
3. **Handles Authentication**: Applies custom headers (if provided) to all API requests
4. **Executes API Calls**: Routes tool calls through ZAPI backend for execution

## Features

- ✅ **Zero-config**: Works out of the box with `z.get_zapi_tools()`
- ✅ **Type-safe**: Automatically generates proper parameter schemas
- ✅ **Flexible auth**: Supports custom headers via JSON file
- ✅ **Error handling**: Gracefully handles API failures
- ✅ **Interactive chat**: Built-in `interactive_chat()` utility

## File Structure

```
zapi/
├── api-headers.json        # Optional: Your API headers (don't commit this!)
├── examples/
│   └── langchain/
│       ├── demo.py         # Demo script
│       └── README.md       # This file
└── ...
```

## Troubleshooting

- If no headers file is found, the tool will proceed without authentication headers
- Check the console output for confirmation that headers were loaded
- Ensure your JSON file is valid (use a JSON validator if needed)
- Make sure you have documented APIs in your ZAPI platform account
