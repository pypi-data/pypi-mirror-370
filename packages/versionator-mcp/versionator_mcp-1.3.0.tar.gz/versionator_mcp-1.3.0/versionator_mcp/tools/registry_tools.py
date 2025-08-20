"""
MCP tool registration for package registry functions
"""

from typing import Any, Dict

from fastmcp import FastMCP

from ..core import get_available_registries, get_registry


def register_versionator_tools(app: FastMCP) -> None:
    """Register all versionator MCP tools with the FastMCP app"""

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
                           - composer (aliases: php, packagist) - PHP packages
                           - nuget (aliases: dotnet, .net) - .NET packages
                           - homebrew (aliases: brew) - Homebrew formulas
                           - nextflow (aliases: nf-core) - Nextflow pipelines
                           - nf-core-module (aliases: nfcore-module, nf-module) - nf-core modules
                           - nf-core-subworkflow (aliases: nfcore-subworkflow, nf-subworkflow) - nf-core subworkflows
                           - swift (aliases: spm) - Swift packages
                           - maven (aliases: mvn) - Maven artifacts
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
            - get_package_version("php", "symfony/console")
            - get_package_version("dotnet", "Newtonsoft.Json")
            - get_package_version("homebrew", "git")
            - get_package_version("nextflow", "nf-core/rnaseq")
            - get_package_version("nf-core-module", "fastqc")
            - get_package_version("nf-core-subworkflow", "bam_sort_stats_samtools")
            - get_package_version("swift", "apple/swift-package-manager")
            - get_package_version("maven", "org.springframework:spring-core")
        """
        registry = get_registry(package_manager)
        version_info = await registry.get_latest_version(package_name)
        return version_info.model_dump()

    # Registry-specific tools
    @app.tool()
    async def get_npm_package(package_name: str) -> Dict[str, Any]:
        """Get the latest version of an npm package.

        Args:
            package_name: The npm package name

        Returns:
            Dictionary containing package version information
        """
        registry = get_registry("npm")
        version_info = await registry.get_latest_version(package_name)
        return version_info.model_dump()

    @app.tool()
    async def get_ruby_gem(gem_name: str) -> Dict[str, Any]:
        """Get the latest version of a Ruby gem.

        Args:
            gem_name: The RubyGems package name

        Returns:
            Dictionary containing gem version information
        """
        registry = get_registry("rubygems")
        version_info = await registry.get_latest_version(gem_name)
        return version_info.model_dump()

    @app.tool()
    async def get_python_package(package_name: str) -> Dict[str, Any]:
        """Get the latest version of a Python package from PyPI.

        Args:
            package_name: The PyPI package name

        Returns:
            Dictionary containing package version information
        """
        registry = get_registry("pypi")
        version_info = await registry.get_latest_version(package_name)
        return version_info.model_dump()

    @app.tool()
    async def get_elixir_package(package_name: str) -> Dict[str, Any]:
        """Get the latest version of an Elixir package from Hex.pm.

        Args:
            package_name: The Hex package name

        Returns:
            Dictionary containing package version information
        """
        registry = get_registry("hex")
        version_info = await registry.get_latest_version(package_name)
        return version_info.model_dump()

    @app.tool()
    async def get_rust_crate(crate_name: str) -> Dict[str, Any]:
        """Get the latest version of a Rust crate from crates.io.

        Args:
            crate_name: The crate name

        Returns:
            Dictionary containing crate version information
        """
        registry = get_registry("crates")
        version_info = await registry.get_latest_version(crate_name)
        return version_info.model_dump()

    @app.tool()
    async def get_bioconda_package(package_name: str) -> Dict[str, Any]:
        """Get the latest version of a Bioconda package from anaconda.org.

        Args:
            package_name: The Bioconda package name

        Returns:
            Dictionary containing package version information
        """
        registry = get_registry("bioconda")
        version_info = await registry.get_latest_version(package_name)
        return version_info.model_dump()

    @app.tool()
    async def get_r_package(package_name: str) -> Dict[str, Any]:
        """Get the latest version of an R package from CRAN.

        Args:
            package_name: The CRAN package name

        Returns:
            Dictionary containing package version information
        """
        registry = get_registry("cran")
        version_info = await registry.get_latest_version(package_name)
        return version_info.model_dump()

    @app.tool()
    async def get_terraform_provider(provider_path: str) -> Dict[str, Any]:
        """Get the latest version of a Terraform provider from registry.terraform.io.

        Args:
            provider_path: The provider path (e.g., "hashicorp/aws")

        Returns:
            Dictionary containing provider version information
        """
        registry = get_registry("terraform")
        version_info = await registry.get_latest_version(provider_path)
        return version_info.model_dump()

    @app.tool()
    async def get_docker_image(image_name: str) -> Dict[str, Any]:
        """Get the latest version of a Docker image from DockerHub.

        Args:
            image_name: The Docker image name (e.g., "nginx", "library/nginx")

        Returns:
            Dictionary containing image version information
        """
        registry = get_registry("dockerhub")
        version_info = await registry.get_latest_version(image_name)
        return version_info.model_dump()

    @app.tool()
    async def get_perl_module(module_name: str) -> Dict[str, Any]:
        """Get the latest version of a Perl module from CPAN.

        Args:
            module_name: The CPAN module name

        Returns:
            Dictionary containing module version information
        """
        registry = get_registry("cpan")
        version_info = await registry.get_latest_version(module_name)
        return version_info.model_dump()

    @app.tool()
    async def get_go_module(module_path: str) -> Dict[str, Any]:
        """Get the latest version of a Go module.

        Args:
            module_path: The Go module path (e.g., "github.com/gin-gonic/gin")

        Returns:
            Dictionary containing module version information
        """
        registry = get_registry("go")
        version_info = await registry.get_latest_version(module_path)
        return version_info.model_dump()

    @app.tool()
    async def get_php_package(package_name: str) -> Dict[str, Any]:
        """Get the latest version of a PHP Composer package from Packagist.

        Args:
            package_name: The Composer package name (vendor/package format)

        Returns:
            Dictionary containing package version information
        """
        registry = get_registry("composer")
        version_info = await registry.get_latest_version(package_name)
        return version_info.model_dump()

    @app.tool()
    async def get_dotnet_package(package_name: str) -> Dict[str, Any]:
        """Get the latest version of a .NET NuGet package.

        Args:
            package_name: The NuGet package name

        Returns:
            Dictionary containing package version information
        """
        registry = get_registry("nuget")
        version_info = await registry.get_latest_version(package_name)
        return version_info.model_dump()

    @app.tool()
    async def get_homebrew_formula(formula_name: str) -> Dict[str, Any]:
        """Get the latest version of a Homebrew formula.

        Args:
            formula_name: The Homebrew formula name

        Returns:
            Dictionary containing formula version information
        """
        registry = get_registry("homebrew")
        version_info = await registry.get_latest_version(formula_name)
        return version_info.model_dump()

    @app.tool()
    async def get_nextflow_pipeline(pipeline_name: str) -> Dict[str, Any]:
        """Get the latest version of a Nextflow pipeline from nf-core.

        Args:
            pipeline_name: The pipeline name (e.g., "nf-core/rnaseq")

        Returns:
            Dictionary containing pipeline version information
        """
        registry = get_registry("nextflow")
        version_info = await registry.get_latest_version(pipeline_name)
        return version_info.model_dump()

    @app.tool()
    async def get_nfcore_module(module_name: str) -> Dict[str, Any]:
        """Get the latest version of an nf-core module.

        Args:
            module_name: The module name (e.g., "fastqc", "bwa/mem")

        Returns:
            Dictionary containing module version information
        """
        registry = get_registry("nf-core-module")
        version_info = await registry.get_latest_version(module_name)
        return version_info.model_dump()

    @app.tool()
    async def get_nfcore_subworkflow(subworkflow_name: str) -> Dict[str, Any]:
        """Get the latest version of an nf-core subworkflow.

        Args:
            subworkflow_name: The subworkflow name (e.g., "bam_sort_stats_samtools")

        Returns:
            Dictionary containing subworkflow version information
        """
        registry = get_registry("nf-core-subworkflow")
        version_info = await registry.get_latest_version(subworkflow_name)
        return version_info.model_dump()

    @app.tool()
    async def get_swift_package(package_name: str) -> Dict[str, Any]:
        """Get the latest version of a Swift package from GitHub.

        Args:
            package_name: The Swift package name (GitHub repo format: owner/repo)

        Returns:
            Dictionary containing package version information
        """
        registry = get_registry("swift")
        version_info = await registry.get_latest_version(package_name)
        return version_info.model_dump()

    @app.tool()
    async def get_maven_artifact(artifact_name: str) -> Dict[str, Any]:
        """Get the latest version of a Maven Central artifact.

        Args:
            artifact_name: The Maven artifact name (groupId:artifactId format)

        Returns:
            Dictionary containing artifact version information
        """
        registry = get_registry("maven")
        version_info = await registry.get_latest_version(artifact_name)
        return version_info.model_dump()
