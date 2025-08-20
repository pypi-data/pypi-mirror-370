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


async def get_crates_version(crate_name: str) -> PackageVersion:
    """
    Get the latest version of a Rust crate from crates.io.

    Args:
        crate_name: The crate name

    Returns:
        PackageVersion with the latest version information

    Raises:
        ValueError: If crate name is invalid
        Exception: If API call fails
    """
    if not crate_name or not crate_name.strip():
        raise ValueError("Crate name cannot be empty")

    crate_name = crate_name.strip()
    url = f"https://crates.io/api/v1/crates/{crate_name}"

    timeout = aiohttp.ClientTimeout(total=_request_timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers={"Accept": "application/json"}) as response:
            if response.status == 404:
                raise Exception(f"Crate '{crate_name}' not found in crates.io registry")
            elif response.status != 200:
                text = await response.text()
                raise Exception(f"crates.io API error {response.status}: {text}")

            data = await response.json()
            crate_info = data.get("crate", {})

            return PackageVersion(
                name=crate_name,
                version=crate_info.get("newest_version", "unknown"),
                registry="crates",
                registry_url=url,
                query_time=datetime.now(timezone.utc).isoformat() + "Z",
                description=crate_info.get("description"),
                homepage=crate_info.get("homepage"),
                license=None,  # License info not in this endpoint
            )


async def get_bioconda_version(package_name: str) -> PackageVersion:
    """
    Get the latest version of a Bioconda package from anaconda.org.

    Args:
        package_name: The Bioconda package name

    Returns:
        PackageVersion with the latest version information

    Raises:
        ValueError: If package name is invalid
        Exception: If API call fails
    """
    if not package_name or not package_name.strip():
        raise ValueError("Package name cannot be empty")

    package_name = package_name.strip()
    url = f"https://api.anaconda.org/package/bioconda/{package_name}"

    timeout = aiohttp.ClientTimeout(total=_request_timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers={"Accept": "application/json"}) as response:
            if response.status == 404:
                raise Exception(f"Package '{package_name}' not found in Bioconda registry")
            elif response.status != 200:
                text = await response.text()
                raise Exception(f"Bioconda API error {response.status}: {text}")

            data = await response.json()

            return PackageVersion(
                name=package_name,
                version=data.get("latest_version", "unknown"),
                registry="bioconda",
                registry_url=url,
                query_time=datetime.now(timezone.utc).isoformat() + "Z",
                description=data.get("summary"),
                homepage=data.get("home"),
                license=data.get("license"),
            )


async def get_cran_version(package_name: str) -> PackageVersion:
    """
    Get the latest version of an R package from CRAN via crandb.

    Args:
        package_name: The CRAN package name

    Returns:
        PackageVersion with the latest version information

    Raises:
        ValueError: If package name is invalid
        Exception: If API call fails
    """
    if not package_name or not package_name.strip():
        raise ValueError("Package name cannot be empty")

    package_name = package_name.strip()
    url = f"https://crandb.r-pkg.org/{package_name}"

    timeout = aiohttp.ClientTimeout(total=_request_timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers={"Accept": "application/json"}) as response:
            if response.status == 404:
                raise Exception(f"Package '{package_name}' not found in CRAN registry")
            elif response.status != 200:
                text = await response.text()
                raise Exception(f"CRAN API error {response.status}: {text}")

            data = await response.json()

            return PackageVersion(
                name=package_name,
                version=data.get("Version", "unknown"),
                registry="cran",
                registry_url=url,
                query_time=datetime.now(timezone.utc).isoformat() + "Z",
                description=data.get("Description"),
                homepage=data.get("URL"),
                license=data.get("License"),
            )


async def get_terraform_version(provider_path: str) -> PackageVersion:
    """
    Get the latest version of a Terraform provider from registry.terraform.io.

    Args:
        provider_path: The provider path (e.g., "hashicorp/aws")

    Returns:
        PackageVersion with the latest version information

    Raises:
        ValueError: If provider path is invalid
        Exception: If API call fails
    """
    if not provider_path or not provider_path.strip():
        raise ValueError("Provider name cannot be empty")

    provider_path = provider_path.strip()
    url = f"https://registry.terraform.io/v1/providers/{provider_path}"

    timeout = aiohttp.ClientTimeout(total=_request_timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers={"Accept": "application/json"}) as response:
            if response.status == 404:
                raise Exception(f"Provider '{provider_path}' not found in Terraform Registry")
            elif response.status != 200:
                text = await response.text()
                raise Exception(f"Terraform Registry API error {response.status}: {text}")

            data = await response.json()

            return PackageVersion(
                name=provider_path,
                version=data.get("version", "unknown"),
                registry="terraform",
                registry_url=url,
                query_time=datetime.now(timezone.utc).isoformat() + "Z",
                description=data.get("description"),
                homepage=data.get("source"),
                license=None,  # License info not in this endpoint
            )


async def get_dockerhub_version(image_name: str) -> PackageVersion:
    """
    Get the latest version of a Docker image from DockerHub.

    Args:
        image_name: The Docker image name (e.g., "nginx", "library/nginx")

    Returns:
        PackageVersion with the latest version information

    Raises:
        ValueError: If image name is invalid
        Exception: If API call fails
    """
    if not image_name or not image_name.strip():
        raise ValueError("Image name cannot be empty")

    image_name = image_name.strip()

    # Handle official images (add library/ prefix if not present and no namespace)
    if "/" not in image_name:
        namespace = "library"
        repo_name = image_name
    else:
        namespace, repo_name = image_name.split("/", 1)

    url = f"https://hub.docker.com/v2/repositories/{namespace}/{repo_name}/tags"

    timeout = aiohttp.ClientTimeout(total=_request_timeout)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers={"Accept": "application/json"}) as response:
            if response.status == 404:
                raise Exception(f"Image '{image_name}' not found in DockerHub registry")
            elif response.status != 200:
                text = await response.text()
                raise Exception(f"DockerHub API error {response.status}: {text}")

            data = await response.json()
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
                query_time=datetime.now(timezone.utc).isoformat() + "Z",
                description=f"Docker image {image_name}",
                homepage=(
                    f"https://hub.docker.com/r/{namespace}/{repo_name}"
                    if namespace != "library"
                    else f"https://hub.docker.com/_/{repo_name}"
                ),
                license=None,  # License info not available in tags endpoint
            )


async def get_cpan_version(module_name: str) -> PackageVersion:
    """
    Get the latest version of a Perl module from CPAN via MetaCPAN.

    Args:
        module_name: The CPAN module name

    Returns:
        PackageVersion with the latest version information

    Raises:
        ValueError: If module name is invalid
        Exception: If API call fails
    """
    if not module_name or not module_name.strip():
        raise ValueError("Module name cannot be empty")

    module_name = module_name.strip()

    # Use MetaCPAN search API as alternative approach
    url = f"https://fastapi.metacpan.org/v1/module/{module_name}"

    timeout = aiohttp.ClientTimeout(total=_request_timeout)
    headers = {
        "Accept": "application/json",
        "User-Agent": "versionator-mcp/1.0 (Package Version Query Tool)",
    }

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 404:
                raise Exception(f"Module '{module_name}' not found in CPAN registry")
            elif response.status != 200:
                text = await response.text()
                raise Exception(f"CPAN API error {response.status}: {text}")

            data = await response.json()

            return PackageVersion(
                name=module_name,
                version=data.get("version", "unknown"),
                registry="cpan",
                registry_url=url,
                query_time=datetime.now(timezone.utc).isoformat() + "Z",
                description=data.get("abstract"),
                homepage=f"https://metacpan.org/pod/{module_name}",
                license=None,  # License info not readily available in this endpoint
            )


async def get_go_version(module_path: str) -> PackageVersion:
    """
    Get the latest version of a Go module.

    For GitHub-hosted modules, uses GitHub API to get latest release.
    For other modules, attempts to use pkg.go.dev API.

    Args:
        module_path: The Go module path (e.g., "github.com/gin-gonic/gin")

    Returns:
        PackageVersion with the latest version information

    Raises:
        ValueError: If module path is invalid
        Exception: If API call fails
    """
    if not module_path or not module_path.strip():
        raise ValueError("Module path cannot be empty")

    module_path = module_path.strip()

    # Handle GitHub-hosted modules
    if module_path.startswith("github.com/"):
        parts = module_path.split("/")
        if len(parts) >= 3:
            owner = parts[1]
            repo = parts[2]

            # Use GitHub API to get latest release
            url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

            timeout = aiohttp.ClientTimeout(total=_request_timeout)
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "versionator-mcp/1.0 (Package Version Query Tool)",
            }

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 404:
                        raise Exception(f"Module '{module_path}' not found or has no releases")
                    elif response.status != 200:
                        text = await response.text()
                        raise Exception(f"GitHub API error {response.status}: {text}")

                    data = await response.json()

                    return PackageVersion(
                        name=module_path,
                        version=data.get("tag_name", "unknown"),
                        registry="go",
                        registry_url=url,
                        query_time=datetime.now(timezone.utc).isoformat() + "Z",
                        description=data.get("body", f"Go module {module_path}"),
                        homepage=f"https://pkg.go.dev/{module_path}",
                        license=None,  # License info not available in releases endpoint
                    )

    # For non-GitHub modules, try pkg.go.dev API
    url = f"https://pkg.go.dev/{module_path}"

    timeout = aiohttp.ClientTimeout(total=_request_timeout)
    headers = {
        "Accept": "text/html",
        "User-Agent": "versionator-mcp/1.0 (Package Version Query Tool)",
    }

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
                query_time=datetime.now(timezone.utc).isoformat() + "Z",
                description=f"Go module {module_path}",
                homepage=url,
                license=None,
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
        # Existing registries
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
        # New registries
        "crates": get_crates_version,
        "cargo": get_crates_version,
        "rust": get_crates_version,
        "bioconda": get_bioconda_version,
        "conda": get_bioconda_version,
        "cran": get_cran_version,
        "r": get_cran_version,
        "terraform": get_terraform_version,
        "tf": get_terraform_version,
        "dockerhub": get_dockerhub_version,
        "docker": get_dockerhub_version,
        "cpan": get_cpan_version,
        "perl": get_cpan_version,
        "go": get_go_version,
        "golang": get_go_version,
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
            package_manager: The package manager/registry. Supported registries:
                           - npm (aliases: node, nodejs) - Node.js packages
                           - rubygems (aliases: gem, ruby) - Ruby gems
                           - pypi (aliases: pip, python) - Python packages
                           - hex (aliases: elixir, hex.pm) - Elixir packages
                           - crates (aliases: cargo, rust) - Rust crates
                           - bioconda (aliases: conda) - Bioconda packages
                           - cran (aliases: r) - R packages
                           - terraform (aliases: tf) - Terraform providers
                           - dockerhub (aliases: docker) - Docker images
                           - cpan (aliases: perl) - Perl modules
                           - go (aliases: golang) - Go modules
            package_name: The name of the package to query

        Returns:
            Dictionary containing package version information

        Examples:
            - get_package_version("npm", "react")
            - get_package_version("python", "django")
            - get_package_version("ruby", "rails")
            - get_package_version("elixir", "ecto")
            - get_package_version("rust", "serde")
            - get_package_version("bioconda", "samtools")
            - get_package_version("r", "ggplot2")
            - get_package_version("terraform", "hashicorp/aws")
            - get_package_version("docker", "nginx")
            - get_package_version("perl", "JSON")
            - get_package_version("go", "github.com/gin-gonic/gin")
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

    @app.tool()
    async def get_rust_crate(crate_name: str) -> Dict[str, Any]:
        """Get the latest version of a Rust crate from crates.io.

        Args:
            crate_name: The crate name

        Returns:
            Dictionary containing crate version information
        """
        version_info = await get_crates_version(crate_name)
        return version_info.model_dump()

    @app.tool()
    async def get_bioconda_package(package_name: str) -> Dict[str, Any]:
        """Get the latest version of a Bioconda package from anaconda.org.

        Args:
            package_name: The Bioconda package name

        Returns:
            Dictionary containing package version information
        """
        version_info = await get_bioconda_version(package_name)
        return version_info.model_dump()

    @app.tool()
    async def get_r_package(package_name: str) -> Dict[str, Any]:
        """Get the latest version of an R package from CRAN.

        Args:
            package_name: The CRAN package name

        Returns:
            Dictionary containing package version information
        """
        version_info = await get_cran_version(package_name)
        return version_info.model_dump()

    @app.tool()
    async def get_terraform_provider(provider_path: str) -> Dict[str, Any]:
        """Get the latest version of a Terraform provider from registry.terraform.io.

        Args:
            provider_path: The provider path (e.g., "hashicorp/aws")

        Returns:
            Dictionary containing provider version information
        """
        version_info = await get_terraform_version(provider_path)
        return version_info.model_dump()

    @app.tool()
    async def get_docker_image(image_name: str) -> Dict[str, Any]:
        """Get the latest version of a Docker image from DockerHub.

        Args:
            image_name: The Docker image name (e.g., "nginx", "library/nginx")

        Returns:
            Dictionary containing image version information
        """
        version_info = await get_dockerhub_version(image_name)
        return version_info.model_dump()

    @app.tool()
    async def get_perl_module(module_name: str) -> Dict[str, Any]:
        """Get the latest version of a Perl module from CPAN.

        Args:
            module_name: The CPAN module name

        Returns:
            Dictionary containing module version information
        """
        version_info = await get_cpan_version(module_name)
        return version_info.model_dump()

    @app.tool()
    async def get_go_module(module_path: str) -> Dict[str, Any]:
        """Get the latest version of a Go module.

        Args:
            module_path: The Go module path (e.g., "github.com/gin-gonic/gin")

        Returns:
            Dictionary containing module version information
        """
        version_info = await get_go_version(module_path)
        return version_info.model_dump()
