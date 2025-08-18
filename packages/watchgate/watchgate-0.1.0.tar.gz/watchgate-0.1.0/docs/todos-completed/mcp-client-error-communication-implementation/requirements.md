# MCP Client Error Communication Implementation

## Overview

Implement a system for Watchgate to communicate startup and configuration errors to MCP clients (like Claude Desktop) through the MCP protocol, providing users with helpful error messages instead of generic "Server disconnected" failures.

Based on completed research (see `docs/todos-completed/mcp-client-error-communication/`), this implementation will use JSON-RPC error responses during the initialization handshake to communicate errors before the server exits.

## Requirements

### 1. Minimal Error Communication Server

Create a lightweight server component that can communicate errors when full startup fails:

- **MinimalStdioServer** class that can:
  - Initialize stdio communication without full proxy setup
  - Handle basic MCP `initialize` requests
  - Send JSON-RPC error responses with structured error data
  - Cleanly shutdown after error communication

### 2. Startup Error Handling

Modify the main entry point to catch and communicate startup errors:

- Wrap proxy initialization in comprehensive error handling
- Categorize common startup errors (config, plugins, permissions, etc.)
- Generate user-friendly error messages with fix instructions
- Fall back to MinimalStdioServer when normal startup fails

### 3. Error Message Generation

Create a system for generating helpful, actionable error messages:

- **Error categories** with specific templates:
  - Configuration file errors (missing, invalid YAML, schema violations)
  - Plugin loading failures (missing policies, invalid config, initialization errors)
  - File system errors (missing directories, permission denied)
  - Upstream server failures (command not found, connection failed)
  
- **Fix instruction generation** based on error type:
  - Specific steps to resolve each error category
  - Example configurations where helpful
  - Links to relevant documentation

### 4. MCP Protocol Compliance

Ensure all error communication follows MCP protocol specifications:

- Use standard JSON-RPC 2.0 error format
- Include Watchgate-specific error codes in reserved range (-32000 to -32099)
- Provide structured error data in the `data` field
- Handle MCP initialization sequence appropriately

### 5. Testing Requirements

Comprehensive test coverage following TDD methodology:

- Unit tests for MinimalStdioServer
- Unit tests for error categorization and message generation
- Integration tests for startup error scenarios
- End-to-end tests simulating various failure modes

## Implementation Plan

### Phase 1: Core Infrastructure (RED)

1. **Write failing tests** for MinimalStdioServer:
   ```python
   # test_minimal_stdio_server.py
   async def test_minimal_server_can_start_and_stop():
       """Test that minimal server can initialize without full proxy."""
   
   async def test_minimal_server_sends_error_response():
       """Test that server can send JSON-RPC error response."""
   
   async def test_minimal_server_handles_initialize_request():
       """Test that server responds to initialize with error."""
   ```

2. **Write failing tests** for error categorization:
   ```python
   # test_startup_errors.py
   def test_categorize_file_not_found_error():
       """Test categorization of missing file errors."""
   
   def test_categorize_yaml_parse_error():
       """Test categorization of YAML syntax errors."""
   
   def test_categorize_permission_error():
       """Test categorization of permission denied errors."""
   ```

### Phase 2: Implementation (GREEN)

1. **Implement MinimalStdioServer**:
   - Create `watchgate/errors/minimal_stdio_server.py`
   - Basic stdio communication without dependencies
   - JSON-RPC message handling for errors

2. **Implement error categorization**:
   - Create `watchgate/errors/startup_errors.py`
   - Error classification system
   - Message template engine

3. **Integrate with main.py**:
   - Wrap `run_proxy()` with error handling
   - Create MinimalStdioServer on startup failure
   - Send appropriate error response

### Phase 3: Refactoring (REFACTOR)

1. **Improve code organization**:
   - Extract common error handling patterns
   - Create reusable error response builders
   - Optimize for maintainability

2. **Enhance error messages**:
   - Add more specific fix instructions
   - Include relevant configuration examples
   - Improve message clarity

## Test Requirements

### CRITICAL: TDD Methodology

**All implementation MUST follow Test-Driven Development (TDD)**:

1. **RED**: Write failing tests FIRST for each requirement
2. **GREEN**: Write minimal code to make tests pass
3. **REFACTOR**: Improve code while keeping tests green

**NO IMPLEMENTATION CODE may be written without a failing test first!**

### Test Coverage Requirements

- **Minimum 95% coverage** for all new code
- **All tests MUST pass** before any task is considered complete
- **Run full test suite** with `pytest tests/` after every change
- **Fix all test warnings** - they often indicate real issues

### Test Categories

1. **Unit Tests** (`tests/unit/`):
   - MinimalStdioServer functionality
   - Error categorization logic
   - Message generation
   - JSON-RPC formatting

2. **Integration Tests** (`tests/integration/`):
   - Startup error handling flow
   - Error communication pipeline
   - Main.py integration

3. **End-to-End Tests** (`tests/e2e/`):
   - Simulate real startup failures
   - Verify error messages reach stdout
   - Test various failure scenarios

### Example Test Structure

```python
# tests/unit/test_minimal_stdio_server.py
import pytest
from watchgate.errors.minimal_stdio_server import MinimalStdioServer

class TestMinimalStdioServer:
    """Test minimal stdio server for error communication."""
    
    async def test_server_starts_without_full_proxy(self):
        """Server should start with minimal dependencies."""
        # This test should FAIL initially (RED)
        server = MinimalStdioServer()
        await server.start()
        assert server.is_running()
        await server.stop()
    
    async def test_server_sends_error_response(self):
        """Server should send JSON-RPC error responses."""
        # This test should FAIL initially (RED)
        server = MinimalStdioServer()
        error_data = {
            "code": -32000,
            "message": "Test error",
            "data": {"details": "Test details"}
        }
        response = await server.create_error_response(error_data)
        assert response["jsonrpc"] == "2.0"
        assert response["error"]["code"] == -32000
```

## Error Response Format

All error responses must follow this structure:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Watchgate startup failed: [brief description]",
    "data": {
      "error_type": "configuration_error|plugin_error|permission_error|upstream_error",
      "details": "[detailed error message]",
      "fix_instructions": "[step-by-step resolution guide]",
      "error_context": {
        "file_path": "/path/to/problem/file",
        "line_number": 42,
        "additional_info": "..."
      }
    }
  },
  "id": 1
}
```

## Error Code Assignments

Reserve Watchgate-specific error codes:

- `-32000`: General startup failure
- `-32001`: Configuration file error
- `-32002`: Plugin loading error
- `-32003`: Permission/filesystem error
- `-32004`: Upstream server error
- `-32005`: Validation error

## Success Criteria

1. **All tests pass**: 100% of tests must be green
2. **Error visibility**: Users see specific errors instead of "Server disconnected"
3. **Actionable messages**: Each error includes clear fix instructions
4. **Protocol compliance**: All responses follow MCP/JSON-RPC specifications
5. **No regressions**: Existing functionality remains intact
6. **Documentation complete**: All docs updated as specified below

## Documentation Updates Required

### User Documentation

1. **docs/user/troubleshooting.md** (create new):
   - Common startup errors and solutions
   - How to interpret error messages
   - Step-by-step fix guides

2. **docs/user/configuration/basic-configuration.md**:
   - Add troubleshooting section
   - Link to error resolution guides

3. **README.md**:
   - Add brief troubleshooting section
   - Link to detailed troubleshooting docs

### Developer Documentation

1. **docs/development/error-handling.md** (create new):
   - Error handling architecture
   - How to add new error categories
   - MinimalStdioServer design

2. **docs/development/testing.md**:
   - Add section on testing error scenarios
   - Examples of error communication tests

3. **docs/api/errors.md** (create new):
   - Document error codes and formats
   - API reference for error handling

### Configuration Examples

1. **examples/error-scenarios/**:
   - Create example configs that trigger each error type
   - Include fix instructions in comments

### Validation Guide Updates

1. **tests/validation/quick-validation-guide.md**:
   - Add new section for testing error communication
   - Include test cases for each error category
   - Update validation checklist

## Implementation Notes

### Design Decisions

1. **Separate minimal server**: Avoids circular dependencies during error handling
2. **Structured error data**: Enables future client-side enhancements
3. **Category-based messages**: Consistent user experience across error types
4. **JSON-RPC compliance**: Ensures compatibility with all MCP clients

### Security Considerations

- Never include sensitive information in error messages
- Sanitize file paths to avoid information disclosure
- Limit error details to what's necessary for resolution

### Performance Considerations

- MinimalStdioServer should start quickly (<100ms)
- Error categorization should be fast (<10ms)
- Total error communication time should be <500ms

## Dependencies

- No new external dependencies required
- Uses existing asyncio and json modules
- Leverages current stdio handling code where possible

## Future Enhancements (Out of Scope)

- Client-side error UI improvements
- Error reporting/telemetry
- Automatic fix attempts
- Configuration validation warnings (non-fatal)

## Review Checklist

Before marking this implementation complete:

- [ ] All tests written following TDD (RED-GREEN-REFACTOR)
- [ ] All tests pass (`pytest tests/`)
- [ ] Test coverage ≥ 95% for new code
- [ ] No test warnings or deprecations
- [ ] Error messages are clear and actionable
- [ ] All documentation updated
- [ ] Code review completed
- [ ] Manual testing with Claude Desktop verified
- [ ] No regressions in existing functionality
- [ ] Validation guide updated and tested