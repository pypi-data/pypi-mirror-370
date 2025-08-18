from .server import mcp
from .tools import tools

def main() -> None:
    "Run the Metricool MCP server"
    mcp.run(transport='stdio')
