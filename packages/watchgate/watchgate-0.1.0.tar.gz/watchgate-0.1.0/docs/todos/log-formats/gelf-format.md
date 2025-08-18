# GelfAuditingPlugin Implementation Requirements

## Overview

GELF (Graylog Extended Log Format) is a structured logging format developed by Graylog to address the limitations of traditional syslog. It provides JSON-based structured logging with support for custom fields and is optimized for log aggregation and analysis.

**Implementation Approach**: Dedicated `GelfAuditingPlugin` class inheriting from `AuditingPlugin` base class for Graylog integration and structured log analysis.

**Note**: This is a first release implementation (v0.1.0) - no backward compatibility concerns. The new plugin architecture will be implemented directly.

## Implementation Requirements

### 1. Format Structure

**GELF Message Structure:**
```json
{
  "version": "1.1",
  "host": "watchgate-server",
  "short_message": "MCP request processed",
  "full_message": "MCP tools/call request for read_file processed successfully by tool_allowlist plugin",
  "timestamp": 1701435025.123456,
  "level": 6,
  "_event_type": "REQUEST",
  "_method": "tools/call",
  "_tool": "read_file",
  "_status": "ALLOWED",
  "_request_id": "123",
  "_plugin": "tool_allowlist",
  "_duration_ms": 45
}
```

### 2. Standard Library Implementation

**Core Requirements:**
- No external dependencies in runtime code
- Use only Python standard library
- Generate GELF 1.1 compliant messages
- Handle custom field prefixing correctly
- Support proper data type handling

**Implementation Class:**
```python
import json
import socket
import time
from typing import Dict, Any, Optional, Union

class GELFFormatter:
    def __init__(self, host: Optional[str] = None):
        self.version = "1.1"
        self.host = host or socket.gethostname()
    
    def _format_gelf_message(self, request: MCPRequest, data: Any, event_type: str) -> Dict[str, Any]:
        """Format Watchgate event as GELF message"""
        gelf_message = {
            "version": self.version,
            "host": self.host,
            "short_message": self._format_short_message(event_type, request, data),
            "timestamp": time.time()
        }
        
        # Add optional fields
        if self.include_full_message:
            gelf_message["full_message"] = self._format_full_message(event_type, request, data)
        
        level = self._map_to_syslog_level(event_type)
        if level is not None:
            gelf_message["level"] = level
        
        # Add custom fields (with underscore prefix)
        custom_fields = self._format_custom_fields(event_type, request, data)
        gelf_message.update(custom_fields)
        
        # Add configured custom fields
        for key, value in self.custom_fields.items():
            gelf_message[f"_{key}"] = value
        
        return gelf_message
    
    def _format_short_message(self, event_data: Dict[str, Any]) -> str:
        """Format short, human-readable message"""
        event_type = event_data.get('event_type', 'EVENT')
        method = event_data.get('method', '')
        status = event_data.get('status', '')
        
        if event_type == 'REQUEST':
            return f"MCP {method} request"
        elif event_type == 'RESPONSE':
            return f"MCP {method} response"
        elif event_type == 'SECURITY_BLOCK':
            return f"Security block: {method}"
        elif event_type == 'ERROR':
            return f"Error: {method}"
        else:
            return f"{event_type}: {method}"
    
    def _format_full_message(self, event_data: Dict[str, Any]) -> Optional[str]:
        """Format detailed message with context"""
        event_type = event_data.get('event_type', 'EVENT')
        method = event_data.get('method', '')
        tool = event_data.get('tool', '')
        status = event_data.get('status', '')
        plugin = event_data.get('plugin', '')
        reason = event_data.get('reason', '')
        
        parts = [f"MCP {method} {event_type.lower()}"]
        
        if tool:
            parts.append(f"for {tool}")
        
        if status:
            parts.append(f"- {status}")
        
        if plugin:
            parts.append(f"by {plugin} plugin")
        
        if reason:
            parts.append(f"({reason})")
        
        return " ".join(parts) if len(parts) > 1 else None
    
    def _format_timestamp(self, timestamp: Optional[Union[float, str]]) -> float:
        """Format timestamp as Unix epoch with decimal precision"""
        if timestamp is None:
            return time.time()
        
        if isinstance(timestamp, str):
            # Parse ISO format if needed
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.timestamp()
            except:
                return time.time()
        
        return float(timestamp)
    
    def _map_to_syslog_level(self, event_type: str) -> Optional[int]:
        """Map Watchgate event type to syslog level (0-7)"""
        mapping = {
            'REQUEST': 6,           # Info
            'RESPONSE': 6,          # Info
            'SECURITY_BLOCK': 4,    # Warning
            'REDACTION': 5,         # Notice
            'ERROR': 3,             # Error
            'UPSTREAM_ERROR': 3,    # Error
            'NOTIFICATION': 6,      # Info
            'TOOLS_FILTERED': 5     # Notice
        }
        return mapping.get(event_type)
    
    def _format_custom_fields(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format custom fields with underscore prefix"""
        custom_fields = {}
        
        # Field mappings (all custom fields must start with underscore)
        field_mappings = {
            'event_type': '_event_type',
            'method': '_method',
            'tool': '_tool',
            'status': '_status',
            'request_id': '_request_id',
            'plugin': '_plugin',
            'reason': '_reason',
            'duration_ms': '_duration_ms',
            'server_name': '_server_name'
        }
        
        for event_field, gelf_field in field_mappings.items():
            value = event_data.get(event_field)
            if value is not None:
                # Convert to appropriate type
                custom_fields[gelf_field] = self._convert_field_value(value)
        
        return custom_fields
    
    def _convert_field_value(self, value: Any) -> Union[str, int, float]:
        """Convert field value to GELF-compatible type"""
        # GELF doesn't support boolean values - they get dropped
        if isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, dict):
            # Convert dict to JSON string
            return json.dumps(value, separators=(',', ':'))
        elif isinstance(value, list):
            # Convert list to JSON string
            return json.dumps(value, separators=(',', ':'))
        else:
            return str(value)
    
    def validate_field_name(self, field_name: str) -> bool:
        """Validate GELF field name against specification"""
        # Must match regex: ^[\\w\\.\\-]*$
        import re
        return bool(re.match(r'^[\w\.\-]*$', field_name))
```

### 3. Watchgate Event Mapping

**Syslog Level Mappings:**
```python
GELF_LEVEL_MAPPINGS = {
    'REQUEST': 6,           # Info
    'RESPONSE': 6,          # Info
    'SECURITY_BLOCK': 4,    # Warning
    'REDACTION': 5,         # Notice
    'ERROR': 3,             # Error
    'UPSTREAM_ERROR': 3,    # Error
    'NOTIFICATION': 6,      # Info
    'TOOLS_FILTERED': 5     # Notice
}
```

**Field Validation:**
```python
def validate_gelf_message(self, gelf_dict: Dict[str, Any]) -> List[str]:
    """Validate GELF message structure"""
    errors = []
    
    # Required fields
    if 'version' not in gelf_dict:
        errors.append("Missing required field: version")
    elif gelf_dict['version'] != "1.1":
        errors.append("Version must be '1.1'")
    
    if 'host' not in gelf_dict:
        errors.append("Missing required field: host")
    
    if 'short_message' not in gelf_dict:
        errors.append("Missing required field: short_message")
    
    # Field name validation
    for field_name in gelf_dict.keys():
        if field_name.startswith('_'):
            if not self.validate_field_name(field_name[1:]):  # Remove underscore
                errors.append(f"Invalid custom field name: {field_name}")
        elif field_name == '_id':
            errors.append("Reserved field name not allowed: _id")
    
    return errors
```

### 4. Data Type Handling

**GELF Data Type Limitations:**
```python
def handle_gelf_data_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle GELF data type limitations"""
    processed = {}
    
    for key, value in data.items():
        if isinstance(value, bool):
            # Boolean values are dropped by Graylog - convert to string
            processed[key] = "true" if value else "false"
        elif isinstance(value, dict):
            # Nested objects not supported - flatten or convert to JSON
            processed[key] = json.dumps(value, separators=(',', ':'))
        elif isinstance(value, list):
            # Arrays have limited support - convert to JSON
            processed[key] = json.dumps(value, separators=(',', ':'))
        elif value is None:
            # Skip None values
            continue
        else:
            processed[key] = value
    
    return processed
```

### 5. Configuration Integration

**Configuration Schema:**
```yaml
plugins:
  auditing:
    - policy: "gelf_auditing"
      config:
        output_file: "logs/audit.gelf"
        host: "watchgate-server"       # Override hostname
        include_full_message: true       # Include detailed message
        flatten_nested_objects: true     # Flatten dict/list values
        timestamp_precision: "milliseconds"  # milliseconds, microseconds
        custom_fields:                   # Additional custom fields
          environment: "production"
          service: "mcp-proxy"
        critical: false                  # Plugin criticality
```

**Configuration Schema (Pydantic):**
```python
class GelfAuditingConfig(BaseModel):
    output_file: str
    host: Optional[str] = None
    include_full_message: bool = True
    flatten_nested_objects: bool = True
    timestamp_precision: Literal["milliseconds", "microseconds"] = "milliseconds"
    custom_fields: Dict[str, Any] = {}
    critical: bool = False
```

## Testing Strategy

### Unit Tests (Standard Library Only)

**Test GELF message generation:**
```python
def test_gelf_format_basic():
    """Test basic GELF message formatting"""
    config = {
        'output_file': 'test.gelf',
        'host': 'test-host'
    }
    plugin = GelfAuditingPlugin(config)
    
    request = create_test_mcp_request()
    decision = PolicyDecision(allowed=True)
    
    gelf_message = plugin._format_gelf_message(request, decision, "REQUEST")
        'status': 'ALLOWED',
        'timestamp': 1701435025.123456,
        'request_id': '123'
    }
    
    result = formatter.format_event(event)
    gelf_message = json.loads(result)
    
    assert gelf_message['version'] == '1.1'
    assert gelf_message['host'] == 'test-host'
    assert gelf_message['short_message'] == 'MCP tools/call request'
    assert gelf_message['level'] == 6
    assert gelf_message['_event_type'] == 'REQUEST'
    assert gelf_message['_request_id'] == '123'
```

**Test custom field handling:**
```python
def test_gelf_custom_fields():
    """Test custom field formatting with underscore prefix"""
    formatter = GELFFormatter()
    event = {
        'event_type': 'SECURITY_BLOCK',
        'method': 'tools/call',
        'tool': 'delete_file',
        'plugin': 'tool_allowlist',
        'reason': 'Tool not in allowlist'
    }
    
    result = formatter.format_event(event)
    gelf_message = json.loads(result)
    
    # All custom fields should have underscore prefix
    assert gelf_message['_event_type'] == 'SECURITY_BLOCK'
    assert gelf_message['_method'] == 'tools/call'
    assert gelf_message['_tool'] == 'delete_file'
    assert gelf_message['_plugin'] == 'tool_allowlist'
    assert gelf_message['_reason'] == 'Tool not in allowlist'
```

**Test data type conversion:**
```python
def test_gelf_data_type_conversion():
    """Test GELF data type handling"""
    formatter = GELFFormatter()
    event = {
        'event_type': 'RESPONSE',
        'duration_ms': 45,  # Integer
        'success': True,    # Boolean
        'metadata': {'key': 'value'},  # Dict
        'empty_field': None  # None value
    }
    
    result = formatter.format_event(event)
    gelf_message = json.loads(result)
    
    assert gelf_message['_duration_ms'] == 45  # Integer preserved
    assert gelf_message['_success'] == 'true'  # Boolean converted to string
    assert gelf_message['_metadata'] == '{"key":"value"}'  # Dict converted to JSON
    assert '_empty_field' not in gelf_message  # None values skipped
```

**Test timestamp formatting:**
```python
def test_gelf_timestamp_formatting():
    """Test timestamp formatting"""
    formatter = GELFFormatter()
    
    # Test with float timestamp
    timestamp = 1701435025.123456
    formatted = formatter._format_timestamp(timestamp)
    assert formatted == 1701435025.123456
    
    # Test with ISO string
    iso_timestamp = "2023-12-01T14:30:25.123456Z"
    formatted = formatter._format_timestamp(iso_timestamp)
    assert isinstance(formatted, float)
    assert formatted > 0
```

### Integration Tests (Watchgate Dependencies)

**Test plugin lifecycle:**
```python
def test_gelf_plugin_integration():
    """Test GELF format with file auditing plugin"""
    config = {
        'output_file': 'test.log',
        'format': 'gelf',
        'gelf_config': {
            'host': 'test-watchgate',
            'include_full_message': True
        }
    }
    
    plugin = FileAuditingPlugin(config)
    test_event = create_test_mcp_request()
    plugin.log_request(test_event, PolicyDecision(allowed=True))
    
    # Verify file output
    with open('test.log', 'r') as f:
        output = f.read()
        gelf_message = json.loads(output)
        assert gelf_message['version'] == '1.1'
        assert gelf_message['host'] == 'test-watchgate'
        assert 'full_message' in gelf_message
```

**Test configuration validation:**
```python
def test_gelf_config_validation():
    """Test GELF configuration validation"""
    valid_config = {
        'format': 'gelf',
        'output_file': 'audit.log',
        'gelf_config': {
            'host': 'watchgate-server',
            'include_full_message': True
        }
    }
    
    errors = validate_auditing_config(valid_config)
    assert len(errors) == 0
```

### Validation Tests (Test-Only Dependencies)

**Test with pygelf:**
```python
def test_gelf_with_pygelf():
    """Test GELF format with pygelf library"""
    pytest.importorskip("pygelf")
    
    formatter = GELFFormatter()
    event = create_test_event()
    gelf_json = formatter.format_event(event)
    
    # Parse with pygelf (indirectly via JSON validation)
    gelf_message = json.loads(gelf_json)
    
    # Validate structure
    assert gelf_message['version'] == '1.1'
    assert 'host' in gelf_message
    assert 'short_message' in gelf_message
    assert 'timestamp' in gelf_message
```

**Test with Graylog mock server:**
```python
def test_gelf_with_mock_graylog():
    """Test GELF format with mock Graylog server"""
    pytest.importorskip("console_gelf_server")
    
    formatter = GELFFormatter()
    event = create_test_event()
    gelf_json = formatter.format_event(event)
    
    # This would require setting up a mock GELF server
    # For now, just validate JSON structure
    gelf_message = json.loads(gelf_json)
    
    # Validate required fields
    required_fields = ['version', 'host', 'short_message']
    for field in required_fields:
        assert field in gelf_message
```

### Compliance Tests

**Test GELF 1.1 specification compliance:**
```python
def test_gelf_specification_compliance():
    """Test adherence to GELF 1.1 specification"""
    formatter = GELFFormatter()
    event = create_comprehensive_test_event()
    gelf_json = formatter.format_event(event)
    
    gelf_message = json.loads(gelf_json)
    
    # Test required fields
    assert gelf_message['version'] == '1.1'
    assert 'host' in gelf_message
    assert 'short_message' in gelf_message
    
    # Test field naming
    for field_name in gelf_message.keys():
        if field_name.startswith('_'):
            # Custom fields must match regex
            assert formatter.validate_field_name(field_name[1:])
        
        # Must not use reserved _id field
        assert field_name != '_id'
    
    # Test data types
    for value in gelf_message.values():
        # Should only contain JSON-compatible types
        assert isinstance(value, (str, int, float, type(None)))
```

## External Validation Tools

### Test-Only Dependencies

**Python Libraries:**
```python
# pyproject.toml
[project.optional-dependencies]
test = [
    "pygelf>=0.4.0",  # GELF library for validation
    "graypy>=2.1.0",  # Alternative GELF library
]
```

**Command-Line Tools:**
```bash
# console-gelf-server for testing
npm install -g console-gelf-server

# Usage
console-gelf-server --port 12201
```

### CI/CD Integration

**GitHub Actions validation:**
```yaml
- name: Install GELF Validators
  run: |
    pip install pygelf graypy
    npm install -g console-gelf-server
    
- name: Test GELF Format
  run: |
    pytest tests/validation/test_gelf_compliance.py -v
```

## Risk Assessment

### Implementation Complexity: **Moderate**

**Challenges:**
- Data type limitations (no booleans, no nested objects)
- Custom field naming restrictions
- Timestamp precision handling
- Field validation requirements

**Mitigation Strategies:**
- Comprehensive data type conversion
- Field name validation
- Clear documentation of limitations
- Extensive test coverage

### Security Considerations

**Potential Issues:**
- JSON injection vulnerabilities
- Information disclosure in custom fields
- Field name validation bypass
- Timestamp manipulation

**Safeguards:**
- JSON serialization security
- Field name validation
- Input sanitization
- Secure timestamp generation

## Acceptance Criteria

### Implementation Complete When:
- [ ] GelfAuditingPlugin class implemented inheriting from AuditingPlugin
- [ ] GELF message formatting implemented using only standard library
- [ ] All Watchgate event types mapped to appropriate syslog levels
- [ ] Custom field handling with underscore prefixing
- [ ] Data type conversion handles GELF limitations
- [ ] Timestamp formatting supports decimal precision
- [ ] Field name validation follows GELF specification
- [ ] Configuration integration with GELF-specific settings
- [ ] Unit tests cover all formatting scenarios
- [ ] Integration tests validate plugin lifecycle
- [ ] Validation tests pass with pygelf library
- [ ] Compliance tests verify GELF 1.1 specification
- [ ] Performance benchmarks meet requirements
- [ ] Security review completed
- [ ] Documentation updated with GELF format examples

### Success Metrics:
- **Format Compliance**: 100% of messages accepted by Graylog server
- **Performance**: GELF formatting adds <8ms overhead per message
- **Security**: No JSON injection vulnerabilities identified
- **Compatibility**: Works with Graylog and other GELF-compatible systems