"""
Composer (Packagist) registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class ComposerRegistry(BaseRegistry):
    """PHP Composer (Packagist) registry implementation"""

    @property
    def registry_name(self) -> str:
        return "composer"

    async def get_latest_version(self, package_name: str) -> PackageVersion:
        """Get the latest version of a PHP Composer package from Packagist"""
        package_name = self.validate_package_name(package_name)
        url = f"https://packagist.org/packages/{package_name}.json"

        data = await self.http_client.get_json(
            url, registry_name="Packagist", package_name=package_name
        )
        package_info = data.get("package", {})

        # Get the latest version from versions
        versions = package_info.get("versions", {})
        if not versions:
            raise Exception(f"No versions found for package '{package_name}'")

        # Find the latest stable version (not dev)
        stable_versions = [v for v in versions.keys() if not v.endswith("-dev")]
        if not stable_versions:
            # If no stable versions, use the first available
            latest_version = list(versions.keys())[0]
        else:
            # Sort versions and get the latest
            latest_version = sorted(stable_versions, reverse=True)[0]

        version_data = versions[latest_version]

        return PackageVersion(
            name=package_name,
            version=latest_version,
            registry="composer",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=version_data.get("description"),
            homepage=version_data.get("homepage"),
            license=(
                version_data.get("license", [None])[0] if version_data.get("license") else None
            ),
        )


# Register with aliases
register_registry(ComposerRegistry, ["php", "packagist"])
