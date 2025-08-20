"""
Configuration management for Versionator MCP Server

Handles server configuration and environment variable loading with validation.
"""

import os
from dataclasses import dataclass


@dataclass
class AppConfig:
    """Application configuration"""

    mcp_host: str
    mcp_port: int
    external_ip: str
    transport_mode: str
    request_timeout: int


def get_config() -> AppConfig:
    """Load configuration from environment variables with validation"""

    # Server configuration
    mcp_host = os.getenv("FASTMCP_HOST", "0.0.0.0")
    mcp_port = int(os.getenv("FASTMCP_PORT", "8083"))
    external_ip = os.getenv("EXTERNAL_IP", "localhost")
    transport_mode = os.getenv("MCP_TRANSPORT", "streamable-http")

    # API configuration
    request_timeout = int(os.getenv("VERSIONATOR_REQUEST_TIMEOUT", "30"))

    # Validate configuration
    if mcp_port < 1 or mcp_port > 65535:
        raise ValueError(f"Invalid port number: {mcp_port}")

    if request_timeout < 1:
        raise ValueError(f"Invalid request timeout: {request_timeout}")

    return AppConfig(
        mcp_host=mcp_host,
        mcp_port=mcp_port,
        external_ip=external_ip,
        transport_mode=transport_mode,
        request_timeout=request_timeout,
    )
