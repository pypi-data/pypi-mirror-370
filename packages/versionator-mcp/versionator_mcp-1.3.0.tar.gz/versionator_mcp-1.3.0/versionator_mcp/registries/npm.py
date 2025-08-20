"""
NPM registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class NPMRegistry(BaseRegistry):
    """NPM package registry implementation"""

    @property
    def registry_name(self) -> str:
        return "npm"

    async def get_latest_version(self, package_name: str) -> PackageVersion:
        """Get the latest version of an npm package"""
        package_name = self.validate_package_name(package_name)
        url = f"https://registry.npmjs.org/{package_name}/latest"

        data = await self.http_client.get_json(url, registry_name="npm", package_name=package_name)

        return PackageVersion(
            name=package_name,
            version=data.get("version", "unknown"),
            registry="npm",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=data.get("description"),
            homepage=data.get("homepage"),
            license=data.get("license"),
        )


# Register with aliases
register_registry(NPMRegistry, ["node", "nodejs"])
