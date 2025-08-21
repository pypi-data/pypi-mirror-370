#!/bin/bash

# Simple uv publishing script
# Usage: ./scripts/publish-uv.sh [test|prod]

set -e

if [ "$1" = "test" ]; then
    echo "Publishing to TestPyPI with uv..."
    uv run python -m build
    uv run twine check dist/*
    uv run twine upload --repository testpypi dist/*
    echo "Testing installation from TestPyPI..."
    uv pip install --index-url https://test.pypi.org/simple/ currency-mcp
    echo "✅ TestPyPI publishing complete!"
elif [ "$1" = "prod" ]; then
    echo "Publishing to PyPI with uv..."
    uv run python -m build
    uv run twine check dist/*
    uv run twine upload dist/*
    echo "✅ PyPI publishing complete!"
else
    echo "Usage: $0 [test|prod]"
    echo "  test: Publish to TestPyPI and test installation"
    echo "  prod: Publish to production PyPI"
    exit 1
fi
