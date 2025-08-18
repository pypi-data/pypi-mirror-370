# Plugin Architecture

**Status**: Implemented

## Problem Statement
Need extensible architecture for security and auditing functionality that allows developers to create custom policies without modifying core code.

## Requirements
- Plugin interfaces for security and auditing functionality
- Plugin discovery and loading system
- Plugin configuration via YAML
- Priority-based plugin execution order
- Plugin isolation (failures don't crash proxy)
- Default plugins that provide immediate value
- Clear extension points for community contributions

## Success Criteria
- [x] Abstract base classes for SecurityPlugin and AuditingPlugin
- [x] Plugin manager with discovery and loading
- [x] YAML-based plugin configuration
- [x] Priority-based execution order
- [x] Error isolation between plugins
- [x] Default security and auditing plugins included
- [x] Well-documented plugin interfaces

## Constraints
- Plugin loading must be deterministic
- Plugin failures should not affect other plugins
- Configuration validation must provide clear error messages
- Plugin system should add minimal startup overhead

## Implementation Notes
- Uses abstract base classes to define plugin contracts
- Plugin manager handles lifecycle and error isolation
- Configuration loader extended for plugin parameters
- Default plugins demonstrate patterns for community development

## Plugin Types

### Security Plugins
- Implement `check_request()`, `check_response()`, `check_notification()`
- Return `PolicyDecision` with allow/block/modify actions
- Access to sender context for intelligent decisions

### Auditing Plugins
- Implement `log_request()`, `log_response()`, `log_notification()`
- Receive `PolicyDecision` from security plugins
- Support multiple output formats and destinations

## Configuration
```yaml
plugins:
  security:
    - policy: "tool_allowlist"
      enabled: true
      priority: 5
      config:
        # plugin-specific config
  auditing:
    - policy: "file_auditing"
      enabled: true
      config:
        # plugin-specific config
```

## References
- Implementation: `watchgate/plugins/manager.py`, `watchgate/plugins/interfaces.py`
- Tests: `tests/unit/test_plugin_manager.py`, `tests/unit/test_plugin_interfaces.py`
- Examples: `watchgate/plugins/security/`, `watchgate/plugins/auditing/`