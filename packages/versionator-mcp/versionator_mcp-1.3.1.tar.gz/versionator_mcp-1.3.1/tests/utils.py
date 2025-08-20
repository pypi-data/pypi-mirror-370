"""
Shared test utilities for Versionator MCP Server tests
"""

# Import registries to trigger registration
import versionator_mcp.registries  # noqa: F401
from versionator_mcp.core import get_registry
from versionator_mcp.core.http_client import HTTPClient


def set_request_timeout(timeout: int) -> None:
    """Set the request timeout for API calls (compatibility function)"""
    HTTPClient._default_timeout = timeout


async def get_latest_version(package_manager: str, package_name: str):
    """Get latest version using the registry factory (compatibility function)"""
    registry = get_registry(package_manager)
    return await registry.get_latest_version(package_name)


# Registry-specific compatibility functions
async def get_npm_version(package_name: str):
    """Get npm version (compatibility function)"""
    registry = get_registry("npm")
    return await registry.get_latest_version(package_name)


async def get_rubygems_version(gem_name: str):
    """Get rubygems version (compatibility function)"""
    registry = get_registry("rubygems")
    return await registry.get_latest_version(gem_name)


async def get_pypi_version(package_name: str):
    """Get pypi version (compatibility function)"""
    registry = get_registry("pypi")
    return await registry.get_latest_version(package_name)


async def get_hex_version(package_name: str):
    """Get hex version (compatibility function)"""
    registry = get_registry("hex")
    return await registry.get_latest_version(package_name)


async def get_crates_version(package_name: str):
    """Get crates version (compatibility function)"""
    registry = get_registry("crates")
    return await registry.get_latest_version(package_name)


async def get_bioconda_version(package_name: str):
    """Get bioconda version (compatibility function)"""
    registry = get_registry("bioconda")
    return await registry.get_latest_version(package_name)


async def get_cran_version(package_name: str):
    """Get cran version (compatibility function)"""
    registry = get_registry("cran")
    return await registry.get_latest_version(package_name)


async def get_terraform_version(provider_name: str):
    """Get terraform version (compatibility function)"""
    registry = get_registry("terraform")
    return await registry.get_latest_version(provider_name)


async def get_dockerhub_version(image_name: str):
    """Get dockerhub version (compatibility function)"""
    registry = get_registry("dockerhub")
    return await registry.get_latest_version(image_name)


async def get_cpan_version(module_name: str):
    """Get cpan version (compatibility function)"""
    registry = get_registry("cpan")
    return await registry.get_latest_version(module_name)


async def get_go_version(module_path: str):
    """Get go version (compatibility function)"""
    registry = get_registry("go")
    return await registry.get_latest_version(module_path)


async def get_composer_version(package_name: str):
    """Get composer version (compatibility function)"""
    registry = get_registry("composer")
    return await registry.get_latest_version(package_name)


async def get_nuget_version(package_name: str):
    """Get nuget version (compatibility function)"""
    registry = get_registry("nuget")
    return await registry.get_latest_version(package_name)


async def get_homebrew_version(formula_name: str):
    """Get homebrew version (compatibility function)"""
    registry = get_registry("homebrew")
    return await registry.get_latest_version(formula_name)


async def get_nextflow_version(pipeline_name: str):
    """Get nextflow version (compatibility function)"""
    registry = get_registry("nextflow")
    return await registry.get_latest_version(pipeline_name)


async def get_swift_version(package_name: str):
    """Get swift version (compatibility function)"""
    registry = get_registry("swift")
    return await registry.get_latest_version(package_name)


async def get_maven_version(artifact_name: str):
    """Get maven version (compatibility function)"""
    registry = get_registry("maven")
    return await registry.get_latest_version(artifact_name)


async def get_nfcore_module_version(module_name: str):
    """Get nf-core module version (compatibility function)"""
    registry = get_registry("nf-core-module")
    return await registry.get_latest_version(module_name)


async def get_nfcore_subworkflow_version(subworkflow_name: str):
    """Get nf-core subworkflow version (compatibility function)"""
    registry = get_registry("nf-core-subworkflow")
    return await registry.get_latest_version(subworkflow_name)


async def get_nfcore_version(package_name: str):
    """Get nf-core version (compatibility function)"""
    registry = get_registry("nf-core-module")
    return await registry.get_latest_version(package_name)
