# Package Manager Integration Plan

## Executive Summary

This plan outlines the Test-Driven Development (TDD) approach to integrate support for Perl (CPAN), Rust (crates.io), Go (Go modules), Bioconda, Terraform Registry, DockerHub, and R (CRAN) into the versionator-mcp project.

## Repository Analysis Results

### Current Architecture
- **Framework**: FastMCP-based MCP server
- **Language**: Python 3.10+
- **Dependencies**: fastmcp>=2.11.3, aiohttp>=3.8.0, pydantic>=2.0.0
- **Testing**: pytest with asyncio support
- **Structure**: Modular design with separate API functions in `versionator_mcp/api/versionator.py`

### Existing Patterns
1. **API Function Pattern**: Each registry has a dedicated async function (e.g., `get_npm_version`)
2. **Generic Function**: `get_latest_version` with registry mapping and aliases
3. **Model-Based Response**: Uses `PackageVersion` Pydantic model for consistent responses
4. **Error Handling**: Fail-hard approach with meaningful exceptions
5. **Tool Registration**: FastMCP `@app.tool()` decorators for MCP exposure

### Current Registry Support
- npm (with aliases: node, nodejs)
- RubyGems (with aliases: gem, ruby)
- PyPI (with aliases: pip, python)
- Hex.pm (with aliases: elixir, hex.pm)

## API Research Results

### 1. Perl (CPAN via MetaCPAN)
- **API**: `https://fastapi.metacpan.org/v1/release/{package_name}`
- **Status**: Robots.txt blocks automated access - need alternative approach
- **Alternative**: `https://metacpan.org/pod/{package_name}` or search API
- **Popular Package**: `JSON`, `DBI`, `Moose`
- **Response Format**: JSON with version, author, description

### 2. Rust (crates.io)
- **API**: `https://crates.io/api/v1/crates/{crate_name}`
- **Status**: ✅ Working - returns JSON with crate metadata
- **Popular Package**: `serde`, `tokio`, `clap`
- **Response Format**: JSON with `crate.newest_version` field

### 3. Go (Go Proxy)
- **API**: `https://proxy.golang.org/{module_path}/@latest`
- **Status**: Robots.txt blocks automated access - need alternative
- **Alternative**: `https://pkg.go.dev/{module_path}` scraping or `https://api.pkg.go.dev/`
- **Popular Package**: `github.com/gin-gonic/gin`, `github.com/gorilla/mux`
- **Response Format**: JSON with version info

### 4. Bioconda (Anaconda.org API)
- **API**: `https://api.anaconda.org/package/bioconda/{package_name}`
- **Status**: ✅ Working - returns JSON with package metadata
- **Popular Package**: `samtools`, `bwa`, `blast`
- **Response Format**: JSON with `latest_version` field

### 5. Terraform Registry
- **API**: `https://registry.terraform.io/v1/providers/{namespace}/{name}`
- **Status**: ✅ Working - returns JSON with provider metadata
- **Popular Package**: `hashicorp/aws`, `hashicorp/azurerm`
- **Response Format**: JSON with `version` field (latest)

### 6. DockerHub
- **API**: `https://hub.docker.com/v2/repositories/{namespace}/{name}/tags`
- **Status**: ✅ Working - returns JSON with tag list
- **Popular Package**: `nginx`, `redis`, `postgres`
- **Response Format**: JSON with `results[0].name` for latest tag

### 7. R (CRAN via crandb)
- **API**: `https://crandb.r-pkg.org/{package_name}`
- **Status**: ✅ Working - returns JSON with package metadata
- **Popular Package**: `ggplot2`, `dplyr`, `shiny`
- **Response Format**: JSON with `Version` field

## Implementation Strategy

### Phase 1: Core Infrastructure (COMPLETED)
- ✅ Repository analysis
- ✅ API research and validation
- ✅ Plan creation

### Phase 2: TDD Implementation

#### 2.1 Test Structure
Each package manager will follow this test pattern:
```python
@pytest.mark.asyncio
async def test_get_{registry}_version_success():
    """Test successful {registry} version retrieval"""
    result = await get_{registry}_version("{popular_package}")
    assert result.name == "{popular_package}"
    assert result.version is not None
    assert result.registry == "{registry}"
    assert "{registry_domain}" in result.registry_url

@pytest.mark.asyncio
async def test_get_{registry}_version_not_found():
    """Test {registry} package not found"""
    with pytest.raises(Exception, match="Package 'nonexistent' not found"):
        await get_{registry}_version("nonexistent")

@pytest.mark.asyncio
async def test_get_{registry}_version_empty_name():
    """Test {registry} with empty package name"""
    with pytest.raises(ValueError, match="Package name cannot be empty"):
        await get_{registry}_version("")
```

#### 2.2 Implementation Order
1. **Perl (CPAN)** - Use MetaCPAN search API as fallback
2. **Rust (crates.io)** - Direct API integration
3. **Go (Go modules)** - Use pkg.go.dev API
4. **Bioconda** - Direct Anaconda API integration
5. **Terraform** - Direct registry API integration
6. **DockerHub** - Direct Hub API integration
7. **R (CRAN)** - Direct crandb API integration

#### 2.3 Function Signatures
```python
async def get_cpan_version(package_name: str) -> PackageVersion
async def get_crates_version(crate_name: str) -> PackageVersion
async def get_go_version(module_path: str) -> PackageVersion
async def get_bioconda_version(package_name: str) -> PackageVersion
async def get_terraform_version(provider_path: str) -> PackageVersion
async def get_dockerhub_version(image_name: str) -> PackageVersion
async def get_cran_version(package_name: str) -> PackageVersion
```

### Phase 3: Registry Mapping Extension

Update `get_latest_version` function to include new registries:
```python
registry_map = {
    # Existing...
    "cpan": get_cpan_version,
    "perl": get_cpan_version,
    "crates": get_crates_version,
    "cargo": get_crates_version,
    "rust": get_crates_version,
    "go": get_go_version,
    "golang": get_go_version,
    "bioconda": get_bioconda_version,
    "conda": get_bioconda_version,
    "terraform": get_terraform_version,
    "tf": get_terraform_version,
    "dockerhub": get_dockerhub_version,
    "docker": get_dockerhub_version,
    "cran": get_cran_version,
    "r": get_cran_version,
}
```

### Phase 4: FastMCP Tool Registration

Add new tools to `register_versionator_api`:
```python
@app.tool()
async def get_perl_package(package_name: str) -> Dict[str, Any]:
    """Get the latest version of a Perl package from CPAN."""

@app.tool()
async def get_rust_crate(crate_name: str) -> Dict[str, Any]:
    """Get the latest version of a Rust crate from crates.io."""

# ... similar for other registries
```

## File Organization Plan

### New Files (Following Single Responsibility Principle)
- `versionator_mcp/api/cpan.py` - CPAN-specific API functions
- `versionator_mcp/api/crates.py` - crates.io-specific API functions
- `versionator_mcp/api/golang.py` - Go modules-specific API functions
- `versionator_mcp/api/bioconda.py` - Bioconda-specific API functions
- `versionator_mcp/api/terraform.py` - Terraform Registry-specific API functions
- `versionator_mcp/api/dockerhub.py` - DockerHub-specific API functions
- `versionator_mcp/api/cran.py` - CRAN-specific API functions

### Modified Files
- `versionator_mcp/api/versionator.py` - Import and integrate new functions
- `tests/test_api.py` - Add comprehensive tests for all new registries

### Shared Utilities
- `versionator_mcp/api/utils.py` - Common HTTP client utilities, error handling

## Error Handling Strategy (Fail Hard Policy)

### Required Behaviors
1. **Throw Exceptions**: All API failures must raise meaningful exceptions
2. **No Fallbacks**: No default values or empty responses on failure
3. **Preserve Error Context**: Include registry name, package name, and HTTP status in exceptions
4. **Input Validation**: Fail fast on invalid/empty package names

### Exception Types
```python
class RegistryError(Exception):
    """Base exception for registry API errors"""
    pass

class PackageNotFoundError(RegistryError):
    """Package not found in registry"""
    pass

class RegistryUnavailableError(RegistryError):
    """Registry API is unavailable"""
    pass
```

## Testing Strategy

### Test Categories
1. **Success Cases**: Valid packages return correct metadata
2. **Not Found Cases**: Invalid packages raise appropriate exceptions
3. **Input Validation**: Empty/None inputs raise ValueError
4. **API Error Cases**: HTTP errors raise appropriate exceptions
5. **Integration Tests**: Generic `get_latest_version` function works with all registries

### Test Data
- Use real, stable packages for success tests
- Use clearly invalid names for not-found tests
- Mock HTTP responses for error condition testing

### Coverage Requirements
- 100% line coverage for new API functions
- All error paths must be tested
- All registry aliases must be tested

## Security Considerations

### Input Sanitization
- Validate package names against expected patterns
- Prevent injection attacks in URL construction
- Limit package name length to prevent DoS

### Rate Limiting
- Implement respectful request patterns
- Add delays between requests if needed
- Handle 429 (Too Many Requests) responses

### API Keys
- No API keys required for public registries
- Document any rate limits or usage policies

## Performance Optimization

### HTTP Client Reuse
- Use session pooling in aiohttp
- Implement connection timeouts
- Add retry logic for transient failures

### Caching Strategy
- Consider implementing response caching for frequently requested packages
- Use appropriate cache TTL based on registry update frequency

## Maintenance Considerations

### API Stability
- Monitor for API changes in external registries
- Implement version detection where possible
- Add logging for API response format changes

### Documentation
- Document all new functions with examples
- Update README with new registry support
- Provide troubleshooting guide for common issues

## Success Criteria

A registry integration is considered complete when:

1. ✅ **Failing Test Written**: Test fails before implementation
2. ✅ **Implementation Passes Test**: Function correctly queries registry API
3. ✅ **Popular Package Verified**: Can successfully query a well-known package
4. ✅ **Error Handling Works**: Appropriate exceptions for all failure modes
5. ✅ **Integration Complete**: Works through generic `get_latest_version` function
6. ✅ **FastMCP Tool Registered**: Available as MCP tool for clients

## Implementation Timeline

### Sprint 1: Core Infrastructure
- [ ] Create new API module files
- [ ] Implement shared utilities
- [ ] Set up test structure

### Sprint 2: Registry Implementation (Batch 1)
- [ ] Rust (crates.io) - Direct API
- [ ] Bioconda - Direct API
- [ ] R (CRAN) - Direct API

### Sprint 3: Registry Implementation (Batch 2)
- [ ] Terraform Registry - Direct API
- [ ] DockerHub - Direct API

### Sprint 4: Complex Registries
- [ ] Perl (CPAN) - Alternative API approach
- [ ] Go (modules) - Alternative API approach

### Sprint 5: Integration & Testing
- [ ] Update generic function
- [ ] Register FastMCP tools
- [ ] Comprehensive testing
- [ ] Documentation updates

## Risk Mitigation

### API Access Issues
- **Risk**: Some APIs block automated access
- **Mitigation**: Use alternative endpoints, implement proper User-Agent headers

### Rate Limiting
- **Risk**: APIs may rate limit requests
- **Mitigation**: Implement exponential backoff, respect rate limit headers

### API Changes
- **Risk**: External APIs may change without notice
- **Mitigation**: Comprehensive error handling, monitoring, graceful degradation

### Package Name Variations
- **Risk**: Different naming conventions across registries
- **Mitigation**: Clear documentation, input validation, helpful error messages

## Conclusion

This plan provides a comprehensive, systematic approach to integrating 7 new package managers into the versionator-mcp project using Test-Driven Development. The modular design ensures maintainability, the fail-hard policy ensures reliability, and the phased approach minimizes risk while delivering incremental value.

The implementation will follow SOLID principles, maintain separation of concerns, and provide a consistent interface for all supported package registries while respecting the unique characteristics of each ecosystem.
