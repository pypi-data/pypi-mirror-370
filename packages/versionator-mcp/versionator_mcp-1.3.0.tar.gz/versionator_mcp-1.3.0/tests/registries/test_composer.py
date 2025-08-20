"""
Tests for Composer registry functionality
"""

import pytest

from tests.conftest import skip_github_api
from tests.utils import get_composer_version


class TestComposerRegistry:
    """Test Composer registry functionality"""

    @pytest.mark.asyncio
    async def test_get_composer_version_success(self):
        """Test successful Composer package version retrieval"""
        result = await get_composer_version("symfony/console")
        assert result.version is not None
        assert result.registry == "composer"
        assert "packagist.org" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_composer_version_not_found(self):
        """Test Composer package not found"""
        with pytest.raises(Exception):
            await get_composer_version("nonexistent")

    @pytest.mark.asyncio
    async def test_get_composer_version_empty_name(self):
        """Test Composer with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_composer_version("")
