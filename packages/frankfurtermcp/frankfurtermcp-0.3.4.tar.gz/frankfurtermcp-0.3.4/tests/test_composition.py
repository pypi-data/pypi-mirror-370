import multiprocessing
import asyncio
import time
from fastmcp import Client

from frankfurtermcp.common import get_nonstdio_mcp_client

# from frankfurtermcp.common import EnvironmentVariables
from frankfurtermcp.composition import (
    COMPOSITION_PREFIX,
    main as mcp_server_composition,
)

import pytest


@pytest.fixture(scope="module")
def mcp_client():
    """
    Fixture to create a client for the MCP server.
    """
    return get_nonstdio_mcp_client()


@pytest.fixture(scope="module", autouse=True)
def mcp_server():
    print("[fixture] Starting MCP server process")
    proc = multiprocessing.Process(
        target=mcp_server_composition,
    )
    proc.start()

    async def wait_for_server(timeout: float = 5.0) -> bool:
        """
        Wait for the MCP server to start and be ready to accept connections.
        """
        client = get_nonstdio_mcp_client()
        ping_result = False
        start = time.time()
        while (time.time() - start) < timeout and not ping_result:
            try:
                async with client:
                    ping_result = await client.ping()
            except Exception:
                # Don't panic, give it a bit more time!
                time.sleep(0.1)
        return ping_result

    try:
        # Check connection to the server
        if not asyncio.run(wait_for_server()):
            raise RuntimeError(
                "The MCP server process did not start in time or is not responding."
            )
        yield  # Run tests now
    finally:
        print("[fixture] Stopping MCP server process")
        if proc.is_alive():
            proc.terminate()
            proc.join()


class TestMCPComposition:
    async def list_tools(self, mcp_client: Client):
        """
        Helper method to call a tool on the MCP server.
        """
        async with mcp_client:
            result = await mcp_client.list_tools()
            await mcp_client.close()
        return result

    def test_list_tools(self, mcp_client):
        """
        Test the whether we can list the tools starting with the Frankfurter MCP tool name prefix.
        """
        tools = asyncio.run(
            self.list_tools(
                mcp_client=mcp_client,
            )
        )
        for tool in tools:
            print(f"Tool name: {tool.name}. Description: {tool.description}")
        assert isinstance(tools, list), "Expected a list of tools"
        assert len(tools) == 6, "Expected 6 tools to be available"
        composed_tools = [
            tool for tool in tools if tool.name.startswith(COMPOSITION_PREFIX)
        ]
        assert all(
            (isinstance(tool.name, str) and tool.name.startswith(COMPOSITION_PREFIX))
            for tool in composed_tools
        ), f"All composed tool names start with '{COMPOSITION_PREFIX}'"
