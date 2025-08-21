#!/bin/bash

# Simple pip publishing script
# Usage: ./scripts/publish-pip.sh [test|prod]

set -e

if [ "$1" = "test" ]; then
    echo "Publishing to TestPyPI..."
    python -m build
    twine check dist/*
    twine upload --repository testpypi dist/*
    echo "Testing installation from TestPyPI..."
    pip install --index-url https://test.pypi.org/simple/ currency-mcp
    echo "✅ TestPyPI publishing complete!"
elif [ "$1" = "prod" ]; then
    echo "Publishing to PyPI..."
    python -m build
    twine check dist/*
    twine upload dist/*
    echo "✅ PyPI publishing complete!"
else
    echo "Usage: $0 [test|prod]"
    echo "  test: Publish to TestPyPI and test installation"
    echo "  prod: Publish to production PyPI"
    exit 1
fi
