from miamcpdoc.main import create_server
from miamcpdoc.splash import SPLASH

def main():
    """What is LLMs Documentation MCP Server."""
    doc_sources = [
        {"name": "WhatIsLLMs", "llms_txt": "https://llmstxt.org/llms.txt"}
    ]
    
    print(SPLASH)
    print("Loading What is LLMs documentation...")
    server = create_server(doc_sources)
    server.run(transport="stdio")

if __name__ == "__main__":
    main()