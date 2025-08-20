"""
Nextflow registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class NextflowRegistry(BaseRegistry):
    """Nextflow pipeline registry implementation"""

    @property
    def registry_name(self) -> str:
        return "nextflow"

    async def get_latest_version(self, pipeline_name: str) -> PackageVersion:
        """Get the latest version of a Nextflow pipeline from nf-core (via GitHub)"""
        pipeline_name = self.validate_package_name(pipeline_name)

        # Convert nf-core/pipeline to GitHub repo format
        if pipeline_name.startswith("nf-core/"):
            repo_path = pipeline_name  # nf-core/rnaseq
        else:
            repo_path = f"nf-core/{pipeline_name}"

        url = f"https://api.github.com/repos/{repo_path}/releases/latest"

        data = await self.http_client.get_json(
            url, registry_name="GitHub", package_name=pipeline_name
        )
        tag_name = data.get("tag_name")

        if not tag_name:
            raise Exception(f"No release found for pipeline '{pipeline_name}'")

        return PackageVersion(
            name=pipeline_name,
            version=tag_name,
            registry="nextflow",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=data.get("body", f"Nextflow pipeline {pipeline_name}"),
            homepage=f"https://github.com/{repo_path}",
            license=None,
        )


# Register with aliases
register_registry(NextflowRegistry, ["nf-core"])
