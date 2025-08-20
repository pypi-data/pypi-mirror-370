"""
Tests for NuGet registry functionality
"""

import pytest

from tests.conftest import skip_github_api
from tests.utils import get_nuget_version


class TestNuGetRegistry:
    """Test NuGet registry functionality"""

    @pytest.mark.asyncio
    async def test_get_nuget_version_success(self):
        """Test successful NuGet package version retrieval"""
        result = await get_nuget_version("Newtonsoft.Json")
        assert result.version is not None
        assert result.registry == "nuget"
        assert "nuget.org" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_nuget_version_not_found(self):
        """Test NuGet package not found"""
        with pytest.raises(Exception, match="Package 'nonexistent' not found in NuGet registry"):
            await get_nuget_version("nonexistent")

    @pytest.mark.asyncio
    async def test_get_nuget_version_empty_name(self):
        """Test NuGet with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_nuget_version("")
