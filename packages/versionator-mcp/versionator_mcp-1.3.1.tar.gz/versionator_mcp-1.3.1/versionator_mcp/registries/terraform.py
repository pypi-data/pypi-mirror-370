"""
Terraform registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class TerraformRegistry(BaseRegistry):
    """Terraform provider registry implementation"""

    @property
    def registry_name(self) -> str:
        return "terraform"

    async def get_latest_version(self, provider_path: str) -> PackageVersion:
        """Get the latest version of a Terraform provider from registry.terraform.io"""
        provider_path = self.validate_package_name(provider_path)
        url = f"https://registry.terraform.io/v1/providers/{provider_path}"

        data = await self.http_client.get_json(
            url, registry_name="Terraform Registry", package_name=provider_path
        )

        return PackageVersion(
            name=provider_path,
            version=data.get("version", "unknown"),
            registry="terraform",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=data.get("description"),
            homepage=data.get("source"),
            license=None,  # License info not in this endpoint
        )


# Register with aliases
register_registry(TerraformRegistry, ["tf"])
