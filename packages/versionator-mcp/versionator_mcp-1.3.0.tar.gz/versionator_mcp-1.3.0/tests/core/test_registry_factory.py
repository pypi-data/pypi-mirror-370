"""
Tests for the registry factory and core functionality
"""

import pytest

from tests.utils import get_latest_version, set_request_timeout


class TestRegistryFactory:
    """Test the registry factory functionality"""

    @pytest.mark.asyncio
    async def test_get_latest_version_npm(self):
        """Test get_latest_version with npm registry"""
        result = await get_latest_version("npm", "react")
        assert result.version is not None
        assert result.registry == "npm"
        assert "npmjs.org" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_latest_version_aliases(self):
        """Test get_latest_version with registry aliases"""
        # Test npm alias
        result = await get_latest_version("node", "react")
        assert result.version is not None
        assert result.registry == "npm"

        # Test pypi alias
        result = await get_latest_version("python", "requests")
        assert result.version is not None
        assert result.registry == "pypi"

    @pytest.mark.asyncio
    async def test_get_latest_version_invalid_manager(self):
        """Test get_latest_version with invalid package manager"""
        with pytest.raises(ValueError, match="Unknown package manager 'invalid-registry'"):
            await get_latest_version("invalid-registry", "some-package")

    @pytest.mark.asyncio
    async def test_get_latest_version_empty_manager(self):
        """Test get_latest_version with empty package manager"""
        with pytest.raises(ValueError, match="Unknown package manager"):
            await get_latest_version("", "package")

    def test_set_request_timeout(self):
        """Test setting request timeout"""
        set_request_timeout(60)
        # Test passes if no exception is raised

    @pytest.mark.asyncio
    async def test_get_latest_version_new_registries(self):
        """Test get_latest_version with newer registries"""
        # Test crates.io
        result = await get_latest_version("crates", "serde")
        assert result.version is not None
        assert result.registry == "crates"

        # Test bioconda
        result = await get_latest_version("bioconda", "samtools")
        assert result.version is not None
        assert result.registry == "bioconda"

    @pytest.mark.asyncio
    async def test_get_latest_version_v12_registries(self):
        """Test get_latest_version with v1.2.0 registries"""
        # Test composer
        result = await get_latest_version("composer", "symfony/console")
        assert result.version is not None
        assert result.registry == "composer"

        # Test nuget
        result = await get_latest_version("nuget", "Newtonsoft.Json")
        assert result.version is not None
        assert result.registry == "nuget"
