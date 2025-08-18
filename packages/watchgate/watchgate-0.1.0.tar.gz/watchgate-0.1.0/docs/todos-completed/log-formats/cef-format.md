# CEF (Common Event Format) Implementation Requirements

## Overview

CEF (Common Event Format) is a standardized logging format originally developed by ArcSight for security event logging. It's widely adopted by SIEM systems including Splunk, ArcSight, and Azure Sentinel.

## Financial Services Deployment Patterns

### Industry Standard for SIEM Integration

**CEF is the industry standard** for financial services SIEM integration due to:
- **Regulatory compliance** requirements for security event logging
- **Standardized format** across multiple SIEM platforms
- **Real-time processing** capabilities for security incident response
- **Structured data** supporting automated threat detection

### Priority SIEM Platforms

**Primary targets that consume CEF:**
- **Splunk** - Enterprise security platform with native CEF parsing
- **IBM QRadar** - Security intelligence platform with CEF connector
- **Azure Sentinel** - Cloud-native SIEM with CEF data connector
- **ArcSight** - Original CEF developer, full native support

### Enterprise Transport Requirements

**TLS Syslog (RFC 5424 over TLS) is the enterprise standard:**
- **Port 6514** - Standard TLS syslog port for encrypted transport
- **Real-time streaming** - Required for security incident response
- **Secure transport** - TLS encryption mandatory for financial data
- **Embedded in syslog** - CEF messages wrapped in syslog headers, not standalone files

**Typical deployment pattern:**
```
Watchgate → TLS Syslog → SIEM Platform
         (Port 6514)   (Splunk/QRadar/Sentinel)
```

### Real-Time vs File-Based Logging

**Real-time streaming preferred:**
- **Security incident response** requires immediate alerting
- **Threat detection** benefits from real-time analysis
- **Compliance monitoring** needs continuous visibility
- **File-based logging** suitable for batch processing and archival only

## Implementation Requirements

### 1. Format Structure

**Complete CEF Format:**
```
[Syslog Header] CEF:Version|Device Vendor|Device Product|Device Version|Device Event Class ID|Name|Severity|[Extension]
```

**Example Output:**
```
Sep 19 08:26:10 host CEF:0|Watchgate|MCP Gateway|1.0.0|100|Request blocked|8|src=192.168.1.100 dst=10.0.0.1 spt=12345 dpt=80 act=blocked reason=Tool not in allowlist
```
*Note: Version (1.0.0) is dynamically determined from Watchgate package version*

### 2. Standard Library Implementation

**Core Requirements:**
- No external dependencies in runtime code
- Use only Python standard library
- Handle character escaping correctly
- Support Watchgate event mapping

**Implementation Class:**
```python
from watchgate.utils.version import get_watchgate_version

class CEFFormatter:
    def __init__(self, device_version: Optional[str] = None):
        self.version = "0"
        self.device_vendor = "Watchgate"
        self.device_product = "MCP Gateway"
        self.device_version = device_version or get_watchgate_version()
    
    def format_event(self, event_data: Dict[str, Any]) -> str:
        """Format Watchgate event as CEF message"""
        # Implementation using only standard library
        pass
    
    def escape_header(self, value: str) -> str:
        """Escape header field values (pipe and backslash)"""
        return str(value).replace('\\', '\\\\').replace('|', '\\|')
    
    def escape_extension(self, value: str) -> str:
        """Escape extension field values (equals, backslash, newlines)"""
        return str(value).replace('\\', '\\\\').replace('=', '\\=').replace('\n', '\\n').replace('\r', '\\r')
```

### 3. Watchgate Event Mapping

**Required Field Mappings:**
- **Device Event Class ID**: Map event_type to numeric IDs
- **Name**: Human-readable event description
- **Severity**: Map Watchgate events to CEF severity (0-10)
- **Extensions**: Map Watchgate fields to CEF extension fields

**Event Type Mapping:**
```python
CEF_EVENT_MAPPINGS = {
    'REQUEST': {'event_id': '100', 'severity': 6, 'name': 'MCP Request'},
    'RESPONSE': {'event_id': '101', 'severity': 6, 'name': 'MCP Response'},
    'SECURITY_BLOCK': {'event_id': '200', 'severity': 8, 'name': 'Security Block'},
    'REDACTION': {'event_id': '201', 'severity': 7, 'name': 'Content Redaction'},
    'ERROR': {'event_id': '400', 'severity': 9, 'name': 'System Error'},
    'UPSTREAM_ERROR': {'event_id': '401', 'severity': 8, 'name': 'Upstream Error'}
}
```

### 4. Extension Field Mappings

**Standard CEF Extensions:**
- `src`: Source IP (use localhost for local requests)
- `dst`: Destination IP (upstream server)
- `suser`: Source user (if available)
- `request`: Request ID for correlation
- `act`: Action taken (allowed/blocked)
- `reason`: Decision reason
- `rt`: Receipt time (timestamp)
- `cs1`: Custom string 1 (plugin name)
- `cs1Label`: Custom string 1 label ("Plugin")

### 5. Configuration Integration

**Configuration Schema:**
```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      config:
        format: "cef"
        output_file: "logs/audit.log"        # For batch processing/archival
        cef_config:
          device_vendor: "Watchgate"        # Optional override
          device_product: "MCP Gateway"        # Optional override
          device_version: "auto"             # "auto" or explicit version override
          include_syslog_header: true        # Include RFC 3164 header
    
    # Recommended: TLS Syslog for financial services
    - policy: "syslog_auditing"
      config:
        format: "cef"
        transport: "tls_syslog"
        syslog_config:
          host: "siem.company.com"
          port: 6514                         # Standard TLS syslog port
          facility: "local0"                 # Syslog facility
          severity: "info"                   # Default severity
          tls_verify: true                   # Certificate verification
          tls_ca_file: "/etc/ssl/siem-ca.pem"  # CA certificate path
        cef_config:
          device_vendor: "Watchgate"
          device_product: "MCP Gateway"
          device_version: "auto"
          include_syslog_header: true        # Required for syslog transport
```

**Transport Method Recommendations:**
- **Financial Services**: Use TLS syslog (port 6514) for real-time SIEM integration
- **Development/Testing**: Use file-based logging for local analysis
- **Hybrid Approach**: Configure both transports for redundancy and archival

## Testing Strategy

### Unit Tests (Standard Library Only)

**Test CEF message generation:**
```python
from watchgate.utils.version import get_watchgate_version

def test_cef_format_basic():
    """Test basic CEF message formatting"""
    formatter = CEFFormatter()
    event = {
        'event_type': 'REQUEST',
        'method': 'tools/call',
        'tool': 'read_file',
        'status': 'ALLOWED',
        'timestamp': '2023-12-01T14:30:25.123456Z',
        'request_id': '123'
    }
    
    result = formatter.format_event(event)
    version = get_watchgate_version()
    assert result.startswith(f'CEF:0|Watchgate|MCP Gateway|{version}|100|MCP Request|6|')
    assert 'request=123' in result
    assert 'act=allowed' in result
```

**Test character escaping:**
```python
def test_cef_header_escaping():
    """Test header field escaping"""
    formatter = CEFFormatter()
    assert formatter.escape_header('test|pipe') == 'test\\|pipe'
    assert formatter.escape_header('test\\backslash') == 'test\\\\backslash'

def test_cef_extension_escaping():
    """Test extension field escaping"""
    formatter = CEFFormatter()
    assert formatter.escape_extension('test=equals') == 'test\\=equals'
    assert formatter.escape_extension('test\nnewline') == 'test\\nnewline'
```

**Test event mapping:**
```python
def test_cef_event_mapping():
    """Test Watchgate event to CEF mapping"""
    formatter = CEFFormatter()
    
    # Test security block event
    event = {'event_type': 'SECURITY_BLOCK', 'reason': 'Tool not in allowlist'}
    result = formatter.format_event(event)
    assert '|200|Security Block|8|' in result
    assert 'act=blocked' in result

def test_cef_dynamic_version():
    """Test dynamic version detection"""
    # Test with explicit version
    formatter = CEFFormatter(device_version="2.0.0")
    assert formatter.device_version == "2.0.0"
    
    # Test with automatic version detection (uses centralized utility)
    formatter = CEFFormatter()
    assert formatter.device_version != "unknown"  # Should get actual version
    
    # Test version appears in output
    event = {'event_type': 'REQUEST', 'method': 'tools/call'}
    result = formatter.format_event(event)
    assert f'|{formatter.device_version}|' in result
```

### Integration Tests (Watchgate Dependencies)

**Test plugin lifecycle:**
```python
def test_cef_plugin_integration():
    """Test CEF format with file auditing plugin"""
    config = {
        'output_file': 'test.log',
        'format': 'cef',
        'cef_config': {
            'device_vendor': 'TestVendor'
        }
    }
    
    plugin = FileAuditingPlugin(config)
    # Test event processing
    test_event = create_test_mcp_request()
    plugin.log_request(test_event, PolicyDecision(allowed=True))
    
    # Verify file output
    with open('test.log', 'r') as f:
        output = f.read()
        assert 'CEF:0|TestVendor|' in output
```

**Test configuration validation:**
```python
def test_cef_config_validation():
    """Test CEF configuration validation"""
    valid_config = {
        'format': 'cef',
        'output_file': 'audit.log',
        'cef_config': {
            'device_vendor': 'Watchgate',
            'include_syslog_header': True
        }
    }
    
    # Should validate successfully
    errors = validate_auditing_config(valid_config)
    assert len(errors) == 0
```

### Validation Tests (Test-Only Dependencies)

**Test with cefevent library:**
```python
def test_cef_with_cefevent_library():
    """Test CEF format with cefevent library validation"""
    pytest.importorskip("cefevent")
    import cefevent
    
    formatter = CEFFormatter()
    event = create_test_event()
    cef_message = formatter.format_event(event)
    
    # Parse with cefevent
    parsed = cefevent.parse(cef_message)
    assert parsed is not None
    assert parsed['DeviceVendor'] == 'Watchgate'
```

**Test with jc command-line tool:**
```python
def test_cef_with_jc_validator():
    """Test CEF format with jc command-line validator"""
    if not shutil.which('jc'):
        pytest.skip("jc command not available")
    
    formatter = CEFFormatter()
    event = create_test_event()
    cef_message = formatter.format_event(event)
    
    # Validate with jc
    result = subprocess.run(
        ['jc', '--cef'],
        input=cef_message,
        text=True,
        capture_output=True
    )
    assert result.returncode == 0
```

### Compliance Tests

**Test CEF specification compliance:**
```python
def test_cef_specification_compliance():
    """Test adherence to CEF specification"""
    formatter = CEFFormatter()
    event = create_comprehensive_test_event()
    cef_message = formatter.format_event(event)
    
    # Test required header format
    assert cef_message.startswith('CEF:0|')
    
    # Test pipe-separated header (exactly 7 fields)
    header_part = cef_message.split('|', 7)
    assert len(header_part) == 8  # 7 header fields + extension
    
    # Test extension field format
    extension = header_part[7]
    assert '=' in extension  # Key-value pairs
    assert not extension.startswith('=')  # No leading equals
```

## External Validation Tools

### Test-Only Dependencies

**Python Libraries:**
```python
# pyproject.toml
[project.optional-dependencies]
test = [
    "cefevent>=0.5.0",  # CEF parsing and validation
]
```

**Command-Line Tools:**
```bash
# Install via pip
pip install jc

# Usage for validation
echo "CEF:0|Watchgate|..." | jc --cef
```

### CI/CD Integration

**GitHub Actions validation:**
```yaml
- name: Install CEF Validators
  run: |
    pip install jc cefevent
    
- name: Test CEF Format
  run: |
    pytest tests/validation/test_cef_compliance.py -v
```

## Risk Assessment

### Implementation Complexity: **Moderate-High**

**Challenges:**
- Complex escaping rules (different for headers vs extensions)
- Character encoding edge cases
- Timestamp format standardization
- Extension field validation

**Mitigation Strategies:**
- Comprehensive test coverage for escaping scenarios
- Reference implementation comparison
- External tool validation
- Thorough testing with production-like workloads

### Security Considerations

**Potential Issues:**
- Log injection via improper escaping
- Information disclosure in extension fields
- Performance impact of escaping operations

**Safeguards:**
- Strict character escaping implementation
- Input validation for all field values
- Performance testing with large message volumes
- Security review of escaping logic

## Acceptance Criteria

### Implementation Complete When:
- [ ] CEF formatter implemented using only standard library
- [ ] All Watchgate event types mapped to CEF format
- [ ] Character escaping correctly implemented for headers and extensions
- [ ] Configuration integration with optional CEF settings
- [ ] Unit tests cover all formatting scenarios
- [ ] Integration tests validate plugin lifecycle
- [ ] Validation tests pass with cefevent library
- [ ] Validation tests pass with jc command-line tool
- [ ] Performance benchmarks meet requirements
- [ ] Security review completed
- [ ] Documentation updated with CEF format examples
- [ ] CI/CD pipeline includes CEF validation tests

### Success Metrics:
- **Format Compliance**: 100% of generated messages parse correctly with external validators
- **Performance**: CEF formatting adds <10ms overhead per message
- **Security**: No escape sequence vulnerabilities identified
- **Compatibility**: Works with Splunk, ArcSight, and Azure Sentinel ingestion