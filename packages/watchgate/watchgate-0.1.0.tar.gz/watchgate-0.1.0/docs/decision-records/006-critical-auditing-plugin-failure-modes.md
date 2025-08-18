# ADR-006: Critical vs Non-Critical Auditing Plugin Failure Modes

**Status**: Accepted  

## Context

Watchgate's auditing plugins need to handle failure scenarios appropriately based on the deployment context. Different use cases have different requirements for auditing reliability:

1. **Development/General Use**: Auditing failures should not break the proxy functionality
2. **Regulated Industries**: Auditing failures may violate compliance requirements and must stop processing
3. **Security-Critical Environments**: Complete audit trails may be mandatory for operation

The original plugin architecture implemented graceful failure for all auditing plugins, where failures are logged but don't affect request processing. However, this approach doesn't support compliance scenarios where auditing is required for regulatory obligations.

## Decision

We will implement **configuration-driven auditing failure behavior** through a `critical` flag on auditing plugins:

```yaml
plugins:
  auditing:
    - name: "file_auditing"
      enabled: true
      config:
        file: "watchgate.log"
        critical: false  # Default: graceful failure
        
    - name: "compliance_logger" 
      enabled: true
      config:
        database_url: "postgresql://..."
        critical: true   # Compliance mode: fatal failure
```

### Implementation Strategy

```python
class AuditingPlugin(PluginInterface):
    """Abstract base for auditing plugins with critical failure support."""
    
    def is_critical(self) -> bool:
        """Return whether this plugin is critical for operation."""
        return getattr(self, 'critical', False)

class FileAuditingPlugin(AuditingPlugin):
    def __init__(self, config: Dict[str, Any]):
        self.critical = config.get("critical", False)
        # ... other initialization
```

### Plugin Manager Behavior

```python
async def log_request(self, request: MCPRequest, decision: PolicyDecision) -> None:
    for plugin in self.auditing_plugins:
        try:
            await plugin.log_request(request, decision)
        except Exception as e:
            if plugin.is_critical():
                # Critical plugin failure - propagate exception
                raise AuditingFailureError(
                    f"Critical auditing plugin {plugin.__class__.__name__} failed: {e}. "
                    f"To continue with non-critical auditing, set 'critical: false' in plugin config."
                )
            else:
                # Non-critical plugin failure - log and continue
                logger.error(f"Auditing plugin {plugin.__class__.__name__} failed: {e}")
```

### Key Design Principles

1. **Backwards Compatibility**: Default behavior remains graceful failure (`critical: false`)
2. **Clear User Guidance**: Error messages explain how to change behavior
3. **Per-Plugin Control**: Each auditing plugin can be configured independently
4. **Fail-Safe Defaults**: Critical mode must be explicitly enabled
5. **Consistent Interface**: All auditing plugins support the critical flag

## Alternatives Considered

### Alternative 1: Always Graceful Failure
```python
# Current behavior - always continue on auditing failures
except Exception as e:
    logger.error(f"Auditing plugin failed: {e}")
    # Continue processing
```
- **Pros**: Simple, never breaks proxy functionality
- **Cons**: Cannot support compliance requirements, silent audit gaps

### Alternative 2: Always Fatal Failure
```python
# Always propagate auditing failures
except Exception as e:
    raise AuditingFailureError(f"Auditing failed: {e}")
```
- **Pros**: Ensures complete audit coverage
- **Cons**: Breaks existing deployments, too rigid for development use

### Alternative 3: Global Critical Flag
```yaml
auditing:
  critical_mode: true  # Global setting for all auditing plugins
```
- **Pros**: Simple configuration, single decision point
- **Cons**: Less flexible, all-or-nothing approach doesn't match real deployment needs

### Alternative 4: Environment-Based Behavior
```python
# Determine behavior based on environment variables
if os.getenv("WATCHGATE_ENV") == "production":
    # Fatal failure in production
else:
    # Graceful failure in development
```
- **Pros**: Automatic behavior based on environment
- **Cons**: Hidden configuration, doesn't support mixed scenarios

## Consequences

### Positive
- **Regulatory Compliance**: Supports regulated industries requiring mandatory auditing
- **Flexible Deployment**: Same codebase works for development and production
- **Clear Configuration**: Explicit control over failure behavior per plugin
- **Backwards Compatible**: Existing configurations continue working unchanged
- **User-Friendly**: Error messages guide users to appropriate configuration

### Negative
- **Increased Complexity**: Plugin manager must handle two failure modes
- **Configuration Burden**: Users must understand when to use critical mode
- **Testing Overhead**: Both failure modes must be tested for each plugin

## Implementation Notes

This decision affects multiple components:

1. **Plugin Interface** (`watchgate/plugins/interfaces.py`):
   - Add `is_critical()` method to `AuditingPlugin` base class
   - Document critical behavior in interface contracts

2. **Plugin Manager** (`watchgate/plugins/manager.py`):
   - Update `log_request()` and `log_response()` to check critical flag
   - Add new `AuditingFailureError` exception type
   - Include helpful error messages with configuration guidance

3. **Default Auditing Plugin** (`watchgate/plugins/auditing/file_auditing.py`):
   - Support `critical` configuration parameter
   - Default to `critical: false` for backwards compatibility

4. **Error Handling** (`watchgate/protocol/errors.py`):
   - Add `AuditingFailureError` exception class
   - Include user guidance in error messages

5. **Documentation**:
   - Update configuration examples to show critical flag usage
   - Document compliance vs development deployment patterns

## Use Cases

### Development/Testing Environment
```yaml
plugins:
  auditing:
    - name: "file_auditing"
      config:
        file: "debug.log"
        critical: false  # Don't break development workflow
```

### Regulated Production Environment
```yaml
plugins:
  auditing:
    - name: "file_auditing"
      config:
        file: "/var/log/watchgate/audit.log"
        critical: true   # Compliance requirement
        
    - name: "database_logger"
      config:
        connection: "postgresql://audit-db/..."
        critical: true   # Redundant compliance logging
```

### Mixed Environment
```yaml
plugins:
  auditing:
    - name: "debug_logger"
      config:
        file: "debug.log"
        critical: false  # Optional debugging
        
    - name: "compliance_logger"
      config:
        endpoint: "https://compliance-api/..."
        critical: true   # Required for operations
```

## Review

This decision will be reviewed when:
- Adding new auditing plugin types with different failure characteristics
- Regulatory requirements change significantly
- User feedback indicates configuration complexity issues
- Performance impact of critical checking becomes significant
