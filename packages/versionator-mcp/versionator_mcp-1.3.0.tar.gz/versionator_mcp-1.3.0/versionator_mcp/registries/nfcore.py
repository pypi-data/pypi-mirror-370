"""
nf-core modules and subworkflows registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class NFCoreModuleRegistry(BaseRegistry):
    """nf-core module registry implementation"""

    @property
    def registry_name(self) -> str:
        return "nf-core-module"

    async def get_latest_version(self, module_name: str) -> PackageVersion:
        """Get the latest version of an nf-core module from the nf-core/modules repository"""
        module_name = self.validate_package_name(module_name)
        module_path = f"modules/nf-core/{module_name}"

        # Check if module exists and get latest commit
        url = f"https://api.github.com/repos/nf-core/modules/commits?path={module_path}&per_page=1"

        data = await self.http_client.get_json(
            url, registry_name="GitHub", package_name=module_name
        )

        if not data or not isinstance(data, list):
            raise Exception(f"Module '{module_name}' not found in nf-core/modules")

        latest_commit = data[0]
        commit_sha = latest_commit["sha"][:7]  # Short SHA
        commit_message = latest_commit["commit"]["message"].split("\n")[0]  # First line only

        return PackageVersion(
            name=f"nf-core/{module_name}",
            version=commit_sha,
            registry="nf-core-module",
            registry_url=f"https://github.com/nf-core/modules/tree/master/{module_path}",
            query_time=self.http_client.get_current_timestamp(),
            description=f"nf-core module: {commit_message}",
            homepage=f"https://github.com/nf-core/modules/tree/master/{module_path}",
            license=None,
        )


class NFCoreSubworkflowRegistry(BaseRegistry):
    """nf-core subworkflow registry implementation"""

    @property
    def registry_name(self) -> str:
        return "nf-core-subworkflow"

    async def get_latest_version(self, subworkflow_name: str) -> PackageVersion:
        """Get the latest version of an nf-core subworkflow from the nf-core/modules repository"""
        subworkflow_name = self.validate_package_name(subworkflow_name)
        subworkflow_path = f"subworkflows/nf-core/{subworkflow_name}"

        # Check if subworkflow exists and get latest commit
        url = f"https://api.github.com/repos/nf-core/modules/commits?path={subworkflow_path}&per_page=1"

        data = await self.http_client.get_json(
            url, registry_name="GitHub", package_name=subworkflow_name
        )

        if not data or not isinstance(data, list):
            raise Exception(f"Subworkflow '{subworkflow_name}' not found in nf-core/modules")

        latest_commit = data[0]
        commit_sha = latest_commit["sha"][:7]  # Short SHA
        commit_message = latest_commit["commit"]["message"].split("\n")[0]  # First line only

        return PackageVersion(
            name=f"nf-core/{subworkflow_name}",
            version=commit_sha,
            registry="nf-core-subworkflow",
            registry_url=f"https://github.com/nf-core/modules/tree/master/{subworkflow_path}",
            query_time=self.http_client.get_current_timestamp(),
            description=f"nf-core subworkflow: {commit_message}",
            homepage=f"https://github.com/nf-core/modules/tree/master/{subworkflow_path}",
            license=None,
        )


# Register both registries with their aliases
register_registry(NFCoreModuleRegistry, ["nfcore-module", "nf-module"])
register_registry(NFCoreSubworkflowRegistry, ["nfcore-subworkflow", "nf-subworkflow"])
