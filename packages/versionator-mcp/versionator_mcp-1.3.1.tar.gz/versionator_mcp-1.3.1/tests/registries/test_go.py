"""
Tests for Go registry functionality
"""

import pytest

from tests.conftest import skip_github_api
from tests.utils import get_go_version


class TestGoRegistry:
    """Test Go registry functionality"""

    @skip_github_api
    @pytest.mark.asyncio
    async def test_get_go_version_success(self):
        """Test successful Go package version retrieval"""
        result = await get_go_version("github.com/gin-gonic/gin")
        assert result.version is not None
        assert result.registry == "go"
        assert "pkg.go.dev" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_go_version_not_found(self):
        """Test Go package not found"""
        with pytest.raises(Exception, match="Module 'nonexistent' not found in Go module registry"):
            await get_go_version("nonexistent")

    @pytest.mark.asyncio
    async def test_get_go_version_empty_name(self):
        """Test Go with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_go_version("")
