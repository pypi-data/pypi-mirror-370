"""
CRAN registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class CRANRegistry(BaseRegistry):
    """CRAN package registry implementation"""

    @property
    def registry_name(self) -> str:
        return "cran"

    async def get_latest_version(self, package_name: str) -> PackageVersion:
        """Get the latest version of an R package from CRAN via crandb"""
        package_name = self.validate_package_name(package_name)
        url = f"https://crandb.r-pkg.org/{package_name}"

        data = await self.http_client.get_json(url, registry_name="CRAN", package_name=package_name)

        return PackageVersion(
            name=package_name,
            version=data.get("Version", "unknown"),
            registry="cran",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=data.get("Description"),
            homepage=data.get("URL"),
            license=data.get("License"),
        )


# Register with aliases
register_registry(CRANRegistry, ["r"])
