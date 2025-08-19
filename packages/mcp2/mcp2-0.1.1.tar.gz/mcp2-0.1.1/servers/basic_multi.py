from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Tool Example")


@mcp.tool()
def plus(a: int, b: int) -> int:
    """multiply two numbers together."""
    return a * b

if __name__ == "__main__":
    mcp.run("stdio")