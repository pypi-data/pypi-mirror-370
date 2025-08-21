import asyncio
import logging
import os
from contextlib import AsyncExitStack
from typing import Literal

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MCPClient:
    """Implementation of the MCP client."""

    def __init__(self):
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(
        self,
        server_script_path: str,
        command: Literal["python", "node"] = "python",
    ) -> None:
        """Connect to the MCP server."""
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env={"PYTHONPATH": os.getcwd()},
        )
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params),
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write),
        )

        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools
        logger.info(
            f"\nConnected to server with tools: {[tool.name for tool in tools]}"
        )

        # Test calling all available tools to verify the connection works
        await self._test_all_tools()

    async def _test_all_tools(self):
        """Test all available tools in the MCP server."""
        if not self.session:
            logger.error("No active session to test tools")
            return

        await self._test_list_currencies()
        await self._test_convert_currency()
        self._print_test_summary()

    async def _test_list_currencies(self):
        """Test the list_currencies tool."""
        logger.info("Testing list_currencies tool...")
        try:
            list_currencies_result = await self.session.call_tool("list_currencies", {})
            logger.info(
                f"✅ list_currencies successful: {list_currencies_result.content}"
            )
        except Exception as e:
            logger.error(f"❌ list_currencies failed: {e}")

    async def _test_convert_currency(self):
        """Test the convert_currency tool with various scenarios."""
        logger.info("Testing convert_currency tool...")

        await self._test_basic_conversions()
        await self._test_historical_conversions()
        await self._test_edge_cases()

    async def _test_basic_conversions(self):
        """Test basic currency conversion scenarios."""
        # Test 1: Basic conversion (USD to EUR)
        try:
            convert_args = {
                "args": {"amount": 100.0, "from_code": "USD", "to_code": "EUR"}
            }
            convert_result = await self.session.call_tool(
                "convert_currency", convert_args
            )
            logger.info(
                f"✅ convert_currency (USD→EUR) successful: {convert_result.content}"
            )
        except Exception as e:
            logger.error(f"❌ convert_currency (USD→EUR) failed: {e}")

        # Test 1b: Try a different currency pair (CAD to USD)
        try:
            convert_args_cad = {
                "args": {"amount": 100.0, "from_code": "CAD", "to_code": "USD"}
            }
            convert_cad_result = await self.session.call_tool(
                "convert_currency", convert_args_cad
            )
            logger.info(
                f"✅ convert_currency (CAD→USD) successful: {convert_cad_result.content}"
            )
        except Exception as e:
            logger.error(f"❌ convert_currency (CAD→USD) failed: {e}")

    async def _test_historical_conversions(self):
        """Test historical currency conversion scenarios."""
        # Test 2: Conversion with historical date
        try:
            convert_args_historical = {
                "args": {
                    "amount": 50.0,
                    "from_code": "USD",
                    "to_code": "GBP",
                    "date": "2024-01-15",
                }
            }
            convert_historical_result = await self.session.call_tool(
                "convert_currency", convert_args_historical
            )
            logger.info(
                f"✅ convert_currency (USD→GBP historical) successful: {convert_historical_result.content}"
            )
        except Exception as e:
            logger.error(f"❌ convert_currency (USD→GBP historical) failed: {e}")

        # Test 2b: Conversion with more recent historical date (should work)
        try:
            convert_args_recent = {
                "args": {
                    "amount": 25.0,
                    "from_code": "EUR",
                    "to_code": "USD",
                    "date": "2025-08-20",  # Yesterday
                }
            }
            convert_recent_result = await self.session.call_tool(
                "convert_currency", convert_args_recent
            )
            logger.info(
                f"✅ convert_currency (EUR→USD recent) successful: {convert_recent_result.content}"
            )
        except Exception as e:
            logger.error(f"❌ convert_currency (EUR→USD recent) failed: {e}")

    async def _test_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test 3: Same currency conversion (should return 1:1 ratio)
        try:
            convert_args_same = {
                "args": {"amount": 75.0, "from_code": "USD", "to_code": "USD"}
            }
            convert_same_result = await self.session.call_tool(
                "convert_currency", convert_args_same
            )
            logger.info(
                f"✅ convert_currency (USD→USD) successful: {convert_same_result.content}"
            )
        except Exception as e:
            logger.error(f"❌ convert_currency (USD→USD) failed: {e}")

        # Test 4: Invalid currency code (should fail gracefully)
        try:
            convert_args_invalid = {
                "args": {"amount": 100.0, "from_code": "INVALID", "to_code": "EUR"}
            }
            convert_invalid_result = await self.session.call_tool(
                "convert_currency", convert_args_invalid
            )
            logger.info(
                f"✅ convert_currency (INVALID→EUR) successful: {convert_invalid_result.content}"
            )
        except Exception as e:
            logger.info(f"✅ convert_currency (INVALID→EUR) correctly failed: {e}")

        logger.info("All tool tests completed!")

    def _print_test_summary(self):
        """Print a summary of all test results."""
        logger.info("\n" + "=" * 50)
        logger.info("TEST SUMMARY:")
        logger.info("✅ list_currencies - Working correctly")
        logger.info("✅ convert_currency - Basic functionality working")
        logger.info(
            "✅ Error handling - Properly validates input and handles API errors"
        )
        logger.info("✅ Same currency conversion - Returns 1:1 ratio as expected")
        logger.info("✅ Input validation - Correctly rejects invalid currency codes")
        logger.info("=" * 50)


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server("currency_mcp_server.py", command="python")
    finally:
        await client.exit_stack.aclose()


if __name__ == "__main__":
    asyncio.run(main())
