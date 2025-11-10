# ZAPI - Zero-Shot API Discovery

ZAPI is an open-source Python library that automatically captures network traffic and API calls from web applications. Perfect for API discovery, LLM training datasets, and understanding how web apps communicate with backends.

## 🔑 Bring Your Own Key (BYOK)

ZAPI requires LLM API keys for enhanced API discovery. Your keys are secured and transmitted safely to our discovery service.

**Supported Providers:**
- **Anthropic**
- **OpenAI**
- **Google** 
- **Groq**

## 📊 HAR Analysis & Cost Estimation

ZAPI includes powerful HAR file analysis capabilities that automatically filter API-relevant traffic, exclude static assets, and provide cost/time estimates for processing. Get detailed statistics before uploading to make informed decisions about your API discovery sessions.


## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install browser binaries (REQUIRED)
playwright install
```

**Requirements:** Python 3.9+, Playwright 1.40.0+, cryptography 41.0.0+

## Environment Setup

Before using ZAPI, set up your environment variables in a `.env` file:

```bash
# Required environment variables
LLM_PROVIDER_API_KEY=your_llm_api_key_here
LLM_PROVIDER=anthropic                    # anthropic, openai, google, groq
LLM_MODEL_NAME=claude-3-5-sonnet-20241022 # model name for your provider
ADOPT_CLIENT_ID=your_client_id_here       # Get from app.adopt.ai
ADOPT_SECRET_KEY=your_secret_key_here     # Get from app.adopt.ai
YOUR_API_URL=your_api_url_here           # Custom API URL
```

**Get Your Credentials:**
Sign up at [app.adopt.ai](https://app.adopt.ai) to get your `ADOPT_CLIENT_ID` and `ADOPT_SECRET_KEY` for OAuth authentication.

## Quick Start

```python
from zapi import ZAPI

# Initialize ZAPI (automatically loads from .env file)
z = ZAPI()

# Launch browser and capture traffic
session = z.launch_browser(url="https://app.example.com/dashboard")

# Export network logs
session.dump_logs("session.har")

# Analyze HAR file before upload (optional but recommended)
from zapi import analyze_har_file
stats, report, _ = analyze_har_file("session.har")
print(f"API entries: {stats.valid_entries}, Estimated cost: ${stats.estimated_cost_usd:.2f}")

# Upload for enhanced API discovery
z.upload_har("session.har")
session.close()
```

**Test Installation:**
```bash
python demo.py
```

**Using .env for LLM Keys (Recommended):**
```bash
# Copy the example file and add your credentials
cp .env.example .env
```

## 📊 HAR Analysis & Statistics

ZAPI includes comprehensive HAR file analysis to help you understand your captured traffic and make informed decisions about processing costs.

### Analyze HAR Files

```python
from zapi import analyze_har_file, HarProcessingError

try:
    # Analyze HAR file with detailed statistics
    stats, report, filtered_file = analyze_har_file(
        "session.har", 
        save_filtered=True,           # Save filtered version with only API entries
        filtered_output_path="api_only.har"  # Optional custom path
    )
    
    # Access detailed statistics
    print(f"Total entries: {stats.total_entries:,}")
    print(f"API-relevant entries: {stats.valid_entries:,}")
    print(f"Unique domains: {stats.unique_domains:,}")
    print(f"Estimated cost: ${stats.estimated_cost_usd:.2f}")
    print(f"Estimated time: {stats.estimated_time_minutes:.1f} minutes")
    
    # Detailed breakdown
    print("\nSkipped entries by reason:")
    for reason, count in stats.skipped_by_reason.items():
        if count > 0:
            print(f"  {reason.replace('_', ' ').title()}: {count:,}")
    
    # Print formatted report
    print("\n" + report)
    
except HarProcessingError as e:
    print(f"HAR analysis failed: {e}")
```
## Usage Examples

### Visible Browser Mode

```python
# Run with visible browser for debugging
z = ZAPI()
session = z.launch_browser(url="https://app.example.com", headless=False)
```

### LLM Key Management

```python
from zapi import ZAPI

# Initialize ZAPI (loads configuration from .env)
z = ZAPI()

# Check configuration
print(f"Provider: {z.get_llm_provider()}")        # 'anthropic'
print(f"Model: {z.get_llm_model_name()}")         # 'claude-3-5-sonnet-20241022'
print(f"Has key: {z.has_llm_key()}")              # True

# Update LLM configuration after initialization
z.set_llm_key("openai", "sk-your-openai-key", "gpt-4")

# Access encrypted key (for debugging)
encrypted_key = z.get_encrypted_llm_key()
decrypted_key = z.get_decrypted_llm_key()  # Use carefully
```

### Complete Workflow with Analysis

```python
from zapi import ZAPI, analyze_har_file

# Initialize ZAPI (loads configuration from .env)
z = ZAPI()

# Capture session
session = z.launch_browser(url="https://app.example.com")
# ... navigate and interact ...
session.dump_logs("session.har")
session.close()

# Analyze before upload
stats, report, _ = analyze_har_file("session.har")
print(f"Found {stats.valid_entries} API entries, estimated cost: ${stats.estimated_cost_usd:.2f}")

# Upload with confirmation
if input("Upload? (y/n): ").lower() == 'y':
    z.upload_har("session.har")
    print("Upload completed!")
```

## 🔗 LangChain Integration & Examples

ZAPI provides seamless integration with LangChain, allowing you to automatically convert your documented APIs into LangChain tools for agent workflows.

**📚 LangChain Examples:**
- **[LangChain Integration Guide](examples/langchain/README.md)** - Complete guide to using ZAPI with LangChain agents
- **[Demo Script](examples/langchain/demo.py)** - Interactive demo showing agent creation and usage

**Quick LangChain Usage:**
```python
from langchain.agents import create_agent
from zapi import ZAPI, interactive_chat

# Initialize and create agent with your APIs as tools
z = ZAPI()
agent = create_agent(z.get_llm_model_name(), z.get_zapi_tools())

# Start interactive chat with your APIs
interactive_chat(agent)
```

## API Reference

### ZAPI Class

**`ZAPI(client_id, secret, llm_provider, llm_model_name, llm_api_key)`**
- `client_id` (str): Client ID for OAuth authentication
- `secret` (str): Secret key for authentication  
- `llm_provider` (str): LLM provider name - supports "groq", "anthropic", "openai", "google"
- `llm_model_name` (str): LLM model name (e.g., "claude-3-5-sonnet-20241022", "gpt-4")
- `llm_api_key` (str): LLM API key for the specified provider
  - Keys are secured using your organization's unique context

**`launch_browser(url, headless=True, **playwright_options)`**
- Returns: `BrowserSession` instance
- Automatically fetches auth token and injects it into all requests

**`set_llm_key(provider, api_key, model_name)`**
- Update LLM configuration after initialization
- Keys are immediately encrypted

**`get_llm_provider()`**
- Returns the configured LLM provider name or None

**`get_llm_model_name()`**
- Returns the configured LLM model name or None

**`get_encrypted_llm_key()`**
- Returns the encrypted LLM API key or None

**`get_decrypted_llm_key()`**
- Returns the decrypted LLM API key or None (use carefully)

**`has_llm_key()`**
- Returns True if LLM key is configured

**`upload_har(filepath)`**
- Upload HAR file with secured LLM keys
- Includes metadata for enhanced API discovery

**`get_documented_apis(page=1, page_size=10)`**
- Fetch list of documented APIs with pagination
- Returns JSON response with API documentation

### BrowserSession Class

| Method | Description |
|--------|-------------|
| `navigate(url, wait_until="networkidle")` | Navigate to URL |
| `click(selector, **kwargs)` | Click element by CSS selector |
| `fill(selector, value, **kwargs)` | Fill form field |
| `wait_for(selector=None, timeout=None)` | Wait for selector or timeout |
| `dump_logs(filepath)` | Export HAR file |
| `close()` | Close browser and cleanup |

## How It Works

```python
try:
    z = ZAPI(
        client_id="invalid", 
        secret="invalid", 
        llm_provider="anthropic",
        llm_model_name="claude-3-5-sonnet-20241022",
        llm_api_key="invalid-key"
    )
except ZAPIAuthenticationError as e:
    print(f"Authentication failed: {e}")
except ZAPIValidationError as e:
    print(f"Input validation error: {e}")
except ZAPINetworkError as e:
    print(f"Network error: {e}")
```

## 🔒 Security & Privacy

**LLM Key Protection:**
- Keys are secured immediately using AES-256-GCM upon initialization
- No plaintext keys stored in memory or logs
- Secure transmission to adopt.ai discovery service
- Each organization gets isolated contexts

**BYOK Configuration:**
- Configure any supported provider: `(provider, model_name, api_key)`
- Support for Groq, Anthropic, OpenAI, and Google
- Secure credential loading with `load_llm_credentials()` function

## 🚀 Enhanced API Discovery with BYOK

When you provide LLM API keys, ZAPI enables enhanced API discovery capabilities:


**When to Use BYOK:**
- Building LLM training datasets from API interactions
- Comprehensive API documentation generation  
- Advanced API security analysis
- Understanding complex application workflows
- Creating intelligent API testing scenarios
- Cost-effective API discovery with upfront estimates

**Example Enhanced Workflow:**
```python
from zapi import ZAPI, analyze_har_file

# Initialize ZAPI (loads configuration from .env)
z = ZAPI()

# Capture session
session = z.launch_browser(url="https://app.example.com")
# ... navigate and interact ...
session.dump_logs("session.har")

# Analyze before upload with cost estimation
stats, report, _ = analyze_har_file("session.har")
print(f"Found {stats.valid_entries} API entries")
print(f"Estimated cost: ${stats.estimated_cost_usd:.2f}")
print(f"Estimated time: {stats.estimated_time_minutes:.1f} minutes")

# Upload for API discovery
z.upload_har("session.har")
session.close()
```
