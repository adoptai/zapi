<h3 align="center">
  <a name="readme-top"></a>
  <img
    src="https://asset.adopt.ai/web/icons/github_banner.png">
</h3>
<div align="center">
<a href="https://GitHub.com/adoptai/zapi/graphs/contributors">
  <img src="https://img.shields.io/github/contributors/adoptai/zapi.svg" alt="GitHub Contributors">
</a>
<a href="https://www.adopt.ai">
  <img src="https://img.shields.io/badge/Visit-Adopt.AI-gr" alt="Visit Adopt AI">
</a>
</div>
<div>
  <p align="center">
    <a href="https://twitter.com/getadoptai">
      <img src="https://img.shields.io/badge/Follow%20on%20X-000000?style=for-the-badge&logo=x&logoColor=white" alt="Follow on X" />
    </a>
    <a href="https://www.linkedin.com/company/getadoptai">
      <img src="https://img.shields.io/badge/Follow%20on%20LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="Follow on LinkedIn" />
    </a>
  </p>
</div>

# ZAPI - Zero-Shot API Discovery

ZAPI by Adopt AI is an open-source Python library that automatically captures network traffic and API calls from web applications. Use it for API discovery, LLM training datasets, advanced API security analysis, and debugging complex browser workflows.

## Highlights
- Automated Playwright-powered browser sessions that inject auth tokens, capture traffic, export HAR logs, and upload them securely.
- Built-in HAR filtering that excludes static assets, surfaces API-only entries, and provides upfront cost/time estimates before processing.
- LangChain integration that converts documented APIs into ready-to-use tools, complete with type-safe schemas and optional custom headers.
- Bring Your Own Key (BYOK) support for **Anthropic**, **OpenAI**, **Google**, and **Groq**, with AES-256-GCM encryption for every credential.
- Comprehensive API reference, error handling helpers, and secure credential loading utilities so you can extend ZAPI safely.

## Table of Contents
- [Requirements & Installation](#requirements--installation)
- [Environment Setup](#environment-setup)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [HAR Analysis & Cost Estimation](#har-analysis--cost-estimation)
- [LangChain Integration](#langchain-integration)
- [API Reference](#api-reference)
- [Security & BYOK](#security--byok)
- [Enhanced Discovery Workflow](#enhanced-discovery-workflow)
- [Troubleshooting & Tips](#troubleshooting--tips)
- [Contributing](#contributing)

## Requirements & Installation

ZAPI targets **Python 3.9+**, **Playwright 1.40.0+**, and **cryptography 41.0.0+**.

```bash
# Install dependencies
pip install -r requirements.txt

# Install browser binaries (REQUIRED)
playwright install
```

**Test the installation**

```bash
python demo.py
```

## Project Structure

| Path | Purpose |
|------|---------|
| `zapi/core.py` | Home of the `ZAPI` class. Handles credential loading (`load_zapi_credentials()`), OAuth token exchange, BYOK encryption via `LLMKeyEncryption`, LangChain key propagation, and helper methods like `upload_har()` and `get_documented_apis()`. |
| `zapi/session.py` | Contains the `BrowserSession` abstraction that wraps Playwright. Manages auth header injection, HAR recording, navigation helpers (`navigate`, `click`, `fill`, `wait_for`), and robust error handling plus synchronous wrappers. |
| `demo.py` | End-to-end workflow script wired to the modules above. Launches a browser, lets you interact manually, saves the HAR (`session.dump_logs`), runs `analyze_har_file(..., save_filtered=True)`, lets you pick the filtered HAR, and finally calls `ZAPI.upload_har()`. Tweak `DEMO_URL`, `OUTPUT_FILE`, and `HEADLESS_BROWSER` at the top before running. |
| `examples/langchain/` | LangChain integration docs and demo agent showing how `z.get_zapi_tools()` converts documented APIs into LangChain tools. |

Use this as a map when extending ZAPI or debugging the flow.

## Environment Setup

1. Sign up at [app.adopt.ai](https://app.adopt.ai) to obtain your `ADOPT_CLIENT_ID`, `ADOPT_SECRET_KEY`, and BYOK token credentials before running ZAPI.
2. Copy the example environment file and add your secrets:

```bash
cp .devenv .env
```

2. **Set up your environment:**
   - Create a `.env` file in the root of the project.
   - Populate it with the required variables:
     ```env
     # Required environment variables
     LLM_API_KEY=your_llm_api_key_here
     LLM_PROVIDER=anthropic                    # anthropic, openai, google, groq
     LLM_MODEL_NAME=your_model_name_here      # Use the latest available model for your provider
     ADOPT_CLIENT_ID=your_client_id_here       # Get from app.adopt.ai
     ADOPT_SECRET_KEY=your_secret_key_here     # Get from app.adopt.ai
     YOUR_API_URL=your_api_url_here            # Custom API URL
     ```

Use `load_llm_credentials()` (provided in the library) to load secrets safely when building custom tooling.

## Quick Start

### Launch, capture, analyze, and upload

```python
from zapi import ZAPI, analyze_har_file

# Initialize ZAPI (automatically loads from .env file)
z = ZAPI()

# Launch browser and capture traffic
session = z.launch_browser(url="https://app.example.com/dashboard")

# Export network logs
session.dump_logs("session.har")

# Analyze HAR file before upload (optional but recommended)
stats, report, _ = analyze_har_file("session.har")
print(f"API entries: {stats.valid_entries}, Estimated cost: ${stats.estimated_cost_usd:.2f}")

# Upload for enhanced API discovery
if input("Upload? (y/n): ").lower() == 'y':
    z.upload_har("session.har")
    print("Upload completed!")

session.close()
```

> Prefer `python demo.py` for the full interactive experience. The script calls the same primitives shown above but adds guardrails: manual browser driving, HAR filtering, filtered/original upload prompts, and descriptive exception handling for every component (`ZAPI`, `BrowserSession`, HAR processing, networking, etc.).

### LLM key management

```python
from zapi import ZAPI

# Initialize ZAPI (loads configuration from .env)
z = ZAPI()

# Check configuration
print(f"Provider: {z.get_llm_provider()}")        # 'anthropic'
print(f"Model: {z.get_llm_model_name()}")         # Your configured model name
print(f"Has key: {z.has_llm_key()}")              # True

# Update LLM configuration after initialization
z.set_llm_key("openai", "sk-your-openai-key", "gpt-4")

# Access encrypted key (for debugging)
encrypted_key = z.get_encrypted_llm_key()
decrypted_key = z.get_decrypted_llm_key()  # Use carefully
```

### Error handling example

```python
try:
    z = ZAPI(
        client_id="invalid",
        secret="invalid",
        llm_provider="anthropic",
        llm_model_name="your-model-name",  # Use the latest available model for your provider
        llm_api_key="invalid-key"
    )
except ZAPIAuthenticationError as e:
    print(f"Authentication failed: {e}")
except ZAPIValidationError as e:
    print(f"Input validation error: {e}")
except ZAPINetworkError as e:
    print(f"Network error: {e}")
```

## HAR Analysis & Cost Estimation

ZAPI ships with a HAR analyzer that filters out static assets, surfaces API-only calls, and estimates processing cost/time before you upload.

```python
from zapi import analyze_har_file, HarProcessingError

try:
    stats, report, filtered_file = analyze_har_file(
        "session.har",
        save_filtered=True,                 # Save filtered version with only API entries
        filtered_output_path="api_only.har" # Optional custom path
    )

    print(f"Total entries: {stats.total_entries:,}")
    print(f"API-relevant entries: {stats.valid_entries:,}")
    print(f"Unique domains: {stats.unique_domains:,}")
    print(f"Estimated cost: ${stats.estimated_cost_usd:.2f}")
    print(f"Estimated time: {stats.estimated_time_minutes:.1f} minutes")

    print("\nSkipped entries by reason:")
    for reason, count in stats.skipped_by_reason.items():
        if count > 0:
            print(f"  {reason.replace('_', ' ').title()}: {count:,}")

    print("\n" + report)

except HarProcessingError as e:
    print(f"HAR analysis failed: {e}")
```

## LangChain Integration

ZAPI converts documented APIs into LangChain-compatible tools, so your agents can reason over real endpoints immediately.

```python
from langchain.agents import create_agent
from zapi import ZAPI, interactive_chat

z = ZAPI()
agent = create_agent(
    z.get_llm_model_name(),
    z.get_zapi_tools(),  # One-liner to fetch and build all tools
    system_prompt="You are a helpful assistant with access to APIs."
)

interactive_chat(agent)
```

Run the interactive demo any time:

```bash
python examples/langchain/demo.py
```

**Tool anatomy**

- `z.get_zapi_tools()` returns standard LangChain `Tool` objects (name, description, args schema) built from your documented APIs.
- Tools automatically display which authentication headers were loaded (values stay hidden for security) so you always know what context the agent has.
- Execution is routed through ZAPI, letting the agent call your APIs with consistent authentication, logging, and error handling.

**Optional API headers**

Create `api-headers.json` in the repository root when you need to pass custom auth to all generated tools:

```json
{
  "headers": {
    "Authorization": "Bearer your-api-token-here",
    "X-API-Key": "your-api-key-here",
    "X-Client-ID": "your-client-id-here"
  }
}
```

Short variants:

**Bearer token**
```json
{
  "headers": {
    "Authorization": "Bearer sk_live_abc123..."
  }
}
```

**API key**
```json
{
  "headers": {
    "X-API-Key": "your_api_key_here",
    "X-Client-ID": "your_client_id"
  }
}
```

**Custom headers**
```json
{
  "headers": {
    "X-Custom-Auth": "custom_value",
    "X-Organization": "org_123",
    "X-Tenant": "tenant_456"
  }
}
```

ZAPI will load the file automatically, hide secret values in logs, and apply the headers to every LangChain tool call. See the dedicated [LangChain Integration Guide](examples/langchain/README.md) for a deeper walkthrough, troubleshooting tips, and additional examples.

## API Reference

### ZAPI class

`ZAPI(client_id, secret, llm_provider, llm_model_name, llm_api_key)`

- `client_id` / `secret`: OAuth credentials from Adopt AI.
- `llm_provider`: `"groq"`, `"anthropic"`, `"openai"`, or `"google"`.
- `llm_model_name`: Any model identifier your provider supports. Use the latest available model for your provider (e.g., check your provider's documentation for current model names).
- `llm_api_key`: Provider-specific API key (encrypted immediately per organization context).

Key methods:

- `launch_browser(url, headless=True, **playwright_options)`: Returns a `BrowserSession` that injects auth tokens into every request.
- `set_llm_key(provider, api_key, model_name)`: Update provider credentials on the fly; keys are encrypted instantly.
- `get_llm_provider()`, `get_llm_model_name()`, `has_llm_key()`: Inspect the active LLM configuration.
- `get_encrypted_llm_key()`, `get_decrypted_llm_key()`: Access credential blobs when you must debug (handle decrypted values carefully).
- `upload_har(filepath)`: Upload a HAR file with metadata for enhanced API discovery.
- `get_documented_apis(page=1, page_size=10)`: Fetch paginated API documentation from the Adopt AI platform.

### BrowserSession class

| Method | Description |
|--------|-------------|
| `navigate(url, wait_until="networkidle")` | Navigate to a URL. |
| `click(selector, **kwargs)` | Click an element with Playwright under the hood. |
| `fill(selector, value, **kwargs)` | Type into an input or textarea. |
| `wait_for(selector=None, timeout=None)` | Wait for a selector or a timeout. |
| `dump_logs(filepath)` | Export HAR traffic for later analysis. |
| `close()` | Close the browser and clean up resources. |

## Security & BYOK

- ZAPI requires valid BYOK credentials to unlock enhanced discovery; every key is encrypted with **AES-256-GCM** as soon as it is provided.
- No plaintext keys are stored in memory or logs, and transmission to the Adopt AI discovery service is secured with per-organization isolation.
- Configure any supported provider by passing `(provider, model_name, api_key)` to `set_llm_key()` or by using the `.env` helpers.
- `load_llm_credentials()` ensures secrets are loaded from disk without exposing them in code.
- Providers currently supported: **Anthropic**, **OpenAI**, **Google**, **Groq**.

## Enhanced Discovery Workflow

When you bring your own LLM API key, ZAPI unlocks deeper API insights:

**When to use BYOK**

- Building LLM training datasets from API interactions.
- Generating comprehensive API documentation.
- Performing advanced API security analysis.
- Understanding complex application workflows end to end.
- Creating intelligent API testing scenarios.
- Budgeting API discovery sessions with upfront estimates.

**Example enhanced workflow**

```python
from zapi import ZAPI, analyze_har_file

z = ZAPI()

session = z.launch_browser(url="https://app.example.com")
# ... navigate and interact ...
session.dump_logs("session.har")

stats, report, _ = analyze_har_file("session.har")
print(f"Found {stats.valid_entries} API entries")
print(f"Estimated cost: ${stats.estimated_cost_usd:.2f}")
print(f"Estimated time: {stats.estimated_time_minutes:.1f} minutes")

z.upload_har("session.har")
session.close()
```

## Troubleshooting & Tips

- If `HarProcessingError` appears, the HAR file is malformed or contains unsupported entries—rerun the capture or inspect the skipped reasons in the report.
- ZAPI proceeds without authentication headers when `api-headers.json` is missing; add it only when needed and validate the JSON beforehand.
- Tools will mention which headers were loaded, but the values stay hidden so you can safely confirm configuration without exposing secrets.
- Always rerun `playwright install` after upgrading browsers or moving to a new machine.
- Use `get_documented_apis()` to verify connectivity with the Adopt AI backend before launching long capture sessions.
- Keep `.env` out of version control and rotate your BYOK tokens regularly through [app.adopt.ai](https://app.adopt.ai).

## Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding features, improving documentation, or adding support for new LLM providers, your help is appreciated.

**Get Started:**
- Read our [Contributing Guide](CONTRIBUTING.md) for development setup, coding standards, and pull request guidelines
- Check out [open issues](https://github.com/adoptai/zapi/issues) for tasks to work on
- Join discussions on [GitHub Discussions](https://github.com/adoptai/zapi/discussions)

**Quick Links:**
- [Development Setup](CONTRIBUTING.md#development-setup)
- [Project Structure](CONTRIBUTING.md#project-structure)
- [Adding New LLM Providers](CONTRIBUTING.md#adding-new-llm-providers)
- [Pull Request Process](CONTRIBUTING.md#pull-request-process)

By contributing to ZAPI, you agree that your contributions will be licensed under the MIT License.
