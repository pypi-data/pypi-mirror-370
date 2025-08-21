#!/bin/bash

# Simple Poetry publishing script
# Usage: ./scripts/publish-poetry.sh [test|prod]

set -e

if [ "$1" = "test" ]; then
    echo "Publishing to TestPyPI with Poetry..."
    poetry config repositories.testpypi https://test.pypi.org/legacy/
    poetry build
    poetry publish --repository testpypi
    echo "Testing installation from TestPyPI..."
    pip install --index-url https://test.pypi.org/simple/ currency-mcp
    echo "✅ TestPyPI publishing complete!"
elif [ "$1" = "prod" ]; then
    echo "Publishing to PyPI with Poetry..."
    poetry build
    poetry publish
    echo "✅ PyPI publishing complete!"
else
    echo "Usage: $0 [test|prod]"
    echo "  test: Publish to TestPyPI and test installation"
    echo "  prod: Publish to production PyPI"
    exit 1
fi
