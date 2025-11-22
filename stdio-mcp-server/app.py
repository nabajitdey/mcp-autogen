# Simple example MCP (Model Capability Provider) server using FastMCP.
# This file registers a couple of small tools (add, multiply) and starts
# a server that communicates over stdio when run as a script.

from mcp.server.fastmcp import FastMCP

# Create an MCP server instance with a human-readable name. The name helps
# identify this server in logs or when multiple MCP servers are in use.
mcp = FastMCP("stdio-server")

# Register a simple calculator tool. The @mcp.tool() decorator registers the
# Python function as an MCP-exposed capability so remote callers can invoke it.
# Type annotations are used to describe the expected input and output types.
@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Add two numbers together.

    :param a: First number
    :param b: Second number
    :return: Sum of a and b
    """
    # Implementation is intentionally trivial: return the arithmetic sum.
    return a + b

# Another registered tool for multiplication. Exposed similarly via the decorator.
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers together.

    :param a: First number
    :param b: Second number
    :return: Product of a and b
    """
    # Return the product of the two inputs.
    return a * b

# The usual Python entry point. When executed directly, start the MCP server.
# transport="stdio" configures the server to communicate over standard input/output,
# which is common for subprocess-based integrations or testing.
if __name__ == "__main__":
    mcp.run(transport="stdio")
