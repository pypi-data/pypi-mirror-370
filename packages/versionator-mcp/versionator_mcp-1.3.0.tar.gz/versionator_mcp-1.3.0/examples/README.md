# MCP Configuration Examples

This directory contains example configuration files for integrating Versionator MCP with different editors and tools.

## Files

- **`cursor/mcp.json`** - Cursor IDE configuration (place in `.cursor/mcp.json`)
- **`windsurf/mcp_config.json`** - Windsurf IDE configuration (place in `~/.codeium/mcp_config.json`)
- **`claude-code/mcp_config.json`** - Claude Code configuration
- **`claude-desktop/claude_desktop_config.json`** - Claude Desktop configuration

## Usage

1. Copy the appropriate configuration file to the correct location for your editor
2. Ensure `versionator-mcp` is installed (`pip install versionator-mcp` or use `uvx`)
3. Restart your editor to load the MCP server

## Alternative Installation Methods

If you prefer not to use `uvx`, you can modify the configurations:

**Using pipx:**
```json
{
  "command": "pipx",
  "args": ["run", "versionator-mcp"]
}
```

**Direct Python:**
```json
{
  "command": "python",
  "args": ["-m", "versionator_mcp.main"]
}
```

**Virtual environment:**
```json
{
  "command": "/path/to/venv/bin/python",
  "args": ["-m", "versionator_mcp.main"]
}
```
