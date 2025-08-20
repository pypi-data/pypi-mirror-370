"""
Tests for Versionator MCP Server API functions
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from versionator_mcp.api.versionator import (
    get_hex_version,
    get_latest_version,
    get_npm_version,
    get_pypi_version,
    get_rubygems_version,
    set_request_timeout,
)


class MockResponse:
    """Mock aiohttp response"""

    def __init__(self, status, json_data=None, text_data=None):
        self.status = status
        self._json_data = json_data
        self._text_data = text_data or ""

    async def json(self):
        return self._json_data

    async def text(self):
        return self._text_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class MockSession:
    """Mock aiohttp session"""

    def __init__(self, response):
        self.response = response

    def get(self, url, **kwargs):
        return self.response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


@pytest.mark.asyncio
async def test_get_npm_version_success():
    """Test successful npm version retrieval"""
    mock_data = {
        "version": "18.2.0",
        "description": "React is a JavaScript library",
        "homepage": "https://react.dev/",
        "license": "MIT",
    }

    mock_response = MockResponse(200, mock_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        result = await get_npm_version("react")

        assert result.name == "react"
        assert result.version == "18.2.0"
        assert result.registry == "npm"
        assert result.description == "React is a JavaScript library"
        assert result.homepage == "https://react.dev/"
        assert result.license == "MIT"
        assert "registry.npmjs.org" in result.registry_url


@pytest.mark.asyncio
async def test_get_npm_version_not_found():
    """Test npm package not found"""
    mock_response = MockResponse(404, text_data="Not found")

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        with pytest.raises(Exception, match="Package 'nonexistent' not found in npm registry"):
            await get_npm_version("nonexistent")


@pytest.mark.asyncio
async def test_get_npm_version_empty_name():
    """Test npm with empty package name"""
    with pytest.raises(ValueError, match="Package name cannot be empty"):
        await get_npm_version("")

    with pytest.raises(ValueError, match="Package name cannot be empty"):
        await get_npm_version("   ")


@pytest.mark.asyncio
async def test_get_npm_version_api_error():
    """Test npm API error handling"""
    mock_response = MockResponse(500, text_data="Internal server error")

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        with pytest.raises(Exception, match="npm API error 500: Internal server error"):
            await get_npm_version("react")


@pytest.mark.asyncio
async def test_get_rubygems_version_success():
    """Test successful RubyGems version retrieval"""
    mock_data = {"version": "7.0.4"}
    mock_response = MockResponse(200, mock_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        result = await get_rubygems_version("rails")

        assert result.name == "rails"
        assert result.version == "7.0.4"
        assert result.registry == "rubygems"
        assert "rubygems.org" in result.registry_url


@pytest.mark.asyncio
async def test_get_rubygems_version_not_found():
    """Test RubyGems gem not found"""
    mock_response = MockResponse(404, text_data="Not found")

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        with pytest.raises(Exception, match="Gem 'nonexistent' not found in RubyGems registry"):
            await get_rubygems_version("nonexistent")


@pytest.mark.asyncio
async def test_get_pypi_version_success():
    """Test successful PyPI version retrieval"""
    mock_data = {
        "info": {
            "version": "4.1.0",
            "summary": "The Web framework for perfectionists",
            "home_page": "https://www.djangoproject.com/",
            "license": "BSD",
        }
    }
    mock_response = MockResponse(200, mock_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        result = await get_pypi_version("django")

        assert result.name == "django"
        assert result.version == "4.1.0"
        assert result.registry == "pypi"
        assert result.description == "The Web framework for perfectionists"
        assert result.homepage == "https://www.djangoproject.com/"
        assert result.license == "BSD"
        assert "pypi.org" in result.registry_url


@pytest.mark.asyncio
async def test_get_pypi_version_not_found():
    """Test PyPI package not found"""
    mock_response = MockResponse(404, text_data="Not found")

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        with pytest.raises(Exception, match="Package 'nonexistent' not found in PyPI registry"):
            await get_pypi_version("nonexistent")


@pytest.mark.asyncio
async def test_get_hex_version_success():
    """Test successful Hex.pm version retrieval"""
    mock_data = {
        "releases": [{"version": "3.8.0"}, {"version": "3.7.0"}],
        "meta": {
            "description": "A toolkit for data mapping",
            "links": {"GitHub": "https://github.com/elixir-ecto/ecto"},
            "licenses": ["Apache-2.0"],
        },
    }
    mock_response = MockResponse(200, mock_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        result = await get_hex_version("ecto")

        assert result.name == "ecto"
        assert result.version == "3.8.0"
        assert result.registry == "hex"
        assert result.description == "A toolkit for data mapping"
        assert result.homepage == "https://github.com/elixir-ecto/ecto"
        assert result.license == "Apache-2.0"
        assert "hex.pm" in result.registry_url


@pytest.mark.asyncio
async def test_get_hex_version_no_releases():
    """Test Hex.pm package with no releases"""
    mock_data = {"releases": [], "meta": {}}
    mock_response = MockResponse(200, mock_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        with pytest.raises(Exception, match="No releases found for package 'newpackage'"):
            await get_hex_version("newpackage")


@pytest.mark.asyncio
async def test_get_latest_version_npm():
    """Test get_latest_version with npm"""
    mock_data = {"version": "18.2.0"}
    mock_response = MockResponse(200, mock_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        result = await get_latest_version("npm", "react")
        assert result.version == "18.2.0"
        assert result.registry == "npm"


@pytest.mark.asyncio
async def test_get_latest_version_aliases():
    """Test get_latest_version with various aliases"""
    # Test npm aliases
    npm_data = {"version": "18.2.0"}
    npm_response = MockResponse(200, npm_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(npm_response)):
        for alias in ["npm", "node", "nodejs"]:
            result = await get_latest_version(alias, "react")
            assert result.registry == "npm"

    # Test Ruby aliases
    ruby_data = {"version": "7.0.4"}
    ruby_response = MockResponse(200, ruby_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(ruby_response)):
        for alias in ["rubygems", "gem", "ruby"]:
            result = await get_latest_version(alias, "rails")
            assert result.registry == "rubygems"

    # Test Python aliases
    pypi_data = {"info": {"version": "4.1.0"}}
    pypi_response = MockResponse(200, pypi_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(pypi_response)):
        for alias in ["pypi", "pip", "python"]:
            result = await get_latest_version(alias, "django")
            assert result.registry == "pypi"

    # Test Elixir aliases
    hex_data = {"releases": [{"version": "3.8.0"}], "meta": {}}
    hex_response = MockResponse(200, hex_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(hex_response)):
        for alias in ["hex", "elixir", "hex.pm"]:
            result = await get_latest_version(alias, "ecto")
            assert result.registry == "hex"


@pytest.mark.asyncio
async def test_get_latest_version_invalid_manager():
    """Test get_latest_version with invalid package manager"""
    with pytest.raises(ValueError, match="Unknown package manager 'cargo'"):
        await get_latest_version("cargo", "tokio")


@pytest.mark.asyncio
async def test_get_latest_version_empty_manager():
    """Test get_latest_version with empty package manager"""
    with pytest.raises(ValueError, match="Package manager cannot be empty"):
        await get_latest_version("", "package")

    with pytest.raises(ValueError, match="Package manager cannot be empty"):
        await get_latest_version("   ", "package")


def test_set_request_timeout():
    """Test setting request timeout"""
    set_request_timeout(60)
    # This test just verifies the function doesn't crash
    # The actual timeout is used internally in the module
