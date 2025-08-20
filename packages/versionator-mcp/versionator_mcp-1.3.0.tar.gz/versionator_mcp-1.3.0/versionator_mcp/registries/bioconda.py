"""
Bioconda registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class BiocondaRegistry(BaseRegistry):
    """Bioconda package registry implementation"""

    @property
    def registry_name(self) -> str:
        return "bioconda"

    async def get_latest_version(self, package_name: str) -> PackageVersion:
        """Get the latest version of a Bioconda package from anaconda.org"""
        package_name = self.validate_package_name(package_name)
        url = f"https://api.anaconda.org/package/bioconda/{package_name}"

        data = await self.http_client.get_json(
            url, registry_name="Bioconda", package_name=package_name
        )

        return PackageVersion(
            name=package_name,
            version=data.get("latest_version", "unknown"),
            registry="bioconda",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=data.get("summary"),
            homepage=data.get("home"),
            license=data.get("license"),
        )


# Register with aliases
register_registry(BiocondaRegistry, ["conda"])
