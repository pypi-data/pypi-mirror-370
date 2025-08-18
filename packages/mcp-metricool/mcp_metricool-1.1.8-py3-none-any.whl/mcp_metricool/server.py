from .tools import tools

mcp = tools.mcp

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
