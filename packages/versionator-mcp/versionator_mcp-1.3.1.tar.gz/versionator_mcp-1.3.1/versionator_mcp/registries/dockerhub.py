"""
DockerHub registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class DockerHubRegistry(BaseRegistry):
    """DockerHub image registry implementation"""

    @property
    def registry_name(self) -> str:
        return "dockerhub"

    async def get_latest_version(self, image_name: str) -> PackageVersion:
        """Get the latest version of a Docker image from DockerHub"""
        image_name = self.validate_package_name(image_name)

        # Handle official images (add library/ prefix if not present and no namespace)
        if "/" not in image_name:
            namespace = "library"
            repo_name = image_name
        else:
            namespace, repo_name = image_name.split("/", 1)

        url = f"https://hub.docker.com/v2/repositories/{namespace}/{repo_name}/tags"

        data = await self.http_client.get_json(
            url, registry_name="DockerHub", package_name=image_name
        )
        results = data.get("results", [])

        if not results:
            raise Exception(f"No tags found for image '{image_name}'")

        # Get the first tag (latest by default from DockerHub API)
        latest_tag = results[0]

        return PackageVersion(
            name=image_name,
            version=latest_tag.get("name", "unknown"),
            registry="dockerhub",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=f"Docker image {image_name}",
            homepage=(
                f"https://hub.docker.com/r/{namespace}/{repo_name}"
                if namespace != "library"
                else f"https://hub.docker.com/_/{repo_name}"
            ),
            license=None,  # License info not available in tags endpoint
        )


# Register with aliases
register_registry(DockerHubRegistry, ["docker"])
