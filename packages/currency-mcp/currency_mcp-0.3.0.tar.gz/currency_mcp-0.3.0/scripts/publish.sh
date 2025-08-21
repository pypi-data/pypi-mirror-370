#!/bin/bash

# Simple master publishing script
# Usage: ./scripts/publish.sh [pip|poetry|uv] [test|prod]

if [ $# -ne 2 ]; then
    echo "Usage: $0 [pip|poetry|uv] [test|prod]"
    echo ""
    echo "Examples:"
    echo "  $0 pip test      # Test with pip"
    echo "  $0 poetry prod   # Production with Poetry"
    echo "  $0 uv test       # Test with uv"
    exit 1
fi

TOOL=$1
TARGET=$2

case $TOOL in
    "pip"|"poetry"|"uv")
        ;;
    *)
        echo "Error: Unknown tool '$TOOL'. Use pip, poetry, or uv."
        exit 1
        ;;
esac

case $TARGET in
    "test"|"prod")
        ;;
    *)
        echo "Error: Unknown target '$TARGET'. Use test or prod."
        exit 1
        ;;
esac

echo "Running $TOOL publishing for $TARGET..."
./scripts/publish-$TOOL.sh $TARGET
