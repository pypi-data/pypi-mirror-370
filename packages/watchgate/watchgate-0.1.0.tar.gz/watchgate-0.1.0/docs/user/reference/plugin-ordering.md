# Plugin Ordering and Priority System

*[Home](../../../README.md) → [User Documentation](../../README.md) → [Reference](../README.md) → Plugin Ordering*

## Overview

Watchgate provides a comprehensive plugin priority system that ensures predictable, configurable plugin execution order for both security and auditing plugins. This system determines the execution order through priority values and provides flexible configuration for complex multi-plugin scenarios.

## How Plugin Ordering Works

### Priority System
- **Priority Range**: 0-100 (inclusive)  
- **Execution Order**: Lower numbers = higher priority (execute first)
- **Default Priority**: 50 (middle of the range)
- **Predictable**: Same input always produces same output

### Plugin Types
- **Security Plugins**: Execute during request/response processing in priority order, stop on first denial
- **Auditing Plugins**: Execute during audit logging in priority order, all plugins execute regardless of outcome
- **Independent Execution**: Security and auditing plugins execute at different times with separate priority systems

## Priority Assignment Guidelines

### Recommended Priority Ranges

#### 0-25: Core Security Plugins
Use this range for fundamental security controls that must execute before other checks:
- Authentication plugins
- Authorization checks
- Critical security validations

```yaml
plugins:
  security:
    - policy: "authentication"
      priority: 10
      config:
        required: true
```

#### 26-50: Content and Policy Plugins  
Use this range for content filtering and policy enforcement:
- Tool access control (default: 30)
- Content access control (default: 40)
- Data loss prevention
- Input validation

```yaml
plugins:
  security:
    - policy: "tool_allowlist"
      priority: 30
      config:
        mode: "allowlist"
        tools: ["read_file", "write_file"]
    
    - policy: "content_access_control"
      priority: 40
      config:
        mode: "allowlist"
        resources: ["public/*", "docs/*.md"]
```

#### 51-75: Compliance and Monitoring
Use this range for compliance checks and monitoring that don't affect core security:
- Rate limiting
- Usage monitoring
- Compliance validation

```yaml
plugins:
  security:
    - policy: "rate_limiter"
      priority: 60
      config:
        requests_per_minute: 100
```

#### 76-100: Observation and Logging
Use this range for plugins that observe but don't modify behavior:
- Audit logging
- Metrics collection
- Debug monitoring

```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      priority: 80
      config:
        file: "watchgate.log"
```

## Plugin Priority Configuration

All plugins support a `priority` field in their configuration:

```yaml
plugins:
  security:
    - policy: tool_allowlist
      enabled: true
      priority: 10  # High priority (executes early)
      config:
        mode: allowlist
        tools: ["read_file", "write_file"]
    
    - policy: content_access_control
      enabled: true
      priority: 20  # Execute after tool_allowlist
      config:
        mode: allowlist
        resources: ["public/*", "docs/*.md"]
    
    - policy: rate_limiter
      enabled: true
      priority: 90  # Low priority (executes last)
      config:
        limit: 100
        window: 60

  auditing:
    - policy: "file_auditing"
      enabled: true
      priority: 10  # First auditing plugin to execute
      config:
        log_level: info
```

## Configuration Examples

### Simple Priority Configuration
```yaml
plugins:
  security:
    - policy: "tool_allowlist"
      enabled: true
      priority: 30
      config:
        mode: "allowlist"
        tools: ["read_file", "write_file"]
  
  auditing:
    - policy: "file_auditing"
      enabled: true
      priority: 50
      config:
        file: "audit.log"
        format: "simple"
```

### Complex Multi-Plugin Setup
```yaml
plugins:
  security:
    # High priority: Core authentication
    - policy: "authentication"
      priority: 10
      config:
        required: true
    
    # Medium priority: Tool filtering
    - policy: "tool_allowlist"
      priority: 30
      config:
        mode: "allowlist"
        tools: ["read_file", "list_directory"]
    
    # Medium priority: Content filtering
    - policy: "content_access_control"
      priority: 40
      config:
        mode: "allowlist"
        resources: ["public/*", "docs/*.md"]
    
    # Low priority: Rate limiting
    - policy: "rate_limiter"
      priority: 70
      config:
        limit: 100
        window: 60
  
  auditing:
    # High priority: Critical audit logging
    - policy: "compliance_audit"
      priority: 20
      config:
        critical: true
        destination: "compliance.log"
    
    # Medium priority: General audit logging
    - policy: "file_auditing"
      priority: 50
      config:
        file: "general.log"
        format: "detailed"
    
    # Low priority: Metrics collection
    - policy: "metrics_collector"
      priority: 80
      config:
        endpoint: "https://metrics.company.com"
```

## Understanding Plugin Interaction

### Sequential Processing
Plugins execute sequentially in priority order:

1. **Security plugins** execute in ascending priority order (10, 20, 30, etc.)
2. If any security plugin denies the request, processing stops immediately
3. **Auditing plugins** execute in ascending priority order, all plugins run

### Plugin Dependencies
When plugins depend on each other's output, use priority to ensure correct order:

```yaml
plugins:
  security:
    # Tool access control must run before content access control
    - policy: "tool_allowlist"
      priority: 20
      config:
        mode: "allowlist"
        tools: ["read_file", "write_file"]
    
    # Content access control runs on allowed tools only
    - policy: "content_access_control"
      priority: 30
      config:
        mode: "allowlist"
        resources: ["public/*"]
```

## Plugin Execution Behavior

### Security Plugins
- Execute in priority order (0-100, ascending)
- Processing stops when any plugin denies the request
- Plugin failures default to denial for security

### Auditing Plugins
- Execute in priority order (0-100, ascending) during audit logging
- All plugins execute regardless of their individual outcomes
- Plugin failures are logged but don't affect request processing
- **Independent from security plugins**: Auditing priority only affects audit log order, not security decisions

## Best Practices

### 1. Leave Gaps Between Priorities
Don't use consecutive priorities. Leave gaps for future plugins:

**Good:**
```yaml
- priority: 10  # Authentication
- priority: 20  # Authorization  
- priority: 30  # Tool filtering
- priority: 50  # Content filtering
```

**Avoid:**
```yaml
- priority: 10
- priority: 11
- priority: 12
- priority: 13
```

### 2. Group Related Plugins
Keep related functionality in the same priority range:

```yaml
# Authentication/Authorization: 10-19
- priority: 10  # Authentication
- priority: 15  # Role-based access

# Content Control: 20-39
- priority: 20  # Tool access control
- priority: 30  # Content access control

# Monitoring: 80-99
- priority: 80  # Audit logging
- priority: 90  # Metrics
```

### 3. Document Priority Decisions
Add comments explaining priority choices:

```yaml
plugins:
  security:
    - policy: "authentication"
      priority: 10  # Must run first - validates user identity
      
    - policy: "tool_allowlist"
      priority: 30  # Runs after auth - filters based on user permissions
      
    - policy: "rate_limiter"
      priority: 70  # Runs last - applies limits after all other checks
```

### 4. Test Plugin Interactions
Always test multi-plugin configurations to ensure correct interaction:

- Verify plugins execute in expected order
- Check that plugin modifications flow correctly
- Test failure scenarios (plugin denies request)

## Troubleshooting

### Common Issues

#### Wrong Execution Order
**Problem**: Plugins execute in unexpected order
**Solution**: Check priority values, ensure lower numbers = higher priority

```yaml
# Problem: Content filter runs before tool access control
- policy: "content_access_control"
  priority: 20
- policy: "tool_allowlist"  
  priority: 30

# Solution: Swap priorities
- policy: "tool_allowlist"
  priority: 20  # Runs first
- policy: "content_access_control"
  priority: 30  # Runs second
```

#### Plugin Conflicts
**Problem**: Plugins interfere with each other
**Solution**: Adjust priorities to ensure correct dependency order

#### Performance Issues
**Problem**: Too many plugins cause slow response times
**Solution**: Optimize high-priority plugins, consider combining similar plugins

### Debug Logging
Enable debug logging to see plugin execution order:

```bash
watchgate --config watchgate.yaml --verbose
```

Look for log messages like:
```
Plugin execution order: [('tool_allowlist', 20), ('content_access_control', 30)]
Executing security plugin tool_allowlist with priority 20
Executing security plugin content_access_control with priority 30
```

## Implementation Details

### Plugin Interface Changes

All plugins now inherit priority from the `PluginInterface` base class:

```python
class PluginInterface(ABC):
    def __init__(self, config: Dict[str, Any]):
        # Set default priority if not specified in config
        self.priority = config.get('priority', 50)
        # Validate priority range
        if not isinstance(self.priority, int) or not (0 <= self.priority <= 100):
            raise ValueError(f"Plugin priority {self.priority} must be between 0 and 100")
```

### Priority Validation
Watchgate validates priority values at startup:
- Must be integers between 0 and 100
- Invalid priorities cause startup failure with clear error messages

### Same Priority Handling
When multiple plugins have the same priority, they execute in registration order:

```yaml
plugins:
  security:
    - policy: "plugin_a"
      priority: 30
    - policy: "plugin_b" 
      priority: 30  # Same priority as plugin_a
    - policy: "plugin_c"
      priority: 30  # Same priority as plugin_a and plugin_b
```

Execution order: plugin_a → plugin_b → plugin_c

## Backward Compatibility

The priority system is fully backward compatible:
- Existing plugins without priority default to 50
- Existing plugin configurations continue to work unchanged
- No changes required to existing plugin implementations

## Migration Guide

### From Unordered to Priority-Based
If you have existing plugins without priorities:

1. **Identify dependencies**: Which plugins need to run before others?
2. **Assign priorities**: Use the recommended ranges above
3. **Test thoroughly**: Verify behavior matches expectations
4. **Update documentation**: Document priority decisions

### Priority Assignment Strategy
1. Start with default priority (50) for all plugins
2. Identify critical plugins that must run first (assign 10-25)
3. Identify plugins that should run last (assign 75-90)
4. Adjust intermediate priorities based on dependencies

## Summary

The plugin priority system provides:
- **Predictable execution order** through numeric priorities
- **Flexible configuration** with 0-100 priority range  
- **Clear dependency management** through priority assignment
- **Backward compatibility** with automatic defaults
- **Debug visibility** through comprehensive logging

Use this guide to design plugin configurations that are maintainable, predictable, and performant.
