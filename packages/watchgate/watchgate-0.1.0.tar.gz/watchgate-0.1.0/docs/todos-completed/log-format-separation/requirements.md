# Log Format Separation Requirements

## Overview

Currently, the FileAuditingPlugin handles multiple log formats through a single format parameter. This architectural decision creates limitations for enterprise users who need multiple simultaneous audit trails for different purposes (compliance, SIEM integration, debugging, etc.).

This document specifies the requirements for separating each log format into its own dedicated plugin, enabling users to run multiple formats simultaneously while maintaining clean separation of concerns.

## Current Architecture Analysis

### Existing Implementation (FileAuditingPlugin)

```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      config:
        format: "json"          # Single format choice
        output_file: "audit.log" # Single output file
```

**Current Format Support:**
- `line` (human-readable single line per event)
- `debug` (key-value pairs for troubleshooting)
- `jsonl` (JSON Lines format)
- `csv` (comma-separated values)
- `cef` (Common Event Format)

### Limitations of Current Architecture

1. **Single Format Constraint**: Users can only choose one format per plugin instance
2. **Multiple Instance Complexity**: Running multiple FileAuditingPlugin instances creates configuration complexity
3. **Format-Specific Features**: Each format has unique configuration needs that clutter the common configuration
4. **Maintenance Burden**: All format logic lives in one large plugin class

## Target Architecture

### Separate Plugin per Format

```yaml
plugins:
  auditing:
    # Human-readable formats
    - policy: "line_auditing"
      config:
        output_file: "audit-ops.log"
        
    - policy: "debug_auditing"
      config:
        output_file: "audit-debug.log"
        
    # Structured formats
    - policy: "json_auditing"
      config:
        output_file: "audit-compliance.json"
        include_request_body: true
        
    - policy: "syslog_auditing"
      config:
        output_file: "audit-syslog.log"
        rfc_format: "5424"
        facility: 16
        
    - policy: "csv_auditing"
      config:
        output_file: "audit-report.csv"
        delimiter: ","
        
    - policy: "cef_auditing"
      config:
        output_file: "audit-siem.cef"
        device_vendor: "Watchgate"
```

## Plugin Architecture Design

### Base Plugin: AuditingPlugin

**Shared functionality for all auditing plugins:**
- File management and rotation
- Async I/O operations
- Error handling and retry logic
- Common event data structures
- Performance monitoring

```python
class AuditingPlugin:
    """Base class for all auditing plugins"""
    
    def __init__(self, config: Dict[str, Any]):
        self.output_file = config.get('output_file')
        self.critical = config.get('critical', False)
        # ... common initialization
    
    async def log_request(self, request: MCPRequest, decision: PolicyDecision) -> None:
        """Abstract method for logging requests"""
        raise NotImplementedError
    
    async def log_response(self, request: MCPRequest, response: MCPResponse) -> None:
        """Abstract method for logging responses"""
        raise NotImplementedError
    
    # Common file management methods
    def _ensure_directory(self, file_path: str) -> None:
        """Ensure directory exists for output file"""
        pass
    
    def _rotate_file_if_needed(self) -> None:
        """Handle file rotation if configured"""
        pass
```

### Format-Specific Plugins

#### 1. HumanReadableAuditingPlugin

**Purpose**: Operational monitoring and human-readable logs

**Formats**: `line`, `debug`

```python
class HumanReadableAuditingPlugin(AuditingPlugin):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.format = config.get('format', 'line')  # 'line' or 'debug'
        
    async def log_request(self, request: MCPRequest, decision: PolicyDecision) -> None:
        if self.format == 'line':
            output = self._format_line(request, decision)
        elif self.format == 'debug':
            output = self._format_debug(request, decision)
        
        await self._write_to_file(output)
```

#### 2. JsonAuditingPlugin

**Purpose**: GRC platform integration and compliance automation

**Financial Services Priority**: Required for modern compliance platforms and API consumption

```python
class JsonAuditingPlugin(AuditingPlugin):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.include_request_body = config.get('include_request_body', False)
        self.pretty_print = config.get('pretty_print', False)
        
        # GRC Platform Integration
        self.compliance_schema = config.get('compliance_schema', 'standard')
        self.include_risk_metadata = config.get('include_risk_metadata', True)
        self.api_compatible = config.get('api_compatible', True)
        
    async def log_request(self, request: MCPRequest, decision: PolicyDecision) -> None:
        event_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': 'REQUEST',
            'method': request.method,
            'status': 'ALLOWED' if decision.allowed else 'BLOCKED',
            # ... additional fields
        }
        
        if self.include_request_body:
            event_data['request_body'] = request.params
            
        if self.include_risk_metadata:
            event_data['compliance_metadata'] = self._generate_compliance_metadata(request, decision)
            
        output = json.dumps(event_data, indent=2 if self.pretty_print else None)
        await self._write_to_file(output)
```

#### 3. SyslogAuditingPlugin

**Purpose**: Centralized logging and SIEM integration with TLS transport

**Financial Services Priority**: Critical for real-time compliance monitoring and secure log delivery

```python
class SyslogAuditingPlugin(AuditingPlugin):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        syslog_config = config.get('syslog_config', {})
        self.rfc_format = syslog_config.get('rfc_format', '5424')
        self.facility = syslog_config.get('facility', 16)
        self.hostname = socket.gethostname()
        
        # TLS Transport Configuration (Priority for Financial Services)
        self.transport = syslog_config.get('transport', 'file')  # 'file', 'udp', 'tcp', 'tls'
        self.remote_host = syslog_config.get('remote_host')
        self.remote_port = syslog_config.get('remote_port', 514)
        self.tls_verify = syslog_config.get('tls_verify', True)
        self.tls_cert_file = syslog_config.get('tls_cert_file')
        
    async def log_request(self, request: MCPRequest, decision: PolicyDecision) -> None:
        if self.rfc_format == '5424':
            output = self._format_rfc5424(request, decision)
        else:
            output = self._format_rfc3164(request, decision)
            
        if self.transport == 'file':
            await self._write_to_file(output)
        elif self.transport == 'tls':
            await self._send_via_tls(output)
        else:
            await self._send_via_network(output)
```

#### 4. CefAuditingPlugin

**Purpose**: Security event management systems and SOX compliance

**Financial Services Priority**: HIGHEST - Industry standard for financial services SIEM integration

```python
class CefAuditingPlugin(AuditingPlugin):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.device_vendor = config.get('device_vendor', 'Watchgate')
        self.device_product = config.get('device_product', 'MCP Gateway')
        self.device_version = config.get('device_version') or get_watchgate_version()
        
        # Financial Services Extensions
        self.compliance_tags = config.get('compliance_tags', ['SOX', 'GDPR'])
        self.risk_scoring = config.get('risk_scoring', True)
        self.regulatory_fields = config.get('regulatory_fields', True)
        
    async def log_request(self, request: MCPRequest, decision: PolicyDecision) -> None:
        cef_message = self._format_cef(request, decision)
        await self._write_to_file(cef_message)
```

#### 5. CsvAuditingPlugin

**Purpose**: SOX compliance reporting and regulatory analysis

**Financial Services Priority**: Critical for SOX Section 404 bulk evidence collection

```python
class CsvAuditingPlugin(AuditingPlugin):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.delimiter = config.get('delimiter', ',')
        self.quote_char = config.get('quote_char', '"')
        self.headers_written = False
        
        # SOX Compliance Extensions
        self.include_compliance_columns = config.get('include_compliance_columns', True)
        self.audit_trail_format = config.get('audit_trail_format', 'SOX_404')
        self.regulatory_schema = config.get('regulatory_schema', 'default')
        
    async def log_request(self, request: MCPRequest, decision: PolicyDecision) -> None:
        if not self.headers_written:
            await self._write_headers()
            self.headers_written = True
            
        csv_row = self._format_csv(request, decision)
        await self._write_to_file(csv_row)
```

## Financial Services Priority Requirements

Based on comprehensive SOX compliance research, the following priority order has been established for financial services organizations:

### Priority 1: CEF Format (Highest Priority)
- **Industry Standard**: Universal acceptance in financial services SIEM systems
- **SOX Compliance**: Critical for automated compliance monitoring and alerting
- **Security Integration**: Required for threat detection and incident response
- **Audit Trail**: Structured format for regulatory audit requirements

### Priority 2: Syslog with TLS Transport
- **Encrypted Network Streaming**: Not just file-based logging but secure network delivery
- **Centralized Logging**: Integration with enterprise log management systems
- **Real-time Monitoring**: Immediate delivery for security operations centers
- **Compliance Streaming**: Real-time compliance monitoring capabilities

### Priority 3: CSV for Compliance Reporting
- **SOX Section 404**: Critical for bulk evidence collection and analysis
- **Regulatory Reporting**: Required format for many compliance frameworks
- **Data Analysis**: Excel-compatible format for compliance teams
- **Audit Evidence**: Structured format for external auditor requirements

### Priority 4: JSON for Modern API Integration
- **Compliance Platforms**: Integration with modern GRC (Governance, Risk, Compliance) systems
- **API Consumption**: Machine-readable format for compliance automation
- **Cloud Integration**: Compatible with cloud-native compliance tools
- **Data Processing**: Structured format for automated compliance analysis

## Implementation Strategy

### Phase 1: Extract Current Formats (Financial Services Priority Order)

1. **Create CEF plugin first** - highest priority for financial services
2. **Create Syslog plugin with TLS transport** - critical for real-time compliance
3. **Create CSV plugin** - essential for SOX compliance reporting
4. **Create JSON plugin** - required for modern compliance platforms
5. **Create remaining format plugins** - operational formats
6. **Update configuration schemas** to support new plugin names
7. **Create base AuditingPlugin** with shared functionality

### Phase 2: Update Remaining Format Requirements

Update the following pending format requirements to specify separate plugins:

- **GELF Format** → `GelfAuditingPlugin`
- **LEEF Format** → `LeefAuditingPlugin`
- **OpenTelemetry Format** → `OtelAuditingPlugin`
- **Syslog Format** → `SyslogAuditingPlugin` (with TLS transport priority)

### Phase 3: Complete Implementation

1. **Update FileAuditingPlugin** to use new architecture internally
2. **Update all documentation** to use new plugin examples
3. **Update all test configurations** to use new plugin structure

**Note**: Since Watchgate has not been released yet (v0.1.0 first release), there are no backward compatibility concerns. We can implement this architecture directly without deprecation warnings or migration paths.

## Configuration Examples

### Current Implementation
```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      config:
        format: "json"
        output_file: "audit.log"
```

### New Architecture
```yaml
plugins:
  auditing:
    - policy: "json_auditing"
      config:
        output_file: "audit.json"
        include_request_body: true
```

### Financial Services Configuration Example

```yaml
plugins:
  auditing:
    # Priority 1: CEF for SIEM integration
    - policy: "cef_auditing"
      config:
        output_file: "audit-siem.cef"
        device_vendor: "Watchgate"
        compliance_tags: ["SOX", "GDPR", "PCI-DSS"]
        risk_scoring: true
        regulatory_fields: true
        
    # Priority 2: Syslog with TLS for real-time compliance
    - policy: "syslog_auditing"
      config:
        output_file: "audit-syslog.log"
        syslog_config:
          rfc_format: "5424"
          facility: 16
          transport: "tls"
          remote_host: "siem.company.com"
          remote_port: 6514
          tls_verify: true
          tls_cert_file: "/etc/ssl/siem-client.crt"
          
    # Priority 3: CSV for SOX compliance reporting
    - policy: "csv_auditing"
      config:
        output_file: "audit-compliance.csv"
        delimiter: ","
        include_compliance_columns: true
        audit_trail_format: "SOX_404"
        regulatory_schema: "financial_services"
        
    # Priority 4: JSON for GRC platform integration
    - policy: "json_auditing"
      config:
        output_file: "audit-grc.json"
        include_request_body: true
        compliance_schema: "grc_standard"
        include_risk_metadata: true
        api_compatible: true
```

**Note**: Since this is a pre-release architecture change, users will start with the new plugin structure directly. No migration is needed.

## Benefits of Separate Plugins

### 1. Multiple Simultaneous Outputs
Users can run multiple formats concurrently for different purposes:
- Operations team: line format for monitoring
- Security team: CEF format for SIEM
- Compliance team: JSON format for auditing
- Development team: debug format for troubleshooting

### 2. Format-Specific Configuration
Each plugin can have configuration options specific to its format:
- Syslog: facility, RFC format, hostname
- CSV: delimiter, quote character, headers
- CEF: device vendor, product, version
- JSON: pretty printing, field inclusion

### 3. Improved Maintainability
- **Single Responsibility**: Each plugin does one thing well
- **Independent Updates**: Can modify one format without affecting others
- **Easier Testing**: Focused test coverage for each format
- **Clear Code Organization**: Format logic is self-contained

### 4. Performance Optimization
- **Format-Specific Optimizations**: Can optimize each format's specific needs
- **Reduced Conditional Logic**: No runtime format switching overhead
- **Independent Buffering**: Each format can use optimal buffering strategy

## Implementation Requirements

### 1. Plugin Discovery
Update plugin discovery to recognize new plugin names (Financial Services Priority Order):
```python
AUDITING_PLUGINS = {
    # Financial Services Priority Order
    'cef_auditing': CefAuditingPlugin,           # Priority 1: SIEM integration
    'syslog_auditing': SyslogAuditingPlugin,     # Priority 2: TLS transport
    'csv_auditing': CsvAuditingPlugin,           # Priority 3: SOX compliance
    'json_auditing': JsonAuditingPlugin,         # Priority 4: GRC platforms
    
    # Operational formats
    'line_auditing': HumanReadableAuditingPlugin,
    'debug_auditing': HumanReadableAuditingPlugin,
    
    # Future formats
    'gelf_auditing': GelfAuditingPlugin,
    'leef_auditing': LeefAuditingPlugin,
    'otel_auditing': OtelAuditingPlugin,
}
```

### 2. Configuration Schema Updates
Create format-specific configuration schemas:
```python
class JsonAuditingConfig(BaseModel):
    output_file: str
    include_request_body: bool = False
    pretty_print: bool = False
    critical: bool = False

class SyslogAuditingConfig(BaseModel):
    output_file: str
    syslog_config: SyslogConfig = SyslogConfig()
    critical: bool = False
```

### 3. Testing Strategy
- **Unit tests** for each plugin independently
- **Integration tests** for multiple plugins running simultaneously
- **Performance tests** comparing old vs new architecture
- **Migration tests** ensuring configuration compatibility

## Risk Assessment

### Low Risk
- **Incremental Migration**: Can implement gradually
- **Clear Separation**: Each format is self-contained
- **Proven Pattern**: Common in enterprise software

### Medium Risk
- **Configuration Complexity**: More plugins to configure
- **Discovery Complexity**: Plugin loading becomes more complex

### Mitigation Strategies
- **Clear Documentation**: Comprehensive implementation guide
- **Configuration Validation**: Clear error messages for invalid configs
- **Examples**: Provide common configuration patterns
- **Gradual Rollout**: Can implement formats incrementally

## Success Metrics

### Functionality
- **Multiple Format Support**: Users can run 3+ formats simultaneously
- **Zero Data Loss**: No audit events lost during migration
- **Configuration Clarity**: Format-specific options clearly separated

### Performance
- **Maintained Throughput**: No performance degradation
- **Reduced Memory Usage**: Format-specific optimizations reduce overhead
- **Faster Startup**: Plugin loading optimizations

### User Experience
- **Easier Configuration**: Format-specific options are discoverable
- **Better Documentation**: Clear examples for each format
- **Flexible Deployment**: Users can choose exactly what they need

## Acceptance Criteria

### Implementation Complete When:
- [ ] Base AuditingPlugin class implemented with shared functionality
- [ ] All existing formats extracted to separate plugins
- [ ] Configuration schemas updated for format-specific options
- [ ] Plugin discovery supports new plugin names
- [ ] All tests pass with new architecture
- [ ] Documentation updated with new configuration examples
- [ ] Implementation guide created for new plugin architecture
- [ ] Performance benchmarks show no degradation
- [ ] Multiple simultaneous formats validated in integration tests

### Success Metrics:
- **Format Independence**: Each format plugin can be developed/tested independently
- **Configuration Clarity**: Format-specific options are clearly separated
- **User Flexibility**: Users can run any combination of formats they need
- **Maintenance Efficiency**: Format updates don't affect other formats