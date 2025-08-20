from miamcpdoc.main import create_server
from miamcpdoc.splash import SPLASH

def main():
    """LangGraph and LangChain Documentation MCP Server."""
    doc_sources = [
        {"name": "LangGraph", "llms_txt": "https://langchain-ai.github.io/langgraph/llms.txt"},
        {"name": "LangChain", "llms_txt": "https://python.langchain.com/llms.txt"}
    ]
    
    print(SPLASH)
    print("Loading LangGraph and LangChain documentation...")
    server = create_server(doc_sources)
    server.run(transport="stdio")

if __name__ == "__main__":
    main()