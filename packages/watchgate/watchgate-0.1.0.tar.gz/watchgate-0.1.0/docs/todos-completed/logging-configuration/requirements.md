# Logging Configuration System

**Status**: Implemented

## Problem Statement
Need flexible logging configuration with multiple output destinations and proper log management for production deployments.

## Requirements
- YAML-based logging configuration integrated with main config
- Multiple output destinations: console (stderr), file, or both
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Automatic log rotation based on file size with backup retention
- Custom log message formatting with timestamps
- Runtime log level override via `--verbose` command-line flag
- Graceful error handling with fallback to console logging
- Backward compatibility with existing command-line behavior

## Success Criteria
- [x] YAML logging configuration schema
- [x] Multiple simultaneous output handlers
- [x] Automatic directory creation and log rotation
- [x] Custom format strings with timestamps
- [x] Verbose flag overrides configured level
- [x] Falls back to stderr when file operations fail
- [x] Maintains backward compatibility

## Constraints
- Must not break existing configurations without logging section
- File operations may fail (permissions, disk space)
- Performance impact should be minimal

## Implementation Notes
- Pydantic validation for logging settings
- Uses Python's RotatingFileHandler for file management
- Handler setup optimized for common configurations
- Enhanced error handling with clear messages

## Configuration
```yaml
logging:
  level: "INFO"
  handlers: ["stderr", "file"]
  file_path: "logs/watchgate.log"
  max_file_size_mb: 10
  backup_count: 5
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
```

## References
- Implementation: `watchgate/config/models.py`, `watchgate/main.py`
- Tests: `tests/unit/test_logging_config.py`
- Integration: `tests/unit/test_main_logging.py`