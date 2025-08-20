"""
Homebrew registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class HomebrewRegistry(BaseRegistry):
    """Homebrew formula registry implementation"""

    @property
    def registry_name(self) -> str:
        return "homebrew"

    async def get_latest_version(self, formula_name: str) -> PackageVersion:
        """Get the latest version of a Homebrew formula"""
        formula_name = self.validate_package_name(formula_name)
        url = f"https://formulae.brew.sh/api/formula/{formula_name}.json"

        data = await self.http_client.get_json(
            url, registry_name="Homebrew", package_name=formula_name
        )
        versions = data.get("versions", {})
        stable_version = versions.get("stable")

        if not stable_version:
            raise Exception(f"No stable version found for formula '{formula_name}'")

        return PackageVersion(
            name=formula_name,
            version=stable_version,
            registry="homebrew",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=data.get("desc"),
            homepage=data.get("homepage"),
            license=data.get("license"),
        )


# Register with aliases
register_registry(HomebrewRegistry, ["brew"])
