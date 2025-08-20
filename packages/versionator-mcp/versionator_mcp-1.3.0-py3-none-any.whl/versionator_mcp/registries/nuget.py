"""
NuGet registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class NuGetRegistry(BaseRegistry):
    """NuGet package registry implementation"""

    @property
    def registry_name(self) -> str:
        return "nuget"

    async def get_latest_version(self, package_name: str) -> PackageVersion:
        """Get the latest version of a .NET NuGet package"""
        package_name = self.validate_package_name(package_name)
        url = f"https://api.nuget.org/v3-flatcontainer/{package_name.lower()}/index.json"

        data = await self.http_client.get_json(
            url, registry_name="NuGet", package_name=package_name
        )
        versions = data.get("versions", [])

        if not versions:
            raise Exception(f"No versions found for package '{package_name}'")

        # Get the latest version (last in the list)
        latest_version = versions[-1]

        return PackageVersion(
            name=package_name,
            version=latest_version,
            registry="nuget",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=f".NET package {package_name}",
            homepage=f"https://www.nuget.org/packages/{package_name}",
            license=None,
        )


# Register with aliases
register_registry(NuGetRegistry, ["dotnet", ".net"])
