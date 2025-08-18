# OtelAuditingPlugin Implementation Requirements

## Overview

OpenTelemetry is a vendor-neutral observability framework that provides a standardized way to collect, process, and export telemetry data. OTEL logging format enables correlation with distributed traces and metrics, making it essential for modern cloud-native environments.

**Implementation Approach**: Dedicated `OtelAuditingPlugin` class inheriting from `AuditingPlugin` base class for OpenTelemetry integration and observability correlation.

**Note**: This is a first release implementation (v0.1.0) - no backward compatibility concerns. The new plugin architecture will be implemented directly.

## Implementation Requirements

### 1. Format Structure

**OTEL Log Record Structure:**
```python
{
  "timestamp": "2023-12-01T14:30:25.123456789Z",  # Nanosecond precision
  "observed_timestamp": "2023-12-01T14:30:25.123456789Z",
  "severity_text": "INFO",
  "severity_number": 9,
  "body": "MCP request processed successfully",
  "attributes": {
    "event_type": "REQUEST",
    "method": "tools/call",
    "tool": "read_file",
    "status": "ALLOWED",
    "request_id": "123",
    "plugin": "tool_allowlist"
  },
  "resource": {
    "service.name": "watchgate",
    "service.version": "1.0.0",
    "deployment.environment": "production"
  },
  "trace_id": "5b8efff798038103d269b633813fc60c",
  "span_id": "eee19b7ec3c1b174"
}
```

### 2. Standard Library Implementation

**Core Requirements:**
- No external dependencies in runtime code
- Use only Python standard library
- Generate OTEL-compliant log records
- Support correlation with traces when available
- Handle resource attributes correctly

**Implementation Class:**
```python
import json
import time
import uuid
from typing import Dict, Any, Optional
from watchgate.utils.version import get_watchgate_version

    def _format_otel_record(self, request: MCPRequest, data: Any, event_type: str) -> Dict[str, Any]:
        """Format Watchgate event as OTEL log record"""
        current_time = time.time()
        log_record = {
            "timestamp": self._format_timestamp(current_time),
            "observed_timestamp": self._format_timestamp(current_time),
            "severity_text": self._map_severity_text(event_type),
            "severity_number": self._map_severity_number(event_type),
            "body": self._format_body(event_type, request, data),
            "attributes": self._format_attributes(event_type, request, data),
            "resource": self._format_resource()
        }
        
        # Add trace correlation if available and enabled
        if self.include_trace_correlation:
            trace_context = self._get_trace_context(request)
            if trace_context:
                log_record.update(trace_context)
        
        return log_record
    
    def _format_timestamp(self, timestamp: Optional[float]) -> str:
        """Format timestamp to RFC 3339 with nanosecond precision"""
        if timestamp is None:
            timestamp = time.time()
        
        # Convert to nanoseconds (OTEL spec requirement)
        if isinstance(timestamp, float):
            nanos = int(timestamp * 1_000_000_000)
        else:
            nanos = int(timestamp)
        
        # Format as RFC 3339
        seconds = nanos // 1_000_000_000
        nanoseconds = nanos % 1_000_000_000
        
        dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
        return f"{dt.strftime('%Y-%m-%dT%H:%M:%S')}.{nanoseconds:09d}Z"
    
    def _map_severity_text(self, event_type: str) -> str:
        """Map Watchgate event type to OTEL severity text"""
        mapping = {
            'REQUEST': 'INFO',
            'RESPONSE': 'INFO',
            'SECURITY_BLOCK': 'WARN',
            'REDACTION': 'WARN',
            'ERROR': 'ERROR',
            'UPSTREAM_ERROR': 'ERROR',
            'NOTIFICATION': 'INFO',
            'TOOLS_FILTERED': 'DEBUG'
        }
        return mapping.get(event_type, 'INFO')
    
    def _map_severity_number(self, event_type: str) -> int:
        """Map Watchgate event type to OTEL severity number (1-24)"""
        mapping = {
            'REQUEST': 9,           # INFO
            'RESPONSE': 9,          # INFO
            'SECURITY_BLOCK': 13,   # WARN
            'REDACTION': 13,        # WARN
            'ERROR': 17,            # ERROR
            'UPSTREAM_ERROR': 17,   # ERROR
            'NOTIFICATION': 9,      # INFO
            'TOOLS_FILTERED': 5     # DEBUG
        }
        return mapping.get(event_type, 9)
    
    def _format_body(self, event_data: Dict[str, Any]) -> str:
        """Format log message body"""
        event_type = event_data.get('event_type', 'EVENT')
        method = event_data.get('method', '')
        status = event_data.get('status', '')
        
        if event_type == 'REQUEST':
            return f"MCP {method} request - {status}"
        elif event_type == 'RESPONSE':
            return f"MCP {method} response - {status}"
        elif event_type == 'SECURITY_BLOCK':
            return f"Security block: {event_data.get('reason', 'Unknown')}"
        else:
            return f"{event_type}: {method} - {status}"
    
    def _format_attributes(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format event attributes"""
        attributes = {}
        
        # Map Watchgate fields to OTEL attributes
        field_mappings = {
            'event_type': 'watchgate.event_type',
            'method': 'watchgate.method',
            'tool': 'watchgate.tool',
            'status': 'watchgate.status',
            'request_id': 'watchgate.request_id',
            'plugin': 'watchgate.plugin',
            'reason': 'watchgate.reason',
            'duration_ms': 'watchgate.duration_ms',
            'server_name': 'watchgate.server_name'
        }
        
        for event_field, otel_field in field_mappings.items():
            value = event_data.get(event_field)
            if value is not None:
                attributes[otel_field] = value
        
        return attributes
```

### 3. Watchgate Event Mapping

**Severity Mappings:**
```python
OTEL_SEVERITY_MAPPINGS = {
    'REQUEST': {'text': 'INFO', 'number': 9},
    'RESPONSE': {'text': 'INFO', 'number': 9},
    'SECURITY_BLOCK': {'text': 'WARN', 'number': 13},
    'REDACTION': {'text': 'WARN', 'number': 13},
    'ERROR': {'text': 'ERROR', 'number': 17},
    'UPSTREAM_ERROR': {'text': 'ERROR', 'number': 17},
    'NOTIFICATION': {'text': 'INFO', 'number': 9},
    'TOOLS_FILTERED': {'text': 'DEBUG', 'number': 5}
}
```

**Resource Attributes:**
```python
def get_resource_attributes(self) -> Dict[str, str]:
    """Get OTEL resource attributes"""
    return {
        "service.name": self.service_name,
        "service.version": self.service_version,
        "service.namespace": "watchgate",
        "deployment.environment": os.getenv("DEPLOYMENT_ENV", "production"),
        "host.name": socket.gethostname(),
        "process.pid": str(os.getpid()),
        "telemetry.sdk.name": "watchgate",
        "telemetry.sdk.version": self.service_version,
        "telemetry.sdk.language": "python"
    }
```

### 4. Trace Correlation

**Trace ID Generation:**
```python
def generate_trace_id(self) -> str:
    """Generate OTEL-compliant trace ID"""
    # 16-byte random value as 32-character hex string
    return uuid.uuid4().hex + uuid.uuid4().hex[:16]

def generate_span_id(self) -> str:
    """Generate OTEL-compliant span ID"""
    # 8-byte random value as 16-character hex string
    return uuid.uuid4().hex[:16]
```

**Correlation Integration:**
```python
def add_trace_correlation(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Add trace correlation to event data"""
    # Check if trace context is available in request
    if 'trace_context' in event_data:
        trace_context = event_data['trace_context']
        event_data['trace_id'] = trace_context.get('trace_id')
        event_data['span_id'] = trace_context.get('span_id')
    
    return event_data
```

### 5. Configuration Integration

**Configuration Schema:**
```yaml
plugins:
  auditing:
    - policy: "otel_auditing"
      config:
        output_file: "logs/audit.otel"
        service_name: "watchgate"
        service_version: "auto"              # "auto" or explicit version override
        service_namespace: "watchgate"
        deployment_environment: "production"
        include_trace_correlation: true
        timestamp_precision: "nanoseconds"   # nanoseconds, microseconds, milliseconds
        resource_attributes:                 # Additional resource attributes
          deployment.environment: "production"
          service.instance.id: "instance-1"
        critical: false                      # Plugin criticality
```

**Configuration Schema (Pydantic):**
```python
class OtelAuditingConfig(BaseModel):
    output_file: str
    service_name: str = "watchgate"
    service_version: Optional[str] = None
    service_namespace: str = "watchgate"
    deployment_environment: str = "production"
    include_trace_correlation: bool = True
    timestamp_precision: Literal["nanoseconds", "microseconds", "milliseconds"] = "nanoseconds"
    resource_attributes: Dict[str, Any] = {}
    critical: bool = False
```

## Testing Strategy

### Unit Tests (Standard Library Only)

**Test OTEL log record generation:**
```python
def test_otel_format_basic():
    """Test basic OTEL log record formatting"""
    config = {
        'output_file': 'test.otel',
        'service_name': 'test-service'
    }
    plugin = OtelAuditingPlugin(config)
    
    request = create_test_mcp_request()
    decision = PolicyDecision(allowed=True)
    
    result = plugin._format_otel_record(request, decision, "REQUEST")
        'method': 'tools/call',
        'tool': 'read_file',
        'status': 'ALLOWED',
        'timestamp': 1701435025.123456,
        'request_id': '123'
    }
    
    result = formatter.format_event(event)
    log_record = json.loads(result)
    
    assert log_record['severity_text'] == 'INFO'
    assert log_record['severity_number'] == 9
    assert log_record['body'] == 'MCP tools/call request - ALLOWED'
    assert log_record['attributes']['watchgate.event_type'] == 'REQUEST'
    assert log_record['resource']['service.name'] == 'test-service'
```

**Test timestamp formatting:**
```python
def test_otel_timestamp_formatting():
    """Test OTEL timestamp formatting"""
    formatter = OTELFormatter()
    
    # Test with float timestamp
    timestamp = 1701435025.123456789
    formatted = formatter._format_timestamp(timestamp)
    
    # Should be RFC 3339 with nanosecond precision
    assert formatted.endswith('Z')
    assert 'T' in formatted
    assert '.' in formatted
    assert len(formatted.split('.')[1]) == 10  # 9 nanoseconds + 'Z'
```

**Test severity mapping:**
```python
def test_otel_severity_mapping():
    """Test event type to OTEL severity mapping"""
    formatter = OTELFormatter()
    
    # Test different event types
    assert formatter._map_severity_text('REQUEST') == 'INFO'
    assert formatter._map_severity_number('REQUEST') == 9
    
    assert formatter._map_severity_text('SECURITY_BLOCK') == 'WARN'
    assert formatter._map_severity_number('SECURITY_BLOCK') == 13
    
    assert formatter._map_severity_text('ERROR') == 'ERROR'
    assert formatter._map_severity_number('ERROR') == 17
```

**Test trace correlation:**
```python
def test_otel_trace_correlation():
    """Test trace ID and span ID correlation"""
    formatter = OTELFormatter()
    event = {
        'event_type': 'REQUEST',
        'method': 'tools/call',
        'trace_id': '5b8efff798038103d269b633813fc60c',
        'span_id': 'eee19b7ec3c1b174'
    }
    
    result = formatter.format_event(event)
    log_record = json.loads(result)
    
    assert log_record['trace_id'] == '5b8efff798038103d269b633813fc60c'
    assert log_record['span_id'] == 'eee19b7ec3c1b174'

def test_otel_dynamic_version():
    """Test dynamic service version detection"""
    # Test with explicit version
    formatter = OTELFormatter(service_version="2.0.0")
    assert formatter.service_version == "2.0.0"
    
    # Test with automatic version detection (uses centralized utility)
    formatter = OTELFormatter()
    assert formatter.service_version != "unknown"  # Should get actual version
    
    # Test version appears in resource attributes
    event = {'event_type': 'REQUEST', 'method': 'tools/call'}
    result = formatter.format_event(event)
    log_record = json.loads(result)
    assert log_record['resource']['service.version'] == formatter.service_version
```

### Integration Tests (Watchgate Dependencies)

**Test plugin lifecycle:**
```python
def test_otel_plugin_integration():
    """Test OTEL format with file auditing plugin"""
    config = {
        'output_file': 'test.log',
        'format': 'otel',
        'otel_config': {
            'service_name': 'test-watchgate',
            'service_version': '1.0.0'
        }
    }
    
    plugin = FileAuditingPlugin(config)
    test_event = create_test_mcp_request()
    plugin.log_request(test_event, PolicyDecision(allowed=True))
    
    # Verify file output
    with open('test.log', 'r') as f:
        output = f.read()
        log_record = json.loads(output)
        assert log_record['resource']['service.name'] == 'test-watchgate'
        assert log_record['severity_text'] == 'INFO'
```

**Test configuration validation:**
```python
def test_otel_config_validation():
    """Test OTEL configuration validation"""
    valid_config = {
        'format': 'otel',
        'output_file': 'audit.log',
        'otel_config': {
            'service_name': 'watchgate',
            'include_trace_correlation': True
        }
    }
    
    errors = validate_auditing_config(valid_config)
    assert len(errors) == 0
```

### Validation Tests (Test-Only Dependencies)

**Test with OpenTelemetry proto:**
```python
def test_otel_with_proto_validation():
    """Test OTEL format with OpenTelemetry protobuf validation"""
    pytest.importorskip("opentelemetry.proto")
    
    formatter = OTELFormatter()
    event = create_test_event()
    otel_json = formatter.format_event(event)
    
    # Parse JSON and validate structure
    log_record = json.loads(otel_json)
    
    # Validate required fields
    assert 'timestamp' in log_record
    assert 'severity_number' in log_record
    assert 'body' in log_record
    assert 'resource' in log_record
```

**Test with OTEL Collector validation:**
```python
def test_otel_with_collector_validation():
    """Test OTEL format with OpenTelemetry Collector"""
    if not shutil.which('otelcol'):
        pytest.skip("OpenTelemetry Collector not available")
    
    formatter = OTELFormatter()
    event = create_test_event()
    otel_json = formatter.format_event(event)
    
    # Write to temporary file for collector validation
    config = create_otel_collector_config()
    
    # Test with collector (would require more complex setup)
    # This is a placeholder for collector integration testing
```

### Compliance Tests

**Test OTEL specification compliance:**
```python
def test_otel_specification_compliance():
    """Test adherence to OTEL logging specification"""
    formatter = OTELFormatter()
    event = create_comprehensive_test_event()
    otel_json = formatter.format_event(event)
    
    log_record = json.loads(otel_json)
    
    # Test required fields
    assert 'timestamp' in log_record
    assert 'body' in log_record
    
    # Test severity number range (1-24)
    severity_num = log_record['severity_number']
    assert 1 <= severity_num <= 24
    
    # Test resource attributes
    resource = log_record['resource']
    assert 'service.name' in resource
    
    # Test attribute naming (should use semantic conventions)
    attributes = log_record['attributes']
    for key in attributes:
        assert key.startswith('watchgate.')  # Namespaced attributes
```

## External Validation Tools

### Test-Only Dependencies

**Python Libraries:**
```python
# pyproject.toml
[project.optional-dependencies]
test = [
    "opentelemetry-api>=1.20.0",
    "opentelemetry-sdk>=1.20.0",
    "opentelemetry-proto>=1.20.0",
    "opentelemetry-exporter-otlp>=1.20.0",
]
```

**Command-Line Tools:**
```bash
# OpenTelemetry Collector
curl -LO https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.89.0/otelcol_0.89.0_linux_amd64.tar.gz

# Validation
otelcol validate --config collector.yaml
```

### CI/CD Integration

**GitHub Actions validation:**
```yaml
- name: Install OTEL Validators
  run: |
    pip install opentelemetry-api opentelemetry-sdk opentelemetry-proto
    
- name: Download OTEL Collector
  run: |
    curl -LO https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.89.0/otelcol_0.89.0_linux_amd64.tar.gz
    tar -xzf otelcol_0.89.0_linux_amd64.tar.gz
    
- name: Test OTEL Format
  run: |
    pytest tests/validation/test_otel_compliance.py -v
```

## Risk Assessment

### Implementation Complexity: **High**

**Challenges:**
- Timestamp precision handling (nanoseconds vs microseconds)
- Trace correlation complexity
- Resource attribute management
- OTEL specification compliance
- JSON schema validation

**Mitigation Strategies:**
- Start with basic log record structure
- Add trace correlation as enhancement
- Comprehensive test coverage
- Reference implementation comparison
- External validation with OTEL tools

### Security Considerations

**Potential Issues:**
- Trace ID information disclosure
- Resource attribute exposure
- JSON injection vulnerabilities
- Performance impact of detailed logging

**Safeguards:**
- Trace ID validation and sanitization
- Resource attribute filtering
- JSON serialization security
- Performance monitoring and limits

## Acceptance Criteria

### Implementation Complete When:
- [ ] OtelAuditingPlugin class implemented inheriting from AuditingPlugin
- [ ] OTEL log record formatting implemented using only standard library
- [ ] All Watchgate event types mapped to OTEL severity levels
- [ ] Timestamp formatting supports nanosecond precision
- [ ] Resource attributes correctly populated
- [ ] Log record attributes follow OTEL semantic conventions
- [ ] Trace correlation implemented for distributed tracing
- [ ] Configuration integration with OTEL-specific settings
- [ ] Unit tests cover all formatting scenarios
- [ ] Integration tests validate plugin lifecycle
- [ ] Validation tests pass with OpenTelemetry proto parsing
- [ ] Compliance tests verify OTEL specification adherence
- [ ] Performance benchmarks meet requirements
- [ ] Security review completed
- [ ] Documentation updated with OTEL format examples

### Success Metrics:
- **Format Compliance**: 100% of log records validate against OTEL spec
- **Performance**: OTEL formatting adds <15ms overhead per message
- **Security**: No trace ID leakage or injection vulnerabilities
- **Compatibility**: Works with Grafana, Datadog, and other OTEL platforms