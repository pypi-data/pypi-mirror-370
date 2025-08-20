"""
Tests for Maven registry functionality
"""

import pytest

from tests.conftest import skip_github_api
from tests.utils import get_maven_version


class TestMavenRegistry:
    """Test Maven registry functionality"""

    @pytest.mark.asyncio
    async def test_get_maven_version_success(self):
        """Test successful Maven package version retrieval"""
        result = await get_maven_version("org.springframework:spring-core")
        assert result.version is not None
        assert result.registry == "maven"
        assert "search.maven.org" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_maven_version_not_found(self):
        """Test Maven package not found"""
        with pytest.raises(
            ValueError, match="Maven artifact name must be in 'groupId:artifactId' format"
        ):
            await get_maven_version("nonexistent")

    @pytest.mark.asyncio
    async def test_get_maven_version_empty_name(self):
        """Test Maven with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_maven_version("")
