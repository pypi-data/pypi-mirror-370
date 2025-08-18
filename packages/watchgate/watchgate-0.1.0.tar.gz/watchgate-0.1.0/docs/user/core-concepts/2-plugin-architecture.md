# Plugin Architecture

*[Home](../../README.md) > [User Guide](../README.md) > [Core Concepts](README.md) > Plugin Architecture*

Watchgate's plugin architecture provides a flexible, modular system for implementing security controls and auditing capabilities. This architecture allows you to customize protection strategies and add new security features as needed.

## Architecture Overview

```
                    Watchgate Proxy
                         ┌─────────────────┐
AI Client Request ───────┤   Plugin Manager ├───────→ MCP Server
                         └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              Security      Auditing    (Future Plugin
              Plugins       Plugins      Types)
          ┌─────────────┐ ┌─────────┐
          │ Tool Access │ │ File    │
          │ Control     │ │ Logger  │
          └─────────────┘ └─────────┘
          ┌─────────────┐ ┌─────────┐
          │ Content     │ │ Metrics │
          │ Access      │ │ Collector│
          │ Control     │ │         │
          └─────────────┘ └─────────┘
```

## Plugin Types

Watchgate supports two main categories of plugins:

### Security Plugins
Security plugins evaluate requests and can **allow** or **deny** operations:

- **Execute in priority order** (lower priority numbers first)
- **Short-circuit on denial**: If any security plugin denies a request, processing stops
- **Fail-safe**: Plugin errors default to denial for security

**Available Security Plugins:**
- `tool_allowlist`: Controls which MCP tools can be executed
- `content_access_control`: Controls which resources/files can be accessed

### Auditing Plugins
Auditing plugins monitor and log activities but **cannot block** requests:

- **Execute in priority order** (lower priority numbers first)
- **All plugins execute**: Auditing continues even if one plugin fails
- **Configurable failure behavior**: Plugin errors can either block MCP communications or continue gracefully

**Available Auditing Plugins:**
- `file_auditing`: Logs activities to files with configurable formats

#### Critical vs Non-Critical Auditing Plugins

Auditing plugins support two failure modes via the `critical` configuration parameter:

**Non-Critical Mode (Default)**:
```yaml
- policy: "file_auditing"
  config:
    critical: false  # Default behavior
```
- **Graceful failure**: If the plugin fails, Watchgate continues processing
- **Use case**: Development, testing, general monitoring where auditing is helpful but not mandatory
- **Behavior**: Plugin errors are logged but don't affect request processing

**Critical Mode**:
```yaml
- policy: "file_auditing"
  config:
    critical: true   # Compliance/regulated environments
```
- **Security precaution**: If the plugin fails, Watchgate blocks MCP communications to prevent unlogged activity
- **Use case**: Regulated industries, compliance requirements, environments where complete audit trails are legally required
- **Behavior**: Plugin errors halt all request processing with clear error messages

This flexibility allows the same Watchgate deployment to work in both development (where auditing failures shouldn't break workflows) and production compliance environments (where auditing failures must halt processing).

## Plugin Lifecycle

### Plugin Loading
1. **Configuration Parsing**: Plugin configurations are loaded from YAML
2. **Priority Validation**: Plugin priorities are validated (0-100 range)
3. **Plugin Instantiation**: Each plugin is created with its configuration
4. **Registration**: Plugins are registered with the Plugin Manager
5. **Sorting**: Plugins are sorted by priority for execution

### Request Processing
1. **Request Received**: Watchgate receives an MCP request
2. **Security Plugin Chain**: Security plugins execute in priority order
3. **Early Exit**: If any security plugin denies, processing stops
4. **MCP Server Call**: If allowed, request is forwarded to MCP server
5. **Response Processing**: Security plugins can modify responses
6. **Audit Logging**: All auditing plugins log the complete interaction

## Plugin Priority System

### Priority Values
- **Range**: 0-100 (inclusive)
- **Execution Order**: Lower numbers execute first (0 = highest priority)
- **Default**: Plugins without explicit priority default to 50

### Recommended Priority Ranges

| Range | Purpose | Examples |
|-------|---------|----------|
| 0-25 | Core Security | Authentication, authorization |
| 26-50 | Content Control | Tool access, content filtering |
| 51-75 | Compliance | Rate limiting, usage monitoring |
| 76-100 | Observation | Audit logging, metrics |

### Priority Configuration
```yaml
plugins:
  security:
    - policy: "tool_allowlist"
      priority: 30    # Execute before content control
      enabled: true
      config: {...}
    
    - policy: "content_access_control"
      priority: 40    # Execute after tool control
      enabled: true
      config: {...}
  
  auditing:
    - policy: "file_auditing"
      priority: 10    # High priority for complete logging
      enabled: true
      config: {...}
```

## Plugin Interface

All plugins implement a common interface that defines their behavior:

### Security Plugin Interface
```python
class SecurityPlugin(PluginInterface):
    async def check_request(self, request: MCPRequest) -> PolicyDecision:
        """Check if incoming request should be allowed, modified, or blocked"""
        pass
    
    async def check_response(self, request: MCPRequest, response: MCPResponse) -> PolicyDecision:
        """Check if outgoing response should be allowed, modified, or blocked"""
        pass
    
    async def check_notification(self, notification: MCPNotification) -> PolicyDecision:
        """Check if notification should be allowed or blocked"""
        pass
```

### **Critical Security Plugin Implementation Requirement**

**All security plugins MUST implement all three check methods with comprehensive security logic:**

- **`check_request`**: Validates incoming requests for security violations
- **`check_response`**: Validates outgoing responses to prevent data leakage  
- **`check_notification`**: Validates notifications to prevent information disclosure

**Security vulnerabilities can occur if any of these methods are not properly implemented.** For example:
- Only checking requests allows malicious content in responses to bypass security
- Only checking requests and responses allows notifications to leak sensitive information
- Incomplete implementations create security gaps that can be exploited

### PolicyDecision Return Values
Security plugins return `PolicyDecision` objects that specify:
```python
PolicyDecision(
    allowed=True,           # Whether to allow the operation
    reason="explanation",   # Human-readable reason for the decision
    metadata={...},         # Additional context for auditing
    modified_content=None   # Optional modified content (for filtering/redaction)
)
```

### Auditing Plugin Interface
```python
class AuditingPlugin(PluginInterface):
    async def audit_request(self, request: MCPRequest, context: RequestContext):
        """Log/audit incoming request"""
        pass
    
    async def audit_response(self, response: MCPResponse, context: ResponseContext):
        """Log/audit outgoing response"""
        pass
    
    async def audit_security_decision(self, decision: PolicyDecision, context: SecurityContext):
        """Log/audit security decisions"""
        pass
```

## Plugin Decision Flow

Understanding how plugin decisions are processed is crucial for debugging and audit compliance. The plugin manager handles three types of outcomes differently:

### Decision Types and Metadata Preservation

1. **Plugin Denies**: Specific plugin reason and metadata are **always preserved**
   - Processing stops immediately 
   - Error messages contain plugin-specific details
   - Audit logs include complete plugin context

2. **All Plugins Allow (No Modifications)**: Generic reason and metadata are used
   - No plugin performed meaningful work
   - Standard "allowed by all plugins" message
   - Generic audit information

3. **Plugin Allows with Modifications**: Modifying plugin's reason and metadata are **preserved**
   - Plugin performed meaningful work (filtering, redaction, etc.)
   - Specific plugin actions documented
   - Detailed audit trail for compliance

### User Experience Examples

**Tool Blocked by Allowlist**:
```
Error: Tool 'delete_system_files' not in allowlist
Audit: BLOCKED - Tool filtering: delete_system_files denied by allowlist policy
```

**Standard Tool Access**:
```
Success: Request processed normally
Audit: ALLOWED - Request allowed by all security plugins  
```

**Content Filtered**:
```
Success: Response processed with content filtering
Audit: ALLOWED - PII detected and redacted: 2 SSNs removed from response
```

For detailed information about plugin decision processing, see the [Plugin Decision Flow](3-plugin-decision-flow.md) guide.

## Plugin Configuration

### Standard Configuration Structure
Every plugin follows a common configuration pattern:

```yaml
plugins:
  security:  # or 'auditing'
    - policy: "plugin_name"      # Plugin identifier
      enabled: true              # Enable/disable plugin
      priority: 30               # Execution priority (optional)
      config:                    # Plugin-specific configuration
        # Plugin-specific settings go here
```

### Plugin-Specific Configuration

#### Tool Access Control Plugin
```yaml
- policy: "tool_allowlist"
  enabled: true
  priority: 30
  config:
    mode: "allowlist"           # allowlist, blocklist, or allow_all
    tools: ["read_file", "write_file"]
    block_message: "Tool access denied"
```

#### Content Access Control Plugin
```yaml
- policy: "content_access_control"
  enabled: true
  priority: 40
  config:
    mode: "allowlist"           # allowlist, blocklist, or allow_all
    resources: ["public/*", "docs/*.md"]
    block_message: "Resource access denied"
```

#### File Logger Plugin
```yaml
- policy: "file_auditing"
  enabled: true
  priority: 80
  config:
    file: "logs/audit.log"
    format: "simple"            # simple, json, or detailed
    mode: "all_events"          # security_only, operations_only, or all_events
    max_file_size_mb: 10
    backup_count: 5
```

## Plugin Interaction Patterns

### Sequential Processing
Plugins execute one after another in priority order:

```yaml
plugins:
  security:
    # Priority 20: Executes first
    - policy: "tool_allowlist"
      priority: 20
      config:
        mode: "allowlist"
        tools: ["read_file", "write_file"]
    
    # Priority 30: Executes second (if first allows)
    - policy: "content_access_control"
      priority: 30
      config:
        mode: "allowlist"
        resources: ["public/*"]
```

### Defense in Depth
Multiple security layers provide comprehensive protection:

1. **Tool Layer**: Controls which operations are possible
2. **Content Layer**: Controls which resources are accessible
3. **Audit Layer**: Monitors all activities

### Plugin Dependencies
When plugins depend on each other's decisions, use priority to ensure correct ordering:

```yaml
plugins:
  security:
    # Authentication must happen first
    - policy: "authentication"
      priority: 10
    
    # Authorization checks identity from authentication
    - policy: "authorization"
      priority: 15
    
    # Tool control applies to authorized users
    - policy: "tool_allowlist"
      priority: 20
```

## Plugin Development

### Creating Custom Plugins
Watchgate's architecture supports custom plugin development:

1. **Inherit from base plugin class**
2. **Implement required methods**
3. **Register with plugin manager**
4. **Configure in YAML**

### Plugin Best Practices

#### Security Plugin Guidelines
- **Fail secure**: Default to denial on errors
- **Be deterministic**: Same input should always produce same output
- **Handle edge cases**: Validate all inputs
- **Log decisions**: Help with debugging and auditing

#### Auditing Plugin Guidelines
- **Don't block processing**: Auditing failures shouldn't affect operations
- **Handle large volumes**: Design for high-throughput scenarios
- **Structured logging**: Use consistent, parseable log formats
- **Resource management**: Handle log rotation and cleanup

## Plugin Management

### Configuration Validation
Watchgate validates plugin configurations at startup:

```bash
# Validate configuration
watchgate debug config --validate --config your-config.yaml

# Check plugin priorities
watchgate debug plugins --validate-priorities --config your-config.yaml

# List available plugins
watchgate debug plugins --list-available
```

### Runtime Monitoring
Monitor plugin behavior through logging:

```bash
# Watch plugin execution
watchgate --config your-config.yaml --verbose

# Analyze plugin performance
grep "Plugin execution" logs/watchgate.log
```

### Troubleshooting Plugins

#### Plugin Not Loading
1. Check plugin name spelling
2. Verify plugin is available
3. Check configuration syntax
4. Review startup logs for errors

#### Plugin Not Executing
1. Verify plugin is enabled
2. Check priority conflicts
3. Ensure plugin dependencies are met
4. Review execution logs

#### Unexpected Plugin Behavior
1. Check plugin configuration
2. Verify input data format
3. Test with simplified configuration
4. Enable debug logging

## Advanced Plugin Patterns

### Environment-Specific Plugins
Use different plugin configurations for different environments:

```yaml
# Development: Permissive policies
plugins:
  security:
    - policy: "tool_allowlist"
      config:
        mode: "blocklist"
        tools: ["delete_file"]  # Only block dangerous operations

# Production: Restrictive policies
plugins:
  security:
    - policy: "tool_allowlist"
      config:
        mode: "allowlist"
        tools: ["read_file"]    # Only allow safe operations
```

### Conditional Plugin Activation
Plugins can be conditionally enabled based on context:

```yaml
plugins:
  security:
    - policy: "rate_limiter"
      enabled: true
      config:
        limit: 100
        window: 3600
        condition: "production"  # Only in production
```

## Summary

Watchgate's plugin architecture provides:

- **Modular Security**: Add or remove security controls as needed
- **Flexible Ordering**: Control execution sequence through priorities
- **Extensibility**: Support for custom plugins and new security patterns
- **Clear Separation**: Distinct security and auditing concerns
- **Fail-Safe Design**: Security-first approach with safe defaults

This architecture enables you to build sophisticated security policies while maintaining clean, maintainable configurations.
