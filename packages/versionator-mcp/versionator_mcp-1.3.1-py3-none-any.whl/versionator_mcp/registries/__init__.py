"""
Package registry implementations for Versionator MCP Server
"""

# Import all registries to trigger registration
from . import (
    bioconda,
    composer,
    cpan,
    cran,
    crates,
    dockerhub,
    go,
    hex,
    homebrew,
    maven,
    nextflow,
    nfcore,
    npm,
    nuget,
    pypi,
    rubygems,
    swift,
    terraform,
)

__all__ = [
    "npm",
    "rubygems",
    "pypi",
    "hex",
    "crates",
    "bioconda",
    "cran",
    "terraform",
    "dockerhub",
    "cpan",
    "go",
    "composer",
    "nuget",
    "homebrew",
    "nextflow",
    "nfcore",
    "swift",
    "maven",
]
