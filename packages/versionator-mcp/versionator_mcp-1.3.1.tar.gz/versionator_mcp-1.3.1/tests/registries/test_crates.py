"""
Tests for crates.io registry functionality
"""

from unittest.mock import patch

import pytest

from tests.conftest import MockResponse, MockSession
from tests.utils import get_crates_version


class TestCratesRegistry:
    """Test crates.io registry functionality"""

    @pytest.mark.asyncio
    async def test_get_crates_version_success(self):
        """Test successful crates.io package version retrieval"""
        mock_response = MockResponse(
            200,
            json_data={
                "crate": {
                    "id": "serde",
                    "name": "serde",
                    "updated_at": "2023-01-15T10:00:00.000000+00:00",
                    "versions": None,
                    "keywords": ["serde", "serialization", "no_std"],
                    "categories": ["encoding"],
                    "badges": [],
                    "created_at": "2014-12-21T22:47:39.000000+00:00",
                    "downloads": 500000000,
                    "recent_downloads": 50000000,
                    "max_version": "1.0.152",
                    "newest_version": "1.0.152",
                    "max_stable_version": "1.0.152",
                    "description": "A generic serialization/deserialization framework",
                    "homepage": "https://serde.rs",
                    "documentation": "https://docs.serde.rs/serde/",
                    "repository": "https://github.com/serde-rs/serde",
                    "links": {
                        "version_downloads": "/api/v1/crates/serde/downloads",
                        "versions": "/api/v1/crates/serde/versions",
                        "owners": "/api/v1/crates/serde/owners",
                        "owner_team": "/api/v1/crates/serde/owner_team",
                        "owner_user": "/api/v1/crates/serde/owner_user",
                        "reverse_dependencies": "/api/v1/crates/serde/reverse_dependencies",
                    },
                    "exact_match": True,
                },
                "versions": [
                    {
                        "id": 123456,
                        "crate": "serde",
                        "num": "1.0.152",
                        "dl_path": "/api/v1/crates/serde/1.0.152/download",
                        "readme_path": "/api/v1/crates/serde/1.0.152/readme",
                        "updated_at": "2023-01-15T10:00:00.000000+00:00",
                        "created_at": "2023-01-15T10:00:00.000000+00:00",
                        "downloads": 1000000,
                        "features": {},
                        "yanked": False,
                        "license": "MIT OR Apache-2.0",
                        "links": {
                            "dependencies": "/api/v1/crates/serde/1.0.152/dependencies",
                            "version_downloads": "/api/v1/crates/serde/1.0.152/downloads",
                            "authors": "/api/v1/crates/serde/1.0.152/authors",
                        },
                        "crate_size": 75000,
                        "published_by": None,
                        "audit_actions": [],
                    }
                ],
                "keywords": [],
                "categories": [],
            },
        )

        with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
            result = await get_crates_version("serde")
            assert result.version == "1.0.152"
            assert result.registry == "crates"
            assert "crates.io" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_crates_version_not_found(self):
        """Test crates.io package not found"""
        with pytest.raises(
            Exception, match="Package 'nonexistent-crate-12345' not found in crates.io registry"
        ):
            await get_crates_version("nonexistent-crate-12345")

    @pytest.mark.asyncio
    async def test_get_crates_version_empty_name(self):
        """Test crates.io with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_crates_version("")
