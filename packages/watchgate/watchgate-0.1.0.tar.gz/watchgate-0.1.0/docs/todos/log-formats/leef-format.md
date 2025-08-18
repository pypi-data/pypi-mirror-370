# LeefAuditingPlugin Implementation Requirements

## Overview

LEEF (Log Event Extended Format) is a proprietary event format developed by IBM Security for IBM QRadar SIEM integration. It provides a structured way to send security events to QRadar, enabling proper categorization, parsing, and analysis within the platform.

**Implementation Approach**: Dedicated `LeefAuditingPlugin` class inheriting from `AuditingPlugin` base class for IBM QRadar integration.

**Note**: This is a first release implementation (v0.1.0) - no backward compatibility concerns. The new plugin architecture will be implemented directly.

## Implementation Requirements

### 1. Format Structure

**LEEF 2.0 Format:**
```
[Syslog Header] LEEF:2.0|Vendor|Product|Version|EventID|Delimiter|key1=value1[delimiter]key2=value2[delimiter]...
```

**Example Output:**
```
Dec 01 14:30:25 watchgate-host LEEF:2.0|Watchgate|MCP Gateway|1.0.0|100|^|devTime=Dec 01 2023 14:30:25^devTimeFormat=MMM dd yyyy HH:mm:ss^src=127.0.0.1^dst=upstream-server^usrName=system^cat=MCP Request^sev=5^msg=MCP tools/call request processed
```

### 2. LeefAuditingPlugin Implementation

**Core Requirements:**
- No external dependencies in runtime code
- Use only Python standard library
- Support both LEEF 1.0 and 2.0 formats
- Handle field delimiter customization
- Proper timestamp formatting
- Dedicated plugin class for LEEF functionality

**Implementation Class:**
```python
import socket
import time
from datetime import datetime
from typing import Dict, Any, Optional
from watchgate.utils.version import get_watchgate_version

class LeefAuditingPlugin(AuditingPlugin):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.version = config.get('leef_version', '2.0')
        self.delimiter = config.get('delimiter', '^')
        self.vendor = config.get('vendor', 'Watchgate')
        self.product = config.get('product', 'MCP Gateway')
        self.product_version = config.get('product_version') or get_watchgate_version()
        self.hostname = socket.gethostname()
        self.include_syslog_header = config.get('include_syslog_header', True)
    
    async def log_request(self, request: MCPRequest, decision: PolicyDecision) -> None:
        """Log MCP request as LEEF message"""
        leef_message = self._format_leef_message(request, decision, "REQUEST")
        await self._write_to_file(leef_message)
    
    async def log_response(self, request: MCPRequest, response: MCPResponse) -> None:
        """Log MCP response as LEEF message"""
        leef_message = self._format_leef_message(request, response, "RESPONSE")
        await self._write_to_file(leef_message)
    
    def _format_leef_message(self, request: MCPRequest, data: Any, event_type: str) -> str:
        """Format Watchgate event as LEEF message"""
        if self.version == "2.0":
            return self._format_leef_20(request, data, event_type)
        else:
            return self._format_leef_10(request, data, event_type)
        elif self.version == "1.0":
            return self._format_leef_10(event_data)
        else:
            raise ValueError(f"Unsupported LEEF version: {self.version}")
    
    def _format_leef_20(self, event_data: Dict[str, Any]) -> str:
        """Format LEEF 2.0 message"""
        # LEEF 2.0 Header
        event_id = self._map_event_id(event_data.get('event_type'))
        header = f"LEEF:{self.version}|{self.vendor}|{self.product}|{self.product_version}|{event_id}|{self.delimiter}|"
        
        # LEEF 2.0 Attributes
        attributes = self._format_attributes(event_data)
        attribute_string = self.delimiter.join(f"{key}={value}" for key, value in attributes.items())
        
        # Add syslog header
        syslog_header = self._format_syslog_header(event_data.get('timestamp'))
        
        return f"{syslog_header} {header}{attribute_string}"
    
    def _format_leef_10(self, event_data: Dict[str, Any]) -> str:
        """Format LEEF 1.0 message (uses tab delimiter)"""
        # LEEF 1.0 Header (no delimiter field)
        event_id = self._map_event_id(event_data.get('event_type'))
        header = f"LEEF:{self.version}|{self.vendor}|{self.product}|{self.product_version}|{event_id}|"
        
        # LEEF 1.0 Attributes (tab-separated)
        attributes = self._format_attributes(event_data)
        attribute_string = "\t".join(f"{key}={value}" for key, value in attributes.items())
        
        # Add syslog header
        syslog_header = self._format_syslog_header(event_data.get('timestamp'))
        
        return f"{syslog_header} {header}{attribute_string}"
    
    def _format_syslog_header(self, timestamp: Optional[float]) -> str:
        """Format syslog header (RFC 3164 format)"""
        if timestamp:
            dt = datetime.fromtimestamp(timestamp)
        else:
            dt = datetime.now()
        
        # Format: Mmm dd HH:MM:SS hostname
        return f"{dt.strftime('%b %d %H:%M:%S')} {self.hostname}"
    
    def _map_event_id(self, event_type: str) -> str:
        """Map Watchgate event type to LEEF event ID"""
        mapping = {
            'REQUEST': '100',
            'RESPONSE': '101',
            'SECURITY_BLOCK': '200',
            'REDACTION': '201',
            'ERROR': '400',
            'UPSTREAM_ERROR': '401',
            'NOTIFICATION': '300',
            'TOOLS_FILTERED': '202'
        }
        return mapping.get(event_type, '999')
    
    def _format_attributes(self, event_data: Dict[str, Any]) -> Dict[str, str]:
        """Format event attributes for LEEF"""
        attributes = {}
        
        # Standard LEEF attributes
        if event_data.get('timestamp'):
            dt = datetime.fromtimestamp(event_data['timestamp'])
            attributes['devTime'] = dt.strftime('%b %d %Y %H:%M:%S')
            attributes['devTimeFormat'] = 'MMM dd yyyy HH:mm:ss'
        
        # Map Watchgate fields to LEEF attributes
        field_mappings = {
            'request_id': 'identSrc',
            'method': 'resource',
            'tool': 'proto',
            'status': 'result',
            'plugin': 'policy',
            'reason': 'msg',
            'duration_ms': 'rt',
            'server_name': 'dhost'
        }
        
        for event_field, leef_field in field_mappings.items():
            value = event_data.get(event_field)
            if value is not None:
                attributes[leef_field] = self._escape_value(str(value))
        
        # Add severity
        attributes['sev'] = str(self._map_severity(event_data.get('event_type')))
        
        # Add category
        attributes['cat'] = self._map_category(event_data.get('event_type'))
        
        # Add source/destination (default to localhost)
        attributes['src'] = '127.0.0.1'
        if event_data.get('server_name'):
            attributes['dst'] = event_data['server_name']
        
        return attributes
    
    def _map_severity(self, event_type: str) -> int:
        """Map Watchgate event type to LEEF severity (1-10)"""
        mapping = {
            'REQUEST': 5,           # Medium
            'RESPONSE': 5,          # Medium
            'SECURITY_BLOCK': 8,    # High
            'REDACTION': 6,         # Medium-High
            'ERROR': 9,             # Very High
            'UPSTREAM_ERROR': 8,    # High
            'NOTIFICATION': 4,      # Low-Medium
            'TOOLS_FILTERED': 6     # Medium-High
        }
        return mapping.get(event_type, 5)
    
    def _map_category(self, event_type: str) -> str:
        """Map Watchgate event type to LEEF category"""
        mapping = {
            'REQUEST': 'MCP Request',
            'RESPONSE': 'MCP Response',
            'SECURITY_BLOCK': 'Security Block',
            'REDACTION': 'Content Redaction',
            'ERROR': 'System Error',
            'UPSTREAM_ERROR': 'Upstream Error',
            'NOTIFICATION': 'MCP Notification',
            'TOOLS_FILTERED': 'Tool Filtering'
        }
        return mapping.get(event_type, 'MCP Event')
    
    def _escape_value(self, value: str) -> str:
        """Escape LEEF attribute values"""
        # LEEF escaping is not well-defined, but we should escape the delimiter
        if self.version == "2.0":
            return value.replace(self.delimiter, f"\\{self.delimiter}")
        else:
            return value.replace("\t", "\\t")
```

### 3. Watchgate Event Mapping

**Event ID Mappings:**
```python
LEEF_EVENT_ID_MAPPINGS = {
    'REQUEST': '100',
    'RESPONSE': '101',
    'SECURITY_BLOCK': '200',
    'REDACTION': '201',
    'ERROR': '400',
    'UPSTREAM_ERROR': '401',
    'NOTIFICATION': '300',
    'TOOLS_FILTERED': '202'
}
```

**Severity Mappings (1-10 scale):**
```python
LEEF_SEVERITY_MAPPINGS = {
    'REQUEST': 5,           # Medium
    'RESPONSE': 5,          # Medium
    'SECURITY_BLOCK': 8,    # High
    'REDACTION': 6,         # Medium-High
    'ERROR': 9,             # Very High
    'UPSTREAM_ERROR': 8,    # High
    'NOTIFICATION': 4,      # Low-Medium
    'TOOLS_FILTERED': 6     # Medium-High
}
```

### 4. Timestamp Handling

**Device Time Formatting:**
```python
def format_device_time(self, timestamp: Optional[float]) -> Dict[str, str]:
    """Format device timestamp for LEEF"""
    if timestamp:
        dt = datetime.fromtimestamp(timestamp)
    else:
        dt = datetime.now()
    
    return {
        'devTime': dt.strftime('%b %d %Y %H:%M:%S'),
        'devTimeFormat': 'MMM dd yyyy HH:mm:ss'
    }
```

### 5. Configuration Integration

**Configuration Schema:**
```yaml
plugins:
  auditing:
    - policy: "leef_auditing"
      config:
        output_file: "logs/audit.leef"
        leef_version: "2.0"             # "1.0" or "2.0"
        delimiter: "^"                  # LEEF 2.0 delimiter
        vendor: "Watchgate"            # Override vendor
        product: "MCP Gateway"            # Override product
        product_version: "auto"         # "auto" or explicit version override
        include_syslog_header: true     # Include syslog header
        critical: false                 # Plugin criticality
```

**Configuration Schema (Pydantic):**
```python
class LeefAuditingConfig(BaseModel):
    output_file: str
    leef_version: Literal["1.0", "2.0"] = "2.0"
    delimiter: str = "^"
    vendor: str = "Watchgate"
    product: str = "MCP Gateway"
    product_version: Optional[str] = None
    include_syslog_header: bool = True
    critical: bool = False
```

## Testing Strategy

### Unit Tests (Standard Library Only)

**Test LEEF message generation:**
```python
def test_leef_format_20():
    """Test LEEF 2.0 message formatting"""
    config = {
        'output_file': 'test.leef',
        'leef_version': '2.0',
        'delimiter': '^'
    }
    plugin = LeefAuditingPlugin(config)
    
    request = create_test_mcp_request()
    decision = PolicyDecision(allowed=True)
    
    result = plugin._format_leef_message(request, decision, "REQUEST")
        'method': 'tools/call',
        'tool': 'read_file',
        'status': 'ALLOWED',
        'timestamp': 1701435025.123456,
        'request_id': '123',
        'plugin': 'tool_allowlist'
    }
    
    result = formatter.format_event(event)
    
    # Check LEEF 2.0 header
    assert 'LEEF:2.0|Watchgate|MCP Gateway|1.0.0|100|^|' in result
    
    # Check attributes
    assert 'identSrc=123' in result
    assert 'resource=tools/call' in result
    assert 'proto=read_file' in result
    assert 'sev=5' in result
    assert 'cat=MCP Request' in result

def test_leef_format_10():
    """Test LEEF 1.0 message formatting"""
    formatter = LEEFFormatter(version="1.0")
    event = {
        'event_type': 'SECURITY_BLOCK',
        'method': 'tools/call',
        'tool': 'delete_file',
        'reason': 'Tool not in allowlist'
    }
    
    result = formatter.format_event(event)
    
    # Check LEEF 1.0 header (no delimiter field)
    assert 'LEEF:1.0|Watchgate|MCP Gateway|1.0.0|200|' in result
    
    # Check tab-separated attributes
    assert '\t' in result
    assert 'sev=8' in result
    assert 'cat=Security Block' in result
```

**Test event ID mapping:**
```python
def test_leef_event_id_mapping():
    """Test event type to LEEF event ID mapping"""
    formatter = LEEFFormatter()
    
    assert formatter._map_event_id('REQUEST') == '100'
    assert formatter._map_event_id('SECURITY_BLOCK') == '200'
    assert formatter._map_event_id('ERROR') == '400'
    assert formatter._map_event_id('UNKNOWN') == '999'
```

**Test severity mapping:**
```python
def test_leef_severity_mapping():
    """Test event type to LEEF severity mapping"""
    formatter = LEEFFormatter()
    
    assert formatter._map_severity('REQUEST') == 5
    assert formatter._map_severity('SECURITY_BLOCK') == 8
    assert formatter._map_severity('ERROR') == 9
```

**Test delimiter escaping:**
```python
def test_leef_delimiter_escaping():
    """Test LEEF delimiter escaping"""
    formatter = LEEFFormatter(version="2.0", delimiter="^")
    
    # Test escaping custom delimiter
    escaped = formatter._escape_value("test^value")
    assert escaped == "test\\^value"
    
    # Test LEEF 1.0 tab escaping
    formatter_10 = LEEFFormatter(version="1.0")
    escaped = formatter_10._escape_value("test\tvalue")
    assert escaped == "test\\tvalue"

def test_leef_dynamic_version():
    """Test dynamic product version detection"""
    # Test with explicit version
    formatter = LEEFFormatter(product_version="2.0.0")
    assert formatter.product_version == "2.0.0"
    
    # Test with automatic version detection (uses centralized utility)
    formatter = LEEFFormatter()
    assert formatter.product_version != "unknown"  # Should get actual version
    
    # Test version appears in output
    event = {'event_type': 'REQUEST', 'method': 'tools/call'}
    result = formatter.format_event(event)
    assert f'|{formatter.product_version}|' in result
```

### Integration Tests (Watchgate Dependencies)

**Test plugin lifecycle:**
```python
def test_leef_plugin_integration():
    """Test LEEF format with file auditing plugin"""
    config = {
        'output_file': 'test.log',
        'format': 'leef',
        'leef_config': {
            'version': '2.0',
            'delimiter': '^',
            'vendor': 'TestVendor'
        }
    }
    
    plugin = FileAuditingPlugin(config)
    test_event = create_test_mcp_request()
    plugin.log_request(test_event, PolicyDecision(allowed=True))
    
    # Verify file output
    with open('test.log', 'r') as f:
        output = f.read()
        assert 'LEEF:2.0|TestVendor|' in output
        assert '^' in output  # Custom delimiter
```

**Test configuration validation:**
```python
def test_leef_config_validation():
    """Test LEEF configuration validation"""
    valid_config = {
        'format': 'leef',
        'output_file': 'audit.log',
        'leef_config': {
            'version': '2.0',
            'delimiter': '^',
            'include_syslog_header': True
        }
    }
    
    errors = validate_auditing_config(valid_config)
    assert len(errors) == 0
    
    # Test invalid version
    invalid_config = valid_config.copy()
    invalid_config['leef_config']['version'] = '3.0'
    errors = validate_auditing_config(invalid_config)
    assert len(errors) > 0
```

### Validation Tests (Test-Only Dependencies)

**Test with python-LEEF library:**
```python
def test_leef_with_python_leef():
    """Test LEEF format with python-LEEF library"""
    # Note: python-LEEF library is incomplete/abandoned
    # This test would need a mock or alternative validation
    formatter = LEEFFormatter()
    event = create_test_event()
    leef_message = formatter.format_event(event)
    
    # Basic validation - check header structure
    assert leef_message.startswith('Dec') or leef_message.startswith('Jan')  # Syslog header
    assert 'LEEF:2.0|Watchgate|MCP Gateway|1.0.0|' in leef_message
```

**Test with QRadar ingestion simulation:**
```python
def test_leef_qradar_simulation():
    """Test LEEF format for QRadar compatibility"""
    formatter = LEEFFormatter()
    events = [
        create_test_request(),
        create_test_security_block(),
        create_test_error()
    ]
    
    for event in events:
        leef_message = formatter.format_event(event)
        
        # Validate structure expected by QRadar
        parts = leef_message.split(' ', 4)  # Split syslog header
        leef_part = parts[4] if len(parts) > 4 else leef_message
        
        # Should have pipe-separated header
        header_parts = leef_part.split('|')
        assert len(header_parts) >= 6  # LEEF:version|vendor|product|version|eventid|delimiter
        assert header_parts[0] == 'LEEF:2.0'
```

### Compliance Tests

**Test LEEF specification compliance:**
```python
def test_leef_specification_compliance():
    """Test adherence to LEEF specification"""
    formatter = LEEFFormatter()
    event = create_comprehensive_test_event()
    leef_message = formatter.format_event(event)
    
    # Test header structure
    assert 'LEEF:2.0|' in leef_message
    
    # Test required fields
    header_parts = leef_message.split('|')
    assert len(header_parts) >= 6
    assert header_parts[0].endswith('LEEF:2.0')  # After syslog header
    assert header_parts[1] == 'Watchgate'  # Vendor
    assert header_parts[2] == 'MCP Gateway'   # Product
    assert header_parts[3] == '1.0.0'       # Version
    assert header_parts[4].isdigit()        # Event ID
    assert header_parts[5] == '^'           # Delimiter
    
    # Test attribute format
    attributes_part = header_parts[6]
    assert '=' in attributes_part
    assert '^' in attributes_part  # Delimiter between attributes
```

## External Validation Tools

### Test-Only Dependencies

**Python Libraries:**
```python
# pyproject.toml
[project.optional-dependencies]
test = [
    # Note: python-LEEF is incomplete, we may need custom validation
    # or use QRadar simulation for testing
]
```

**Command-Line Tools:**
```bash
# No specific LEEF command-line validators available
# Testing requires QRadar environment or custom validation
```

### CI/CD Integration

**GitHub Actions validation:**
```yaml
- name: Test LEEF Format
  run: |
    # Custom LEEF validation since no standard tools exist
    pytest tests/validation/test_leef_compliance.py -v
```

## Risk Assessment

### Implementation Complexity: **Moderate-High**

**Challenges:**
- Limited external validation tools
- Version differences (1.0 vs 2.0)
- Delimiter handling complexity
- Timestamp format requirements
- QRadar-specific expectations

**Mitigation Strategies:**
- Comprehensive test coverage
- Both version support
- Clear delimiter configuration
- Reference implementation testing
- Documentation of QRadar compatibility

### Security Considerations

**Potential Issues:**
- Log injection via delimiter manipulation
- Information disclosure in LEEF messages
- Timestamp manipulation
- QRadar-specific vulnerabilities

**Safeguards:**
- Proper delimiter escaping
- Input validation for all fields
- Secure timestamp generation
- Regular security review

## Acceptance Criteria

### Implementation Complete When:
- [ ] LeefAuditingPlugin class implemented inheriting from AuditingPlugin
- [ ] LEEF message formatting implemented for both versions 1.0 and 2.0
- [ ] All Watchgate event types mapped to LEEF event IDs
- [ ] Severity mapping implemented (1-10 scale)
- [ ] Delimiter handling works correctly for both versions
- [ ] Timestamp formatting matches LEEF requirements
- [ ] Attribute escaping prevents delimiter conflicts
- [ ] Configuration integration with LEEF-specific settings
- [ ] Unit tests cover all formatting scenarios
- [ ] Integration tests validate plugin lifecycle
- [ ] Compliance tests verify LEEF specification adherence
- [ ] Performance benchmarks meet requirements
- [ ] Security review completed
- [ ] Documentation updated with LEEF format examples

### Success Metrics:
- **Format Compliance**: Messages structured correctly for QRadar ingestion
- **Performance**: LEEF formatting adds <10ms overhead per message
- **Security**: No delimiter injection vulnerabilities identified
- **Compatibility**: Works with IBM QRadar SIEM platform