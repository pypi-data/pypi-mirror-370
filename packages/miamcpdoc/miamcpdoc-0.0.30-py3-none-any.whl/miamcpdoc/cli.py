#!/usr/bin/env python3
"""Command-line interface for mcp-llms-txt server."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict

import yaml

from miamcpdoc._version import __version__
from miamcpdoc.main import create_server, DocSource
from miamcpdoc.splash import SPLASH


class CustomFormatter(
    argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    # Custom formatter to preserve epilog formatting while showing default values
    pass


EPILOG = """
Examples:
  # Create initial config.yaml in current directory
  miamcpdoc --init
  
  # Create config.yaml with interactive prompts
  miamcpdoc --init --interactive
  
  # Use default bundled configuration
  miamcpdoc --default
  miamcpdoc -D
  
  # Directly specifying llms.txt URLs with optional names
  miamcpdoc --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt
  
  # Using a local file (absolute or relative path)
  miamcpdoc --urls LocalDocs:/path/to/llms.txt --allowed-domains '*'
  
  # Using a YAML config file
  miamcpdoc --yaml config.yaml

  # Using a JSON config file
  miamcpdoc --json config.json

  # Combining multiple documentation sources
  miamcpdoc --yaml config.yaml --json config.json --urls LangGraph:https://langchain-ai.github.io/langgraph/llms.txt

  # Using SSE transport with default host (127.0.0.1) and port (8000)
  miamcpdoc --yaml config.yaml --transport sse
  
  # Using SSE transport with custom host and port
  miamcpdoc --yaml config.yaml --transport sse --host 0.0.0.0 --port 9000
  
  # Using SSE transport with additional HTTP options
  miamcpdoc --yaml config.yaml --follow-redirects --timeout 15 --transport sse --host localhost --port 8080
  
  # Allow fetching from additional domains. The domains hosting the llms.txt files are always allowed.
  miamcpdoc --yaml config.yaml --allowed-domains https://example.com/ https://another-example.com/
  
  # Allow fetching from any domain
  miamcpdoc --yaml config.yaml --allowed-domains '*'
"""


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    # Custom formatter to preserve epilog formatting
    parser = argparse.ArgumentParser(
        description="MCP LLMS-TXT Documentation Server",
        formatter_class=CustomFormatter,
        epilog=EPILOG,
    )

    # Initialization options
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create a config.yaml file in the current directory",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Use interactive prompts when creating config (requires --init)",
    )
    parser.add_argument(
        "--default",
        "-D",
        action="store_true",
        help="Use the default bundled configuration",
    )

    # Allow combining multiple doc source methods
    parser.add_argument(
        "--yaml", "-y", type=str, help="Path to YAML config file with doc sources"
    )
    parser.add_argument(
        "--json", "-j", type=str, help="Path to JSON config file with doc sources"
    )
    parser.add_argument(
        "--urls",
        "-u",
        type=str,
        nargs="+",
        help="List of llms.txt URLs or file paths with optional names (format: 'url_or_path' or 'name:url_or_path')",
    )

    parser.add_argument(
        "--follow-redirects",
        action="store_true",
        help="Whether to follow HTTP redirects",
    )
    parser.add_argument(
        "--allowed-domains",
        type=str,
        nargs="*",
        help="Additional allowed domains to fetch documentation from. Use '*' to allow all domains.",
    )
    parser.add_argument(
        "--timeout", type=float, default=10.0, help="HTTP request timeout in seconds"
    )
    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio", "sse"],
        help="Transport protocol for MCP server",
    )

    parser.add_argument(
        "--creative-frameworks",
        action="store_true",
        help="Load documentation for Creative Orientation, Narrative Remixing, and RISE Frameworks.",
    )
    parser.add_argument(
        "--miadi-mcp-server-docs",
        action="store_true",
        help="Load documentation for Miadi MCP Server.",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        help=(
            "Log level for the server. Use one on the following: DEBUG, INFO, "
            "WARNING, ERROR."
            " (only used with --transport sse)"
        ),
    )

    # SSE-specific options
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the server to (only used with --transport sse)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (only used with --transport sse)",
    )

    # Version information
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"miamcpdoc {__version__}",
        help="Show version information and exit",
    )

    return parser.parse_args()


def load_config_file(file_path: str, file_format: str) -> List[Dict[str, str]]:
    """Load configuration from a file.

    Args:
        file_path: Path to the config file
        file_format: Format of the config file ("yaml" or "json")

    Returns:
        List of doc source configurations
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            if file_format.lower() == "yaml":
                config = yaml.safe_load(file)
            elif file_format.lower() == "json":
                config = json.load(file)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")

        if not isinstance(config, list):
            raise ValueError("Config file must contain a list of doc sources")

        return config
    except (FileNotFoundError, yaml.YAMLError, json.JSONDecodeError) as e:
        print(f"Error loading config file: {e}", file=sys.stderr)
        sys.exit(1)


def get_default_config_path() -> Path:
    """Get the path to the bundled default config file.
    
    Returns:
        Path to the default config.yaml file
    """
    return Path(__file__).parent / "default_config.yaml"


def create_config_file(config_path: str, interactive: bool = False) -> None:
    """Create a config.yaml file.
    
    Args:
        config_path: Path where to create the config file
        interactive: Whether to use interactive prompts
    """
    if os.path.exists(config_path):
        print(f"Config file already exists at {config_path}")
        return
    
    if interactive:
        print("Creating interactive config.yaml...")
        print("Enter documentation sources (press Enter with empty name to finish):")
        
        doc_sources = []
        while True:
            name = input("Documentation source name (or press Enter to finish): ").strip()
            if not name:
                break
            
            url = input(f"llms.txt URL for {name}: ").strip()
            if not url:
                print("URL cannot be empty, skipping...")
                continue
                
            description = input(f"Description for {name} (optional): ").strip()
            
            source = {"name": name, "llms_txt": url}
            if description:
                source["description"] = description
            
            doc_sources.append(source)
        
        if not doc_sources:
            print("No sources provided, using default configuration...")
            # Copy default config
            default_path = get_default_config_path()
            with open(default_path, 'r', encoding='utf-8') as src:
                content = src.read()
        else:
            content = yaml.dump(doc_sources, default_flow_style=False, sort_keys=False)
    else:
        # Copy default config
        default_path = get_default_config_path()
        with open(default_path, 'r', encoding='utf-8') as src:
            content = src.read()
    
    with open(config_path, 'w', encoding='utf-8') as dst:
        dst.write(content)
    
    print(f"Created config file at {config_path}")


def create_doc_sources_from_urls(urls: List[str]) -> List[DocSource]:
    """Create doc sources from a list of URLs or file paths with optional names.

    Args:
        urls: List of llms.txt URLs or file paths with optional names
             (format: 'url_or_path' or 'name:url_or_path')

    Returns:
        List of DocSource objects
    """
    doc_sources = []
    for entry in urls:
        if not entry.strip():
            continue
        if ":" in entry and not entry.startswith(("http:", "https:")):
            # Format is name:url
            name, url = entry.split(":", 1)
            doc_sources.append({"name": name, "llms_txt": url})
        else:
            # Format is just url
            doc_sources.append({"llms_txt": entry})
    return doc_sources


def main() -> None:
    """Main entry point for the CLI."""
    # Check if any arguments were provided
    if len(sys.argv) == 1:
        # No arguments, print help
        # Use the same custom formatter as parse_args()
        help_parser = argparse.ArgumentParser(
            description="MCP LLMS-TXT Documentation Server",
            formatter_class=CustomFormatter,
            epilog=EPILOG,
        )
        # Add version to help parser too
        help_parser.add_argument(
            "--version",
            "-V",
            action="version",
            version=f"miamcpdoc {__version__}",
            help="Show version information and exit",
        )
        help_parser.print_help()
        sys.exit(0)

    args = parse_args()

    # Handle initialization
    if args.init:
        if args.interactive and not args.init:
            print("Error: --interactive requires --init", file=sys.stderr)
            sys.exit(1)
        
        config_path = "config.yaml"
        create_config_file(config_path, args.interactive)
        return

    if args.creative_frameworks:
        from miamcpdoc import creative_frameworks_mcp
        creative_frameworks_mcp.main()
        return

    if args.miadi_mcp_server_docs:
        from miamcpdoc import mcp_server_docs_mcp
        mcp_server_docs_mcp.main()
        return

    # Load doc sources based on command-line arguments
    doc_sources: List[DocSource] = []

    # Handle default configuration
    if args.default:
        default_config_path = get_default_config_path()
        doc_sources.extend(load_config_file(str(default_config_path), "yaml"))
    
    # Check if any source options were provided (unless using default)
    if not args.default and not (args.yaml or args.json or args.urls):
        print(
            "Error: At least one source option (--yaml, --json, --urls, or --default) is required",
            file=sys.stderr,
        )
        sys.exit(1)

    # Merge doc sources from all provided methods
    if args.yaml:
        doc_sources.extend(load_config_file(args.yaml, "yaml"))
    if args.json:
        doc_sources.extend(load_config_file(args.json, "json"))
    if args.urls:
        doc_sources.extend(create_doc_sources_from_urls(args.urls))

    # Only used with SSE transport
    settings = {
        "host": args.host,
        "port": args.port,
        "log_level": "INFO",
    }

    # Create and run the server
    server = create_server(
        doc_sources,
        follow_redirects=args.follow_redirects,
        timeout=args.timeout,
        settings=settings,
        allowed_domains=args.allowed_domains,
    )

    if args.transport == "sse":
        print()
        print(SPLASH)
        print()

        print(
            f"Launching MCPDOC server with {len(doc_sources)} doc sources",
        )

    # Pass transport-specific options
    server.run(transport=args.transport)


if __name__ == "__main__":
    main()
