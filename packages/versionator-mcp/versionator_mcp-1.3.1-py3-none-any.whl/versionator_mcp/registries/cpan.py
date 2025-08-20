"""
CPAN registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class CPANRegistry(BaseRegistry):
    """CPAN module registry implementation"""

    @property
    def registry_name(self) -> str:
        return "cpan"

    async def get_latest_version(self, module_name: str) -> PackageVersion:
        """Get the latest version of a Perl module from CPAN via MetaCPAN"""
        module_name = self.validate_package_name(module_name)
        url = f"https://fastapi.metacpan.org/v1/module/{module_name}"

        headers = {
            "Accept": "application/json",
            "User-Agent": "versionator-mcp/1.0 (Package Version Query Tool)",
        }

        data = await self.http_client.get_json(
            url, headers=headers, registry_name="CPAN", package_name=module_name
        )

        return PackageVersion(
            name=module_name,
            version=data.get("version", "unknown"),
            registry="cpan",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=data.get("abstract"),
            homepage=f"https://metacpan.org/pod/{module_name}",
            license=None,  # License info not readily available in this endpoint
        )


# Register with aliases
register_registry(CPANRegistry, ["perl"])
