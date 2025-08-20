"""
Data models for Versionator MCP Server

Defines Pydantic models for package version information.
"""

from typing import Optional

from pydantic import BaseModel, Field


class PackageVersion(BaseModel):
    """Represents a package version from a registry"""

    name: str = Field(description="The package name")
    version: str = Field(description="The latest version string")
    registry: str = Field(description="The package registry (npm, rubygems, pypi, hex)")
    registry_url: str = Field(description="The full URL used to query the registry")
    query_time: str = Field(description="ISO timestamp when the version was queried")

    # Optional fields that some registries provide
    description: Optional[str] = Field(None, description="Package description if available")
    homepage: Optional[str] = Field(None, description="Package homepage URL if available")
    license: Optional[str] = Field(None, description="Package license if available")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "react",
                "version": "18.2.0",
                "registry": "npm",
                "registry_url": "https://registry.npmjs.org/react/latest",
                "query_time": "2024-01-15T10:30:00Z",
                "description": "React is a JavaScript library for building user interfaces.",
                "homepage": "https://react.dev/",
                "license": "MIT",
            }
        }
    }
