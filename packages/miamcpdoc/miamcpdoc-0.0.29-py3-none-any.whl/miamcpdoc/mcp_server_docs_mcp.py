import os

from miamcpdoc.main import create_server
from miamcpdoc.splash import SPLASH

def main():
    """Miadi MCP Server Documentation MCP Server."""
    doc_sources = [
        {"name": "MiadiMCPServer", "llms_txt": os.path.join(os.path.dirname(__file__), "mcp_server_docs", "llms-miadi-mcp-server.txt")}
    ]
    
    print(SPLASH)
    print("Miadi MCP Server documentation server is running (blocking terminal). Press Ctrl+C to stop.")
    server = create_server(doc_sources)
    server.run(transport="stdio")

if __name__ == "__main__":
    main()