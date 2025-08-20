"""
Tests for npm registry
"""

from unittest.mock import patch

import pytest

from tests.conftest import MockResponse, MockSession
from tests.utils import get_npm_version


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
