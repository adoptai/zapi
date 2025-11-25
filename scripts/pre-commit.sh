#!/bin/bash
# Pre-commit script for ZAPI
# This script runs Ruff linting and formatting checks before allowing a commit

set -e  # Exit on error

echo "🔍 Running pre-commit checks..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if ruff is installed
if ! command -v ruff &> /dev/null; then
    echo -e "${RED}❌ Ruff is not installed!${NC}"
    echo "Install it with: pip install ruff"
    exit 1
fi

# Run Ruff linter
echo "📝 Running Ruff linter..."
if ruff check .; then
    echo -e "${GREEN}✅ Linting passed!${NC}"
else
    echo -e "${RED}❌ Linting failed!${NC}"
    echo ""
    echo "Run 'ruff check . --fix' to auto-fix issues"
    exit 1
fi

echo ""

# Run Ruff formatter check
echo "🎨 Checking code formatting..."
if ruff format --check .; then
    echo -e "${GREEN}✅ Formatting check passed!${NC}"
else
    echo -e "${RED}❌ Code is not formatted correctly!${NC}"
    echo ""
    echo "Run 'ruff format .' to format your code"
    exit 1
fi

echo ""
echo -e "${GREEN}✨ All pre-commit checks passed! Ready to commit.${NC}"
