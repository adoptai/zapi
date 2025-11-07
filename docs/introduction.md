# Introducing ZAPI - Zero-Config API Intelligence

**3 min read**

_Automatically discover, capture, and document APIs from any web application_

We're excited to introduce **ZAPI** - an open-source Python library that automatically captures network traffic and API calls from web applications. Perfect for API discovery, creating LLM training datasets, and understanding how web applications communicate with their backends.

ZAPI makes it easy to:

* **Capture network traffic** from any web application automatically
* **Export HAR files** compatible with Chrome DevTools and other analysis tools
* **Upload and document APIs** to the adopt.ai platform
* **Interact with web pages** using simple Python commands
* **Run headless or visible** browser sessions for debugging
* **Retrieve documented APIs** with pagination support

## Installation

Install ZAPI and its dependencies:

```bash
pip install -r requirements.txt

# Install browser binaries (REQUIRED)
playwright install
```

**Requirements:** Python 3.9+, Playwright 1.40.0+

## Quick Start

### 1. Get Your API Credentials

ZAPI uses OAuth authentication with the adopt.ai platform and supports LLM integration. You'll need:
- A `client_id` 
- A `secret` key
- An LLM `provider` (anthropic, openai, google, or groq)
- An LLM `api_key` for your chosen provider
- An LLM `model_name` (e.g., "claude-3-5-sonnet-20241022")

Add these to your environment or use them directly in your code.

### 2. Your First API Capture

Start ZAPI with just a few lines of code:

```python
from zapi import ZAPI

# Initialize with client credentials and LLM configuration
z = ZAPI(
    client_id="YOUR_CLIENT_ID", 
    secret="YOUR_SECRET",
    llm_provider="anthropic",
    llm_api_key="sk-ant-YOUR_API_KEY",
    llm_model_name="claude-3-5-sonnet-20241022"
)

# Launch browser and capture traffic
session = z.launch_browser(url="https://app.example.com/dashboard")

# Export network logs
session.dump_logs("session.har")
session.close()
```

The library will:
1. Authenticates with the adopt.ai OAuth API
2. Encrypts your LLM API key for secure tool ingestion
3. Launches a browser with automatic token injection
4. Capturees all network traffic during your session
5. Exports everything to standard HAR format with encrypted LLM metadata

### 3. Test Your Installation

You can also load credentials from a `.env` file:

```bash
# Create .env file with your credentials
echo "LLM_PROVIDER=anthropic" >> .env
echo "LLM_API_KEY=sk-ant-your-key-here" >> .env
echo "LLM_MODEL_NAME=claude-3-5-sonnet-20241022" >> .env
```

Run the demo script to verify everything works:

```bash
python demo.py
```

## LLM Integration & Security

### Supported LLM Providers

ZAPI supports 4 main LLM providers with full validation:

- **Anthropic**
- **OpenAI**:
- **Google**:
- **Groq**:

### Secure Key Encryption

All LLM API keys are encrypted before being used for tool ingestion:

```python
# Keys are automatically encrypted when ZAPI is initialized
z = ZAPI(
    client_id="YOUR_CLIENT_ID",
    secret="YOUR_SECRET", 
    llm_provider="anthropic",
    llm_api_key="sk-ant-your-key",  # Encrypted automatically
    llm_model_name="claude-3-5-sonnet-20241022"
)

# Check if LLM key is configured
if z.has_llm_key():
    print(f"Using provider: {z.get_llm_provider()}")
    print(f"Using model: {z.get_llm_model_name()}")
```

## Core Features & Examples

### Basic Navigation & Interaction

ZAPI provides simple methods for interacting with web applications:

```python
from zapi import ZAPI

z = ZAPI(
    client_id="YOUR_CLIENT_ID", 
    secret="YOUR_SECRET",
    llm_provider="anthropic",
    llm_api_key="sk-ant-YOUR_API_KEY",
    llm_model_name="claude-3-5-sonnet-20241022"
)
session = z.launch_browser(url="https://app.example.com")

# Navigate and interact
session.navigate("/dashboard")
session.click("#settings-button")
session.fill("#search-input", "query")
session.wait_for("#results")

session.dump_logs("session.har")
session.close()
```

### Using Context Managers

For automatic cleanup, use ZAPI sessions as context managers:

```python
z = ZAPI(
    client_id="YOUR_CLIENT_ID", 
    secret="YOUR_SECRET",
    llm_provider="openai",
    llm_api_key="sk-YOUR_OPENAI_KEY",
    llm_model_name="gpt-4"
)

with z.launch_browser(url="https://app.example.com") as session:
    session.navigate("/api-endpoint")
    session.wait_for(timeout=2000)
    session.dump_logs("session.har")
# Browser automatically closed
```

### Uploading to adopt.ai

Once you've captured traffic, upload it to the adopt.ai platform for automatic API documentation:

```python
z = ZAPI(
    client_id="YOUR_CLIENT_ID", 
    secret="YOUR_SECRET",
    llm_provider="anthropic",
    llm_api_key="sk-ant-YOUR_API_KEY",
    llm_model_name="claude-3-5-sonnet-20241022"
)

# Capture traffic
session = z.launch_browser(url="https://app.example.com")
session.dump_logs("session.har")
session.close()

# Upload for documentation (includes encrypted LLM metadata)
z.upload_har("session.har")
```

The adopt.ai platform will:
- Parse all API calls from your HAR file
- Generate documentation automatically 
- Use your encrypted LLM key for enhanced processing
- Make APIs available for LLM agents and tools

### HAR Analysis & Cost Estimation

Before uploading, analyze your HAR files to understand what will be processed and estimate costs:

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
    
    # Show which entries were filtered out and why
    print("\nSkipped entries by reason:")
    for reason, count in stats.skipped_by_reason.items():
        if count > 0:
            print(f"  {reason.replace('_', ' ').title()}: {count:,}")
    
    # Print full formatted report
    print("\n" + report)
    
except HarProcessingError as e:
    print(f"HAR analysis failed: {e}")
```

**HAR Processing Features:**
- **Smart Filtering**: Automatically excludes static assets (JS, CSS, images, fonts)
- **Cost Estimation**: Provides processing cost estimates
- **Time Estimation**: Calculates expected processing time
- **Domain Analysis**: Lists all unique domains found in the session
- **Skip Reasons**: Detailed breakdown of why entries were filtered out
- **Filtered Export**: Option to save a clean HAR file with only API-relevant entries

### Retrieving Documented APIs

After uploading, retrieve your documented APIs programmatically:

```python
z = ZAPI(
    client_id="YOUR_CLIENT_ID", 
    secret="YOUR_SECRET",
    llm_provider="groq",
    llm_api_key="gsk_YOUR_GROQ_KEY",
    llm_model_name="mixtral-8x7b-32768"
)

# Get first page of documented APIs
api_list = z.get_documented_apis(page=1, page_size=10)

# Paginate through all APIs
for page in range(1, api_list['total_pages'] + 1):
    apis = z.get_documented_apis(page=page, page_size=10)
    for api in apis['items']:
        print(f"{api['title']}: {api['path']}")
```

### Visible Browser Mode for Debugging

When developing or debugging, run with a visible browser:

```python
# See the browser in action
session = z.launch_browser(
    url="https://app.example.com", 
    headless=False  # Makes browser visible
)

# Great for debugging selectors and interactions
input("Press ENTER when done navigating...")
session.dump_logs("debug_session.har")
session.close()
```

## Advanced Usage

### Concurrent Sessions with Async

For advanced users, ZAPI supports async operations for concurrent browser sessions:

```python
import asyncio
from zapi.session import BrowserSession

async def capture_session(url, output_file, token):
    session = BrowserSession(auth_token=token, headless=True)
    await session._initialize(initial_url=url)
    await session._wait_for_async(timeout=1000)
    await session._dump_logs_async(output_file)
    await session._close_async()

# Run multiple sessions concurrently
await asyncio.gather(
    capture_session("https://api.example.com/v1/users", "users.har", token),
    capture_session("https://api.example.com/v1/products", "products.har", token),
    capture_session("https://api.example.com/v1/orders", "orders.har", token),
)
```

### Custom Playwright Options

Pass any Playwright browser launch options:

```python
session = z.launch_browser(
    url="https://app.example.com",
    headless=True,
    wait_until="networkidle",  # Wait for network to be idle
    slow_mo=50,  # Slow down operations by 50ms
    timeout=30000  # 30 second timeout
)
```

## Best Practices

### 1. Use Descriptive HAR Filenames

```python
# Good - descriptive names
session.dump_logs("checkout-flow-2024-11-05.har")
session.dump_logs("user-authentication-session.har")

# Less helpful
session.dump_logs("session1.har")
session.dump_logs("test.har")
```

### 2. Organize HAR Files by Feature

```
captures/
├── authentication/
│   ├── login-flow.har
│   └── oauth-callback.har
├── checkout/
│   ├── cart-operations.har
│   └── payment-processing.har
└── admin/
    └── user-management.har
```

### 3. Always Close Sessions

Use context managers or explicit `close()` calls to clean up resources:

```python
# Option 1: Context manager (preferred)
with z.launch_browser(url="...") as session:
    # Your code here
    pass

# Option 2: Explicit close
session = z.launch_browser(url="...")
try:
    # Your code here
    pass
finally:
    session.close()
```

### 4. Handle Authentication States

For applications requiring login, navigate and authenticate before capturing API traffic:

```python
z = ZAPI(
    client_id="YOUR_CLIENT_ID",
    secret="YOUR_SECRET", 
    llm_provider="google",
    llm_api_key="YOUR_GOOGLE_API_KEY",
    llm_model_name="gemini-pro"
)

session = z.launch_browser(url="https://app.example.com/login", headless=False)

# Manually log in when browser opens
input("Log in, then press ENTER to continue...")

# Now capture authenticated API calls
session.navigate("/dashboard")
session.navigate("/api/data")
session.dump_logs("authenticated-session.har")
session.close()
```

### 5. Complete Workflow with Analysis

Here's a complete workflow that includes HAR analysis and cost estimation:

```python
from zapi import ZAPI, load_llm_credentials, analyze_har_file

# Load credentials securely
llm_provider, llm_api_key, llm_model_name = load_llm_credentials()

# Initialize ZAPI
z = ZAPI(
    client_id="YOUR_CLIENT_ID",
    secret="YOUR_SECRET", 
    llm_provider=llm_provider,
    llm_api_key=llm_api_key,
    llm_model_name=llm_model_name
)

# Capture session
session = z.launch_browser(url="https://app.example.com")
# ... navigate and interact ...
session.dump_logs("session.har")
session.close()

# Analyze before upload with cost estimation
stats, report, _ = analyze_har_file("session.har")
print(f"Found {stats.valid_entries} API entries")
print(f"Estimated cost: ${stats.estimated_cost_usd:.2f}")
print(f"Estimated time: {stats.estimated_time_minutes:.1f} minutes")

# Upload with confirmation
if input("Upload? (y/n): ").lower() == 'y':
    z.upload_har("session.har")
    print("Upload completed!")
```

## API Reference

### ZAPI Class

**`ZAPI(client_id, secret, llm_provider, llm_model_name, llm_api_key)`**
- `client_id` (str): OAuth client ID for authentication
- `secret` (str): OAuth secret key
- `llm_provider` (str): LLM provider name ("anthropic", "openai", "google", "groq")
- `llm_model_name` (str): LLM model name (e.g., "claude-3-5-sonnet-20241022")
- `llm_api_key` (str): LLM API key for the specified provider
- Raises `ZAPIValidationError` if credentials are empty or LLM key format is invalid
- Raises `ZAPIAuthenticationError` if authentication fails
- Raises `ZAPINetworkError` if network requests fail

**`launch_browser(url, headless=True, wait_until="load", **playwright_options)`**
- Returns: `BrowserSession` instance
- `url` (str): Initial URL to navigate to
- `headless` (bool): Run browser in headless mode
- `wait_until` (str): When navigation is complete ("load", "domcontentloaded", "networkidle")

**`upload_har(har_file)`**
- Uploads HAR file to adopt.ai for API documentation
- `har_file` (str): Path to HAR file
- Includes encrypted LLM metadata if LLM key is configured
- Returns: JSON response from API

**`set_llm_key(provider, api_key, model_name)`**
- Update LLM configuration after initialization
- `provider` (str): LLM provider name
- `api_key` (str): API key for the provider
- `model_name` (str): Model name to use

**`has_llm_key()`**
- Returns: True if LLM key is configured, False otherwise

**`get_llm_provider()`**
- Returns: Configured LLM provider name or None

**`get_llm_model_name()`**
- Returns: Configured LLM model name or None

**`get_documented_apis(page=1, page_size=10)`**
- Retrieves documented APIs with pagination
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 10)
- Returns: JSON with `items`, `total`, `page`, `page_size`, `total_pages`

### HAR Analysis Functions

**`analyze_har_file(har_file_path, save_filtered=False, filtered_output_path=None)`**
- Comprehensive HAR file analysis with statistics and filtering
- `har_file_path` (str): Path to the HAR file to analyze
- `save_filtered` (bool): Whether to save a filtered HAR file with only API entries
- `filtered_output_path` (str): Optional path for filtered HAR file (auto-generated if None)
- Returns: `(HarStats, formatted_report, filtered_file_path)` tuple
- Automatically excludes static assets and non-API content
- Provides cost and time estimates for processing

**`load_llm_credentials()`**
- Load LLM credentials securely from environment variables or configuration
- Returns: `(provider, api_key, model_name)` tuple
- Supports .env files and fallback configuration

**`HarProcessor(har_file_path)`**
- Low-level HAR processing class for custom analysis
- Methods: `load_and_process()`, `save_filtered_har()`, `get_summary_report()`

### HarStats Object

```python
@dataclass
class HarStats:
    total_entries: int              # Total entries in HAR file
    valid_entries: int              # API-relevant entries after filtering
    skipped_entries: int            # Entries filtered out
    unique_domains: int             # Number of unique domains
    estimated_cost_usd: float       # Estimated processing cost
    estimated_time_minutes: float   # Estimated processing time
    skipped_by_reason: Dict[str, int]  # Breakdown by skip reason
    domains: List[str]              # List of all domains found
```

### BrowserSession Class

| Method | Description |
|--------|-------------|
| `navigate(url, wait_until="networkidle")` | Navigate to URL |
| `click(selector, **kwargs)` | Click element by CSS selector |
| `fill(selector, value, **kwargs)` | Fill form field |
| `wait_for(selector=None, timeout=None)` | Wait for selector or timeout |
| `dump_logs(filepath)` | Export HAR file |
| `close()` | Close browser and cleanup |

## How ZAPI Works

ZAPI's workflow is simple but powerful:

1. **Authentication**: Calls the adopt.ai OAuth API to obtain an access token
2. **LLM Key Encryption**: Encrypts your LLM API key for secure tool ingestion
3. **Token Injection**: Automatically injects the Bearer token in all request headers
4. **Traffic Capture**: Records complete network activity during browser interactions
5. **Smart Analysis**: Filters HAR files to exclude static assets and estimate costs
6. **Export**: Saves everything to standard HAR format compatible with Chrome DevTools
7. **Documentation**: Uploads to adopt.ai with secured LLM metadata for enhanced API processing

## Use Cases

- **API Discovery**: Reverse-engineer undocumented APIs from web applications
- **LLM Training Data**: Create datasets of API calls for training language models
- **Testing & QA**: Capture network traffic for debugging and analysis
- **Documentation**: Automatically generate API documentation from real usage
- **Integration Development**: Understand third-party APIs without documentation
- **Security Research**: Analyze application behavior and API communication patterns

## Get Started Today

Install ZAPI and start discovering APIs:

```bash
pip install -r requirements.txt
playwright install

# Set up your .env file with credentials
echo "LLM_PROVIDER=anthropic" >> .env
echo "LLM_API_KEY=sk-ant-your-key" >> .env
echo "LLM_MODEL_NAME=claude-3-5-sonnet-20241022" >> .env

python demo.py
```

Join the community and contribute:

* **GitHub**: https://github.com/adoptai/zapi
* **adopt.ai Platform**: https://app.adopt.ai
* **License**: MIT

