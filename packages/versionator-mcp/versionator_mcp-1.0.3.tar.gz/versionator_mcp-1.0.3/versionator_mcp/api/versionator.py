"""
Package registry API functions for Versionator MCP Server

Provides functions to query npm, RubyGems, PyPI, and Hex.pm for latest package versions.
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import aiohttp
from fastmcp import FastMCP

from ..models import PackageVersion

# Module-level configuration
_request_timeout: int = 30


def set_request_timeout(timeout: int) -> None:
    """Set the request timeout for API calls"""
    global _request_timeout
    _request_timeout = timeout


async def get_npm_version(package_name: str) -> PackageVersion:
    """
    Get the latest version of an npm package.

    Args:
        package_name: The npm package name

    Returns:
        PackageVersion with the latest version information

    Raises:
        ValueError: If package name is invalid
        Exception: If API call fails
    """
    if not package_name or not package_name.strip():
        raise ValueError("Package name cannot be empty")

    package_name = package_name.strip()
    url = f"https://registry.npmjs.org/{package_name}/latest"

    timeout = aiohttp.ClientTimeout(total=_request_timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers={"Accept": "application/json"}) as response:
            if response.status == 404:
                raise Exception(f"Package '{package_name}' not found in npm registry")
            elif response.status != 200:
                text = await response.text()
                raise Exception(f"npm API error {response.status}: {text}")

            data = await response.json()

            return PackageVersion(
                name=package_name,
                version=data.get("version", "unknown"),
                registry="npm",
                registry_url=url,
                query_time=datetime.now(timezone.utc).isoformat() + "Z",
                description=data.get("description"),
                homepage=data.get("homepage"),
                license=data.get("license"),
            )


async def get_rubygems_version(gem_name: str) -> PackageVersion:
    """
    Get the latest version of a Ruby gem.

    Args:
        gem_name: The RubyGems package name

    Returns:
        PackageVersion with the latest version information

    Raises:
        ValueError: If gem name is invalid
        Exception: If API call fails
    """
    if not gem_name or not gem_name.strip():
        raise ValueError("Gem name cannot be empty")

    gem_name = gem_name.strip()
    url = f"https://rubygems.org/api/v1/versions/{gem_name}/latest.json"

    timeout = aiohttp.ClientTimeout(total=_request_timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            if response.status == 404:
                raise Exception(f"Gem '{gem_name}' not found in RubyGems registry")
            elif response.status != 200:
                text = await response.text()
                raise Exception(f"RubyGems API error {response.status}: {text}")

            data = await response.json()

            return PackageVersion(
                name=gem_name,
                version=data.get("version", "unknown"),
                registry="rubygems",
                registry_url=url,
                query_time=datetime.now(timezone.utc).isoformat() + "Z",
                description=None,
                homepage=None,
                license=None,
            )


async def get_pypi_version(package_name: str) -> PackageVersion:
    """
    Get the latest version of a Python package from PyPI.

    Args:
        package_name: The PyPI package name

    Returns:
        PackageVersion with the latest version information

    Raises:
        ValueError: If package name is invalid
        Exception: If API call fails
    """
    if not package_name or not package_name.strip():
        raise ValueError("Package name cannot be empty")

    package_name = package_name.strip()
    url = f"https://pypi.org/pypi/{package_name}/json"

    timeout = aiohttp.ClientTimeout(total=_request_timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers={"Accept": "application/json"}) as response:
            if response.status == 404:
                raise Exception(f"Package '{package_name}' not found in PyPI registry")
            elif response.status != 200:
                text = await response.text()
                raise Exception(f"PyPI API error {response.status}: {text}")

            data = await response.json()
            info = data.get("info", {})

            return PackageVersion(
                name=package_name,
                version=info.get("version", "unknown"),
                registry="pypi",
                registry_url=url,
                query_time=datetime.now(timezone.utc).isoformat() + "Z",
                description=info.get("summary"),
                homepage=info.get("home_page") or info.get("project_url"),
                license=info.get("license"),
            )


async def get_hex_version(package_name: str) -> PackageVersion:
    """
    Get the latest version of an Elixir package from Hex.pm.

    Args:
        package_name: The Hex package name

    Returns:
        PackageVersion with the latest version information

    Raises:
        ValueError: If package name is invalid
        Exception: If API call fails
    """
    if not package_name or not package_name.strip():
        raise ValueError("Package name cannot be empty")

    package_name = package_name.strip()
    url = f"https://hex.pm/api/packages/{package_name}"

    timeout = aiohttp.ClientTimeout(total=_request_timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            if response.status == 404:
                raise Exception(f"Package '{package_name}' not found in Hex.pm registry")
            elif response.status != 200:
                text = await response.text()
                raise Exception(f"Hex.pm API error {response.status}: {text}")

            data = await response.json()

            # Get the latest version from releases array (first item is latest)
            releases = data.get("releases", [])
            if not releases:
                raise Exception(f"No releases found for package '{package_name}'")

            latest_version = releases[0].get("version", "unknown")
            meta = data.get("meta", {})

            return PackageVersion(
                name=package_name,
                version=latest_version,
                registry="hex",
                registry_url=url,
                query_time=datetime.now(timezone.utc).isoformat() + "Z",
                description=meta.get("description"),
                homepage=meta.get("links", {}).get("GitHub"),
                license=", ".join(meta.get("licenses", [])),
            )


async def get_latest_version(package_manager: str, package_name: str) -> PackageVersion:
    """
    Get the latest version of a package from the specified package manager.

    Args:
        package_manager: The package manager/registry (npm, rubygems, pypi, hex)
        package_name: The package name

    Returns:
        PackageVersion with the latest version information

    Raises:
        ValueError: If package manager or package name is invalid
        Exception: If API call fails
    """
    if not package_manager or not package_manager.strip():
        raise ValueError("Package manager cannot be empty")

    package_manager = package_manager.strip().lower()

    # Map common aliases
    registry_map = {
        "npm": get_npm_version,
        "node": get_npm_version,
        "nodejs": get_npm_version,
        "rubygems": get_rubygems_version,
        "gem": get_rubygems_version,
        "ruby": get_rubygems_version,
        "pypi": get_pypi_version,
        "pip": get_pypi_version,
        "python": get_pypi_version,
        "hex": get_hex_version,
        "elixir": get_hex_version,
        "hex.pm": get_hex_version,
    }

    if package_manager not in registry_map:
        valid_options = ", ".join(sorted(set(registry_map.keys())))
        raise ValueError(
            f"Unknown package manager '{package_manager}'. Valid options: {valid_options}"
        )

    return await registry_map[package_manager](package_name)


def register_versionator_api(app: FastMCP) -> None:
    """Register versionator API functions with the MCP app"""

    @app.tool()
    async def get_package_version(package_manager: str, package_name: str) -> Dict[str, Any]:
        """Get the latest version of a package from the specified registry.

        Args:
            package_manager: The package manager/registry (npm, rubygems, pypi, hex)
                           Also accepts aliases: node, ruby, python, elixir
            package_name: The name of the package to query

        Returns:
            Dictionary containing package version information

        Examples:
            - get_package_version("npm", "react")
            - get_package_version("python", "django")
            - get_package_version("ruby", "rails")
            - get_package_version("elixir", "ecto")
        """
        version_info = await get_latest_version(package_manager, package_name)
        return version_info.model_dump()

    @app.tool()
    async def get_npm_package(package_name: str) -> Dict[str, Any]:
        """Get the latest version of an npm package.

        Args:
            package_name: The npm package name

        Returns:
            Dictionary containing package version information
        """
        version_info = await get_npm_version(package_name)
        return version_info.model_dump()

    @app.tool()
    async def get_ruby_gem(gem_name: str) -> Dict[str, Any]:
        """Get the latest version of a Ruby gem.

        Args:
            gem_name: The RubyGems package name

        Returns:
            Dictionary containing gem version information
        """
        version_info = await get_rubygems_version(gem_name)
        return version_info.model_dump()

    @app.tool()
    async def get_python_package(package_name: str) -> Dict[str, Any]:
        """Get the latest version of a Python package from PyPI.

        Args:
            package_name: The PyPI package name

        Returns:
            Dictionary containing package version information
        """
        version_info = await get_pypi_version(package_name)
        return version_info.model_dump()

    @app.tool()
    async def get_elixir_package(package_name: str) -> Dict[str, Any]:
        """Get the latest version of an Elixir package from Hex.pm.

        Args:
            package_name: The Hex package name

        Returns:
            Dictionary containing package version information
        """
        version_info = await get_hex_version(package_name)
        return version_info.model_dump()
