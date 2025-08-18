# Security Plugin Critical Handling

## Status: COMPLETED ✅

Implementation is complete and simplified. The `get_security_impact()` method was removed as it provided no significant value.

## Feature Overview

Security plugins can now be configured as critical or non-critical, allowing for more flexible deployment scenarios while maintaining security guarantees.

## Implementation Summary

### SecurityPlugin Interface Changes
- Added `critical` config parameter (defaults to True for security)
- Added `is_critical()` method that returns the config value
- **Removed**: `get_security_impact()` method (deemed unnecessary)

### Plugin Manager Behavior
- **Critical plugins**: Failures block operations (fail-closed for security)
- **Non-critical plugins**: Failures log warnings and continue processing
- Uses `plugin.is_critical()` to determine failure behavior

### Existing Plugin Support
All existing security plugins now support the critical configuration:
- `ToolAllowlistPlugin`
- `BasicSecretsFilterPlugin` 
- `BasicPIIFilterPlugin`
- `BasicPromptInjectionDefensePlugin`

## Configuration

```yaml
plugins:
  security:
    - policy: "tool_allowlist"
      enabled: true
      config:
        critical: true  # Default: fail-closed on errors
        mode: "allowlist"
        tools: ["safe_tool1", "safe_tool2"]
    
    - policy: "basic_secrets_filter"  
      enabled: true
      config:
        critical: false  # Allow operation to continue if this fails
        action: "audit_only"
```

## Security Considerations

### Critical Security Principle
**Security plugins default to fail-closed behavior.** The `critical: false` configuration must be:
- Explicitly set by administrators
- Used only for auxiliary/non-essential security features
- Well-documented with security implications

### Risk Mitigation
- **Default critical behavior**: Prevents accidental security bypasses
- **Explicit configuration**: Non-critical behavior requires intentional configuration
- **Clear logging**: Non-critical failures are logged with clear warnings

## Testing

Comprehensive test coverage includes:
- Interface critical behavior tests
- Plugin manager critical failure handling tests  
- Existing plugin compatibility tests
- Mixed critical/non-critical scenario tests

## Backward Compatibility

No backward compatibility concerns - this is a fresh implementation without the deprecated ALWAYS_CRITICAL_PLUGINS concept.
        mode: "allowlist"
        tools: ["read_file"]
        critical: true  # Default: always critical for core security
        
    - policy: "security_metrics"
      enabled: true  
      config:
        endpoint: "https://metrics.example.com"
        critical: false  # Non-critical: metrics collection
        
    - policy: "advanced_threat_detection"
      enabled: true
      config:
        ai_endpoint: "https://threat-detection.example.com"
        critical: false  # Non-critical: can fall back to basic security
        fallback_mode: "basic_patterns"  # What to do when this fails
```

### Security Plugin Categories

#### Configurable Critical Status
All security plugins can be configured as critical or non-critical:
- **Core Access Control**: `tool_allowlist`, `path_access_control` (typically critical)
- **Data Protection**: `secrets_filter`, `pii_filter` (typically critical in block mode)
- **Enhanced Detection**: Advanced threat detection, ML-based filters (may be non-critical)
- **Auxiliary Security**: Security metrics, additional logging (typically non-critical)
- **Performance Monitoring**: Security performance tracking (typically non-critical)
- **Development Aids**: Debug security plugins, testing helpers (typically non-critical)

### Implementation Requirements

#### Plugin Interface Updates
```python
class SecurityPlugin(PluginInterface):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # Security plugins can be configured as critical or non-critical
        self.critical = config.get("critical", True)  # Default to critical for security
    
    def is_critical(self) -> bool:
        """Return whether this plugin is critical for operation.
        
        Returns:
            bool: True if plugin failures should halt processing, False otherwise
        """
        return self.critical
    
```

#### Plugin Manager Updates
```python
class PluginManager:
    async def handle_security_plugin_failure(self, plugin, error, request):
        if plugin.is_critical():
            # Current behavior: fail closed
            return PolicyDecision(allowed=False, reason=f"Critical security plugin failed: {error}")
        else:
            # New behavior: log and continue with degraded security
            logger.warning(f"Non-critical security plugin {plugin.__class__.__name__} failed: {error}")
            logger.warning(f"Security impact: {plugin.get_security_impact()}")
            
            # Continue processing with remaining plugins
            return None  # Let other plugins continue processing
```

### Security Safeguards

#### Security Impact Documentation
When non-critical plugins fail, basic warning messages are logged. More detailed security impact documentation may be added in future versions if needed.

## Implementation Phases

### Phase 1: Foundation
1. **Plugin categorization**: Review existing security plugins and their typical critical needs
2. **Interface updates**: Add critical behavior methods to SecurityPlugin base class
3. **Plugin manager updates**: Handle non-critical plugin failures gracefully  
4. **Documentation**: Security impact documentation for all plugins

### Phase 2: Non-Critical Behavior
1. **Logging enhancements**: Clear warnings when security plugins fail
2. **Monitoring integration**: Alert on security plugin failures
3. **Testing**: Comprehensive testing of degraded security scenarios
4. **Plugin updates**: Update existing security plugins with critical configuration and security impact

### Phase 3: Advanced Features
1. **Fallback mechanisms**: Some plugins can fall back to simpler behavior
2. **Runtime reconfiguration**: Ability to change critical status at runtime
3. **Security dashboard**: View current security plugin status
4. **Auto-recovery**: Attempt to restart failed non-critical plugins

## Security Testing Requirements

### Test Scenarios
1. **Critical plugin failure**: Verify requests are blocked
2. **Non-critical plugin failure**: Verify processing continues with warnings
3. **Configuration flexibility**: Verify all plugins can be configured as critical or non-critical
4. **Logging verification**: Verify security failures are properly logged
5. **Impact documentation**: Verify all plugins document security impact

### Security Review Checklist
- [ ] All security plugins can be configured as critical or non-critical
- [ ] Non-critical failures are logged prominently  
- [ ] Security impact is clearly documented
- [ ] Configuration changes require explicit administrator action
- [ ] No silent security degradation
- [ ] Monitoring alerts on security plugin failures

## Use Cases

### Development Environment
```yaml
# Development configuration with some non-critical security
plugins:
  security:
    - policy: "tool_allowlist"
      config:
        mode: "allowlist" 
        tools: ["read_file", "write_file", "list_directory"]
        critical: true  # Can be configured as critical or non-critical
        
    - policy: "advanced_threat_detection"
      config:
        enabled: true
        critical: false  # Allow development to continue if AI service is down
```

### Production Environment
```yaml
# Production: most plugins critical for maximum security
plugins:
  security:
    - policy: "tool_allowlist"
      config:
        mode: "allowlist"
        tools: ["read_file"]
        critical: true  # Can be configured as critical or non-critical
        
    - policy: "secrets_filter"
      config:
        action: "block"
        critical: true  # Can be configured as critical or non-critical
        
    - policy: "security_metrics"
      config:
        endpoint: "https://metrics.company.com"
        critical: false  # Metrics failure shouldn't block operations
```

## Migration Strategy

Since this is a new feature in development, existing configurations will need to be updated to include the `critical` parameter for security plugins. The default behavior will remain secure (critical: true) for all security plugins.

## Related Features

- [Auditing Plugin Critical Handling](../auditing-plugin-critical-handling/) - Existing pattern for auditing plugins
- [Plugin Architecture](../plugin-architecture/) - Base plugin system  
- [Security Model Documentation](../../user/core-concepts/security-model.md)

## Success Criteria

1. **Security maintained**: Core security guarantees are never compromised
2. **Flexibility added**: Non-critical security plugins can fail gracefully
3. **Clear documentation**: Security impact is well-documented
4. **Safe defaults**: Default behavior is secure
5. **Monitoring enabled**: Plugin failures are visible to administrators