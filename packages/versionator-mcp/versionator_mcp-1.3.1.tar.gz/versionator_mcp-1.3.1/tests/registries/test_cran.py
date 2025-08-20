"""
Tests for CRAN registry functionality
"""

import pytest

from tests.utils import get_cran_version


class TestCRANRegistry:
    """Test CRAN registry functionality"""

    @pytest.mark.asyncio
    async def test_get_cran_version_success(self):
        """Test successful CRAN package version retrieval"""
        result = await get_cran_version("ggplot2")
        assert result.version is not None
        assert result.registry == "cran"
        assert "crandb.r-pkg.org" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_cran_version_not_found(self):
        """Test CRAN package not found"""
        with pytest.raises(Exception, match="Package 'nonexistent-r-package' not found"):
            await get_cran_version("nonexistent-r-package")

    @pytest.mark.asyncio
    async def test_get_cran_version_empty_name(self):
        """Test CRAN with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_cran_version("")
