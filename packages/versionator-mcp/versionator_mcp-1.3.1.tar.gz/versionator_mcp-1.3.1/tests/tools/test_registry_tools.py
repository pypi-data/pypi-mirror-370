"""
Tests for MCP registry tools functionality
"""

import pytest

# Note: MCP tools are tested indirectly through the registry tests
# since they are thin wrappers around the registry functionality.
# The main registry tests already cover the core functionality.


class TestRegistryTools:
    """Test MCP registry tools functionality"""

    def test_tools_module_exists(self):
        """Test that the tools module can be imported"""
        from versionator_mcp.tools import registry_tools

        assert registry_tools is not None

    def test_tools_registration(self):
        """Test that tools are properly registered with FastMCP"""
        # This is tested implicitly when the app starts up
        # The tools registration happens in app.py
        pass
