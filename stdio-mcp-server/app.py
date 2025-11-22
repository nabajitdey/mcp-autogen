from mcp.server.fastmcp import FastMCP

# Create an MCP server with a name
mcp = FastMCP("stdio-server")

# Register a simple calculator tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Add two numbers together.
    
    :param a: First number
    :param b: Second number
    :return: Sum of a and b
    """
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers together.
    
    :param a: First number
    :param b: Second number
    :return: Product of a and b
    """
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")
