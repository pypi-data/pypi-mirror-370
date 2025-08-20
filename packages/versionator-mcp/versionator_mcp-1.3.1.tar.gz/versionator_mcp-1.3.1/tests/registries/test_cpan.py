"""
Tests for CPAN registry functionality
"""

import pytest

from tests.conftest import skip_github_api
from tests.utils import get_cpan_version


class TestCPANRegistry:
    """Test CPAN registry functionality"""

    @pytest.mark.asyncio
    async def test_get_cpan_version_success(self):
        """Test successful CPAN package version retrieval"""
        result = await get_cpan_version("DBI")
        assert result.version is not None
        assert result.registry == "cpan"
        assert "metacpan.org" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_cpan_version_not_found(self):
        """Test CPAN package not found"""
        with pytest.raises(Exception, match="Package 'nonexistent' not found in CPAN registry"):
            await get_cpan_version("nonexistent")

    @pytest.mark.asyncio
    async def test_get_cpan_version_empty_name(self):
        """Test CPAN with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_cpan_version("")
