"""
Versionator MCP Server

An MCP server that queries package registries (npm, RubyGems, PyPI, Hex.pm)
for the latest release versions of packages.
"""

__version__ = "1.0.0"
__all__ = ["create_app", "get_config"]

from .app import create_app
from .config import get_config
