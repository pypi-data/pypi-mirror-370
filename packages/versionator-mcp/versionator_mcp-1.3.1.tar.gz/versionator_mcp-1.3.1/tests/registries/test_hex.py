"""
Tests for Hex.pm registry functionality
"""

from unittest.mock import patch

import pytest

from tests.conftest import MockResponse, MockSession
from tests.utils import get_hex_version


class TestHexRegistry:
    """Test Hex.pm registry functionality"""

    @pytest.mark.asyncio
    async def test_get_hex_version_success(self):
        """Test successful Hex.pm package version retrieval"""
        mock_response = MockResponse(
            200,
            json_data={
                "name": "ecto",
                "meta": {
                    "description": "A toolkit for data mapping and language integrated query for Elixir",
                    "licenses": ["Apache-2.0"],
                    "links": {
                        "GitHub": "https://github.com/elixir-ecto/ecto",
                        "Docs": "https://hexdocs.pm/ecto/",
                    },
                    "maintainers": ["José Valim", "Eric Meadows-Jönsson"],
                },
                "releases": [
                    {
                        "version": "3.9.2",
                        "inserted_at": "2022-10-25T10:00:00Z",
                        "updated_at": "2022-10-25T10:00:00Z",
                        "url": "https://repo.hex.pm/tarballs/ecto-3.9.2.tar",
                        "has_docs": True,
                        "docs_html_url": "https://hexdocs.pm/ecto/3.9.2/",
                        "requirements": {
                            "decimal": {
                                "app": "decimal",
                                "optional": False,
                                "requirement": "~> 1.6 or ~> 2.0",
                            },
                            "jason": {"app": "jason", "optional": True, "requirement": "~> 1.0"},
                            "telemetry": {
                                "app": "telemetry",
                                "optional": False,
                                "requirement": "~> 0.4 or ~> 1.0",
                            },
                        },
                        "retirement": None,
                    },
                    {
                        "version": "3.9.1",
                        "inserted_at": "2022-09-15T10:00:00Z",
                        "updated_at": "2022-09-15T10:00:00Z",
                        "url": "https://repo.hex.pm/tarballs/ecto-3.9.1.tar",
                        "has_docs": True,
                        "docs_html_url": "https://hexdocs.pm/ecto/3.9.1/",
                        "requirements": {},
                        "retirement": None,
                    },
                ],
            },
        )

        with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
            result = await get_hex_version("ecto")
            assert result.version == "3.9.2"
            assert result.registry == "hex"
            assert "hex.pm" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_hex_version_no_releases(self):
        """Test Hex.pm package with no releases"""
        mock_response = MockResponse(200, json_data={"name": "newpackage", "releases": []})

        with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
            with pytest.raises(Exception, match="No releases found for package 'newpackage'"):
                await get_hex_version("newpackage")
