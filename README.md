# ZAPI - Zero-Shot API Discovery

ZAPI is an open-source Python library that automatically captures network traffic and API calls from web applications. Perfect for API discovery, LLM training datasets, and understanding how web apps communicate with backends.

## 🔑 Bring Your Own Key (BYOK)

ZAPI supports secure LLM API key integration using a generic key-value approach. **Anthropic is explicitly supported** as our primary provider with full validation and optimized pipeline integration. Your keys are encrypted using organization-specific contexts and transmitted securely to our discovery service.

**Supported Providers:**
- **🔥 Anthropic** (Primary support - fully validated, optimized for our pipelines)
- 📦 OpenAI, Google, Cohere, HuggingFace (Extended support - basic validation, extensible)


## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install browser binaries (REQUIRED)
playwright install
```

**Requirements:** Python 3.9+, Playwright 1.40.0+, cryptography 41.0.0+

## Quick Start

```python
from zapi import ZAPI

# Initialize with client credentials
z = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")

# Launch browser and capture traffic
session = z.launch_browser(url="https://app.example.com/dashboard")

# Export network logs
session.dump_logs("session.har")
session.close()
```

### With LLM Keys (BYOK)

```python
from zapi import ZAPI

# Initialize with your LLM API keys for enhanced discovery
llm_keys = {
    "anthropic": "sk-ant-your-anthropic-key-here",  # Primary supported
    "openai": "sk-your-openai-key-here"             # Extended support
}

z = ZAPI(
    client_id="YOUR_CLIENT_ID", 
    secret="YOUR_SECRET",
    llm_keys=llm_keys  # Encrypted using your org_id
)

session = z.launch_browser(url="https://app.example.com")
session.dump_logs("session.har")

# Upload with encrypted LLM keys for enhanced API discovery
z.upload_har("session.har")  # Keys included securely
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
## Usage Examples

### Navigation & Interaction

```python
from zapi import ZAPI

z = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")
session = z.launch_browser(url="https://app.example.com")

# Navigate and interact
session.navigate("/dashboard")
session.click("#settings-button")
session.fill("#search-input", "query")
session.wait_for("#results")

session.dump_logs("session.har")
session.close()
```

### Context Manager

```python
z = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")

with z.launch_browser(url="https://app.example.com") as session:
    session.navigate("/api-endpoint")
    session.wait_for(timeout=2000)
    session.dump_logs("session.har")
# Auto cleanup
```

### Visible Browser Mode

```python
# Run with visible browser for debugging
session = z.launch_browser(url="https://app.example.com", headless=False)
```

### LLM Key Management

```python
from zapi import ZAPI, LLMProvider

# Method 1: Constructor with keys
z = ZAPI(
    client_id="YOUR_CLIENT_ID",
    secret="YOUR_SECRET", 
    llm_keys={"anthropic": "sk-ant-your-key"}  # Anthropic primary support
)

# Method 2: Set keys after initialization
z = ZAPI(client_id="YOUR_CLIENT_ID", secret="YOUR_SECRET")
z.set_llm_keys({
    "anthropic": "sk-ant-your-anthropic-key",
    "openai": "sk-your-openai-key"
})

# Check configured providers
print(f"Configured: {z.get_llm_providers()}")  # ['anthropic', 'openai']
print(f"Has keys: {z.has_llm_keys()}")         # True

# Generic approach - any provider supported
z.set_llm_keys({"custom_provider": "your-api-key"})
```

## API Reference

### ZAPI Class

**`ZAPI(client_id, secret, llm_keys=None)`**
- `client_id` (str): Client ID for OAuth authentication
- `secret` (str): Secret key for authentication  
- `llm_keys` (dict, optional): LLM API keys using generic `{"provider": "api_key"}` format
  - **Anthropic keys receive full validation and pipeline optimization**
  - Other providers get basic validation for extensibility
  - Keys are encrypted using your organization's unique context

**`launch_browser(url, headless=True, **playwright_options)`**
- Returns: `BrowserSession` instance
- Automatically fetches auth token and injects it into all requests

**`set_llm_keys(llm_keys)`**
- Set or update LLM API keys after initialization
- Keys are immediately encrypted and stored securely

**`get_llm_providers()`**
- Returns list of configured LLM provider names

**`has_llm_keys()`**
- Returns True if LLM keys are configured

**`upload_har(filepath)`**
- Upload HAR file with optional encrypted LLM keys
- Includes `byok_enabled` flag and encrypted key metadata

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

When initialized, ZAPI:
1. Calls the adopt.ai OAuth API to obtain an access token
2. **Validates the JWT token and extracts your organization ID**
3. **Encrypts any provided LLM keys using your org_id as encryption context**
4. Injects the auth token as a Bearer token in all request headers
5. Captures complete network traffic during browser interactions
6. Exports to standard HAR format compatible with Chrome DevTools
7. **Optionally uploads HAR files with encrypted LLM keys for enhanced API discovery**

## 🔒 Security & Privacy

**LLM Key Protection:**
- Keys encrypted immediately using AES-256-GCM with your organization's unique context
- No plaintext keys stored in memory or logs
- Ephemeral decryption only during secure transmission to adopt.ai
- Each organization gets isolated encryption contexts
- **Anthropic keys receive additional validation to ensure format correctness**

**Generic BYOK Approach:**
- Use any LLM provider with `{"provider": "api_key"}` format
- Anthropic optimized for our discovery pipelines with full validation
- Other providers supported with basic validation for extensibility
- Future-proof architecture for adding new providers

## 🚀 Enhanced API Discovery with BYOK

When you provide LLM API keys, ZAPI enables enhanced API discovery capabilities:

**Benefits:**
- **🔍 Deeper API Analysis**: Your LLM keys enable more sophisticated API pattern recognition
- **📊 Richer Insights**: Enhanced understanding of API semantics and relationships
- **🎯 Anthropic Optimization**: Primary support with pipeline optimizations for best results
- **🔐 Zero Trust**: Your keys never leave your organization's encrypted context
- **⚡ Seamless Integration**: Same simple API, enhanced discovery when keys provided

**When to Use BYOK:**
- Building LLM training datasets from API interactions
- Comprehensive API documentation generation
- Advanced API security analysis
- Understanding complex application workflows
- Creating intelligent API testing scenarios

**Example Enhanced Workflow:**
```python
# Standard discovery
z_basic = ZAPI(client_id="ID", secret="SECRET")
z_basic.upload_har("session.har")  # Basic traffic analysis

# Enhanced discovery with Anthropic
z_enhanced = ZAPI(
    client_id="ID", 
    secret="SECRET",
    llm_keys={"anthropic": "sk-ant-your-key"}
)
z_enhanced.upload_har("session.har")  # Enhanced AI-powered analysis
```
