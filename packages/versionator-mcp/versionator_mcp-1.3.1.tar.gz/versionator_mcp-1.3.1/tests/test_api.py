"""
Versionator MCP Server API tests - refactored into modular files

This file serves as the main entry point for all tests. The actual tests are now
organized in separate files by functionality for better maintainability.
"""

import tests.core.test_http_client
import tests.core.test_registry_factory
import tests.registries.test_hex

# Import key test modules to ensure pytest discovers them
import tests.registries.test_npm
import tests.registries.test_pypi
import tests.registries.test_rubygems
