# Auditing Plugin Migration Guide

## Overview
Watchgate v0.1.0 has replaced the generic `file_auditing` plugin with format-specific auditing plugins. Each plugin is optimized for its specific use case and output format.

## Plugin Name Changes

| Old Plugin | New Plugin | Purpose |
|------------|------------|---------|
| `file_auditing` with `format: "line"` | `line_auditing` | Human-readable single-line format for operations |
| `file_auditing` with `format: "debug"` | `debug_auditing` | Detailed format for troubleshooting |
| `file_auditing` with `format: "json"` | `json_auditing` | JSON/JSONL format for API integration |
| `file_auditing` with `format: "csv"` | `csv_auditing` | CSV format for compliance reporting |
| N/A | `cef_auditing` | CEF format for SIEM integration |
| N/A | `syslog_auditing` | Syslog format for centralized logging |
| N/A | `otel_auditing` | OpenTelemetry format for observability |

## Configuration Changes

### Before (Old Format)
```yaml
auditing:
  - policy: "file_auditing"
    enabled: true
    config:
      file: "logs/audit.log"
      format: "json"  # or "line", "debug", "csv"
      max_file_size_mb: 10
      backup_count: 5
```

### After (New Format)
```yaml
auditing:
  - policy: "json_auditing"  # Choose specific plugin for format
    enabled: true
    config:
      output_file: "logs/audit.log"  # Changed from 'file' to 'output_file'
      # Format-specific options (varies by plugin)
      pretty_print: false  # JSON-specific
      include_request_body: true  # JSON-specific
      max_file_size_mb: 10
      backup_count: 5
```

## Key Changes

1. **No more `format` parameter** - Format is determined by plugin choice
2. **`file` renamed to `output_file`** - Consistent naming across plugins
3. **Format-specific options** - Each plugin has specialized configuration options
4. **Path expansion support** - All plugins support `~` and environment variables in paths

## Format-Specific Options

### JSON Auditing (`json_auditing`)
- `pretty_print`: Format with indentation (default: false)
- `include_request_body`: Include full request parameters (default: false)
- `compliance_schema`: Choose compliance format (default: "standard")
- `include_risk_metadata`: Include risk assessment (default: true)
- `timestamp_format`: "iso8601" or "unix_timestamp" (default: "iso8601")

### CSV Auditing (`csv_auditing`)
- `csv_config.delimiter`: Field delimiter (default: ",")
- `csv_config.quote_char`: Quote character (default: '"')
- `csv_config.audit_trail_format`: "SOX_404", "GDPR", or "standard"
- `csv_config.include_compliance_columns`: Add compliance metadata (default: true)

### CEF Auditing (`cef_auditing`)
- `cef_config.device_vendor`: Vendor name (default: "Watchgate")
- `cef_config.device_product`: Product name (default: "MCP Gateway")
- `cef_config.device_version`: Version (default: auto-detected)
- `cef_config.compliance_tags`: List of compliance frameworks

### Syslog Auditing (`syslog_auditing`)
- `syslog_config.rfc_format`: "5424" or "3164" (default: "5424")
- `syslog_config.facility`: Syslog facility code (default: 16)
- `syslog_config.transport`: "file", "udp", "tcp", "tls" (default: "file")

### OpenTelemetry Auditing (`otel_auditing`)
- `service_name`: Service identifier (default: "watchgate")
- `service_version`: Version (default: auto-detected)
- `deployment_environment`: Environment name (default: "production")
- `include_trace_correlation`: Enable trace correlation (default: true)

## Migration Examples

### Example 1: Simple JSON Logging
**Before:**
```yaml
auditing:
  - policy: "file_auditing"
    config:
      file: "audit.log"
      format: "json"
```

**After:**
```yaml
auditing:
  - policy: "json_auditing"
    config:
      output_file: "audit.log"
```

### Example 2: Human-Readable Logging
**Before:**
```yaml
auditing:
  - policy: "file_auditing"
    config:
      file: "/var/log/watchgate.log"
      format: "line"
```

**After:**
```yaml
auditing:
  - policy: "line_auditing"
    config:
      output_file: "/var/log/watchgate.log"
```

### Example 3: JSON Lines for Log Aggregation
**Before:**
```yaml
auditing:
  - policy: "file_auditing"
    config:
      file: "events.jsonl"
      format: "json"
```

**After:**
```yaml
auditing:
  - policy: "json_auditing"
    config:
      output_file: "events.jsonl"
      pretty_print: false  # Ensures single-line JSON (JSONL)
      include_request_body: true
```

## Benefits of the New System

1. **Type Safety**: Each plugin has its own configuration schema
2. **Better Validation**: Format-specific options are validated at startup
3. **Clearer Intent**: Plugin name immediately indicates output format
4. **Extensibility**: New formats can be added without affecting existing ones
5. **Performance**: Format-specific optimizations in each plugin
6. **Maintainability**: Separate code paths for each format reduce complexity

## Backward Compatibility

Since this is v0.1.0 (first release), there is no backward compatibility requirement. All configurations must be updated to use the new plugin names and parameters.