# Small HTTP MCP (Model-Controller-Processor) server example using FastMCP.
# This module exposes simple tools (find_max, find_min) via the MCP framework
# so they can be invoked remotely over a streamable HTTP transport.
from mcp.server.fastmcp import FastMCP

# Create an MCP application instance.
# The string identifier "sse-server" names this MCP instance; it can be used
# by clients or logs to distinguish different services.
mcp = FastMCP("sse-server")

# Register a callable as an MCP "tool". The decorator wraps the function
# and makes it discoverable and invocable by MCP clients.
@mcp.tool()
def find_max(numbers: list[int]) -> int:
    """
    Find the maximum number in a list of integers.
    
    :param numbers: List of integers
    :return: Maximum integer from the list
    """
    # Rely on Python's built-in max() which raises ValueError on empty lists.
    return max(numbers)

# Another tool registration example. Tools should be pure/simple functions
# where possible so they are easy to serialize/execute remotely.
@mcp.tool()
def find_min(numbers: list[int]) -> int:
    """
    Find the minimum number in a list of integers.
    
    :param numbers: List of integers
    :return: Minimum integer from the list
    """
    # Use built-in min(). Both min and max keep runtime complexity linear.
    return min(numbers)


# Standard Python entry point check. Running this file directly will start
# the MCP server using the specified transport. When imported as a module,
# this block is not executed.
if __name__ == "__main__":
    # Start the MCP application. transport="streamable-http" selects an HTTP
    # transport that supports streaming (e.g., server-sent events).
    # Adjust transport and configuration as needed for deployment.
    mcp.run(transport="streamable-http")
