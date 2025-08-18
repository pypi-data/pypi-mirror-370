# Audit System

*[Home](../../README.md) > [User Guide](../README.md) > [Core Concepts](README.md) > Audit System*

Watchgate's audit system provides comprehensive visibility into AI agent activities, security decisions, and system operations. The audit system is designed to support compliance requirements, security monitoring, incident response, and operational debugging.

## Logging Architecture

```
                    Watchgate Proxy
                         │
                    ┌────┴─────┐
                    │  Plugin  │
                    │ Manager  │
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │Security │ │Auditing │ │ System  │
        │ Events  │ │ Events  │ │  Logs   │
        └─────────┘ └─────────┘ └─────────┘
              │          │          │
              └──────────┼──────────┘
                         ▼
                   ┌─────────────┐
                   │ File Logger │
                   │   Plugin    │
                   └─────────────┘
                         │
                    ┌────┴─────┐
                    │ Log Files│
                    │ • Simple │
                    │ • JSON   │
                    │ • Detail │
                    └──────────┘
```

## Log Types

### Security Logs
Record all security-related events and decisions:

- **Tool Access Decisions**: Allowed/blocked tool execution attempts
- **Content Access Decisions**: Allowed/blocked resource access attempts
- **Plugin Execution**: Which security plugins processed each request
- **Policy Violations**: When requests violate security policies

### Audit Logs
Comprehensive record of all AI agent activities:

- **Request/Response Pairs**: Complete MCP communication logs
- **Tool Executions**: Every tool call and its result
- **Resource Access**: All file and resource operations
- **Session Information**: Client connections and disconnections

### System Logs
Operational information about Watchgate itself:

- **Startup/Shutdown**: Watchgate lifecycle events
- **Configuration Loading**: Plugin initialization and configuration validation
- **Error Conditions**: System errors, plugin failures, connectivity issues
- **Performance Metrics**: Request processing times, plugin execution duration

## Log Formats

Watchgate supports multiple log formats to accommodate different use cases:

### JSON Format (Default)
Machine-readable format for automated processing:

```json
{"timestamp": "2024-01-15T10:30:15Z", "event_type": "TOOL_CALL", "tool": "read_file", "params": {"path": "document.txt"}, "request_id": "123"}
{"timestamp": "2024-01-15T10:30:16Z", "event_type": "TOOL_RESULT", "tool": "read_file", "status": "SUCCESS", "request_id": "123"}
{"timestamp": "2024-01-15T10:30:45Z", "event_type": "SECURITY_BLOCK", "tool": "delete_file", "reason": "Tool blocked by allowlist policy", "request_id": "124"}
```

**Use Cases**:
- Log aggregation systems (ELK, Splunk)
- Automated analysis and alerting
- API integration with monitoring tools

### Simple Format
Human-readable format for easy analysis:

```
2024-01-15 10:30:15 UTC - REQUEST: tools/call - read_file - ALLOWED
2024-01-15 10:30:16 UTC - RESPONSE: success
2024-01-15 10:30:45 UTC - SECURITY_BLOCK: delete_file - [tool_allowlist] Tool blocked by allowlist policy
```

**Use Cases**:
- Manual log review
- Quick debugging
- Simple monitoring scripts

### Detailed Format
Comprehensive format with maximum context:

```
[2024-01-15 10:30:15.123] REQUEST_ID=123 SOURCE=claude_desktop EVENT=TOOL_CALL TOOL=read_file PARAMS={"path": "document.txt"} SECURITY_CHECKS=["tool_allowlist:ALLOWED"]
[2024-01-15 10:30:16.456] REQUEST_ID=123 SOURCE=filesystem_server EVENT=TOOL_RESULT TOOL=read_file STATUS=SUCCESS DURATION=1.333s
[2024-01-15 10:30:45.789] REQUEST_ID=124 SOURCE=claude_desktop EVENT=SECURITY_BLOCK TOOL=delete_file REASON="Tool blocked by allowlist policy" PLUGIN=tool_allowlist POLICY_MODE=allowlist
```

**Use Cases**:
- Forensic analysis
- Performance debugging
- Compliance reporting

### CEF Format
Machine-readable format for SIEM systems and security event correlation:

```
CEF:0|Watchgate|MCP Gateway|1.0.0|100|MCP Request|6|rt=2023-12-01T14:30:25.123456Z request=123 act=allowed cs1=tool_allowlist cs1Label=Plugin cs2=tools/call cs2Label=Method cs3=read_file cs3Label=Tool src=127.0.0.1 dst=127.0.0.1
CEF:0|Watchgate|MCP Gateway|1.0.0|200|Security Block|8|rt=2023-12-01T14:30:25.123456Z request=456 act=blocked reason=Tool not in allowlist cs1=tool_allowlist cs1Label=Plugin cs2=tools/call cs2Label=Method cs3=delete_file cs3Label=Tool src=127.0.0.1 dst=127.0.0.1
```

**Use Cases**:
- SIEM integration (Splunk, ArcSight, Azure Sentinel)
- Security event correlation
- Compliance reporting and auditing
- Enterprise security monitoring

**Configuration**:
```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      config:
        format: "cef"
        cef_config:
          device_vendor: "Watchgate"      # Optional override
          device_product: "MCP Gateway"      # Optional override
          device_version: "auto"           # Auto-detect or explicit version
```

### CSV Format
Structured format for spreadsheet and data analysis tools:

```csv
timestamp,event_type,method,tool,status,request_id,plugin,reason,duration_ms,server_name
2023-12-01T14:30:25.123456Z,REQUEST,tools/call,read_file,ALLOWED,123,tool_allowlist,Request approved,,
2023-12-01T14:30:25.123456Z,SECURITY_BLOCK,tools/call,delete_file,BLOCKED,456,tool_allowlist,Tool not in allowlist,,
```

**Use Cases**:
- Data analysis and reporting
- Spreadsheet import
- Business intelligence tools
- Statistical analysis

**Configuration**:
```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      config:
        format: "csv"
        csv_config:
          delimiter: ","
          quote_style: "minimal"
          null_value: ""
```

## Log Content

Watchgate logs all MCP communications and security decisions by default, providing complete visibility into:

- **Tool Executions**: Every tool call and its result
- **Security Decisions**: All allow/block decisions with reasoning
- **Protocol Communications**: MCP handshakes and status updates
- **Plugin Activities**: Which plugins processed each request
- **Performance Metrics**: Request durations and response times

## Log Configuration

### Basic Configuration
```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      enabled: true
      config:
        output_file: "logs/watchgate.log"
        format: "json"
```

### Advanced Configuration
```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      enabled: true
      config:
        output_file: "logs/watchgate.log"
        format: "json"
        max_file_size_mb: 50
        backup_count: 10
```

### Multiple Log Files
Configure different log files for different purposes:

```yaml
plugins:
  auditing:
    # JSON format for automated analysis
    - policy: "file_auditing"
      enabled: true
      config:
        output_file: "logs/audit.log"
        format: "json"
        
    # Simple format for manual review
    - policy: "file_auditing"
      enabled: true
      config:
        output_file: "logs/human-readable.log"
        format: "simple"
        
    # Detailed format for forensic analysis
    - policy: "file_auditing"
      enabled: true
      config:
        output_file: "logs/detailed.log"
        format: "detailed"
```

## Log Rotation and Management

### Automatic Log Rotation
Watchgate automatically rotates logs to prevent disk space issues:

```yaml
config:
  output_file: "logs/watchgate.log"
  max_file_size_mb: 50      # Rotate when file reaches 50MB
  backup_count: 10          # Keep 10 backup files
```

**Rotation Behavior**:
- Current log: `watchgate.log`
- Previous logs: `watchgate.log.1`, `watchgate.log.2`, etc.
- Oldest logs are automatically deleted when `backup_count` is exceeded

### Manual Log Management
```bash
# View recent log entries
tail -f logs/watchgate.log

# Search for specific events
grep "SECURITY_BLOCK" logs/watchgate.log

# Analyze log patterns
awk '/TOOL_CALL/ {count++} END {print "Total tool calls:", count}' logs/watchgate.log

# Compress old logs
gzip logs/watchgate.log.1 logs/watchgate.log.2
```

## Log Analysis and Monitoring

### Real-Time Monitoring
```bash
# Monitor security events
tail -f logs/watchgate.log | jq -r 'select(.event_type == "SECURITY_BLOCK" or .event_type == "PLUGIN_ERROR")'

# Watch tool usage
tail -f logs/watchgate.log | jq -r 'select(.event_type == "REQUEST" and .tool)'

# Monitor specific tools
tail -f logs/watchgate.log | jq -r 'select(.tool == "delete_file")'
```

### Security Analytics
```bash
# Most frequently blocked tools
jq -r 'select(.event_type == "SECURITY_BLOCK") | .tool' logs/watchgate.log | sort | uniq -c | sort -nr

# Security events by hour
jq -r 'select(.event_type == "SECURITY_BLOCK") | .timestamp[0:13]' logs/watchgate.log | sort | uniq -c

# Plugin performance analysis
jq -r 'select(.duration_ms) | .duration_ms' logs/watchgate.log | sort -n | tail -10

# Security plugin activity
jq -r 'select(.event_type == "SECURITY_BLOCK") | .plugin' logs/watchgate.log | sort | uniq -c | sort -nr
```

### Operational Analytics
```bash
# Tool usage statistics
jq -r 'select(.event_type == "REQUEST" and .tool) | .tool' logs/watchgate.log | sort | uniq -c | sort -nr

# Request volume by hour
jq -r 'select(.event_type == "REQUEST") | .timestamp[0:13]' logs/watchgate.log | sort | uniq -c

# Average response time
jq -r 'select(.event_type == "RESPONSE" and .duration_ms) | .duration_ms' logs/watchgate.log | awk '{sum+=$1; count++} END {printf "Average: %.2f ms\n", sum/count}'

# Error rate analysis
total_requests=$(jq -r 'select(.event_type == "REQUEST")' logs/watchgate.log | wc -l)
error_responses=$(jq -r 'select(.event_type == "RESPONSE" and .status == "error")' logs/watchgate.log | wc -l)
echo "Error rate: $(echo "scale=2; $error_responses * 100 / $total_requests" | bc)%"
```

## Integration with External Systems

### ELK Stack Integration
For JSON format logs:

```yaml
# Logstash configuration for Watchgate logs
input {
  file {
    path => "/path/to/logs/watchgate.log"
    codec => "json"
    tags => ["watchgate"]
  }
}

filter {
  if "watchgate" in [tags] {
    mutate {
      add_field => { "source_system" => "watchgate" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "watchgate-%{+YYYY.MM.dd}"
  }
}
```

### Splunk Integration
```bash
# Splunk configuration for Watchgate logs
[monitor:///path/to/logs/watchgate.log]
disabled = false
index = watchgate
sourcetype = watchgate_json
```

### Custom Log Processing
```python
import json

def process_watchgate_logs(log_file):
    security_events = 0
    tool_usage = {}
    
    with open(log_file, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line)
                
                if log_entry.get('event_type') == 'SECURITY_BLOCK':
                    security_events += 1
                
                if log_entry.get('event_type') == 'TOOL_CALL':
                    tool = log_entry.get('tool', 'unknown')
                    tool_usage[tool] = tool_usage.get(tool, 0) + 1
                    
            except json.JSONDecodeError:
                continue
    
    return {
        'security_events': security_events,
        'tool_usage': tool_usage
    }
```

## Performance Considerations

### Log Buffer Management
```yaml
config:
  buffer_size: 1000        # Number of log entries to buffer
  flush_interval: 5        # Flush buffer every 5 seconds
```

### Disk Space Management
```yaml
config:
  max_file_size_mb: 25     # Smaller files for faster rotation
  backup_count: 5          # Fewer backups to save space
```

### Network Logging
For high-volume environments, consider network logging:

```yaml
config:
  remote_endpoint: "https://logs.company.com/watchgate"
  local_backup: true       # Still maintain local logs
```

## Compliance and Regulatory Requirements

### Audit Trail Requirements
Watchgate logging supports common compliance requirements:

- **Complete audit trail**: Every AI interaction is logged
- **Tamper-evident logs**: Log rotation and backup procedures
- **Retention policies**: Configurable log retention periods
- **Access controls**: File permissions protect log integrity

### GDPR Compliance
```yaml
config:
  anonymize_sensitive_data: true
  retention_days: 90
  personal_data_patterns: ["email", "phone", "ssn"]
```

### SOX Compliance
```yaml
config:
  financial_data_detection: true
  mandatory_logging: true
  log_integrity_checks: true
```

## Troubleshooting Log Issues

### Log Files Not Created
1. Check directory permissions
2. Verify disk space availability
3. Check file path in configuration
4. Ensure logging plugin is enabled

### Log Rotation Not Working
1. Verify `max_file_size_mb` setting
2. Check disk space for rotation
3. Ensure write permissions on log directory
4. Review error logs for rotation failures

### Performance Issues
1. Reduce log verbosity (`mode: "critical"`)
2. Increase buffer size and flush interval
3. Use log rotation with smaller file sizes
4. Consider remote logging for high-volume scenarios

## Summary

Watchgate's audit system provides:

- **Comprehensive Visibility**: Complete record of all AI agent activities
- **Flexible Formats**: Support for human-readable and machine-readable logs
- **Automatic Management**: Log rotation and retention handling
- **Security Focus**: Emphasis on security events and policy violations
- **Integration Ready**: Support for common log analysis tools
- **Compliance Support**: Features for regulatory and audit requirements

This audit system enables organizations to maintain complete visibility into AI agent behavior while supporting security monitoring, compliance, and operational requirements.
