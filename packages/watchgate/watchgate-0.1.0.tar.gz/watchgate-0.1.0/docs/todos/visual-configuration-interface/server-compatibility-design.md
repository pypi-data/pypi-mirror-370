# Server Compatibility Design for Visual Configuration Interface

## Problem Statement

The Watchgate TUI needs to determine which security plugins are compatible with which MCP servers to provide an intuitive configuration experience. Our plugins fall into three categories:

1. **Universal plugins** that work with any MCP server (PII filter, secrets filter, prompt injection defense)
2. **Server-specific plugins** that only work with particular MCP servers (filesystem server security)
3. **Dynamic plugins** that work with any server but need server capabilities to configure properly (tool allowlist)

The challenge is enabling the TUI to automatically show only relevant plugins for each configured server without requiring users to understand these compatibility constraints.

## Solution: Python Class Attributes

We extend the existing `POLICIES`-based plugin system with optional class attributes that declare compatibility requirements. This approach leverages MCP servers' `serverInfo.name` field for identification during TUI configuration.

### Design Principles

1. **No breaking changes** - Existing plugin loading continues unchanged
2. **Optional declarations** - Plugins can add compatibility info incrementally  
3. **Simple semantics** - Presence/absence of attributes has clear meaning
4. **Exact matching only** - No pattern matching for v1 simplicity
5. **Server discovery** - TUI runs servers briefly to get identification info

## Implementation

### Universal Plugins (Default Behavior)

Plugins with no compatibility declaration work with all servers:

```python
class BasicPIIFilterPlugin(SecurityPlugin):
    """PII filter that works with any MCP server."""
    # No compatibility attributes = universal
    pass

POLICIES = {
    "pii": BasicPIIFilterPlugin
}
```

### Server-Specific Plugins

Plugins that only work with specific servers declare exact `serverInfo.name` values:

```python
class FilesystemServerSecurityPlugin(SecurityPlugin):
    """Security plugin specific to filesystem MCP servers."""
    
    COMPATIBLE_SERVERS = ["secure-filesystem-server"]
    
    # Plugin implementation...

POLICIES = {
    "filesystem_server": FilesystemServerSecurityPlugin
}
```

### Dynamic Configuration Plugins

Plugins that need server capabilities for configuration declare discovery requirements:

```python
class ToolAllowlistPlugin(SecurityPlugin):
    """Controls which tools can be accessed."""
    
    # Universal - works with any server
    # But needs tool list for configuration UI
    REQUIRES_DISCOVERY = ["tools"]
    
    # Plugin implementation...

POLICIES = {
    "tool_allowlist": ToolAllowlistPlugin
}
```

## Server Identification

The TUI identifies MCP servers by running them briefly during configuration and reading their `serverInfo.name` field:

```python
# Example server responses during initialization
{
    "@modelcontextprotocol/server-filesystem": {
        "serverInfo": {"name": "secure-filesystem-server", "version": "0.2.0"}
    },
    "mcp-server-sqlite-npx": {
        "serverInfo": {"name": "sqlite-manager", "version": "0.1.0"}  
    },
    "@modelcontextprotocol/server-github": {
        "serverInfo": {"name": "github-mcp-server", "version": "0.6.2"}
    }
}
```

## TUI Integration

### Plugin Discovery Flow

1. **Load all plugins** using existing discovery mechanism
2. **Check compatibility attributes** on each plugin class
3. **Categorize plugins** by compatibility requirements

```python
def discover_plugin_compatibility():
    """Discover all plugins and their compatibility info."""
    plugins = []
    
    for policy_name, plugin_class in discover_plugins().items():
        compatible_servers = getattr(plugin_class, 'COMPATIBLE_SERVERS', None)
        requires_discovery = getattr(plugin_class, 'REQUIRES_DISCOVERY', [])
        
        plugins.append({
            "policy": policy_name,
            "class": plugin_class,
            "is_universal": compatible_servers is None,
            "compatible_servers": compatible_servers or [],
            "requires_discovery": requires_discovery
        })
    
    return plugins
```

### Server-Plugin Matching

```python
def is_plugin_compatible(plugin_class, server_name):
    """Check if plugin is compatible with server."""
    compatible_servers = getattr(plugin_class, 'COMPATIBLE_SERVERS', None)
    # No declaration = universal compatibility
    return compatible_servers is None or server_name in compatible_servers
```

### Configuration UI Flow

1. **User adds MCP servers** (command + arguments)
2. **TUI runs servers** to get `serverInfo.name` 
3. **TUI shows compatible plugins** for each server
4. **For discovery plugins**, TUI fetches required info (tools, resources, etc.)
5. **User configures plugins** with server-aware context

### Visual Presentation

```
╭─ Security Configuration for: secure-filesystem-server ────╮
│                                                           │
│ Universal Security (all servers):                        │
│   ☑ PII Filter               [Configure]                │  
│   ☑ Secrets Filter           [Configure]                │
│   ☐ Prompt Injection Defense [Configure]                │
│                                                           │
│ Server-Specific:                                         │
│   ☑ Filesystem Security      [Configure]                │
│                                                           │
│ Tool Access Control:                                     │  
│   ☐ Tool Allowlist          [Configure]                 │
│     Available tools: read_file, write_file, list_dir    │
│                                                           │
╰───────────────────────────────────────────────────────────╯
```

## Implementation Plan

### Phase 1: Add Compatibility Attributes

Update existing plugins with compatibility declarations:

**watchgate/plugins/security/filesystem_server.py:**
```python
class FilesystemServerSecurityPlugin(SecurityPlugin):
    COMPATIBLE_SERVERS = ["secure-filesystem-server"]
    # ... existing implementation
```

**watchgate/plugins/security/tool_allowlist.py:**
```python
class ToolAllowlistPlugin(SecurityPlugin):
    REQUIRES_DISCOVERY = ["tools"] 
    # ... existing implementation
```

**Other plugins:** Leave unchanged (universal by default)

### Phase 2: TUI Server Discovery

Implement server identification in TUI:
- Start each configured MCP server temporarily
- Send `initialize` request to get `serverInfo`
- Cache server information for plugin matching
- Handle server startup failures gracefully

### Phase 3: Plugin-Server Matching

Integrate compatibility checking in TUI:
- Filter plugins based on server compatibility
- Group universal vs server-specific plugins in UI
- Enable discovery-dependent configuration only after server info is available

## Current Plugin Compatibility

Based on our existing plugins:

| Plugin | Type | Compatible Servers | Discovery Needs |
|--------|------|-------------------|----------------|
| pii | Universal | All servers | None |
| secrets | Universal | All servers | None |
| prompt_injection | Universal | All servers | None |
| filesystem_server | Server-specific | secure-filesystem-server | None |
| tool_allowlist | Universal + Dynamic | All servers | tools |

## Future Considerations

### Pattern Matching

For v2, we could add pattern support while maintaining backwards compatibility:

```python
COMPATIBLE_SERVERS = [
    "secure-filesystem-server",  # Exact match
    {"pattern": "*filesystem*"}  # Future: pattern matching
]
```

### Extended Discovery

Additional discovery types could be added:

```python
REQUIRES_DISCOVERY = ["tools", "resources", "prompts", "custom_capabilities"]
```

### Plugin Metadata

UI-specific metadata could be added alongside compatibility:

```python
UI_METADATA = {
    "display_name": "Filesystem Security",
    "description": "Path traversal and access control",
    "category": "security",
    "documentation_url": "https://docs.example.com/plugins/filesystem"
}
```

## Benefits

1. **Zero Breaking Changes**: Existing plugins continue to work without modification
2. **Gradual Adoption**: Plugins can add compatibility info over time
3. **Simple Mental Model**: Presence/absence of attributes has clear semantics
4. **Easy Implementation**: Three lines of compatibility checking logic
5. **Extensible**: Can add more sophisticated matching later if needed
6. **Self-Documenting**: Plugin compatibility is visible in the code

This design provides the foundation for an intuitive TUI configuration experience while maintaining the flexibility and simplicity that makes Watchgate easy to extend and maintain.