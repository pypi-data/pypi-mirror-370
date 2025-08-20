"""
Tests for Swift registry functionality
"""

import pytest

from tests.conftest import skip_github_api
from tests.utils import get_swift_version


class TestSwiftRegistry:
    """Test Swift registry functionality"""

    @skip_github_api
    @pytest.mark.asyncio
    async def test_get_swift_version_success(self):
        """Test successful Swift package version retrieval"""
        result = await get_swift_version("Alamofire/Alamofire")
        assert result.version is not None
        assert result.registry == "swift"
        assert "github.com" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_swift_version_not_found(self):
        """Test Swift package not found"""
        with pytest.raises(ValueError, match="Swift package name must be in 'owner/repo' format"):
            await get_swift_version("nonexistent")

    @pytest.mark.asyncio
    async def test_get_swift_version_empty_name(self):
        """Test Swift with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_swift_version("")
