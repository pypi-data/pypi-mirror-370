"""
Maven Central registry implementation
"""

from ..core import BaseRegistry, register_registry
from ..models import PackageVersion


class MavenRegistry(BaseRegistry):
    """Maven Central registry implementation"""

    @property
    def registry_name(self) -> str:
        return "maven"

    async def get_latest_version(self, artifact_name: str) -> PackageVersion:
        """Get the latest version of a Maven Central artifact"""
        artifact_name = self.validate_package_name(artifact_name)

        # Parse groupId:artifactId
        if ":" not in artifact_name:
            raise ValueError("Maven artifact name must be in 'groupId:artifactId' format")

        group_id, artifact_id = artifact_name.split(":", 1)

        url = f"https://search.maven.org/solrsearch/select?q=g:{group_id}+AND+a:{artifact_id}&rows=1&wt=json"

        data = await self.http_client.get_json(
            url, registry_name="Maven Central", package_name=artifact_name
        )
        docs = data.get("response", {}).get("docs", [])

        if not docs:
            raise Exception(f"Artifact '{artifact_name}' not found")

        doc = docs[0]
        latest_version = doc.get("latestVersion")

        if not latest_version:
            raise Exception(f"No version found for artifact '{artifact_name}'")

        return PackageVersion(
            name=artifact_name,
            version=latest_version,
            registry="maven",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=f"Maven artifact {artifact_name}",
            homepage=f"https://search.maven.org/artifact/{group_id}/{artifact_id}",
            license=None,
        )


# Register with aliases
register_registry(MavenRegistry, ["mvn"])
