# Contributing to ZAPI

Thank you for your interest in contributing to ZAPI! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Documentation Requirements](#documentation-requirements)
- [Pull Request Process](#pull-request-process)
- [Adding New LLM Providers](#adding-new-llm-providers)
- [Testing Guidelines](#testing-guidelines)
- [Release Process](#release-process)

## Development Setup

### Prerequisites

- Python 3.9 or later
- pip (Python package manager)
- Git
- [Playwright](https://playwright.dev/python/) browser binaries

### Getting Started

1. Fork and clone the repository:

   ```bash
   git clone https://github.com/YOUR_USERNAME/zapi.git
   cd zapi
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Install Playwright browser binaries:

   ```bash
   playwright install
   ```

5. Set up your environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your credentials from app.adopt.ai
   ```

6. Test the installation:

   ```bash
   python demo.py
   ```

### Development Commands

```bash
# Run the demo script
python demo.py

# Run specific examples
python examples/basic_usage.py
python examples/langchain/demo.py

# Test HAR processing
python -c "from zapi import analyze_har_file; analyze_har_file('demo_session.har')"

# Format code (if using black)
black zapi/ examples/ demo.py

# Lint code (if using pylint)
pylint zapi/
```

## Project Structure

```
zapi/
├── zapi/                      # Main package directory
│   ├── __init__.py           # Package exports
│   ├── core.py               # ZAPI class, OAuth, BYOK encryption
│   ├── session.py            # BrowserSession with Playwright
│   ├── auth.py               # Authentication handlers
│   ├── providers.py          # LLM provider validation
│   ├── encryption.py         # AES-256-GCM key encryption
│   ├── har_processing.py     # HAR analysis and filtering
│   ├── utils.py              # Helper utilities
│   ├── constants.py          # Configuration constants
│   ├── exceptions.py         # Custom exception classes
│   └── integrations/
│       └── langchain/
│           └── tool.py       # LangChain tool integration
├── examples/                  # Example scripts
│   ├── basic_usage.py
│   ├── async_usage.py
│   └── langchain/
│       ├── demo.py           # Interactive LangChain demo
│       └── README.md         # LangChain integration guide
├── docs/                      # Documentation
├── demo.py                    # End-to-end demo script
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Package metadata
├── setup.py                  # Setup script
├── README.md                 # Main documentation
└── CONTRIBUTING.md           # This file
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `zapi/core.py` | Main `ZAPI` class with credential loading, OAuth token exchange, BYOK encryption, HAR upload, and API documentation fetching |
| `zapi/session.py` | `BrowserSession` wrapper around Playwright with auth injection, HAR recording, navigation helpers, and error handling |
| `zapi/providers.py` | LLM provider validation for Anthropic, OpenAI, Google, and Groq with format-specific checks |
| `zapi/encryption.py` | `LLMKeyEncryption` class using AES-256-GCM for secure key storage |
| `zapi/har_processing.py` | `HarProcessor` for filtering static assets, analyzing API calls, and cost estimation |
| `zapi/integrations/langchain/tool.py` | `ZAPILangchainTool` for converting documented APIs into LangChain tools |

## Coding Standards

### Python Style Guide

1. Follow [PEP 8](https://pep8.org/) style guidelines
2. Use type hints for all function parameters and return values
3. Use docstrings for all public classes, methods, and functions
4. Keep functions focused and under 50 lines when possible
5. Use meaningful variable and function names
6. Prefer explicit over implicit
7. Use `pathlib.Path` for file operations
8. Use f-strings for string formatting

### File Headers

Every Python module should include a docstring at the top:

```python
"""Module description.

Detailed explanation of what this module does and how it fits
into the larger ZAPI architecture.
"""
```

### Function Documentation

Every public function must include a docstring with:

1. Brief description
2. Args section with type hints
3. Returns section
4. Raises section for exceptions
5. Example usage (for user-facing functions)

Example:

```python
def analyze_har_file(
    har_file_path: str,
    save_filtered: bool = False,
    filtered_output_path: Optional[str] = None
) -> Tuple[HarStats, str, Optional[str]]:
    """
    Analyze a HAR file and generate statistics.
    
    This function loads a HAR file, filters out static assets,
    and provides cost/time estimates for API discovery processing.
    
    Args:
        har_file_path: Path to the HAR file to analyze
        save_filtered: Whether to save filtered HAR with only API entries
        filtered_output_path: Custom path for filtered HAR (optional)
    
    Returns:
        Tuple of (statistics, formatted_report, filtered_file_path)
    
    Raises:
        HarProcessingError: If HAR file is invalid or cannot be processed
        FileNotFoundError: If HAR file does not exist
    
    Example:
        >>> stats, report, filtered = analyze_har_file("session.har", save_filtered=True)
        >>> print(f"API entries: {stats.valid_entries}")
        >>> print(f"Estimated cost: ${stats.estimated_cost_usd:.2f}")
    """
    # Implementation
```

### Error Handling

1. Use custom exception classes from `zapi/exceptions.py`
2. Provide meaningful error messages
3. Include context in error messages (e.g., file paths, URLs)
4. Document all exceptions in function docstrings
5. Use try-except blocks appropriately
6. Log errors when appropriate

Example:

```python
from .core import ZAPIValidationError, ZAPINetworkError

def upload_har(self, har_file: str):
    """Upload HAR file to ZAPI service."""
    try:
        with open(har_file, 'rb') as f:
            # Upload logic
            pass
    except FileNotFoundError:
        raise ZAPIValidationError(f"HAR file not found: '{har_file}'")
    except requests.exceptions.ConnectionError:
        raise ZAPINetworkError(
            "Cannot connect to ZAPI service. "
            "Please check your internet connection."
        )
```

### Code Organization

1. Group imports in this order:
   - Standard library imports
   - Third-party imports
   - Local application imports
2. Use blank lines to separate logical sections
3. Keep related functionality together
4. Extract complex logic into helper functions
5. Use constants for magic numbers and strings

## Documentation Requirements

### Module Documentation

Each module should have:

1. Clear docstring explaining its purpose
2. Usage examples for public APIs
3. Type hints for all functions
4. Inline comments for complex logic

### README Updates

When adding new features:

1. Update the main README.md with usage examples
2. Add to the appropriate section (Quick Start, API Reference, etc.)
3. Include code examples that users can copy-paste
4. Update the Table of Contents if adding new sections

### Example Scripts

When creating example scripts:

1. Add them to the `examples/` directory
2. Include a header comment explaining what the example demonstrates
3. Make examples self-contained and runnable
4. Use clear variable names and comments
5. Handle errors gracefully with informative messages

## Pull Request Process

1. Create a feature branch from `dev`:

   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the coding standards

3. Test your changes thoroughly:
   - Run existing examples to ensure no regressions
   - Test error cases
   - Test with different Python versions if possible

4. Update documentation:
   - Add/update docstrings
   - Update README.md if needed
   - Add example usage if applicable

5. Commit your changes with clear messages:

   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

6. Push to your fork and create a pull request:

   ```bash
   git push origin feature/your-feature-name
   ```

7. In your pull request description:
   - Explain what the change does
   - Link to any related issues
   - Include screenshots/examples if applicable
   - List any breaking changes

8. Wait for review and address feedback

### Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Write clear commit messages
- Include tests if applicable
- Update documentation
- Ensure code passes linting
- Respond to review comments promptly

## Adding New LLM Providers

To add support for a new LLM provider:

1. Update `zapi/providers.py`:

   ```python
   class LLMProvider(Enum):
       # ... existing providers ...
       NEW_PROVIDER = "newprovider"
   ```

2. Add validation logic in `_validate_key_format()`:

   ```python
   elif provider == LLMProvider.NEW_PROVIDER.value:
       if not api_key.startswith("expected-prefix-"):
           raise LLMKeyException("NewProvider API keys must start with 'expected-prefix-'")
       if len(api_key) < 20:
           raise LLMKeyException("NewProvider API keys must be at least 20 characters long")
   ```

3. Update `get_supported_providers_info()`:

   ```python
   "newprovider": {
       "display_name": "NewProvider",
       "support_level": "main",
       "description": "Fully supported with complete validation"
   }
   ```

4. Update documentation:
   - Add provider to README.md supported providers list
   - Add example usage in Environment Setup section
   - Update `zapi/utils.py` if needed for environment variable mapping

5. Test the new provider:
   - Test key validation
   - Test encryption/decryption
   - Test with actual API calls if possible

## Testing Guidelines

### Manual Testing

1. Test with the demo script:
   ```bash
   python demo.py
   ```

2. Test specific features:
   ```bash
   # Test HAR analysis
   python -c "from zapi import analyze_har_file; print(analyze_har_file('demo_session.har'))"
   
   # Test LangChain integration
   python examples/langchain/demo.py
   ```

3. Test error cases:
   - Invalid credentials
   - Invalid URLs
   - Missing files
   - Network errors

### Testing Checklist

Before submitting a PR, verify:

- [ ] Code runs without errors
- [ ] All examples still work
- [ ] Error messages are clear and helpful
- [ ] Documentation is updated
- [ ] No sensitive data in code or commits
- [ ] Code follows style guidelines
- [ ] New features have usage examples

## Release Process

ZAPI follows semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Creating a Release

1. Update version in `pyproject.toml` and `setup.py`
2. Update `__version__` in `zapi/__init__.py`
3. Update CHANGELOG.md (if exists) with changes
4. Create a release commit:
   ```bash
   git commit -am "Release v0.2.0"
   ```
5. Create a tag:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
6. Create a GitHub release with release notes
7. Publish to PyPI (maintainers only):
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## Questions and Support

- **Issues**: [GitHub Issues](https://github.com/adoptai/zapi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/adoptai/zapi/discussions)
- **Website**: [adopt.ai](https://www.adopt.ai)
- **Twitter**: [@getadoptai](https://twitter.com/getadoptai)
- **LinkedIn**: [Adopt AI](https://www.linkedin.com/company/getadoptai)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other contributors

## License

By contributing to ZAPI, you agree that your contributions will be licensed under the MIT License.

Copyright (c) 2025 AdoptAI

See [LICENSE](LICENSE) file for full license text.

---

Thank you for contributing to ZAPI! Your contributions help make API discovery and LLM integration easier for everyone. 🚀

