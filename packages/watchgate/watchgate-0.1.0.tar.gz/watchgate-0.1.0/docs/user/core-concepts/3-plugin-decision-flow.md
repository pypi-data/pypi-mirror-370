# Plugin Decision Flow

*[Home](../../README.md) > [User Guide](../README.md) > [Core Concepts](README.md) > Plugin Decision Flow*

Understanding how Watchgate processes plugin decisions is crucial for effective debugging, configuration, and compliance. This guide explains when and how plugin context (reasons and metadata) is preserved or replaced with generic information.

## Overview

Watchgate's plugin manager processes requests and responses through security plugins sequentially. The final decision that reaches your audit logs and error messages depends on whether plugins **deny**, **allow without modification**, or **allow with modification**.

## Decision Preservation Logic

### 1. Plugin Denies Request (Early Exit)
**Behavior**: Plugin metadata is **always preserved**
**Why**: Processing stops immediately when a plugin denies access

```python
# Example: Tool blocked by allowlist
PolicyDecision(
    allowed=False,
    reason="Tool 'delete_system_files' not in allowlist",
    metadata={"tool": "delete_system_files", "mode": "allowlist"}
)
```

**User Experience**:
- **Error Message**: "Tool 'delete_system_files' not in allowlist"
- **Audit Log**: Contains specific plugin reason and metadata
- **Debugging**: Clear indication of which plugin and why it blocked the request

### 2. All Plugins Allow Without Modification
**Behavior**: Plugin metadata is **replaced with generic information**
**Why**: No plugin performed meaningful work requiring specific context

```python
# Example: Request allowed by all plugins
PolicyDecision(
    allowed=True,
    reason="Request allowed by all security plugins",
    metadata={"plugin_count": 2}
)
```

**User Experience**:
- **Error Message**: Generic "allowed by all plugins" message
- **Audit Log**: Shows successful processing but no specific plugin details
- **Debugging**: Indicates normal processing without special handling

### 3. Plugin Allows with Modification
**Behavior**: Plugin metadata is **preserved from the modifying plugin**
**Why**: Plugin performed meaningful work (filtering, redaction, etc.) that should be documented

```python
# Example: PII detected and redacted
PolicyDecision(
    allowed=True,
    reason="PII detected and redacted: 2 SSNs removed from response",
    metadata={"pii_detected": ["ssn"], "redacted_count": 2},
    modified_response=redacted_response
)
```

**User Experience**:
- **Error Message**: "PII detected and redacted: 2 SSNs removed from response"
- **Audit Log**: Contains detailed information about what was modified
- **Debugging**: Clear indication of plugin actions taken

## Sequential Processing Behavior

When multiple plugins modify responses, the **last modifying plugin's metadata wins**:

```python
# Plugin 1: Removes administrative tools
PolicyDecision(
    allowed=True,
    reason="Administrative tools filtered from response",
    metadata={"tools_removed": 3},
    modified_response=filtered_response
)

# Plugin 2: Redacts PII from remaining tools
PolicyDecision(
    allowed=True,
    reason="PII redacted from tool descriptions",
    metadata={"pii_redacted": True},
    modified_response=redacted_response
)

# Final decision preserves Plugin 2's context
```

## Practical Examples

### Example 1: Tool Access Control

**Configuration**:
```yaml
plugins:
  security:
    - policy: "tool_allowlist"
      config:
        mode: "allowlist"
        tools: ["read_file", "list_directory"]
```

**Scenarios**:

| Request | Plugin Decision | Final Reason | Metadata Preserved? |
|---------|----------------|--------------|-------------------|
| `read_file` | Allow | "Request allowed by all security plugins" | ❌ Generic |
| `delete_file` | Deny | "Tool 'delete_file' not in allowlist" | ✅ Specific |
| `tools/list` | Allow + Filter | "Tools filtered to match allowlist policy" | ✅ Specific |

### Example 2: Content Filtering

**Configuration**:
```yaml
plugins:
  security:
    - policy: "presidio_pii"
      config:
        mode: "regex"
        action: "redact"
        entities: ["US_SSN", "EMAIL_ADDRESS"]
```

**Scenarios**:

| Response Content | Plugin Decision | Final Reason | Metadata Preserved? |
|------------------|----------------|--------------|-------------------|
| "Hello world" | Allow | "Response allowed by all security plugins" | ❌ Generic |
| "SSN: 123-45-6789" | Allow + Redact | "PII detected and redacted: 1 SSN" | ✅ Specific |
| "Email: user@example.com" | Allow + Redact | "PII detected and redacted: 1 email" | ✅ Specific |

## User Experience Impact

### Error Messages
Users see meaningful, actionable error messages instead of generic responses:

**Before Enhancement**:
```
Error: Response allowed by all security plugins
```

**After Enhancement**:
```
Error: PII detected and redacted: 2 SSNs and 1 email address removed from response
```

### Audit Logs
Compliance and debugging logs contain specific plugin information:

**Before Enhancement**:
```
2024-01-01 12:00:00 - REQUEST: tools/call - ALLOWED
```

**After Enhancement**:
```
2024-01-01 12:00:00 - REQUEST: tools/call - ALLOWED - Tool filtering applied: 3 administrative tools removed
```

### Debugging Information
Developers can understand exactly what plugins did:

**Generic Decision**:
- Limited debugging information
- Requires plugin-specific logging
- Unclear what processing occurred

**Preserved Decision**:
- Clear plugin actions documented
- Specific reasons for modifications
- Structured metadata for analysis

## Plugin Development Best Practices

### Meaningful Reasons
Write human-readable reason strings that explain the plugin's action:

```python
# Good
reason="PII detected and redacted: 2 SSNs removed from response"

# Avoid
reason="PII plugin processed request"
```

### Structured Metadata
Include structured data for programmatic processing:

```python
# Good
metadata={
    "pii_detected": ["ssn", "email"],
    "redacted_count": 3,
    "confidence_scores": [0.95, 0.87, 0.92]
}

# Avoid
metadata={"processed": True}
```

### Modification Indicators
Only use `modified_response` when the plugin actually changes content:

```python
# Good - Plugin modified response
if content_was_modified:
    return PolicyDecision(
        allowed=True,
        reason="Content filtered",
        metadata={"changes": "details"},
        modified_response=modified_content
    )

# Good - Plugin didn't modify response
return PolicyDecision(
    allowed=True,
    reason="Content review passed"
)
```

## Troubleshooting Plugin Decisions

### Check Plugin Configuration
Verify plugins are configured correctly:

```yaml
plugins:
  security:
    - policy: "your_plugin"
      enabled: true  # Ensure plugin is enabled
      config:
        # Verify configuration parameters
```

### Review Plugin Order
Plugin execution order affects which metadata is preserved:

```yaml
plugins:
  security:
    - policy: "tool_filter"
      priority: 10  # Executes first
    - policy: "pii_redactor"  
      priority: 20  # Executes second, metadata preserved if modifies
```

### Examine Audit Logs
Look for specific vs. generic decision reasons:

```
# Generic - no plugin modifications
"Request allowed by all security plugins"

# Specific - plugin performed work
"PII detected and redacted: 2 SSNs removed"
```

## Compliance Considerations

### Audit Trail Completeness
- **Blocking Actions**: Always logged with specific plugin reasons
- **Modification Actions**: Logged with detailed plugin context when responses are modified
- **Allow Actions**: Logged with generic context when no modifications occur

### Regulatory Requirements
- **GDPR**: PII processing actions documented in audit logs
- **HIPAA**: Health information filtering recorded with specific details
- **SOX**: Financial data access controls logged with plugin-specific reasons

### Data Retention
- Plugin metadata provides detailed audit trail for compliance reviews
- Structured metadata enables automated compliance reporting and analysis
- Specific reasons support forensic analysis and incident response

## Configuration Examples

### Comprehensive Security Setup
```yaml
plugins:
  security:
    - policy: "tool_allowlist"
      priority: 10
      config:
        mode: "allowlist"
        tools: ["read_file", "list_directory"]
        
    - policy: "presidio_pii"
      priority: 20
      config:
        mode: "regex"
        action: "redact"
        entities: ["US_SSN", "EMAIL_ADDRESS", "PHONE_NUMBER"]
        
    - policy: "content_filter"
      priority: 30
      config:
        blocked_patterns: ["password", "secret", "token"]
```

### Audit Integration
```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      config:
        file: "compliance.log"
        format: "detailed"  # Include plugin metadata
        
    - policy: "siem_integration"
      config:
        endpoint: "https://siem.example.com"
        include_metadata: true  # Forward plugin context
```

This plugin decision flow ensures that your audit logs, error messages, and debugging information contain the most relevant and actionable information possible, while maintaining backward compatibility with existing configurations.
