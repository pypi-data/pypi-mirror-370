#!/usr/bin/env python3
"""
Script to generate the remaining registry test files
"""

import os

# Registry configurations: (registry_name, test_package, expected_registry_name, registry_url_fragment)
registries = [
    ("dockerhub", "nginx", "dockerhub", "hub.docker.com"),
    ("cpan", "DBI", "cpan", "metacpan.org"),
    ("go", "github.com/gin-gonic/gin", "go", "pkg.go.dev"),
    ("composer", "symfony/console", "composer", "packagist.org"),
    ("nuget", "Newtonsoft.Json", "nuget", "nuget.org"),
    ("homebrew", "wget", "homebrew", "formulae.brew.sh"),
    ("nextflow", "nf-core/rnaseq", "nextflow", "github.com"),
    ("swift", "Alamofire/Alamofire", "swift", "github.com"),
    ("maven", "org.springframework:spring-core", "maven", "search.maven.org"),
    ("nfcore", "fastqc", "nfcore", "github.com"),
]

template = '''"""
Tests for {registry_title} registry functionality
"""

import pytest

from tests.conftest import skip_github_api
from tests.utils import get_{registry_name}_version


class Test{registry_class}Registry:
    """Test {registry_title} registry functionality"""

    @pytest.mark.asyncio
    async def test_get_{registry_name}_version_success(self):
        """Test successful {registry_title} package version retrieval"""
        result = await get_{registry_name}_version("{test_package}")
        assert result.version is not None
        assert result.registry == "{expected_registry}"
        assert "{url_fragment}" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_{registry_name}_version_not_found(self):
        """Test {registry_title} package not found"""
        with pytest.raises(Exception, match="Package 'nonexistent' not found in {registry_title} registry"):
            await get_{registry_name}_version("nonexistent")

    @pytest.mark.asyncio
    async def test_get_{registry_name}_version_empty_name(self):
        """Test {registry_title} with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_{registry_name}_version("")
'''

github_template = '''"""
Tests for {registry_title} registry functionality
"""

import pytest

from tests.conftest import skip_github_api
from tests.utils import get_{registry_name}_version


class Test{registry_class}Registry:
    """Test {registry_title} registry functionality"""

    @skip_github_api
    @pytest.mark.asyncio
    async def test_get_{registry_name}_version_success(self):
        """Test successful {registry_title} package version retrieval"""
        result = await get_{registry_name}_version("{test_package}")
        assert result.version is not None
        assert result.registry == "{expected_registry}"
        assert "{url_fragment}" in result.registry_url

    @pytest.mark.asyncio
    async def test_get_{registry_name}_version_not_found(self):
        """Test {registry_title} package not found"""
        with pytest.raises(Exception, match="Package 'nonexistent' not found in GitHub registry"):
            await get_{registry_name}_version("nonexistent")

    @pytest.mark.asyncio
    async def test_get_{registry_name}_version_empty_name(self):
        """Test {registry_title} with empty package name"""
        with pytest.raises(ValueError, match="Package name cannot be empty"):
            await get_{registry_name}_version("")
'''


def generate_test_file(registry_name, test_package, expected_registry, url_fragment):
    registry_title = registry_name.title()
    if registry_name == "dockerhub":
        registry_title = "DockerHub"
    elif registry_name == "cpan":
        registry_title = "CPAN"
    elif registry_name == "nuget":
        registry_title = "NuGet"
    elif registry_name == "nfcore":
        registry_title = "nf-core"

    registry_class = registry_title.replace("-", "").replace(".", "")

    # Use GitHub template for registries that use GitHub API
    if registry_name in ["go", "nextflow", "swift", "nfcore"]:
        content = github_template.format(
            registry_name=registry_name,
            registry_title=registry_title,
            registry_class=registry_class,
            test_package=test_package,
            expected_registry=expected_registry,
            url_fragment=url_fragment,
        )
    else:
        content = template.format(
            registry_name=registry_name,
            registry_title=registry_title,
            registry_class=registry_class,
            test_package=test_package,
            expected_registry=expected_registry,
            url_fragment=url_fragment,
        )

    filename = f"tests/registries/test_{registry_name}.py"
    with open(filename, "w") as f:
        f.write(content)
    print(f"Generated {filename}")


if __name__ == "__main__":
    for registry_name, test_package, expected_registry, url_fragment in registries:
        generate_test_file(registry_name, test_package, expected_registry, url_fragment)
    print("All registry test files generated!")
