"""
Crates.io registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class CratesRegistry(BaseRegistry):
    """Crates.io package registry implementation"""

    @property
    def registry_name(self) -> str:
        return "crates"

    async def get_latest_version(self, crate_name: str) -> PackageVersion:
        """Get the latest version of a Rust crate from crates.io"""
        crate_name = self.validate_package_name(crate_name)
        url = f"https://crates.io/api/v1/crates/{crate_name}"

        data = await self.http_client.get_json(
            url, registry_name="crates.io", package_name=crate_name
        )
        crate_info = data.get("crate", {})

        return PackageVersion(
            name=crate_name,
            version=crate_info.get("newest_version", "unknown"),
            registry="crates",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=crate_info.get("description"),
            homepage=crate_info.get("homepage"),
            license=None,  # License info not in this endpoint
        )


# Register with aliases
register_registry(CratesRegistry, ["cargo", "rust"])
