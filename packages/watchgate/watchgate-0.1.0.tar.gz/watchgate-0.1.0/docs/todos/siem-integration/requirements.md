# SIEM Integration Technical Requirements

## Executive Summary

This document specifies technical requirements for implementing SIEM (Security Information and Event Management) connectors in Watchgate. Based on market analysis, we prioritize integration with the three dominant SIEM platforms in enterprise environments:

1. **Splunk Enterprise Security** (52% market share in financial services)
2. **IBM QRadar** (9% market share with SOX extensions)
3. **Microsoft Azure Sentinel** (13% market share, growing cloud adoption)

## Architecture Overview

### Integration Model
- **Plugin-based approach**: Each SIEM platform implemented as an auditing plugin
- **Configurable transport**: Support multiple delivery methods per platform
- **Format flexibility**: Platform-specific log formats with fallback options
- **Reliability**: Buffering, retry logic, and failover mechanisms
- **Performance**: Asynchronous delivery with batching support

### Core Components
```
Watchgate Core
├── SIEM Connector Framework
│   ├── Transport Layer (TLS Syslog, HTTPS, TCP)
│   ├── Format Engine (CEF, LEEF, JSON, Syslog)
│   ├── Authentication Manager
│   └── Delivery Manager (Buffering, Retry, Failover)
├── Platform-Specific Plugins
│   ├── SplunkPlugin
│   ├── QRadarPlugin
│   └── AzureSentinelPlugin
└── Configuration System
    ├── SIEM Platform Profiles
    └── Transport Configuration
```

## Platform-Specific Requirements

### 1. Splunk Enterprise Security

#### Preferred Log Formats
1. **CEF (Common Event Format)** - Primary recommendation
   - Version: CEF:0
   - Extensions: Custom fields for Watchgate-specific data
   - Field mapping: MCP requests/responses to CEF fields

2. **JSON** - Secondary option
   - Structured JSON with timestamp, severity, and event data
   - Compatible with Splunk's JSON parsing

3. **Syslog RFC3164/RFC5424** - Fallback option
   - Structured syslog with key=value pairs
   - Facility: Local0 (16), Severity: Info (6)

#### Transport Methods
1. **Splunk Connect for Syslog (SC4S)** - Primary
   - TLS Syslog (RFC5424 over TLS)
   - Port: 6514 (default)
   - Certificate validation required
   - Mutual TLS support

2. **HTTP Event Collector (HEC)** - Secondary
   - HTTPS POST to /services/collector/event
   - Bearer token authentication
   - Batch API support (up to 1MB per request)
   - JSON payload format

3. **Universal Forwarder** - Tertiary
   - File-based input with log rotation
   - Splunk forwarder monitors Watchgate log files
   - Requires local Splunk forwarder installation

#### Authentication Requirements
- **SC4S**: Client certificate + CA validation
- **HEC**: Bearer token (minimum 36 characters)
- **File-based**: File system permissions

#### Configuration Schema
```yaml
siem:
  splunk:
    enabled: true
    transport: "sc4s"  # sc4s | hec | file
    format: "cef"      # cef | json | syslog
    
    # SC4S Configuration
    sc4s:
      host: "splunk-sc4s.example.com"
      port: 6514
      tls:
        enabled: true
        verify_certs: true
        ca_file: "/path/to/ca.pem"
        cert_file: "/path/to/client.pem"
        key_file: "/path/to/client.key"
        
    # HEC Configuration
    hec:
      endpoint: "https://splunk.example.com:8088"
      token: "your-hec-token"
      index: "watchgate"
      source: "watchgate"
      sourcetype: "watchgate:audit"
      
    # Delivery Options
    delivery:
      batch_size: 100
      batch_timeout: 30
      retry_attempts: 3
      retry_backoff: 2.0
```

#### SC4S Integration Details
- **Destination parsing**: SC4S automatically routes based on source metadata
- **Index routing**: Configure SC4S filters for Watchgate events
- **Field extraction**: Use SC4S parsers for structured data extraction
- **Performance**: SC4S handles high-volume ingestion with buffering

### 2. IBM QRadar

#### Preferred Log Formats
1. **LEEF (Log Event Extended Format)** - Primary
   - Version: LEEF:2.0
   - IBM-native format with optimal QRadar parsing
   - Custom attributes for Watchgate event data

2. **CEF** - Secondary
   - Standard CEF format with QRadar-specific extensions
   - Good compatibility with existing QRadar parsers

3. **JSON** - Tertiary
   - Structured JSON for custom parsing
   - Requires QRadar DSM configuration

#### Transport Methods
1. **Syslog over TLS** - Primary
   - RFC5424 format over TLS
   - Port: 6514 (configurable)
   - Certificate-based authentication

2. **Syslog over UDP/TCP** - Secondary
   - Traditional syslog (RFC3164)
   - UDP Port: 514, TCP Port: 514
   - Less secure but widely supported

3. **QRadar REST API** - Tertiary
   - Direct API submission via HTTPS
   - OAuth 2.0 or API key authentication
   - Real-time event submission

#### Authentication Requirements
- **TLS Syslog**: Client certificate validation
- **Plain Syslog**: Source IP filtering
- **REST API**: OAuth 2.0 token or API key

#### Device Support Module (DSM) Requirements
- **Custom DSM**: Watchgate-specific event parsing
- **Event mapping**: Map MCP events to QRadar's Unified Data Model
- **Property definitions**: Custom properties for Watchgate fields
- **Test patterns**: Regex patterns for event classification

#### Configuration Schema
```yaml
siem:
  qradar:
    enabled: true
    transport: "syslog_tls"  # syslog_tls | syslog_udp | syslog_tcp | rest_api
    format: "leef"           # leef | cef | json
    
    # Syslog Configuration
    syslog:
      host: "qradar.example.com"
      port: 6514
      facility: "local0"
      severity: "info"
      tls:
        enabled: true
        verify_certs: true
        ca_file: "/path/to/qradar-ca.pem"
        cert_file: "/path/to/client.pem"
        key_file: "/path/to/client.key"
        
    # REST API Configuration
    rest_api:
      endpoint: "https://qradar.example.com/api/ariel/events"
      auth_method: "oauth2"  # oauth2 | api_key
      client_id: "watchgate-client"
      client_secret: "your-client-secret"
      
    # DSM Configuration
    dsm:
      device_type: "Watchgate"
      event_category: "Application Activity"
      log_source_identifier: "watchgate"
```

#### DSM Development Requirements
- **Event patterns**: Regex patterns for LEEF/CEF parsing
- **Property extraction**: Map log fields to QRadar properties
- **Categorization**: Classify events into appropriate QRadar categories
- **Testing**: Validate parsing with sample Watchgate events

### 3. Microsoft Azure Sentinel

#### Preferred Log Formats
1. **JSON** - Primary
   - Azure-native JSON format
   - CommonSecurityLog schema compatibility
   - Custom fields in AdditionalExtensions

2. **CEF** - Secondary
   - Standard CEF format via CommonSecurityLog table
   - Automatic parsing via built-in parsers
   - Good compatibility with Azure analytics

3. **Syslog** - Tertiary
   - RFC5424 format via Syslog table
   - Basic structured logging
   - Requires custom parsing queries

#### Transport Methods
1. **Azure Monitor Data Collector API** - Primary
   - HTTPS POST to custom log ingestion
   - Azure AD authentication
   - Direct ingestion to Log Analytics workspace

2. **Azure Event Hubs** - Secondary
   - High-throughput streaming ingestion
   - Kafka-compatible protocol
   - Automatic scaling and partitioning

3. **Log Analytics Agent** - Tertiary
   - File-based ingestion via agent
   - Custom log parsing rules
   - Requires agent installation

#### Authentication Requirements
- **Data Collector API**: Azure AD service principal or shared key
- **Event Hubs**: Connection string or Azure AD
- **Log Analytics Agent**: Workspace ID and key

#### Data Connector Requirements
- **Custom connector**: Watchgate-specific data ingestion
- **Schema mapping**: Map MCP events to Sentinel tables
- **Analytics rules**: Detection rules for Watchgate events
- **Workbook**: Visualization dashboard for Watchgate data

#### Configuration Schema
```yaml
siem:
  azure_sentinel:
    enabled: true
    transport: "data_collector_api"  # data_collector_api | event_hubs | log_analytics_agent
    format: "json"                   # json | cef | syslog
    
    # Data Collector API Configuration
    data_collector_api:
      workspace_id: "your-workspace-id"
      shared_key: "your-shared-key"
      log_type: "Watchgate"
      endpoint: "https://your-workspace-id.ods.opinsights.azure.com/api/logs"
      
    # Event Hubs Configuration
    event_hubs:
      connection_string: "Endpoint=sb://your-namespace.servicebus.windows.net/..."
      hub_name: "watchgate-events"
      
    # Authentication
    auth:
      method: "service_principal"  # service_principal | shared_key
      tenant_id: "your-tenant-id"
      client_id: "your-client-id"
      client_secret: "your-client-secret"
      
    # Schema Configuration
    schema:
      table_name: "Watchgate_CL"
      timestamp_field: "TimeGenerated"
      custom_fields:
        - "RequestId_s"
        - "MCPMethod_s"
        - "UpstreamServer_s"
        - "SecurityDecision_s"
```

#### Sentinel Integration Details
- **KQL queries**: Custom analytics rules for Watchgate events
- **Incident creation**: Automatic incident generation for security events
- **Threat intelligence**: Integration with threat intelligence feeds
- **SOAR integration**: Automated response via Logic Apps

## Implementation Architecture

### Plugin Framework

#### Base SIEM Plugin Interface
```python
class SIEMPlugin(AuditingPlugin):
    """Base class for SIEM integration plugins."""
    
    async def initialize(self) -> None:
        """Initialize SIEM connection and authentication."""
        pass
    
    async def log_request(self, request: MCPRequest, decision: PolicyDecision) -> None:
        """Log MCP request with security decision."""
        pass
    
    async def log_response(self, request: MCPRequest, response: MCPResponse) -> None:
        """Log MCP response."""
        pass
    
    async def log_error(self, request: MCPRequest, error: Exception) -> None:
        """Log error events."""
        pass
    
    async def flush_events(self) -> None:
        """Flush buffered events to SIEM."""
        pass
```

#### Transport Layer
```python
class SIEMTransport(ABC):
    """Abstract base class for SIEM transport methods."""
    
    @abstractmethod
    async def send_event(self, event: Dict[str, Any]) -> bool:
        """Send single event to SIEM."""
        pass
    
    @abstractmethod
    async def send_batch(self, events: List[Dict[str, Any]]) -> bool:
        """Send batch of events to SIEM."""
        pass
```

#### Format Engine
```python
class SIEMFormatter(ABC):
    """Abstract base class for SIEM event formatting."""
    
    @abstractmethod
    def format_request(self, request: MCPRequest, decision: PolicyDecision) -> Dict[str, Any]:
        """Format MCP request for SIEM consumption."""
        pass
    
    @abstractmethod
    def format_response(self, request: MCPRequest, response: MCPResponse) -> Dict[str, Any]:
        """Format MCP response for SIEM consumption."""
        pass
```

### Event Schema Design

#### Core Event Structure
```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "event_type": "mcp_request",
  "severity": "info",
  "source": "watchgate",
  "version": "1.0",
  "correlation_id": "req-123456",
  "session_id": "session-abc",
  "client_info": {
    "client_id": "claude-desktop",
    "client_version": "1.0.0"
  },
  "mcp_data": {
    "method": "tools/call",
    "tool_name": "filesystem",
    "parameters": {
      "path": "/tmp/test.txt",
      "operation": "read"
    }
  },
  "security_decision": {
    "allowed": true,
    "plugin": "filesystem_security",
    "reason": "Path allowed by policy",
    "risk_score": 2
  },
  "upstream_server": {
    "name": "filesystem-server",
    "command": "node filesystem-mcp-server.js"
  }
}
```

#### Event Types
- **mcp_request**: MCP method invocation
- **mcp_response**: MCP method response
- **security_decision**: Security policy decision
- **audit_event**: General audit event
- **error_event**: Error or exception
- **system_event**: Watchgate system events

### Reliability Features

#### Buffering Strategy
- **Memory buffer**: In-memory queue for recent events
- **Disk buffer**: Persistent storage for event overflow
- **Buffer limits**: Configurable size and time limits
- **Overflow handling**: Drop oldest events when buffer is full

#### Retry Logic
- **Exponential backoff**: Increasing delay between retries
- **Maximum attempts**: Configurable retry limit
- **Circuit breaker**: Temporary failure protection
- **Failover**: Secondary SIEM endpoints

#### Monitoring
- **Delivery metrics**: Success/failure rates
- **Performance metrics**: Latency and throughput
- **Health checks**: SIEM connectivity monitoring
- **Alerting**: Failed delivery notifications

## Configuration Management

### Global SIEM Configuration
```yaml
siem:
  # Global settings
  enabled: true
  buffer_size: 1000
  flush_interval: 30
  retry_attempts: 3
  retry_backoff: 2.0
  
  # Platform configurations
  platforms:
    splunk:
      enabled: true
      priority: 1
      # ... platform-specific config
    
    qradar:
      enabled: false
      priority: 2
      # ... platform-specific config
      
    azure_sentinel:
      enabled: false
      priority: 3
      # ... platform-specific config
```

### Environment-Specific Overrides
- **Development**: Mock SIEM endpoints for testing
- **Staging**: Separate SIEM instances for validation
- **Production**: Full SIEM integration with monitoring

## Security Considerations

### Authentication Security
- **Certificate management**: Automated certificate rotation
- **Token security**: Encrypted token storage
- **Credential isolation**: Separate credentials per environment
- **Audit logging**: Log all authentication attempts

### Data Privacy
- **PII filtering**: Remove sensitive data before SIEM transmission
- **Data minimization**: Send only necessary event data
- **Encryption**: TLS encryption for all transport methods
- **Compliance**: GDPR, HIPAA, SOX compliance considerations

### Network Security
- **Firewall rules**: Restrict SIEM connectivity to authorized systems
- **Network segmentation**: Isolate SIEM traffic
- **VPN connectivity**: Secure tunneling for remote SIEM access
- **Certificate pinning**: Prevent man-in-the-middle attacks

## Performance Requirements

### Throughput Targets
- **Minimum**: 1,000 events per second
- **Target**: 10,000 events per second
- **Peak**: 50,000 events per second (with buffering)

### Latency Requirements
- **Normal operation**: <100ms event delivery
- **Batch processing**: <1 second batch delivery
- **Retry scenarios**: <30 second maximum delay

### Resource Utilization
- **Memory usage**: <100MB for buffering
- **CPU overhead**: <5% additional load
- **Network bandwidth**: Configurable rate limiting

## Testing Requirements

### Unit Testing
- **Plugin functionality**: Individual SIEM plugin testing
- **Transport methods**: Mock SIEM endpoints
- **Format validation**: Event format compliance
- **Configuration parsing**: Schema validation

### Integration Testing
- **End-to-end flow**: Watchgate → SIEM platform
- **Real SIEM instances**: Validation with actual platforms
- **Performance testing**: Load testing with realistic data
- **Failover testing**: Network interruption scenarios

### Compliance Testing
- **Format compliance**: CEF, LEEF, JSON schema validation
- **Security testing**: Authentication and encryption validation
- **Audit testing**: Verify all events are logged correctly
- **Regulatory compliance**: SOX, GDPR, HIPAA requirements

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- SIEM plugin framework
- Base transport and format classes
- Configuration schema
- Unit testing framework

### Phase 2: Splunk Integration (Weeks 3-4)
- Splunk plugin implementation
- SC4S and HEC transport methods
- CEF format support
- Integration testing

### Phase 3: QRadar Integration (Weeks 5-6)
- QRadar plugin implementation
- LEEF format support
- DSM development
- Performance optimization

### Phase 4: Azure Sentinel Integration (Weeks 7-8)
- Azure Sentinel plugin implementation
- Data Collector API transport
- JSON format optimization
- Sentinel analytics rules

### Phase 5: Production Readiness (Weeks 9-10)
- Reliability features (buffering, retry, failover)
- Performance optimization
- Security hardening
- Documentation and deployment guides

## Success Metrics

### Functional Metrics
- **Event delivery rate**: >99.9% successful delivery
- **Format compliance**: 100% valid event formats
- **Platform compatibility**: Full integration with all target SIEMs
- **Configuration coverage**: Support for all major deployment scenarios

### Performance Metrics
- **Throughput**: Meet or exceed performance targets
- **Latency**: <100ms normal operation, <1s batch processing
- **Resource usage**: Within specified limits
- **Availability**: >99.9% uptime

### Security Metrics
- **Authentication success**: 100% secure authentication
- **Data encryption**: All data encrypted in transit
- **Compliance**: Pass all regulatory compliance tests
- **Audit completeness**: 100% event coverage

## Deliverables

### Code Deliverables
- SIEM plugin framework
- Platform-specific plugins (Splunk, QRadar, Azure Sentinel)
- Transport layer implementations
- Format engines (CEF, LEEF, JSON, Syslog)
- Configuration schema and validation
- Comprehensive test suite

### Documentation Deliverables
- Technical implementation guide
- Configuration reference
- SIEM-specific setup guides
- Troubleshooting documentation
- Performance tuning guide
- Security best practices

### Integration Deliverables
- QRadar DSM package
- Splunk app/add-on (if needed)
- Azure Sentinel connector
- Sample configuration files
- Deployment scripts
- Monitoring dashboards

This technical requirements document provides the foundation for implementing robust SIEM integration capabilities in Watchgate, ensuring compatibility with the most important enterprise SIEM platforms while maintaining security, performance, and reliability standards.