# Versionator MCP Server

[![CI Pipeline](https://github.com/trianglegrrl/versionator-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/trianglegrrl/versionator-mcp/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/versionator-mcp.svg)](https://badge.fury.io/py/versionator-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

An MCP (Model Context Protocol) server that queries package registries across 19 different ecosystems to retrieve the latest release versions of packages. It follows a strict fail-hard policy and always returns current data.

## Features

- **19 Package Registries**: npm, RubyGems, PyPI, Hex.pm, crates.io, Bioconda, CRAN, Terraform Registry, DockerHub, CPAN, Go modules, Composer, NuGet, Homebrew, Nextflow, nf-core modules, nf-core subworkflows, Swift Package Manager, Maven Central
- **Language/Ecosystem Aliases**: Use familiar names like `python`, `rust`, `go`, etc.
- **No Caching**: Always returns current latest version
- **Fail-Hard Error Handling**: No fallbacks or stale data
- **Rich Metadata**: Package descriptions, homepages, and license information
- **Configurable Timeouts**: Adjust API request timeouts as needed
- **Test Client Included**: `vmcp` command-line tool for testing and manual queries
- **Optimized for Claude Desktop Integration**

## Quick Start

### Option 1: Using uvx (Recommended)

The easiest way to use Versionator with Claude Desktop is via [uvx](https://github.com/astral-sh/uv):

```bash
# Install uvx if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run Versionator directly with uvx
uvx versionator-mcp
```

### Option 2: Install Locally

```bash
# Install from PyPI
pip install versionator-mcp

# Or install with pipx for isolated environment
pipx install versionator-mcp
```

## Editor Integration

### Claude Desktop

Add configuration to your Claude Desktop MCP settings:

**Config Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Recommended (uvx):**
```json
{
  "mcpServers": {
    "versionator": {
      "command": "uvx",
      "args": ["versionator-mcp"]
    }
  }
}
```

**Alternative methods:**
```json
{
  "mcpServers": {
    "versionator": {
      "command": "pipx",
      "args": ["run", "versionator-mcp"]
    }
  }
}
```

### Cursor

Create `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "versionator": {
      "command": "uvx",
      "args": ["versionator-mcp"],
      "env": {
        "VERSIONATOR_REQUEST_TIMEOUT": "30"
      }
    }
  }
}
```

**Global configuration**: `~/.cursor/mcp.json`

**Pro Tip**: This repository includes a `.cursor/mcp.json` and `.cursor/rules` file that:
- Configures Versionator for immediate use
- Sets up rules to automatically check package versions before installations
- Ensures you always get current version information when working with dependencies

### Windsurf

Edit `~/.codeium/mcp_config.json`:

```json
{
  "mcpServers": {
    "versionator": {
      "command": "uvx",
      "args": ["versionator-mcp"]
    }
  }
}
```

**UI Method**: Settings → Tools → Windsurf Settings → Add Server

### Claude Code

Add to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "versionator": {
      "command": "uvx",
      "args": ["versionator-mcp"]
    }
  }
}
```

> 📁 **Example configs**: See [`examples/`](examples/) directory for complete configuration files

## Available Functions

### 1. `get_package_version` - Universal Package Version Query

Query the latest version from any supported registry.

**Parameters:**
- `package_manager` (str): Registry name or alias
- `package_name` (str): Name of the package

**Supported Registries:**
- `npm` (aliases: `node`, `nodejs`) - Node.js packages
- `rubygems` (aliases: `gem`, `ruby`) - Ruby gems
- `pypi` (aliases: `pip`, `python`) - Python packages
- `hex` (aliases: `elixir`, `hex.pm`) - Elixir packages
- `crates` (aliases: `cargo`, `rust`) - Rust crates
- `bioconda` (aliases: `conda`) - Bioconda packages
- `cran` (aliases: `r`) - R packages
- `terraform` (aliases: `tf`) - Terraform providers
- `dockerhub` (aliases: `docker`) - Docker images
- `cpan` (aliases: `perl`) - Perl modules
- `go` (aliases: `golang`) - Go modules
- `composer` (aliases: `php`, `packagist`) - PHP packages
- `nuget` (aliases: `dotnet`, `.net`) - .NET packages
- `homebrew` (aliases: `brew`) - macOS packages
- `nextflow` (aliases: `nf-core`) - Nextflow pipelines
- `nf-core-module` (aliases: `nfcore-module`, `nf-module`) - nf-core modules
- `nf-core-subworkflow` (aliases: `nfcore-subworkflow`, `nf-subworkflow`) - nf-core subworkflows
- `swift` (aliases: `spm`) - Swift packages
- `maven` (aliases: `mvn`) - Java artifacts

**Examples:**
```python
# Query npm package
get_package_version("npm", "react")
# Returns: {"name": "react", "version": "19.1.1", ...}

# Query with aliases
get_package_version("python", "django")
get_package_version("rust", "serde")
get_package_version("go", "github.com/gin-gonic/gin")
get_package_version("terraform", "hashicorp/aws")
get_package_version("docker", "nginx")
get_package_version("r", "ggplot2")
get_package_version("php", "symfony/console")
get_package_version("dotnet", "Newtonsoft.Json")
get_package_version("homebrew", "git")
get_package_version("nextflow", "nf-core/rnaseq")
get_package_version("nf-core-module", "fastqc")
get_package_version("nf-core-subworkflow", "bam_sort_stats_samtools")
get_package_version("swift", "apple/swift-package-manager")
get_package_version("maven", "org.springframework:spring-core")
```

### 2. Registry-Specific Functions

- `get_npm_package(package_name)` - NPM packages
- `get_ruby_gem(gem_name)` - RubyGems packages
- `get_python_package(package_name)` - PyPI packages
- `get_elixir_package(package_name)` - Hex.pm packages
- `get_rust_crate(crate_name)` - Rust crates
- `get_bioconda_package(package_name)` - Bioconda packages
- `get_r_package(package_name)` - R packages
- `get_terraform_provider(provider_path)` - Terraform providers
- `get_docker_image(image_name)` - Docker images
- `get_perl_module(module_name)` - Perl modules
- `get_go_module(module_path)` - Go modules
- `get_php_package(package_name)` - PHP/Composer packages
- `get_dotnet_package(package_name)` - .NET/NuGet packages
- `get_homebrew_formula(formula_name)` - Homebrew formulas
- `get_nextflow_pipeline(pipeline_name)` - Nextflow pipelines
- `get_nfcore_module(module_name)` - nf-core modules
- `get_nfcore_subworkflow(subworkflow_name)` - nf-core subworkflows
- `get_swift_package(package_name)` - Swift packages
- `get_maven_artifact(artifact_name)` - Maven artifacts

## Response Format

All functions return a PackageVersion object:

```json
{
  "name": "react",
  "version": "19.1.1",
  "registry": "npm",
  "registry_url": "https://registry.npmjs.org/react/latest",
  "query_time": "2025-08-13T10:30:00Z",
  "description": "React is a JavaScript library for building user interfaces.",
  "homepage": "https://react.dev/",
  "license": "MIT"
}
```

## Testing with vmcp

The project includes a command-line test client called `vmcp` for manual testing and verification:

### Installation and Usage

```bash
# Make the vmcp script executable (if needed)
chmod +x vmcp

# Query packages from different registries
./vmcp python pandas          # Query PyPI for pandas
./vmcp npm react              # Query npm for react
./vmcp rust serde             # Query crates.io for serde
./vmcp go github.com/gin-gonic/gin  # Query Go modules
./vmcp terraform hashicorp/aws      # Query Terraform registry
./vmcp docker nginx           # Query DockerHub
./vmcp perl JSON              # Query CPAN
./vmcp r ggplot2              # Query CRAN
./vmcp bioconda samtools      # Query Bioconda
./vmcp php symfony/console    # Query Packagist for PHP packages
./vmcp dotnet Newtonsoft.Json # Query NuGet for .NET packages
./vmcp homebrew git           # Query Homebrew formulas
./vmcp nextflow nf-core/rnaseq # Query Nextflow pipelines
./vmcp nf-core-module fastqc  # Query nf-core modules
./vmcp nf-core-subworkflow bam_sort_stats_samtools # Query nf-core subworkflows
./vmcp swift apple/swift-package-manager # Query Swift packages
./vmcp maven org.springframework:spring-core # Query Maven Central

# List all available MCP tools
./vmcp --list-tools

# Check server health
./vmcp --health
```

### Example Output

```bash
$ ./vmcp rust serde
🔍 Querying rust/serde...
✅ serde @ v1.0.215 (crates)
   📝 A generic serialization/deserialization framework
   🏠 https://serde.rs
```

The `vmcp` client is particularly useful for:
- **Testing your MCP setup** before integrating with editors
- **Verifying package queries** work correctly
- **Debugging connection issues** with the MCP server
- **Exploring available tools** and their capabilities

## Error Handling

The server follows a strict **FAIL HARD** policy:

- **No Fallbacks**: Never returns cached or default values
- **No Suppression**: All errors propagate to the caller
- **Clear Messages**: Errors include context and details
- **Input Validation**: Validates before making API calls

Common errors:
- `ValueError`: Invalid package name or unknown package manager
- `Exception`: Package not found or API failures

## Configuration

Environment variables (optional):

- `VERSIONATOR_REQUEST_TIMEOUT`: API request timeout in seconds (default: 30)

## Troubleshooting

### Common MCP Issues

1. **Server not starting**: Check that the command path is correct in your configuration
2. **Permission errors**: Ensure the Python executable has proper permissions
3. **Package not found**: Verify the package is installed and accessible from the command line
4. **Editor not detecting server**: Restart your editor after adding MCP configuration

### Testing Your Setup

You can test the server directly from the command line:

```bash
# Test with uvx
uvx versionator-mcp

# Test with pipx
pipx run versionator-mcp

# Test direct installation
python -m versionator_mcp.main
```

The server should start and show initialization messages. Press `Ctrl+C` to stop.

## Alternative: HTTP Server Mode

For advanced use cases, you can run Versionator as an HTTP server:

```bash
# Start HTTP server (default port 8083)
FASTMCP_PORT=8083 python -m versionator_mcp.main

# Custom port
FASTMCP_PORT=9000 python -m versionator_mcp.main
```

Then configure Claude Desktop with:

```json
{
  "mcpServers": {
    "versionator": {
      "url": "http://localhost:8083/mcp",
      "transport": "http"
    }
  }
}
```

**Note**: HTTP mode requires manually starting the server before using Claude Desktop.

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/trianglegrrl/versionator-mcp.git
cd versionator-mcp

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Project Structure

The project follows a clean, modular architecture:

```
versionator_mcp/
├── __init__.py
├── app.py                    # FastMCP app factory and configuration
├── config.py                 # Environment configuration management
├── main.py                   # Entry point for the MCP server
├── models.py                 # Pydantic data models
├── core/                     # Core utilities and base classes
│   ├── __init__.py
│   ├── base_registry.py      # Abstract base class for registries
│   ├── http_client.py        # Shared HTTP client utilities
│   └── registry_factory.py   # Registry factory and mapping
├── registries/               # Individual registry implementations
│   ├── __init__.py
│   ├── npm.py               # NPM registry
│   ├── rubygems.py          # RubyGems registry
│   ├── pypi.py              # PyPI registry
│   ├── hex.py               # Hex.pm registry
│   ├── crates.py            # Crates.io registry
│   ├── bioconda.py          # Bioconda registry
│   ├── cran.py              # CRAN registry
│   ├── terraform.py         # Terraform registry
│   ├── dockerhub.py         # DockerHub registry
│   ├── cpan.py              # CPAN registry
│   ├── go.py                # Go modules registry
│   ├── composer.py          # PHP Composer registry
│   ├── nuget.py             # NuGet registry
│   ├── homebrew.py          # Homebrew registry
│   ├── nextflow.py          # Nextflow registry
│   ├── nfcore.py            # nf-core modules/subworkflows
│   ├── swift.py             # Swift Package Manager
│   └── maven.py             # Maven Central
└── tools/                   # MCP tool registration
    ├── __init__.py
    └── registry_tools.py     # MCP tool definitions
```

### Architecture Benefits

- **Modular Design**: Each registry is implemented in its own file with a consistent interface
- **Single Responsibility**: Each module has a clear, focused purpose
- **Easy Extension**: Adding new registries requires minimal changes to existing code
- **Testability**: Individual registries can be tested in isolation
- **Maintainability**: Changes to one registry don't affect others
- **DRY Principle**: Common HTTP logic is shared across all registries

### Adding New Registries

To add support for a new package registry:

1. **Create Registry Implementation**: Create a new file in `versionator_mcp/registries/` (e.g., `new_registry.py`)
2. **Extend BaseRegistry**: Implement the abstract methods from `BaseRegistry`
3. **Register with Factory**: Call `register_registry()` with your class and aliases
4. **Add MCP Tool**: Add corresponding tool function in `registry_tools.py`

Example:

```python
# versionator_mcp/registries/new_registry.py
from ..core import BaseRegistry, register_registry
from ..models import PackageVersion

class NewRegistry(BaseRegistry):
    @property
    def registry_name(self) -> str:
        return "new_registry"

    async def get_latest_version(self, package_name: str) -> PackageVersion:
        package_name = self.validate_package_name(package_name)
        url = f"https://api.new-registry.com/packages/{package_name}"

        data = await self.http_client.get_json(url, registry_name="NewRegistry", package_name=package_name)

        return PackageVersion(
            name=package_name,
            version=data.get("version", "unknown"),
            registry="new_registry",
            registry_url=url,
            query_time=self.http_client.get_current_timestamp(),
            description=data.get("description"),
            homepage=data.get("homepage"),
            license=data.get("license"),
        )

# Register with aliases
register_registry(NewRegistry, ["new", "nr"])
```

### Pre-commit Hooks (Recommended)

This project uses pre-commit hooks to ensure code quality and prevent issues:

```bash
# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type pre-push

# Run hooks manually on all files
pre-commit run --all-files
```

**Pre-commit hooks** (run on `git commit`):
- Trailing whitespace removal, end-of-file fixing, YAML validation
- Large file detection, merge conflict detection, debug statement detection
- **Black** code formatting, **isort** import sorting, **mypy** type checking

**Pre-push hooks** (run on `git push`):
- **pytest** test suite (skips GitHub API tests to avoid rate limits)

The hooks automatically fix formatting issues when possible and prevent commits/pushes that don't meet quality standards.

### Running Tests

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=versionator_mcp

# Run linting
black --check .
isort --check-only .
mypy versionator_mcp/
```

### Testing the MCP Server

```bash
# Test stdio transport (default)
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python -m versionator_mcp.main
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the test suite (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Registry APIs

The server queries these endpoints:

- **npm**: `https://registry.npmjs.org/{package}/latest`
- **RubyGems**: `https://rubygems.org/api/v1/versions/{gem}/latest.json`
- **PyPI**: `https://pypi.org/pypi/{package}/json`
- **Hex.pm**: `https://hex.pm/api/packages/{package}`
- **crates.io**: `https://crates.io/api/v1/crates/{crate}`
- **Bioconda**: `https://api.anaconda.org/package/bioconda/{package}`
- **CRAN**: `https://crandb.r-pkg.org/{package}`
- **Terraform**: `https://registry.terraform.io/v1/providers/{provider_path}`
- **DockerHub**: `https://hub.docker.com/v2/repositories/{namespace}/{repo}/tags`
- **CPAN**: `https://fastapi.metacpan.org/v1/module/{module}`
- **Go Modules**: `https://api.github.com/repos/{owner}/{repo}/releases/latest` (GitHub-hosted)
- **Composer**: `https://packagist.org/packages/{vendor}/{package}.json`
- **NuGet**: `https://api.nuget.org/v3-flatcontainer/{package}/index.json`
- **Homebrew**: `https://formulae.brew.sh/api/formula/{formula}.json`
- **Nextflow**: `https://api.github.com/repos/nf-core/{pipeline}/releases/latest`
- **nf-core modules**: `https://api.github.com/repos/nf-core/modules/commits?path=modules/nf-core/{module}`
- **nf-core subworkflows**: `https://api.github.com/repos/nf-core/modules/commits?path=subworkflows/nf-core/{subworkflow}`
- **Swift**: `https://api.github.com/repos/{owner}/{repo}/releases/latest`
- **Maven**: `https://search.maven.org/solrsearch/select?q=g:{group}+AND+a:{artifact}`

## Performance Considerations

- **No Caching**: Each call makes a fresh API request
- **Timeout**: Configurable via `VERSIONATOR_REQUEST_TIMEOUT`
- **Concurrent Requests**: Async implementation allows parallel queries
- **Rate Limits**: Be mindful of registry rate limits

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.3.0 (Refactored Architecture & Type Safety)
- **REFACTORED**: Complete codebase restructure for improved maintainability
- **NEW**: Modular registry architecture with individual files for each package manager
- **NEW**: Abstract base class pattern for consistent registry implementations
- **NEW**: Factory pattern for registry management and discovery
- **NEW**: Shared HTTP client utilities to eliminate code duplication
- **NEW**: Modular test structure mirroring the main codebase organization
- **IMPROVED**: 100% type safety compliance - zero mypy errors across 30 source files
- **IMPROVED**: Enhanced type annotations throughout the entire codebase
- **IMPROVED**: HTTP client return type flexibility for diverse API responses
- **IMPROVED**: Proper forward reference handling for type checking
- **IMPROVED**: Registry factory type safety with Optional parameter handling
- **IMPROVED**: Separation of concerns - MCP tools, registries, and core utilities
- **IMPROVED**: Easy extensibility - adding new registries requires minimal code changes
- **IMPROVED**: Better testability with isolated registry implementations
- **IMPROVED**: Consistent error handling across all registries
- **IMPROVED**: Developer experience with clear project structure and full IDE type support
- **MAINTAINED**: Full backward compatibility - all existing functionality preserved
- **MAINTAINED**: All 19 package registries with identical behavior
- **MAINTAINED**: Complete MCP tool compatibility
- **QUALITY**: 56 comprehensive tests passing with 6 appropriately skipped in CI
- **QUALITY**: Organized test structure with individual files per registry

### v1.2.3
- **FIXED**: GitHub API rate limit issues in CI by skipping GitHub-dependent tests
- **IMPROVED**: CI reliability - 47 tests pass, 15 appropriately skipped in CI environment
- **ENHANCED**: Maintains full test coverage locally while ensuring green CI builds
- **QUALITY**: Resolves PyPI publish workflow failures caused by rate limiting
- All features from v1.2.2 included with CI reliability improvements

### v1.2.2
- **FIXED**: Black code formatting compliance for nf-core functions
- **IMPROVED**: CI/CD pipeline reliability with direct test execution in publish workflow
- **ENHANCED**: Eliminated race condition between CI status checking and PyPI publish
- All features from v1.2.1 included with formatting fixes

### v1.2.1
- **NEW**: Added support for nf-core modules and subworkflows:
  - **nf-core modules** - `nf-core-module`, `nfcore-module`, `nf-module`
  - **nf-core subworkflows** - `nf-core-subworkflow`, `nfcore-subworkflow`, `nf-subworkflow`
- **NEW**: Registry-specific MCP tools:
  - `get_nfcore_module(module_name)` for nf-core modules
  - `get_nfcore_subworkflow(subworkflow_name)` for nf-core subworkflows
- **IMPROVED**: Enhanced Nextflow ecosystem coverage for scientific computing
- **IMPROVED**: Updated documentation with nf-core module/subworkflow examples
- **QUALITY**: 62 comprehensive tests - all passing ✅
- **QUALITY**: Full backward compatibility maintained

### v1.2.0
- **NEW**: Added support for 6 additional package registries:
  - PHP Composer (Packagist) - `composer`, `php`, `packagist`
  - .NET NuGet - `nuget`, `dotnet`, `.net`
  - Homebrew - `homebrew`, `brew`
  - Nextflow (nf-core) - `nextflow`, `nf-core`
  - Swift Package Manager - `swift`, `spm`
  - Maven Central - `maven`, `mvn`
- **NEW**: Registry-specific MCP tools for all new package managers
- **IMPROVED**: Enhanced vmcp test client with examples for all 17 registries
- **IMPROVED**: Comprehensive documentation updates with new API endpoints
- **IMPROVED**: Updated error messages and validation for new registries
- **QUALITY**: 56 comprehensive tests - all passing ✅
- **QUALITY**: Full backward compatibility maintained

### v1.1.0
- **NEW**: Added support for 7 additional package registries:
  - Rust (crates.io) - `rust`, `cargo`, `crates`
  - Bioconda (anaconda.org) - `bioconda`, `conda`
  - R (CRAN) - `r`, `cran`
  - Terraform Registry - `terraform`, `tf`
  - DockerHub - `docker`, `dockerhub`
  - Perl (CPAN) - `perl`, `cpan`
  - Go Modules - `go`, `golang`
- **NEW**: Added `vmcp` command-line test client
- **NEW**: Registry-specific MCP tools for each package manager
- **IMPROVED**: Enhanced documentation with comprehensive examples
- **IMPROVED**: Updated error messages and validation

### v1.0.0
- Initial release
- Support for npm, RubyGems, PyPI, and Hex.pm
- Optimized for Claude Desktop integration
- uvx and pipx support
- Comprehensive error handling
- MCP protocol compliance
