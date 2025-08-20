#!/usr/bin/env python3
"""
Main entry point for Versionator MCP Server

Handles transport mode detection and server startup configuration
with support for both stdio and streamable HTTP transports.
"""

import os
import sys

from .app import create_app
from .config import get_config


def main() -> None:
    """Main entry point for the Versionator MCP server."""

    # Create the application
    app = create_app()

    # Get configuration
    config = get_config()

    # Check transport mode
    if config.transport_mode == "stdio":
        print("Starting Versionator MCP Server in STDIO mode", file=sys.stderr)
        app.run(transport="stdio")
    else:
        print(f"Starting Versionator MCP Server")
        print(f"Transport: Streamable HTTP (Standard MCP)")
        print(f"Server will bind to: {config.mcp_host}:{config.mcp_port}")
        print(f"External access URL: http://{config.external_ip}:{config.mcp_port}")
        print(f"MCP endpoint: http://{config.external_ip}:{config.mcp_port}/mcp")

        # Set the host and port environment variables for FastMCP
        os.environ["FASTMCP_HOST"] = config.mcp_host
        os.environ["FASTMCP_PORT"] = str(config.mcp_port)

        # Enable debug logging
        os.environ["FASTMCP_DEBUG"] = "true"
        os.environ["FASTMCP_LOG_LEVEL"] = "DEBUG"

        # Run the server with Streamable HTTP transport (standard for remote MCP servers)
        app.run(transport="streamable-http")


if __name__ == "__main__":
    main()
