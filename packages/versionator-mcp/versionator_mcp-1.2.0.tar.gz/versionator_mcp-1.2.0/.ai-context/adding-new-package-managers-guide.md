# Adding New Package Managers to Versionator-MCP

## Quick Reference Guide

This document provides a step-by-step process for adding new package managers to the versionator-mcp project, following the proven TDD methodology established in v1.1.0.

## Prerequisites

- Python 3.10+
- All existing tests passing
- All linting checks passing (black, isort, mypy)
- Understanding of the target package manager's API

## Step-by-Step Process

### 1. **Investigation Phase**
- Research the package manager's public API
- Identify the correct endpoint for package version queries
- Test API manually with popular packages
- Document API response format and required parameters
- Note any authentication, rate limiting, or special headers needed

### 2. **Test-Driven Development (TDD)**

#### 2.1 Write Failing Tests
Create tests in `tests/test_api.py` following this pattern:

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
    with pytest.raises(Exception, match="Package .* not found"):
        await get_{registry}_version("nonexistent-package-12345")

@pytest.mark.asyncio
async def test_get_{registry}_version_empty_name():
    """Test {registry} with empty package name"""
    with pytest.raises(ValueError, match="Package name cannot be empty"):
        await get_{registry}_version("")
```

#### 2.2 Red Phase - Confirm Tests Fail
```bash
pytest tests/test_api.py::test_get_{registry}_version_success -v
# Should fail with ImportError or similar
```

#### 2.3 Green Phase - Implement Function
Add function to `versionator_mcp/api/versionator.py`:

```python
async def get_{registry}_version(package_name: str) -> PackageVersion:
    """Get the latest version of a package from {Registry}."""
    if not package_name or not package_name.strip():
        raise ValueError("Package name cannot be empty")
    
    package_name = package_name.strip()
    
    async with aiohttp.ClientSession() as session:
        url = f"https://api.{registry}.com/packages/{package_name}"
        
        async with session.get(url) as response:
            if response.status == 404:
                raise Exception(f"Package '{package_name}' not found in {registry}")
            elif response.status != 200:
                raise Exception(f"Failed to fetch package info: HTTP {response.status}")
            
            data = await response.json()
            
            return PackageVersion(
                name=package_name,
                version=data["version"],  # Adjust based on API response
                description=data.get("description", ""),
                homepage=data.get("homepage", ""),
                registry="{registry}",
                registry_url=url
            )
```

#### 2.4 Refactor Phase - Clean Up Code
- Ensure consistent error handling
- Add proper type hints
- Follow existing code patterns
- Optimize for readability and maintainability

### 3. **Integration Testing**

#### 3.1 Update Generic Function
Add registry mappings to `get_latest_version`:

```python
registry_map = {
    # ... existing registries ...
    "{registry}": get_{registry}_version,
    "{alias1}": get_{registry}_version,
    "{alias2}": get_{registry}_version,
}
```

#### 3.2 Test Generic Function
Add test for new registry in `test_get_latest_version_new_registries`:

```python
# Test {registry}
result = await get_latest_version("{registry}", "{popular_package}")
assert result.registry == "{registry}"
```

### 4. **FastMCP Tool Registration**

Add MCP tool in `register_versionator_api`:

```python
@app.tool()
async def get_{registry}_package(package_name: str) -> Dict[str, Any]:
    """Get the latest version of a package from {Registry}."""
    try:
        result = await get_{registry}_version(package_name)
        return result.model_dump()
    except Exception as e:
        return {"error": str(e)}
```

### 5. **Validation with vmcp**

Test the new registry with the vmcp client:

```bash
./vmcp {registry} {popular_package}
# Should return version information successfully
```

### 6. **Quality Assurance**

#### 6.1 Run All Tests
```bash
pytest tests/ -v
# ALL tests must pass - no exceptions
```

#### 6.2 Run Linting
```bash
black --check .
isort --check-only .
mypy versionator_mcp/
# ALL linting must pass - no exceptions
```

### 7. **Documentation Updates**

Update the following files:
- `README.md` - Add new registry to supported list
- `versionator_mcp/app.py` - Update logging messages
- Function docstrings - Include new registry in examples

### 8. **Release Preparation**

- Update version in `pyproject.toml`
- Update changelog
- Commit all changes
- Run final test suite
- Tag and release

## Critical Success Criteria

**A package manager integration is ONLY considered complete when:**

1. ✅ **All Tests Pass** - No failing tests anywhere in the codebase
2. ✅ **All Linting Passes** - Black, isort, mypy all clean
3. ✅ **Popular Package Verified** - Can query a well-known package successfully
4. ✅ **vmcp Integration Works** - Manual testing with vmcp succeeds
5. ✅ **Error Handling Complete** - Proper exceptions for all failure modes
6. ✅ **Generic Function Updated** - Works through `get_latest_version`
7. ✅ **MCP Tool Registered** - Available as FastMCP tool

## Fail-Hard Policy

**NON-NEGOTIABLE REQUIREMENTS:**

- ❌ **NO** try/catch blocks that suppress errors with just logging
- ❌ **NO** fallback values when operations should fail
- ❌ **NO** changing test assertions to make them pass
- ❌ **NO** removing or commenting out failing tests
- ✅ **YES** throw meaningful exceptions with context
- ✅ **YES** fail fast when preconditions aren't met
- ✅ **YES** preserve error information for debugging

## Common Patterns

### API Response Handling
```python
# Always check status codes
if response.status == 404:
    raise Exception(f"Package '{package_name}' not found in {registry}")
elif response.status != 200:
    raise Exception(f"Failed to fetch package info: HTTP {response.status}")

# Extract version from various response formats
version = data.get("version") or data.get("latest_version") or data["releases"][-1]
```

### Input Validation
```python
if not package_name or not package_name.strip():
    raise ValueError("Package name cannot be empty")

package_name = package_name.strip()
```

### URL Construction
```python
# Handle special cases like vendor/package format
if "/" in package_name:
    vendor, package = package_name.split("/", 1)
    url = f"https://api.registry.com/packages/{vendor}/{package}"
else:
    url = f"https://api.registry.com/packages/{package_name}"
```

## Testing Strategy

### Use Real Packages for Success Tests
- Choose stable, popular packages that won't disappear
- Examples: `react` (npm), `rails` (rubygems), `django` (pypi)

### Use Obviously Invalid Names for Error Tests
- Use names like `nonexistent-package-12345`
- Avoid names that might accidentally exist

### Mock Only When Necessary
- Prefer real API calls for integration testing
- Mock only for error conditions that are hard to trigger

## This Process Works

This methodology successfully delivered v1.1.0 with 7 new package managers:
- 37 comprehensive tests - all passing ✅
- Zero breaking changes
- Consistent API across all registries
- Robust error handling
- Full vmcp integration

Following this process ensures quality, reliability, and maintainability for all new package manager integrations.
