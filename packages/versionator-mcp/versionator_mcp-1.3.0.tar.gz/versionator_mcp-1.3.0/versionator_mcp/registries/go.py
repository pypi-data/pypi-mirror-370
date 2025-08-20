"""
Go modules registry implementation
"""

import aiohttp

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class GoRegistry(BaseRegistry):
    """Go modules registry implementation"""

    @property
    def registry_name(self) -> str:
        return "go"

    async def get_latest_version(self, module_path: str) -> PackageVersion:
        """Get the latest version of a Go module"""
        module_path = self.validate_package_name(module_path)

        # Handle GitHub-hosted modules
        if module_path.startswith("github.com/"):
            parts = module_path.split("/")
            if len(parts) >= 3:
                owner = parts[1]
                repo = parts[2]

                # Use GitHub API to get latest release
                url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

                headers = {
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "versionator-mcp/1.0 (Package Version Query Tool)",
                }

                data = await self.http_client.get_json(
                    url, headers=headers, registry_name="GitHub", package_name=module_path
                )

                return PackageVersion(
                    name=module_path,
                    version=data.get("tag_name", "unknown"),
                    registry="go",
                    registry_url=url,
                    query_time=self.http_client.get_current_timestamp(),
                    description=data.get("body", f"Go module {module_path}"),
                    homepage=f"https://pkg.go.dev/{module_path}",
                    license=None,  # License info not available in releases endpoint
                )

        # For non-GitHub modules, try pkg.go.dev API
        url = f"https://pkg.go.dev/{module_path}"

        headers = {
            "Accept": "text/html",
            "User-Agent": "versionator-mcp/1.0 (Package Version Query Tool)",
        }

        timeout = aiohttp.ClientTimeout(total=self.http_client.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 404:
                    raise Exception(f"Module '{module_path}' not found in Go module registry")
                elif response.status != 200:
                    text = await response.text()
                    raise Exception(f"Go module API error {response.status}: {text}")

                # For now, return a basic response since we can't parse HTML easily
                # In a real implementation, you'd parse the HTML to extract version info
                return PackageVersion(
                    name=module_path,
                    version="latest",  # Placeholder - would need HTML parsing to get actual version
                    registry="go",
                    registry_url=url,
                    query_time=self.http_client.get_current_timestamp(),
                    description=f"Go module {module_path}",
                    homepage=url,
                    license=None,
                )


# Register with aliases
register_registry(GoRegistry, ["golang"])
