"""
App factory for Versionator MCP Server

Contains the FastMCP application factory and lifespan management
for package registry API access.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastmcp import FastMCP

from .config import get_config


def create_app() -> FastMCP:
    """Create and configure the FastMCP application"""

    @asynccontextmanager
    async def lifespan(app: FastMCP) -> AsyncGenerator[None, None]:
        """Initialize server on startup"""

        # Setup logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        logger = logging.getLogger("versionator-mcp-server")

        try:
            # Get configuration
            config = get_config()

            # Set timeout in HTTP client
            from .core.http_client import HTTPClient

            HTTPClient._default_timeout = config.request_timeout

            logger.info(f"Versionator MCP Server starting...")
            logger.info(f"Request timeout: {config.request_timeout}s")
            logger.info(
                f"Supported registries: npm, rubygems, pypi, hex, crates, bioconda, cran, terraform, dockerhub, cpan, go, composer, nuget, homebrew, nextflow, nf-core-module, nf-core-subworkflow, swift, maven"
            )
            logger.info(
                f"Available functions: get_package_version, get_npm_package, get_ruby_gem, get_python_package, get_elixir_package, get_rust_crate, get_bioconda_package, get_r_package, get_terraform_provider, get_docker_image, get_perl_module, get_go_module, get_php_package, get_dotnet_package, get_homebrew_formula, get_nextflow_pipeline, get_nfcore_module, get_nfcore_subworkflow, get_swift_package, get_maven_artifact"
            )

            yield

        except Exception as e:
            logger.error(f"Failed to initialize server: {e}")
            raise
        finally:
            logger.info("Versionator MCP Server shutdown complete")

    # Prepare FastMCP system prompt (instructions) to guide LLMs when connected via MCP
    instructions = (
        "You are connected to the Versionator MCP server. Use the package registry tools to get "
        "the latest versions of packages. Follow these rules:\n\n"
        "1) Call explore_versionator-mcp-server_data_model once at the start to understand available functions.\n"
        "2) Use get_package_version(package_manager, package_name) for general package queries.\n"
        "3) Use specific registry functions for targeted queries:\n"
        "   - get_npm_package(package_name) for npm packages\n"
        "   - get_ruby_gem(gem_name) for Ruby gems\n"
        "   - get_python_package(package_name) for PyPI packages\n"
        "   - get_elixir_package(package_name) for Hex packages\n"
        "   - get_rust_crate(crate_name) for Rust crates\n"
        "   - get_bioconda_package(package_name) for Bioconda packages\n"
        "   - get_r_package(package_name) for R/CRAN packages\n"
        "   - get_terraform_provider(provider_path) for Terraform providers\n"
        "   - get_docker_image(image_name) for Docker images\n"
        "   - get_perl_module(module_name) for Perl/CPAN modules\n"
        "   - get_go_module(module_path) for Go modules\n"
        "   - get_php_package(package_name) for PHP/Composer packages\n"
        "   - get_dotnet_package(package_name) for .NET/NuGet packages\n"
        "   - get_homebrew_formula(formula_name) for Homebrew formulas\n"
        "   - get_nextflow_pipeline(pipeline_name) for Nextflow pipelines\n"
        "   - get_nfcore_module(module_name) for nf-core modules\n"
        "   - get_nfcore_subworkflow(subworkflow_name) for nf-core subworkflows\n"
        "   - get_swift_package(package_name) for Swift packages\n"
        "   - get_maven_artifact(artifact_name) for Maven artifacts\n"
        "4) Supported package managers: npm, rubygems, pypi, hex, crates, bioconda, cran, terraform, dockerhub, cpan, go, composer, nuget, homebrew, nextflow, nf-core-module, nf-core-subworkflow, swift, maven\n"
        "5) Always specify the exact package name you want to query.\n"
        "6) Present version information clearly with package name, version, and registry.\n"
    )

    # Create the FastMCP application
    app = FastMCP("versionator-mcp-server", instructions=instructions, lifespan=lifespan)

    # Import registries to trigger registration
    from . import registries  # noqa: F401

    # Import and register MCP tools
    from .tools import register_versionator_tools

    register_versionator_tools(app)

    # Add health check endpoint
    @app.tool()
    async def health_check() -> dict:
        """Health check endpoint for Docker and monitoring"""
        return {
            "status": "healthy",
            "service": "versionator-mcp-server",
            "timestamp": asyncio.get_event_loop().time(),
        }

    # Also expose a reusable prompt template via FastMCP prompts API
    @app.prompt(
        name="versionator_usage_guide",
        title="Versionator MCP Usage Guide",
        description="How to use Versionator tools effectively",
    )
    def versionator_usage_guide() -> list[dict]:
        return [{"role": "system", "content": instructions}]

    return app
