# ZAPI Scripts

Utility scripts for ZAPI development and maintenance.

## Pre-commit Script

**File:** `pre-commit.sh`

Runs Ruff linting and formatting checks before allowing a commit.

### Usage

```bash
# Make it executable (one-time)
chmod +x scripts/pre-commit.sh

# Run manually
./scripts/pre-commit.sh
```

### What it checks

- ✅ Ruff linting (with auto-fix suggestions)
- ✅ Ruff formatting (with format suggestions)
- ❌ Exits with error if checks fail

### Alternative: Use pre-commit hooks

For automatic checks on every commit:

```bash
pip install pre-commit
pre-commit install
```

This uses `.pre-commit-config.yaml` and runs automatically on `git commit`.
