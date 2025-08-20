"""
Tests for Terraform Registry functionality
"""

import pytest

from tests.utils import get_terraform_version


class TestTerraformRegistry:
    """Test Terraform Registry functionality"""

    @pytest.mark.asyncio
    async def test_get_terraform_version_success(self):
        """Test successful Terraform Registry provider version retrieval"""
        result = await get_terraform_version("hashicorp/aws")
        assert result.version is not None
        assert result.registry == "terraform"
        assert "registry.terraform.io" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_terraform_version_not_found(self):
        """Test Terraform Registry provider not found"""
        with pytest.raises(
            Exception,
            match="Package 'nonexistent/provider' not found in Terraform Registry registry",
        ):
            await get_terraform_version("nonexistent/provider")

    @pytest.mark.asyncio
    async def test_get_terraform_version_empty_name(self):
        """Test Terraform Registry with empty provider name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_terraform_version("")
