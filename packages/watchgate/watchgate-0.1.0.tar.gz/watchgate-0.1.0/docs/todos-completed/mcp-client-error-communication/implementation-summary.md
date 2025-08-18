# MCP Client Error Communication - Implementation Summary

**Status**: Implemented ✅  
**Completed**: 2025-07-01  

## Overview

The MCP client error communication feature has been successfully implemented, allowing Watchgate to communicate startup and configuration errors to MCP clients (like Claude Desktop) with user-friendly error messages and fix instructions.

## Implementation Details

### Components Created

1. **MinimalStdioServer** (`watchgate/cli/minimal_stdio_server.py`)
   - Lightweight MCP server that can start even when full proxy initialization fails
   - Handles basic JSON-RPC communication to send error responses
   - Categorizes exceptions into user-friendly startup errors

2. **StartupErrorHandler** (`watchgate/cli/startup_error_handler.py`)
   - Integrates between Watchgate's main entry point and the minimal server
   - Handles both async and sync error contexts
   - Detects environment (MCP client vs terminal) to avoid stdio issues

3. **StartupError** dataclass (`watchgate/protocol/errors.py`)
   - Represents startup errors with user-friendly information
   - Includes error code, message, details, and fix instructions

### Error Categorization

The system categorizes common startup errors into specific types:

| Error Type | Code | Description | Example Fix Instructions |
|------------|------|-------------|-------------------------|
| Configuration Error | -32001 | Config file issues | "Create the file or check YAML syntax" |
| Plugin Loading Error | -32002 | Plugin initialization failures | "Check available policies" |
| Permission Error | -32003 | File system permissions | "Check file permissions" |
| Upstream Unavailable | -32004 | Upstream server errors | "Ensure server is installed" |

### Integration Points

1. **main.py** - Updated to use StartupErrorHandler for all startup exceptions
2. **Error codes** - Extended MCPErrorCodes with startup-specific codes
3. **Tests** - Comprehensive unit tests for error categorization and communication

## Usage Examples

### Example 1: Missing Configuration File

When Watchgate is started with a non-existent config file:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32001,
    "message": "Watchgate startup failed: Configuration file not found",
    "data": {
      "error_type": "configuration_error",
      "details": "The file /path/to/config.yaml does not exist",
      "fix_instructions": "Create the file or specify a valid configuration path"
    }
  },
  "id": 1
}
```

### Example 2: Log Directory Not Found

When a plugin tries to create a log file in a non-existent directory:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32001,
    "message": "Watchgate startup failed: Log directory does not exist",
    "data": {
      "error_type": "directory_not_found",
      "details": "The directory /xxx/nonexistent/dir does not exist",
      "fix_instructions": "Create the directory with: mkdir -p /xxx/nonexistent/dir",
      "error_context": {
        "directory_path": "/xxx/nonexistent/dir"
      }
    }
  },
  "id": 1
}
```

### Example 3: Invalid Plugin Policy

When configuration references an unknown plugin policy:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32002,
    "message": "Watchgate startup failed: Plugin loading failed",
    "data": {
      "error_type": "plugin_error",
      "details": "Unknown policy 'fake_plugin'. Available policies: tool_allowlist, pii_filter, secrets_filter, prompt_injection_defense",
      "fix_instructions": "Available policies: tool_allowlist, pii_filter, secrets_filter, prompt_injection_defense"
    }
  },
  "id": 1
}
```

## Technical Considerations

### macOS Stdio Limitations

On macOS, when stdin/stdout are captured by subprocess (as in tests), asyncio cannot connect to the pipes, resulting in an OSError. The implementation detects this case and exits immediately rather than hanging.

### Environment Detection

The system attempts to detect whether it's running in an MCP client context by checking:
- Whether stdin is a TTY (terminal)
- Platform-specific considerations (macOS pipe handling)

### Error Communication Flow

1. Startup error occurs in Watchgate
2. StartupErrorHandler categorizes the error
3. MinimalStdioServer is created with the error information
4. Server waits for MCP client to send initialize request
5. Server responds with JSON-RPC error containing fix instructions
6. Process exits with error code

## Testing

Comprehensive unit tests were created covering:
- Error categorization for different exception types
- JSON-RPC error response formatting
- Startup error handler behavior
- Integration with existing test suite

## Future Enhancements

1. **Extended Error Context**: Include more contextual information like config file line numbers for YAML errors
2. **Error Recovery**: For some errors, offer automatic recovery options
3. **Localization**: Support for error messages in different languages
4. **Error Code Documentation**: Comprehensive documentation of all error codes and their meanings

## Migration Notes

This feature is fully backward compatible. Existing configurations and usage patterns continue to work unchanged. The error communication only activates when Watchgate fails to start.