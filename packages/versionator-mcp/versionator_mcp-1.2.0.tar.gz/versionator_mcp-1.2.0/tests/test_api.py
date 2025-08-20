"""
Tests for Versionator MCP Server API functions
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from versionator_mcp.api.versionator import (
    get_hex_version,
    get_latest_version,
    get_npm_version,
    get_pypi_version,
    get_rubygems_version,
    set_request_timeout,
)


class MockResponse:
    """Mock aiohttp response"""

    def __init__(self, status, json_data=None, text_data=None):
        self.status = status
        self._json_data = json_data
        self._text_data = text_data or ""

    async def json(self):
        return self._json_data

    async def text(self):
        return self._text_data

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class MockSession:
    """Mock aiohttp session"""

    def __init__(self, response):
        self.response = response

    def get(self, url, **kwargs):
        return self.response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


@pytest.mark.asyncio
async def test_get_npm_version_success():
    """Test successful npm version retrieval"""
    mock_data = {
        "version": "18.2.0",
        "description": "React is a JavaScript library",
        "homepage": "https://react.dev/",
        "license": "MIT",
    }

    mock_response = MockResponse(200, mock_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        result = await get_npm_version("react")

        assert result.name == "react"
        assert result.version == "18.2.0"
        assert result.registry == "npm"
        assert result.description == "React is a JavaScript library"
        assert result.homepage == "https://react.dev/"
        assert result.license == "MIT"
        assert "registry.npmjs.org" in result.registry_url


@pytest.mark.asyncio
async def test_get_npm_version_not_found():
    """Test npm package not found"""
    mock_response = MockResponse(404, text_data="Not found")

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        with pytest.raises(Exception, match="Package 'nonexistent' not found in npm registry"):
            await get_npm_version("nonexistent")


@pytest.mark.asyncio
async def test_get_npm_version_empty_name():
    """Test npm with empty package name"""
    with pytest.raises(ValueError, match="Package name cannot be empty"):
        await get_npm_version("")

    with pytest.raises(ValueError, match="Package name cannot be empty"):
        await get_npm_version("   ")


@pytest.mark.asyncio
async def test_get_npm_version_api_error():
    """Test npm API error handling"""
    mock_response = MockResponse(500, text_data="Internal server error")

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        with pytest.raises(Exception, match="npm API error 500: Internal server error"):
            await get_npm_version("react")


@pytest.mark.asyncio
async def test_get_rubygems_version_success():
    """Test successful RubyGems version retrieval"""
    mock_data = {"version": "7.0.4"}
    mock_response = MockResponse(200, mock_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        result = await get_rubygems_version("rails")

        assert result.name == "rails"
        assert result.version == "7.0.4"
        assert result.registry == "rubygems"
        assert "rubygems.org" in result.registry_url


@pytest.mark.asyncio
async def test_get_rubygems_version_not_found():
    """Test RubyGems gem not found"""
    mock_response = MockResponse(404, text_data="Not found")

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        with pytest.raises(Exception, match="Gem 'nonexistent' not found in RubyGems registry"):
            await get_rubygems_version("nonexistent")


@pytest.mark.asyncio
async def test_get_pypi_version_success():
    """Test successful PyPI version retrieval"""
    mock_data = {
        "info": {
            "version": "4.1.0",
            "summary": "The Web framework for perfectionists",
            "home_page": "https://www.djangoproject.com/",
            "license": "BSD",
        }
    }
    mock_response = MockResponse(200, mock_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        result = await get_pypi_version("django")

        assert result.name == "django"
        assert result.version == "4.1.0"
        assert result.registry == "pypi"
        assert result.description == "The Web framework for perfectionists"
        assert result.homepage == "https://www.djangoproject.com/"
        assert result.license == "BSD"
        assert "pypi.org" in result.registry_url


@pytest.mark.asyncio
async def test_get_pypi_version_not_found():
    """Test PyPI package not found"""
    mock_response = MockResponse(404, text_data="Not found")

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        with pytest.raises(Exception, match="Package 'nonexistent' not found in PyPI registry"):
            await get_pypi_version("nonexistent")


@pytest.mark.asyncio
async def test_get_hex_version_success():
    """Test successful Hex.pm version retrieval"""
    mock_data = {
        "releases": [{"version": "3.8.0"}, {"version": "3.7.0"}],
        "meta": {
            "description": "A toolkit for data mapping",
            "links": {"GitHub": "https://github.com/elixir-ecto/ecto"},
            "licenses": ["Apache-2.0"],
        },
    }
    mock_response = MockResponse(200, mock_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        result = await get_hex_version("ecto")

        assert result.name == "ecto"
        assert result.version == "3.8.0"
        assert result.registry == "hex"
        assert result.description == "A toolkit for data mapping"
        assert result.homepage == "https://github.com/elixir-ecto/ecto"
        assert result.license == "Apache-2.0"
        assert "hex.pm" in result.registry_url


@pytest.mark.asyncio
async def test_get_hex_version_no_releases():
    """Test Hex.pm package with no releases"""
    mock_data = {"releases": [], "meta": {}}
    mock_response = MockResponse(200, mock_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        with pytest.raises(Exception, match="No releases found for package 'newpackage'"):
            await get_hex_version("newpackage")


@pytest.mark.asyncio
async def test_get_latest_version_npm():
    """Test get_latest_version with npm"""
    mock_data = {"version": "18.2.0"}
    mock_response = MockResponse(200, mock_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(mock_response)):
        result = await get_latest_version("npm", "react")
        assert result.version == "18.2.0"
        assert result.registry == "npm"


@pytest.mark.asyncio
async def test_get_latest_version_aliases():
    """Test get_latest_version with various aliases"""
    # Test npm aliases
    npm_data = {"version": "18.2.0"}
    npm_response = MockResponse(200, npm_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(npm_response)):
        for alias in ["npm", "node", "nodejs"]:
            result = await get_latest_version(alias, "react")
            assert result.registry == "npm"

    # Test Ruby aliases
    ruby_data = {"version": "7.0.4"}
    ruby_response = MockResponse(200, ruby_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(ruby_response)):
        for alias in ["rubygems", "gem", "ruby"]:
            result = await get_latest_version(alias, "rails")
            assert result.registry == "rubygems"

    # Test Python aliases
    pypi_data = {"info": {"version": "4.1.0"}}
    pypi_response = MockResponse(200, pypi_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(pypi_response)):
        for alias in ["pypi", "pip", "python"]:
            result = await get_latest_version(alias, "django")
            assert result.registry == "pypi"

    # Test Elixir aliases
    hex_data = {"releases": [{"version": "3.8.0"}], "meta": {}}
    hex_response = MockResponse(200, hex_data)

    with patch("aiohttp.ClientSession", return_value=MockSession(hex_response)):
        for alias in ["hex", "elixir", "hex.pm"]:
            result = await get_latest_version(alias, "ecto")
            assert result.registry == "hex"


@pytest.mark.asyncio
async def test_get_latest_version_invalid_manager():
    """Test get_latest_version with invalid package manager"""
    with pytest.raises(ValueError, match="Unknown package manager 'invalid-registry'"):
        await get_latest_version("invalid-registry", "some-package")


@pytest.mark.asyncio
async def test_get_latest_version_empty_manager():
    """Test get_latest_version with empty package manager"""
    with pytest.raises(ValueError, match="Package manager cannot be empty"):
        await get_latest_version("", "package")

    with pytest.raises(ValueError, match="Package manager cannot be empty"):
        await get_latest_version("   ", "package")


def test_set_request_timeout():
    """Test setting request timeout"""
    set_request_timeout(60)
    # This test just verifies the function doesn't crash
    # The actual timeout is used internally in the module


# =============================================================================
# NEW PACKAGE MANAGER TESTS (TDD - These should FAIL initially)
# =============================================================================


# Rust (crates.io) Tests
@pytest.mark.asyncio
async def test_get_crates_version_success():
    """Test successful crates.io version retrieval"""
    from versionator_mcp.api.versionator import get_crates_version

    result = await get_crates_version("serde")
    assert result.name == "serde"
    assert result.version is not None
    assert result.registry == "crates"
    assert "crates.io" in result.registry_url


@pytest.mark.asyncio
async def test_get_crates_version_not_found():
    """Test crates.io package not found"""
    from versionator_mcp.api.versionator import get_crates_version

    with pytest.raises(Exception, match="Crate 'nonexistent-crate-12345' not found"):
        await get_crates_version("nonexistent-crate-12345")


@pytest.mark.asyncio
async def test_get_crates_version_empty_name():
    """Test crates.io with empty package name"""
    from versionator_mcp.api.versionator import get_crates_version

    with pytest.raises(ValueError, match="Crate name cannot be empty"):
        await get_crates_version("")


# Bioconda Tests
@pytest.mark.asyncio
async def test_get_bioconda_version_success():
    """Test successful Bioconda version retrieval"""
    from versionator_mcp.api.versionator import get_bioconda_version

    result = await get_bioconda_version("samtools")
    assert result.name == "samtools"
    assert result.version is not None
    assert result.registry == "bioconda"
    assert "anaconda.org" in result.registry_url


@pytest.mark.asyncio
async def test_get_bioconda_version_not_found():
    """Test Bioconda package not found"""
    from versionator_mcp.api.versionator import get_bioconda_version

    with pytest.raises(Exception, match="Package 'nonexistent-bio-package' not found"):
        await get_bioconda_version("nonexistent-bio-package")


@pytest.mark.asyncio
async def test_get_bioconda_version_empty_name():
    """Test Bioconda with empty package name"""
    from versionator_mcp.api.versionator import get_bioconda_version

    with pytest.raises(ValueError, match="Package name cannot be empty"):
        await get_bioconda_version("")


# R (CRAN) Tests
@pytest.mark.asyncio
async def test_get_cran_version_success():
    """Test successful CRAN version retrieval"""
    from versionator_mcp.api.versionator import get_cran_version

    result = await get_cran_version("ggplot2")
    assert result.name == "ggplot2"
    assert result.version is not None
    assert result.registry == "cran"
    assert "crandb.r-pkg.org" in result.registry_url


@pytest.mark.asyncio
async def test_get_cran_version_not_found():
    """Test CRAN package not found"""
    from versionator_mcp.api.versionator import get_cran_version

    with pytest.raises(Exception, match="Package 'nonexistent-r-package' not found"):
        await get_cran_version("nonexistent-r-package")


@pytest.mark.asyncio
async def test_get_cran_version_empty_name():
    """Test CRAN with empty package name"""
    from versionator_mcp.api.versionator import get_cran_version

    with pytest.raises(ValueError, match="Package name cannot be empty"):
        await get_cran_version("")


# Terraform Registry Tests
@pytest.mark.asyncio
async def test_get_terraform_version_success():
    """Test successful Terraform Registry version retrieval"""
    from versionator_mcp.api.versionator import get_terraform_version

    result = await get_terraform_version("hashicorp/aws")
    assert result.name == "hashicorp/aws"
    assert result.version is not None
    assert result.registry == "terraform"
    assert "registry.terraform.io" in result.registry_url


@pytest.mark.asyncio
async def test_get_terraform_version_not_found():
    """Test Terraform Registry provider not found"""
    from versionator_mcp.api.versionator import get_terraform_version

    with pytest.raises(Exception, match="Provider 'nonexistent/provider' not found"):
        await get_terraform_version("nonexistent/provider")


@pytest.mark.asyncio
async def test_get_terraform_version_empty_name():
    """Test Terraform Registry with empty provider name"""
    from versionator_mcp.api.versionator import get_terraform_version

    with pytest.raises(ValueError, match="Provider name cannot be empty"):
        await get_terraform_version("")


# DockerHub Tests
@pytest.mark.asyncio
async def test_get_dockerhub_version_success():
    """Test successful DockerHub version retrieval"""
    from versionator_mcp.api.versionator import get_dockerhub_version

    result = await get_dockerhub_version("nginx")
    assert result.name == "nginx"
    assert result.version is not None
    assert result.registry == "dockerhub"
    assert "hub.docker.com" in result.registry_url


@pytest.mark.asyncio
async def test_get_dockerhub_version_not_found():
    """Test DockerHub image not found"""
    from versionator_mcp.api.versionator import get_dockerhub_version

    with pytest.raises(Exception, match="Image 'nonexistent-docker-image' not found"):
        await get_dockerhub_version("nonexistent-docker-image")


@pytest.mark.asyncio
async def test_get_dockerhub_version_empty_name():
    """Test DockerHub with empty image name"""
    from versionator_mcp.api.versionator import get_dockerhub_version

    with pytest.raises(ValueError, match="Image name cannot be empty"):
        await get_dockerhub_version("")


# Perl (CPAN) Tests
@pytest.mark.asyncio
async def test_get_cpan_version_success():
    """Test successful CPAN version retrieval"""
    from versionator_mcp.api.versionator import get_cpan_version

    result = await get_cpan_version("JSON")
    assert result.name == "JSON"
    assert result.version is not None
    assert result.registry == "cpan"
    assert "metacpan.org" in result.registry_url


@pytest.mark.asyncio
async def test_get_cpan_version_not_found():
    """Test CPAN module not found"""
    from versionator_mcp.api.versionator import get_cpan_version

    with pytest.raises(Exception, match="Module 'NonExistentPerlModule' not found"):
        await get_cpan_version("NonExistentPerlModule")


@pytest.mark.asyncio
async def test_get_cpan_version_empty_name():
    """Test CPAN with empty module name"""
    from versionator_mcp.api.versionator import get_cpan_version

    with pytest.raises(ValueError, match="Module name cannot be empty"):
        await get_cpan_version("")


# Go Modules Tests
@pytest.mark.asyncio
async def test_get_go_version_success():
    """Test successful Go module version retrieval"""
    from versionator_mcp.api.versionator import get_go_version

    result = await get_go_version("github.com/gin-gonic/gin")
    assert result.name == "github.com/gin-gonic/gin"
    assert result.version is not None
    assert result.registry == "go"
    assert "github.com" in result.registry_url or "pkg.go.dev" in result.registry_url


@pytest.mark.asyncio
async def test_get_go_version_not_found():
    """Test Go module not found"""
    from versionator_mcp.api.versionator import get_go_version

    with pytest.raises(Exception, match="Module 'github.com/nonexistent/module' not found"):
        await get_go_version("github.com/nonexistent/module")


@pytest.mark.asyncio
async def test_get_go_version_empty_name():
    """Test Go modules with empty module path"""
    from versionator_mcp.api.versionator import get_go_version

    with pytest.raises(ValueError, match="Module path cannot be empty"):
        await get_go_version("")


# Generic function tests for new registries
@pytest.mark.asyncio
async def test_get_latest_version_new_registries():
    """Test get_latest_version with new registry aliases"""
    # Test Rust aliases
    rust_aliases = ["crates", "cargo", "rust"]
    for alias in rust_aliases:
        result = await get_latest_version(alias, "serde")
        assert result.registry == "crates"

    # Test Bioconda aliases
    bioconda_aliases = ["bioconda", "conda"]
    for alias in bioconda_aliases:
        result = await get_latest_version(alias, "samtools")
        assert result.registry == "bioconda"

    # Test R aliases
    r_aliases = ["cran", "r"]
    for alias in r_aliases:
        result = await get_latest_version(alias, "ggplot2")
        assert result.registry == "cran"

    # Test Terraform aliases
    terraform_aliases = ["terraform", "tf"]
    for alias in terraform_aliases:
        result = await get_latest_version(alias, "hashicorp/aws")
        assert result.registry == "terraform"

    # Test DockerHub aliases
    docker_aliases = ["dockerhub", "docker"]
    for alias in docker_aliases:
        result = await get_latest_version(alias, "nginx")
        assert result.registry == "dockerhub"

    # Test Perl aliases
    perl_aliases = ["cpan", "perl"]
    for alias in perl_aliases:
        result = await get_latest_version(alias, "JSON")
        assert result.registry == "cpan"

    # Test Go aliases
    go_aliases = ["go", "golang"]
    for alias in go_aliases:
        result = await get_latest_version(alias, "github.com/gin-gonic/gin")
        assert result.registry == "go"


# =============================================================================
# NEW PACKAGE MANAGER TESTS v1.2.0 (TDD - These should FAIL initially)
# =============================================================================


# PHP Composer Tests
@pytest.mark.asyncio
async def test_get_composer_version_success():
    """Test successful Composer version retrieval"""
    from versionator_mcp.api.versionator import get_composer_version

    result = await get_composer_version("symfony/console")
    assert result.name == "symfony/console"
    assert result.version is not None
    assert result.registry == "composer"
    assert "packagist.org" in result.registry_url


@pytest.mark.asyncio
async def test_get_composer_version_not_found():
    """Test Composer package not found"""
    from versionator_mcp.api.versionator import get_composer_version

    with pytest.raises(Exception, match="Package 'nonexistent/package' not found"):
        await get_composer_version("nonexistent/package")


@pytest.mark.asyncio
async def test_get_composer_version_empty_name():
    """Test Composer with empty package name"""
    from versionator_mcp.api.versionator import get_composer_version

    with pytest.raises(ValueError, match="Package name cannot be empty"):
        await get_composer_version("")


# .NET NuGet Tests
@pytest.mark.asyncio
async def test_get_nuget_version_success():
    """Test successful NuGet version retrieval"""
    from versionator_mcp.api.versionator import get_nuget_version

    result = await get_nuget_version("Newtonsoft.Json")
    assert result.name == "Newtonsoft.Json"
    assert result.version is not None
    assert result.registry == "nuget"
    assert "nuget.org" in result.registry_url


@pytest.mark.asyncio
async def test_get_nuget_version_not_found():
    """Test NuGet package not found"""
    from versionator_mcp.api.versionator import get_nuget_version

    with pytest.raises(Exception, match="Package 'NonExistentNuGetPackage' not found"):
        await get_nuget_version("NonExistentNuGetPackage")


@pytest.mark.asyncio
async def test_get_nuget_version_empty_name():
    """Test NuGet with empty package name"""
    from versionator_mcp.api.versionator import get_nuget_version

    with pytest.raises(ValueError, match="Package name cannot be empty"):
        await get_nuget_version("")


# Homebrew Tests
@pytest.mark.asyncio
async def test_get_homebrew_version_success():
    """Test successful Homebrew version retrieval"""
    from versionator_mcp.api.versionator import get_homebrew_version

    result = await get_homebrew_version("git")
    assert result.name == "git"
    assert result.version is not None
    assert result.registry == "homebrew"
    assert "formulae.brew.sh" in result.registry_url


@pytest.mark.asyncio
async def test_get_homebrew_version_not_found():
    """Test Homebrew formula not found"""
    from versionator_mcp.api.versionator import get_homebrew_version

    with pytest.raises(Exception, match="Formula 'nonexistent-formula' not found"):
        await get_homebrew_version("nonexistent-formula")


@pytest.mark.asyncio
async def test_get_homebrew_version_empty_name():
    """Test Homebrew with empty formula name"""
    from versionator_mcp.api.versionator import get_homebrew_version

    with pytest.raises(ValueError, match="Formula name cannot be empty"):
        await get_homebrew_version("")


# Nextflow Tests
@pytest.mark.asyncio
async def test_get_nextflow_version_success():
    """Test successful Nextflow pipeline version retrieval"""
    from versionator_mcp.api.versionator import get_nextflow_version

    result = await get_nextflow_version("nf-core/rnaseq")
    assert result.name == "nf-core/rnaseq"
    assert result.version is not None
    assert result.registry == "nextflow"
    assert "github.com" in result.registry_url


@pytest.mark.asyncio
async def test_get_nextflow_version_not_found():
    """Test Nextflow pipeline not found"""
    from versionator_mcp.api.versionator import get_nextflow_version

    with pytest.raises(Exception, match="Pipeline 'nf-core/nonexistent' not found"):
        await get_nextflow_version("nf-core/nonexistent")


@pytest.mark.asyncio
async def test_get_nextflow_version_empty_name():
    """Test Nextflow with empty pipeline name"""
    from versionator_mcp.api.versionator import get_nextflow_version

    with pytest.raises(ValueError, match="Pipeline name cannot be empty"):
        await get_nextflow_version("")


# Swift Package Manager Tests
@pytest.mark.asyncio
async def test_get_swift_version_success():
    """Test successful Swift Package Manager version retrieval"""
    from versionator_mcp.api.versionator import get_swift_version

    result = await get_swift_version("apple/swift-package-manager")
    assert result.name == "apple/swift-package-manager"
    assert result.version is not None
    assert result.registry == "swift"
    assert "github.com" in result.registry_url


@pytest.mark.asyncio
async def test_get_swift_version_not_found():
    """Test Swift package not found"""
    from versionator_mcp.api.versionator import get_swift_version

    with pytest.raises(Exception, match="Package 'nonexistent/swift-package' not found"):
        await get_swift_version("nonexistent/swift-package")


@pytest.mark.asyncio
async def test_get_swift_version_empty_name():
    """Test Swift Package Manager with empty package name"""
    from versionator_mcp.api.versionator import get_swift_version

    with pytest.raises(ValueError, match="Package name cannot be empty"):
        await get_swift_version("")


# Maven Central Tests
@pytest.mark.asyncio
async def test_get_maven_version_success():
    """Test successful Maven Central version retrieval"""
    from versionator_mcp.api.versionator import get_maven_version

    result = await get_maven_version("org.springframework:spring-core")
    assert result.name == "org.springframework:spring-core"
    assert result.version is not None
    assert result.registry == "maven"
    assert "search.maven.org" in result.registry_url


@pytest.mark.asyncio
async def test_get_maven_version_not_found():
    """Test Maven Central artifact not found"""
    from versionator_mcp.api.versionator import get_maven_version

    with pytest.raises(Exception, match="Artifact 'com.nonexistent:artifact' not found"):
        await get_maven_version("com.nonexistent:artifact")


@pytest.mark.asyncio
async def test_get_maven_version_empty_name():
    """Test Maven Central with empty artifact name"""
    from versionator_mcp.api.versionator import get_maven_version

    with pytest.raises(ValueError, match="Artifact name cannot be empty"):
        await get_maven_version("")


# Generic function tests for v1.2.0 registries
@pytest.mark.asyncio
async def test_get_latest_version_v12_registries():
    """Test get_latest_version with v1.2.0 registry aliases"""
    # Test PHP Composer aliases
    composer_aliases = ["composer", "php", "packagist"]
    for alias in composer_aliases:
        result = await get_latest_version(alias, "symfony/console")
        assert result.registry == "composer"

    # Test .NET NuGet aliases
    nuget_aliases = ["nuget", "dotnet", ".net"]
    for alias in nuget_aliases:
        result = await get_latest_version(alias, "Newtonsoft.Json")
        assert result.registry == "nuget"

    # Test Homebrew aliases
    homebrew_aliases = ["homebrew", "brew"]
    for alias in homebrew_aliases:
        result = await get_latest_version(alias, "git")
        assert result.registry == "homebrew"

    # Test Nextflow aliases
    nextflow_aliases = ["nextflow", "nf-core"]
    for alias in nextflow_aliases:
        result = await get_latest_version(alias, "nf-core/rnaseq")
        assert result.registry == "nextflow"

    # Test Swift aliases
    swift_aliases = ["swift", "spm"]
    for alias in swift_aliases:
        result = await get_latest_version(alias, "apple/swift-package-manager")
        assert result.registry == "swift"

    # Test Maven aliases
    maven_aliases = ["maven", "mvn"]
    for alias in maven_aliases:
        result = await get_latest_version(alias, "org.springframework:spring-core")
        assert result.registry == "maven"
