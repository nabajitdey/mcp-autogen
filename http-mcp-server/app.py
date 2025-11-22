from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sse-server")

@mcp.tool()
def find_max(numbers: list[int]) -> int:
    """
    Find the maximum number in a list of integers.
    
    :param numbers: List of integers
    :return: Maximum integer from the list
    """
    return max(numbers)

@mcp.tool()
def find_min(numbers: list[int]) -> int:
    """
    Find the minimum number in a list of integers.
    
    :param numbers: List of integers
    :return: Minimum integer from the list
    """
    return min(numbers)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
