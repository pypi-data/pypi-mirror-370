# File Auditing Plugin

**Status**: Implemented

## Problem Statement
Need to log MCP communications to files for audit trail, debugging, and compliance purposes.

## Requirements
- Log all MCP method calls to file
- Include timestamps and request information
- Human-readable format
- Basic log rotation by size
- Configurable log file location
- Integration with security plugin decisions

## Success Criteria
- [x] Logs all MCP requests and responses
- [x] Timestamps and structured information
- [x] Human-readable log format
- [x] Log rotation when files get large
- [x] Configurable file path
- [x] Includes security plugin decisions

## Configuration
```yaml
plugins:
  auditing:
    - policy: "file_auditing"
      enabled: true
      config:
        file: "watchgate.log"
        max_size_mb: 10
        format: "simple"
        mode: "all_events"
```

## References
- Implementation: `watchgate/plugins/auditing/file_auditing.py`
- Tests: `tests/unit/test_file_auditing_plugin.py`