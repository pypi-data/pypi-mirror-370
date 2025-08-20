"""
Tests for Nextflow registry functionality
"""

import pytest

from tests.conftest import skip_github_api
from tests.utils import get_nextflow_version


class TestNextflowRegistry:
    """Test Nextflow registry functionality"""

    @skip_github_api
    @pytest.mark.asyncio
    async def test_get_nextflow_version_success(self):
        """Test successful Nextflow package version retrieval"""
        result = await get_nextflow_version("nf-core/rnaseq")
        assert result.version is not None
        assert result.registry == "nextflow"
        assert "github.com" in result.registry_url

    @skip_github_api
    @pytest.mark.asyncio
    async def test_get_nextflow_version_not_found(self):
        """Test Nextflow package not found"""
        with pytest.raises(Exception, match="Package 'nonexistent' not found in GitHub registry"):
            await get_nextflow_version("nonexistent")

    @pytest.mark.asyncio
    async def test_get_nextflow_version_empty_name(self):
        """Test Nextflow with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_nextflow_version("")
