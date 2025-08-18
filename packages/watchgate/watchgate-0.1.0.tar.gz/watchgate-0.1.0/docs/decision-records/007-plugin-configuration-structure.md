# ADR-007: Plugin Configuration Structure

**Status**: Accepted  
**Date**: v0.1.0 Development  
**Deciders**: Development Team  
**Technical Story**: Plugin configuration system evolution

## Historical Context

This ADR documented the original path-based plugin configuration approach for v0.1.0. This decision has been superseded by the implementation of a policy-based plugin manifest system.

### Original Path-Based Decision (v0.1.0 Initial)
Watchgate v0.1.0 initially implemented a path-based plugin configuration system:

```yaml
plugins:
  security:
    - path: "./plugins/security/tool_allowlist.py"
      enabled: true
      config:
        mode: "allowlist"
        tools: ["read_file"]
```

### Evolution to Policy-Based System (v0.1.0 Final)
During v0.1.0 development, the system evolved to use a policy-based manifest approach:

```yaml
plugins:
  security:
    - policy: "tool_allowlist"
      enabled: true
      config:
        mode: "allowlist"
        tools: ["read_file", "list_directory"]
```

## Current Implementation (Policy-Based)

The final v0.1.0 implementation uses a **policy-based plugin configuration** system where:

1. **Plugins declare policies** via POLICIES manifest in their modules
2. **Configuration references policies** by name rather than file paths
3. **Plugin discovery** is automatic based on installed plugin manifests

### Key Benefits of Policy-Based Approach
- **Abstraction**: Configuration independent of file structure
- **Discoverability**: Automatic policy discovery from installed plugins
- **Flexibility**: Multiple plugins can implement the same policy
- **Maintainability**: Plugin reorganization doesn't break configurations

## Implementation Details

### Plugin Manifest System
Each plugin module contains a POLICIES manifest:

```python
# In watchgate/plugins/security/tool_allowlist.py
POLICIES = {
    "tool_allowlist": {
        "name": "Tool Allowlist",
        "description": "Controls tool access via allowlist/blocklist",
        "category": "security",
        "version": "1.0.0",
        "class": "ToolAllowlistPlugin"
    }
}
```

### Configuration Schema
Plugin configurations use policy names:

```yaml
plugins:
  security:
    - policy: "tool_allowlist"  # References policy name, not file path
      enabled: true
      config:
        mode: "allowlist"
        tools: ["read_file", "write_file"]
```

### Discovery and Loading Process
1. Plugin manager scans installed plugins for POLICIES manifests
2. Builds registry of available policies and their implementations
3. Configuration loader validates policy names against available policies
4. Runtime loads appropriate plugin classes based on policy names

## Migration Impact

### Breaking Changes from Path-Based System
- Configuration field changed from `path:` to `policy:`
- Plugin discovery no longer requires explicit file paths
- Validation checks policy availability instead of file existence

### Benefits Gained
- **Simplified configuration**: No need to know internal file structure
- **Better error messages**: Clear indication when policies are unavailable
- **Plugin portability**: Plugins can be reorganized without config changes
- **Extensibility**: Foundation for future plugin marketplace/registry

## Legacy Information

The remainder of this document contains the original path-based design rationale, preserved for historical context.

<details>
<summary>Original Path-Based Design (Historical)</summary>

### Original Decision Rationale
The path-based approach was chosen initially to avoid premature optimization and infrastructure complexity. However, during implementation, the benefits of a policy-based manifest system became apparent and justified the additional complexity.

### Original Consequences

#### Positive (Path-Based)
- **Simplicity**: No indirection between configuration and plugin location
- **Transparency**: Users see exactly which files are being loaded
- **No infrastructure dependency**: Works entirely offline
- **Familiar pattern**: Similar to Docker volumes, Kubernetes ConfigMaps
- **Easy debugging**: Clear path from config to plugin file

#### Negative (Path-Based)
- **More verbose**: Full file paths instead of short names
- **Manual management**: No automatic plugin discovery from registry
- **Path dependencies**: Configuration tied to specific file structure

#### Neutral (Path-Based)
- **Compatibility**: Registry support can be added alongside existing configurations
- **Plugin distribution**: Third-party plugins distributed as files

</details>

## Related ADRs

- See [v0.1.0 Implementation Plan](../../versions/v0.1.0/v0.1.0-implementation-plan.md) for detailed implementation approach
- This ADR documents the evolution from the original path-based system to the final policy-based implementation

---

**Note**: This ADR has been updated to reflect the actual implementation used in v0.1.0. The policy-based plugin manifest system replaced the originally planned path-based system during development.
```yaml
plugins:
  security:
    local:
      - name: "tool_allowlist"
        path: "./plugins/..."
    registry:
      - name: "enterprise_ldap"
        version: "1.0.0"
```

**Rejected**: Adds unnecessary nesting and empty sections for v0.1.0

### 2. URI-Based System
```yaml
plugins:
  security:
    - plugin: "file://./plugins/security/tool_allowlist.py"
    - plugin: "registry://hub.watchgate.dev/security/ldap@1.0.0"
```

**Rejected**: More complex parsing and validation for minimal benefit

### 3. Keep Name-Based with Built-in Registry
```yaml
plugins:
  security:
    - name: "tool_allowlist"  # Resolves to built-in plugin
```

**Rejected**: Creates confusion between built-in vs. user plugins

## Review Criteria

This approach may need adjustment when:
- Users request easier plugin distribution mechanisms
- Multiple third-party plugins exist that would benefit from centralized hosting
- Plugin management complexity becomes a significant user pain point
- Registry infrastructure can be properly maintained and supported

The path-based approach provides a solid foundation while preserving options for registry-based enhancements.
