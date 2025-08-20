"""
Tests for RubyGems registry
"""

from unittest.mock import patch

import pytest

from tests.conftest import MockResponse, MockSession
from tests.utils import get_rubygems_version


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
        with pytest.raises(Exception, match="Package 'nonexistent' not found in RubyGems registry"):
            await get_rubygems_version("nonexistent")
