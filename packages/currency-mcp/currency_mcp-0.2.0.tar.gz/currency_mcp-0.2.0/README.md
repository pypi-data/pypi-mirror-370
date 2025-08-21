# Currency MCP Server

A Model Context Protocol (MCP) server for currency conversion using the reliable [Frankfurter API](https://api.frankfurter.app/).

## Features

- **Real-time Exchange Rates**: Get current exchange rates for 31+ currencies
- **Historical Data**: Convert currencies using historical rates
- **MCP Integration**: Seamlessly integrates with MCP-compatible AI tools
- **No API Keys Required**: Free and reliable service
- **Async Support**: Built with modern async Python

## Installation

```bash
pip install currency-mcp
```

## Quick Start

```python
from currency_mcp_server import mcp

# The server is now ready to handle MCP requests
# Use with any MCP-compatible client
```

## Available Tools

### `list_currencies`
Lists all supported currencies with descriptions.

### `convert_currency`
Converts amounts between currencies with support for:
- Current exchange rates
- Historical rates (with date parameter)
- Input validation
- Error handling

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/currency-mcp.git
cd currency-mcp

# Install dependencies
uv sync

# Run tests
python tests/client.py
```

## License

MIT License - see LICENSE file for details.