"""
Hex.pm registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class HexRegistry(BaseRegistry):
    """Hex.pm package registry implementation"""

    @property
    def registry_name(self) -> str:
        return "hex"

    async def get_latest_version(self, package_name: str) -> PackageVersion:
        """Get the latest version of an Elixir package from Hex.pm"""
        package_name = self.validate_package_name(package_name)
        url = f"https://hex.pm/api/packages/{package_name}"

        data = await self.http_client.get_json(
            url, registry_name="Hex.pm", package_name=package_name
        )

        # Get the latest version from releases array (first item is latest)
        releases = data.get("releases", [])
        if not releases:
            raise Exception(f"No releases found for package '{package_name}'")

        latest_version = releases[0].get("version", "unknown")
        meta = data.get("meta", {})

        return PackageVersion(
            name=package_name,
            version=latest_version,
            registry="hex",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=meta.get("description"),
            homepage=meta.get("links", {}).get("GitHub"),
            license=", ".join(meta.get("licenses", [])),
        )


# Register with aliases
register_registry(HexRegistry, ["elixir", "hex.pm"])
