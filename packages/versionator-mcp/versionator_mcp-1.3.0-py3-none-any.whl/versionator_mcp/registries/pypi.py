"""
PyPI registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class PyPIRegistry(BaseRegistry):
    """PyPI package registry implementation"""

    @property
    def registry_name(self) -> str:
        return "pypi"

    async def get_latest_version(self, package_name: str) -> PackageVersion:
        """Get the latest version of a Python package from PyPI"""
        package_name = self.validate_package_name(package_name)
        url = f"https://pypi.org/pypi/{package_name}/json"

        data = await self.http_client.get_json(url, registry_name="PyPI", package_name=package_name)
        info = data.get("info", {})

        return PackageVersion(
            name=package_name,
            version=info.get("version", "unknown"),
            registry="pypi",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=info.get("summary"),
            homepage=info.get("home_page") or info.get("project_url"),
            license=info.get("license"),
        )


# Register with aliases
register_registry(PyPIRegistry, ["pip", "python"])
