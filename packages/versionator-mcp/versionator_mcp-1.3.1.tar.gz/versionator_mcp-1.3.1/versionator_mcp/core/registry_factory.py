"""
Registry factory for creating and managing package registry instances
"""

from typing import Dict, Optional, Type

from .base_registry import BaseRegistry
from .http_client import HTTPClient


class RegistryFactory:
    """Factory for creating and managing registry instances"""

    def __init__(self) -> None:
        self._registries: Dict[str, Type[BaseRegistry]] = {}
        self._aliases: Dict[str, str] = {}
        self._http_client = HTTPClient()

    def register(
        self, registry_class: Type[BaseRegistry], aliases: Optional[list[str]] = None
    ) -> None:
        """
        Register a registry class with optional aliases.

        Args:
            registry_class: The registry class to register
            aliases: List of alias names for this registry
        """
        # Create instance to get registry name
        instance = registry_class(self._http_client)
        registry_name = instance.registry_name

        self._registries[registry_name] = registry_class

        # Register aliases
        if aliases:
            for alias in aliases:
                self._aliases[alias.lower()] = registry_name

    def get_registry(self, name: str) -> BaseRegistry:
        """
        Get a registry instance by name or alias.

        Args:
            name: Registry name or alias

        Returns:
            Registry instance

        Raises:
            ValueError: If registry not found
        """
        name = name.lower().strip()

        # Check if it's an alias first
        if name in self._aliases:
            registry_name = self._aliases[name]
        else:
            registry_name = name

        if registry_name not in self._registries:
            available = sorted(set(list(self._registries.keys()) + list(self._aliases.keys())))
            raise ValueError(
                f"Unknown package manager '{name}'. Valid options: {', '.join(available)}"
            )

        registry_class = self._registries[registry_name]
        return registry_class(self._http_client)

    def get_available_registries(self) -> list[str]:
        """Get list of all available registry names and aliases"""
        return sorted(set(list(self._registries.keys()) + list(self._aliases.keys())))


# Global factory instance
_factory = RegistryFactory()


def register_registry(
    registry_class: Type[BaseRegistry], aliases: Optional[list[str]] = None
) -> None:
    """Register a registry class with the global factory"""
    _factory.register(registry_class, aliases)


def get_registry(name: str) -> BaseRegistry:
    """Get a registry instance from the global factory"""
    return _factory.get_registry(name)


def get_available_registries() -> list[str]:
    """Get list of all available registry names and aliases"""
    return _factory.get_available_registries()
