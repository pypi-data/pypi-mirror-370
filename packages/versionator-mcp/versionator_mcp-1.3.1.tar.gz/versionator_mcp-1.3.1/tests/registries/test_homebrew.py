"""
Tests for Homebrew registry functionality
"""

import pytest

from tests.conftest import skip_github_api
from tests.utils import get_homebrew_version


class TestHomebrewRegistry:
    """Test Homebrew registry functionality"""

    @pytest.mark.asyncio
    async def test_get_homebrew_version_success(self):
        """Test successful Homebrew package version retrieval"""
        result = await get_homebrew_version("wget")
        assert result.version is not None
        assert result.registry == "homebrew"
        assert "formulae.brew.sh" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_homebrew_version_not_found(self):
        """Test Homebrew package not found"""
        with pytest.raises(Exception, match="Package 'nonexistent' not found in Homebrew registry"):
            await get_homebrew_version("nonexistent")

    @pytest.mark.asyncio
    async def test_get_homebrew_version_empty_name(self):
        """Test Homebrew with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_homebrew_version("")
