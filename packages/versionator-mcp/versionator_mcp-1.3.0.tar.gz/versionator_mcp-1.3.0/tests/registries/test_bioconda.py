"""
Tests for Bioconda registry functionality
"""

import pytest

from tests.utils import get_bioconda_version


class TestBiocondaRegistry:
    """Test Bioconda registry functionality"""

    @pytest.mark.asyncio
    async def test_get_bioconda_version_success(self):
        """Test successful Bioconda package version retrieval"""
        result = await get_bioconda_version("samtools")
        assert result.version is not None
        assert result.registry == "bioconda"
        assert "anaconda.org" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_bioconda_version_not_found(self):
        """Test Bioconda package not found"""
        with pytest.raises(Exception, match="Package 'nonexistent-bio-package' not found"):
            await get_bioconda_version("nonexistent-bio-package")

    @pytest.mark.asyncio
    async def test_get_bioconda_version_empty_name(self):
        """Test Bioconda with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_bioconda_version("")
