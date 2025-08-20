"""
Swift Package Manager registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class SwiftRegistry(BaseRegistry):
    """Swift Package Manager registry implementation"""

    @property
    def registry_name(self) -> str:
        return "swift"

    async def get_latest_version(self, package_name: str) -> PackageVersion:
        """Get the latest version of a Swift package (via GitHub releases)"""
        package_name = self.validate_package_name(package_name)

        # Ensure it's in owner/repo format
        if "/" not in package_name:
            raise ValueError("Swift package name must be in 'owner/repo' format")

        url = f"https://api.github.com/repos/{package_name}/releases/latest"

        data = await self.http_client.get_json(
            url, registry_name="GitHub", package_name=package_name
        )
        tag_name = data.get("tag_name")

        if not tag_name:
            raise Exception(f"No release found for package '{package_name}'")

        return PackageVersion(
            name=package_name,
            version=tag_name,
            registry="swift",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=data.get("body", f"Swift package {package_name}"),
            homepage=f"https://github.com/{package_name}",
            license=None,
        )


# Register with aliases
register_registry(SwiftRegistry, ["spm"])
