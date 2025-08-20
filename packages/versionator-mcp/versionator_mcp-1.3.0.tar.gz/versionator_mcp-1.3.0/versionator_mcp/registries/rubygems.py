"""
RubyGems registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class RubyGemsRegistry(BaseRegistry):
    """RubyGems package registry implementation"""

    @property
    def registry_name(self) -> str:
        return "rubygems"

    async def get_latest_version(self, gem_name: str) -> PackageVersion:
        """Get the latest version of a Ruby gem"""
        gem_name = self.validate_package_name(gem_name)
        url = f"https://rubygems.org/api/v1/versions/{gem_name}/latest.json"

        data = await self.http_client.get_json(url, registry_name="RubyGems", package_name=gem_name)

        return PackageVersion(
            name=gem_name,
            version=data.get("version", "unknown"),
            registry="rubygems",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=None,
            homepage=None,
            license=None,
        )


# Register with aliases
register_registry(RubyGemsRegistry, ["gem", "ruby"])
