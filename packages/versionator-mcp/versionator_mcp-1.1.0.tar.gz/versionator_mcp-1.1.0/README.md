# Versionator MCP Server

[![CI Pipeline](https://github.com/trianglegrrl/versionator-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/trianglegrrl/versionator-mcp/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/versionator-mcp.svg)](https://badge.fury.io/py/versionator-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

An MCP (Model Context Protocol) server that queries package registries across 11 different ecosystems to retrieve the latest release versions of packages. It follows a strict fail-hard policy and always returns current data.

## Features

- **11 Package Registries**: npm, RubyGems, PyPI, Hex.pm, crates.io, Bioconda, CRAN, Terraform Registry, DockerHub, CPAN, Go modules
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

## Performance Considerations

- **No Caching**: Each call makes a fresh API request
- **Timeout**: Configurable via `VERSIONATOR_REQUEST_TIMEOUT`
- **Concurrent Requests**: Async implementation allows parallel queries
- **Rate Limits**: Be mindful of registry rate limits

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

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