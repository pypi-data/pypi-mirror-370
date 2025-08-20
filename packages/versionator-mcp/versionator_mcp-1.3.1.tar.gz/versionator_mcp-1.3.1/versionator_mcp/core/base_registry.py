"""
Abstract base class for package registry implementations
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from ..models import PackageVersion

if TYPE_CHECKING:
    from .http_client import HTTPClient


class BaseRegistry(ABC):
    """Abstract base class for all package registry implementations"""

    def __init__(self, http_client: Optional["HTTPClient"] = None):
        """Initialize registry with optional HTTP client"""
        if http_client is None:
            from .http_client import HTTPClient

            http_client = HTTPClient()
        self.http_client = http_client

    @property
    @abstractmethod
    def registry_name(self) -> str:
        """Return the name of this registry (e.g., 'npm', 'pypi')"""
        pass

    @abstractmethod
    async def get_latest_version(self, package_name: str) -> PackageVersion:
        """
        Get the latest version of a package from this registry.

        Args:
            package_name: The package name to query

        Returns:
            PackageVersion with the latest version information

        Raises:
            ValueError: If package name is invalid
            Exception: If API call fails
        """
        pass

    def validate_package_name(self, package_name: str) -> str:
        """
        Validate and normalize package name.

        Args:
            package_name: The package name to validate

        Returns:
            Normalized package name

        Raises:
            ValueError: If package name is invalid
        """
        if not package_name or not package_name.strip():
            raise ValueError("Package name cannot be empty")
        return package_name.strip()
