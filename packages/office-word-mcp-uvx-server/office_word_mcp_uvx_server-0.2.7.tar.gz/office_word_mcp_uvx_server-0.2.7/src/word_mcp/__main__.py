"""Word MCP Server main entry point."""

from .server import mcp

if __name__ == "__main__":
    # 运行 Word MCP 服务器
    mcp.run()