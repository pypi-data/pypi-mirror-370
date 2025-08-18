# SyslogAuditingPlugin Implementation Requirements

## Overview

Syslog is a standard protocol for centralized logging that allows systems to send log messages to a remote server. We will implement RFC 5424 (modern standard) with RFC 3164 compatibility for maximum interoperability.

**Implementation Approach**: Dedicated `SyslogAuditingPlugin` class inheriting from `AuditingPlugin` base class for centralized logging and SIEM integration.

**Note**: This is a first release implementation (v0.1.0) - no backward compatibility concerns. The new plugin architecture will be implemented directly.

## Implementation Requirements

### 1. Format Structure

**RFC 5424 Format:**
```
<Priority>Version Timestamp Hostname App-Name ProcID MsgID [Structured-Data] Message
```

**Example Output:**
```
<165>1 2023-12-01T14:30:25.123Z watchgate-host watchgate 1234 REQUEST [watchgate@32473 event_type="REQUEST" method="tools/call" tool="read_file" status="ALLOWED" request_id="123"] MCP request processed successfully
```

### 2. FileAuditingPlugin Integration

**Core Requirements:**
- No external dependencies in runtime code
- Use only Python standard library
- Support both RFC 5424 and RFC 3164 output
- Handle priority calculation correctly
- Proper timestamp formatting
- Implement directly in FileAuditingPlugin class

**Implementation Approach:**
```python
class FileAuditingPlugin(AuditingPlugin):
    def __init__(self, config: Dict[str, Any]):
        # ... existing initialization ...
        
        # Syslog-specific configuration
        if self.config.format == "syslog":
            syslog_config = self.config.syslog_config or {}
            self.syslog_facility = syslog_config.get("facility", 16)  # local0
            self.syslog_rfc_format = syslog_config.get("rfc_format", "5424")
            self.syslog_app_name = syslog_config.get("app_name", "watchgate")
            self.syslog_hostname = self._get_hostname(syslog_config.get("hostname", "auto"))
            self.syslog_proc_id = str(os.getpid())
            self.include_structured_data = syslog_config.get("include_structured_data", True)
    
    def _format_syslog_message(self, event_data: Dict[str, Any]) -> str:
        """Format Watchgate event as syslog message"""
        if self.syslog_rfc_format == "5424":
            return self._format_rfc5424(event_data)
        elif self.syslog_rfc_format == "3164":
            return self._format_rfc3164(event_data)
        else:
            raise ValueError(f"Unsupported RFC format: {self.syslog_rfc_format}")
    
    def _calculate_syslog_priority(self, severity: int) -> int:
        """Calculate syslog priority: Facility * 8 + Severity"""
        return self.syslog_facility * 8 + severity
```

### 3. Watchgate Event Mapping

**Severity Level Mappings:**
```python
SYSLOG_SEVERITY_MAPPINGS = {
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

**Message ID Mappings:**
```python
SYSLOG_MSGID_MAPPINGS = {
    'REQUEST': 'REQ',
    'RESPONSE': 'RESP',
    'SECURITY_BLOCK': 'BLOCK',
    'REDACTION': 'REDACT',
    'ERROR': 'ERR',
    'UPSTREAM_ERROR': 'UERR',
    'NOTIFICATION': 'NOTIF',
    'TOOLS_FILTERED': 'FILTER'
}
```

### 4. Structured Data Implementation

**RFC 5424 Structured Data (FileAuditingPlugin methods):**
```python
def _format_structured_data(self, event_data: Dict[str, Any]) -> str:
    """Format structured data section for RFC 5424"""
    if not self.include_structured_data:
        return "-"
        
    sd_id = "watchgate@32473"  # Private enterprise number
    
    # Core fields
    sd_params = []
    if event_data.get('event_type'):
        sd_params.append(f'event_type="{self._escape_sd_value(event_data["event_type"])}"')
    if event_data.get('method'):
        sd_params.append(f'method="{self._escape_sd_value(event_data["method"])}"')
    if event_data.get('request_id'):
        sd_params.append(f'request_id="{self._escape_sd_value(event_data["request_id"])}"')
    if event_data.get('plugin'):
        sd_params.append(f'plugin="{self._escape_sd_value(event_data["plugin"])}"')
    
    if sd_params:
        return f'[{sd_id} {" ".join(sd_params)}]'
    else:
        return "-"  # No structured data

def _escape_sd_value(self, value: str) -> str:
    """Escape structured data parameter values"""
    return str(value).replace('\\', '\\\\').replace('"', '\\"').replace(']', '\\]')
```

### 5. Configuration Integration

**Configuration Schema:**
```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      config:
        format: "syslog"
        output_file: "logs/audit.log"
        syslog_config:
          rfc_format: "5424"              # "5424" or "3164"
          facility: 16                    # local0 = 16
          app_name: "watchgate"         # Application name
          hostname: "auto"                # "auto" or explicit hostname
          include_structured_data: true   # RFC 5424 only
```

## Testing Strategy

### Unit Tests (Standard Library Only)

**Test syslog message generation:**
```python
def test_syslog_format_rfc5424():
    """Test RFC 5424 syslog message formatting"""
    config = {
        'output_file': 'test.log',
        'rfc_format': '5424',
        'facility': 16,
        'app_name': 'watchgate'
    }
    plugin = SyslogAuditingPlugin(config)
    
    event = {
        'event_type': 'REQUEST',
        'method': 'tools/call',
        'tool': 'read_file',
        'status': 'ALLOWED',
        'timestamp': datetime(2023, 12, 1, 14, 30, 25, 123456, timezone.utc),
        'request_id': '123'
    }
    
    result = plugin._format_syslog_message(event)
    assert result.startswith('<134>1 2023-12-01T14:30:25.123456Z')
    assert 'watchgate' in result
    assert '[watchgate@32473' in result
    assert 'event_type="REQUEST"' in result

def test_syslog_format_rfc3164():
    """Test RFC 3164 syslog message formatting"""
    config = {
        'output_file': 'test.log',
        'rfc_format': '3164',
        'facility': 16,
        'app_name': 'watchgate'
    }
    plugin = SyslogAuditingPlugin(config)
    
    event = {
        'event_type': 'REQUEST',
        'method': 'tools/call',
        'status': 'ALLOWED',
        'timestamp': datetime(2023, 12, 1, 14, 30, 25),
    }
    
    result = plugin._format_syslog_message(event)
    assert result.startswith('<134>Dec  1 14:30:25')
    assert 'watchgate:' in result
```

**Test priority calculation:**
```python
def test_syslog_priority_calculation():
    """Test syslog priority calculation"""
    config = {
        'format': 'syslog',
        'output_file': 'test.log',
        'syslog_config': {'facility': 16}
    }
    plugin = FileAuditingPlugin(config)
    
    # Test different severity levels
    assert plugin._calculate_syslog_priority(6) == 134  # facility=16, severity=6
    assert plugin._calculate_syslog_priority(4) == 132  # facility=16, severity=4
    assert plugin._calculate_syslog_priority(3) == 131  # facility=16, severity=3
```

**Test structured data escaping:**
```python
def test_syslog_structured_data_escaping():
    """Test structured data parameter escaping"""
    config = {'format': 'syslog', 'output_file': 'test.log'}
    plugin = FileAuditingPlugin(config)
    
    # Test various characters that need escaping
    assert plugin._escape_sd_value('test"quote') == 'test\\"quote'
    assert plugin._escape_sd_value('test\\backslash') == 'test\\\\backslash'
    assert plugin._escape_sd_value('test]bracket') == 'test\\]bracket'
```

**Test timestamp formatting:**
```python
def test_syslog_timestamp_formatting():
    """Test timestamp formatting for both RFC standards"""
    config = {'format': 'syslog', 'output_file': 'test.log'}
    plugin = FileAuditingPlugin(config)
    dt = datetime(2023, 12, 1, 14, 30, 25, 123456, timezone.utc)
    
    # RFC 5424 format
    rfc5424_ts = plugin._format_timestamp_rfc5424(dt)
    assert rfc5424_ts == "2023-12-01T14:30:25.123456Z"
    
    # RFC 3164 format
    rfc3164_ts = plugin._format_timestamp_rfc3164(dt)
    assert rfc3164_ts == "Dec  1 14:30:25"
```

### Integration Tests (Watchgate Dependencies)

**Test plugin lifecycle:**
```python
def test_syslog_plugin_integration():
    """Test syslog format with file auditing plugin"""
    config = {
        'output_file': 'test.log',
        'format': 'syslog',
        'syslog_config': {
            'rfc_format': '5424',
            'facility': 16,
            'app_name': 'test-agent'
        }
    }
    
    plugin = FileAuditingPlugin(config)
    test_event = create_test_mcp_request()
    plugin.log_request(test_event, PolicyDecision(allowed=True))
    
    # Verify file output
    with open('test.log', 'r') as f:
        output = f.read()
        assert '<134>1' in output  # Priority and version
        assert 'test-agent' in output
```

**Test configuration validation:**
```python
def test_syslog_config_validation():
    """Test syslog configuration validation"""
    valid_config = {
        'format': 'syslog',
        'output_file': 'audit.log',
        'syslog_config': {
            'rfc_format': '5424',
            'facility': 16,
            'include_structured_data': True
        }
    }
    
    errors = validate_auditing_config(valid_config)
    assert len(errors) == 0
    
    # Test invalid RFC format
    invalid_config = valid_config.copy()
    invalid_config['syslog_config']['rfc_format'] = 'invalid'
    errors = validate_auditing_config(invalid_config)
    assert len(errors) > 0
```

### Validation Tests (Test-Only Dependencies)

**Test with syslog-rfc5424-parser:**
```python
def test_syslog_with_rfc5424_parser():
    """Test syslog format with RFC 5424 parser"""
    pytest.importorskip("syslog_rfc5424_parser")
    from syslog_rfc5424_parser import SyslogMessage
    
    config = {
        'format': 'syslog',
        'output_file': 'test.log',
        'syslog_config': {'rfc_format': '5424'}
    }
    plugin = FileAuditingPlugin(config)
    event = create_test_event()
    syslog_message = plugin._format_syslog_message(event)
    
    # Parse with RFC 5424 parser
    parsed = SyslogMessage.parse(syslog_message)
    assert parsed.priority == 134
    assert parsed.hostname == socket.gethostname()
    assert parsed.appname == "watchgate"
```

**Test with logger command:**
```python
def test_syslog_with_logger_command():
    """Test syslog format with system logger command"""
    if not shutil.which('logger'):
        pytest.skip("logger command not available")
    
    config = {
        'format': 'syslog',
        'output_file': 'test.log',
        'syslog_config': {'rfc_format': '3164'}
    }
    plugin = FileAuditingPlugin(config)
    event = create_test_event()
    syslog_message = plugin._format_syslog_message(event)
    
    # Test that logger accepts the message
    result = subprocess.run(
        ['logger', '--rfc3164', '--stderr'],
        input=syslog_message,
        text=True,
        capture_output=True
    )
    assert result.returncode == 0
```

### Compliance Tests

**Test RFC 5424 compliance:**
```python
def test_rfc5424_compliance():
    """Test adherence to RFC 5424 specification"""
    config = {
        'format': 'syslog',
        'output_file': 'test.log',
        'syslog_config': {'rfc_format': '5424'}
    }
    plugin = FileAuditingPlugin(config)
    event = create_comprehensive_test_event()
    syslog_message = plugin._format_syslog_message(event)
    
    # Test required format: <PRI>VER SP TIMESTAMP SP HOSTNAME SP APP-NAME SP PROCID SP MSGID SP STRUCTURED-DATA SP MSG
    parts = syslog_message.split(' ', 7)
    assert len(parts) == 8
    
    # Test priority format
    assert parts[0].startswith('<') and parts[0].endswith('>1')
    
    # Test timestamp format (RFC 3339)
    timestamp = parts[2]
    assert 'T' in timestamp
    assert timestamp.endswith('Z')
```

**Test RFC 3164 compliance:**
```python
def test_rfc3164_compliance():
    """Test adherence to RFC 3164 specification"""
    config = {
        'format': 'syslog',
        'output_file': 'test.log',
        'syslog_config': {'rfc_format': '3164'}
    }
    plugin = FileAuditingPlugin(config)
    event = create_comprehensive_test_event()
    syslog_message = plugin._format_syslog_message(event)
    
    # Test required format: <PRI>TIMESTAMP HOSTNAME TAG: MSG
    assert syslog_message.startswith('<134>')
    
    # Test timestamp format (Mmm dd hh:mm:ss)
    # Should have month name, not number
    assert any(month in syslog_message for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
```

## External Validation Tools

### Test-Only Dependencies

**Python Libraries:**
```python
# pyproject.toml
[project.optional-dependencies]
test = [
    "syslog-rfc5424-parser>=0.3.0",  # RFC 5424 parsing
    "rfc5424-logging-handler>=1.4.0",  # RFC 5424 generation
]
```

**Command-Line Tools:**
```bash
# System logger command (usually pre-installed)
logger --rfc5424 "test message"
logger --rfc3164 "test message"

# Test syslog server
# rsyslog or syslog-ng for full integration testing
```

### CI/CD Integration

**GitHub Actions validation:**
```yaml
- name: Install Syslog Validators
  run: |
    pip install syslog-rfc5424-parser rfc5424-logging-handler
    
- name: Test Syslog Format
  run: |
    pytest tests/validation/test_syslog_compliance.py -v
```

## Risk Assessment

### Implementation Complexity: **Moderate**

**Challenges:**
- RFC 5424 vs RFC 3164 differences
- Timestamp format handling
- Structured data escaping
- Priority calculation accuracy

**Mitigation Strategies:**
- Comprehensive test coverage for both RFC standards
- Reference implementation comparison
- External tool validation
- Clear documentation of format differences

### Security Considerations

**Potential Issues:**
- Log injection via improper escaping
- Information disclosure in structured data
- Timestamp manipulation

**Safeguards:**
- Strict parameter escaping in structured data
- Input validation for all field values
- Secure timestamp generation
- Regular security review

## Acceptance Criteria

### Implementation Complete When:
- [ ] Syslog formatting methods implemented in FileAuditingPlugin for both RFC 5424 and RFC 3164
- [ ] All Watchgate event types mapped to appropriate syslog severity
- [ ] Priority calculation correctly implemented
- [ ] Structured data escaping properly handled
- [ ] Timestamp formatting compliant with both RFC standards
- [ ] Configuration integration with syslog-specific settings
- [ ] Unit tests cover all formatting scenarios
- [ ] Integration tests validate plugin lifecycle
- [ ] Validation tests pass with syslog-rfc5424-parser
- [ ] Validation tests pass with logger command
- [ ] Compliance tests verify RFC adherence
- [ ] Performance benchmarks meet requirements
- [ ] Security review completed
- [ ] Documentation updated with syslog format examples

### Success Metrics:
- **Format Compliance**: 100% of messages parse correctly with RFC parsers
- **Performance**: Syslog formatting adds <5ms overhead per message
- **Security**: No injection vulnerabilities in structured data
- **Compatibility**: Works with rsyslog, syslog-ng, and major log servers