"""
Tests for nf-core registry functionality
"""

import pytest

from tests.conftest import skip_github_api
from tests.utils import get_nfcore_version


class TestnfcoreRegistry:
    """Test nf-core registry functionality"""

    @skip_github_api
    @pytest.mark.asyncio
    async def test_get_nfcore_version_success(self):
        """Test successful nf-core package version retrieval"""
        result = await get_nfcore_version("fastqc")
        assert result.version is not None
        assert result.registry == "nf-core-module"
        assert "github.com" in result.registry_url

    @skip_github_api
    @pytest.mark.asyncio
    async def test_get_nfcore_version_not_found(self):
        """Test nf-core package not found"""
        with pytest.raises(Exception, match="Module 'nonexistent' not found"):
            await get_nfcore_version("nonexistent")

    @pytest.mark.asyncio
    async def test_get_nfcore_version_empty_name(self):
        """Test nf-core with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_nfcore_version("")
