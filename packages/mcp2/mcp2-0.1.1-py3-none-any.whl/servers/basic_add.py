from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Tool Example")


@mcp.tool()
def sum(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    mcp.run("sse")