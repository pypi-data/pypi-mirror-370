"""
Tests for DockerHub registry functionality
"""

import pytest

from tests.conftest import skip_github_api
from tests.utils import get_dockerhub_version


class TestDockerHubRegistry:
    """Test DockerHub registry functionality"""

    @pytest.mark.asyncio
    async def test_get_dockerhub_version_success(self):
        """Test successful DockerHub package version retrieval"""
        result = await get_dockerhub_version("nginx")
        assert result.version is not None
        assert result.registry == "dockerhub"
        assert "hub.docker.com" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_dockerhub_version_not_found(self):
        """Test DockerHub package not found"""
        with pytest.raises(
            Exception, match="Package 'nonexistent' not found in DockerHub registry"
        ):
            await get_dockerhub_version("nonexistent")

    @pytest.mark.asyncio
    async def test_get_dockerhub_version_empty_name(self):
        """Test DockerHub with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_dockerhub_version("")
