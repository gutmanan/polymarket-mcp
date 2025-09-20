#!/usr/bin/env python
import sys

from dotenv import load_dotenv

from .server import mcp


def setup_environment():
    # Load environment variables from .env file
    try:
        load_dotenv()
        sys.stderr.write("Loaded environment variables from .env file\n")
    except Exception as e:
        sys.stderr.write(f"Note: .env file not loaded, using default environment variables: {str(e)}\n")
        sys.exit(1)

def run_server():
    """Main entry point for the Polymarket MCP Server"""
    setup_environment()

    sys.stderr.write("\nStarting Polymarket MCP Server...\n")
    sys.stderr.write("Running server in standard mode...\n")

    # Run the server with the stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run_server()
