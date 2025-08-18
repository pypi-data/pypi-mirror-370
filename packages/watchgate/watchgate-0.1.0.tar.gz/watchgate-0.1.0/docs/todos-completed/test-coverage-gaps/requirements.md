# Test Coverage Gaps Requirements

## Overview

This document outlines the requirements for addressing test coverage gaps identified in the Watchgate codebase. Analysis revealed that while ~70% of implemented features have test coverage, several important areas lack adequate testing.

## Background

A comprehensive analysis of Watchgate's functionality claims versus test coverage revealed the following gaps:
- CLI debug commands exist but lack test coverage
- Log rotation is configured but actual rotation behavior is untested
- Complex nested configuration scenarios lack edge case testing
- Concurrent request handling has no stress or race condition tests
- Notification support is implemented but has no validation tests

## Requirements

### 1. CLI Debug Commands Tests (Unit Tests)

**Scope**: Test all debug subcommands in the CLI interface

**Test Cases Required**:
- `watchgate debug config --validate`:
  - Valid configuration file
  - Invalid YAML syntax
  - Missing required fields
  - Type validation errors
  - Non-existent config file
- `watchgate debug plugins --list-available`:
  - Normal operation listing all available plugins
  - Empty plugin directory scenario
  - Plugin discovery errors
- `watchgate debug plugins --validate-priorities`:
  - Valid priority configuration
  - Duplicate priorities
  - Invalid priority values (outside 0-100)
  - Mixed security/auditing plugin priorities
- `watchgate debug plugins --validate-config`:
  - Valid plugin configurations
  - Invalid plugin configuration schema
  - Missing required plugin config fields

**Success Criteria**:
- 100% code coverage for CLI debug command handlers
- All error paths tested with appropriate error messages
- Mock internal components to isolate CLI behavior

### 2. Log Rotation Tests (Integration Tests)

**Scope**: Test the log rotation behavior when logs reach configured size limits

**Test Cases Required**:
- Basic rotation:
  - Write logs until maxBytes is exceeded
  - Verify backup file creation with correct naming (.1, .2, etc.)
  - Verify main log file is truncated after rotation
- Multiple rotation cycles:
  - Test backupCount limit enforcement
  - Verify oldest logs are deleted when limit reached
- Edge cases:
  - Rotation with concurrent writes
  - Rotation when backup files already exist
  - Permission errors during rotation
  - Disk full scenarios

**Success Criteria**:
- Log rotation triggers at configured size
- Backup files maintain correct naming sequence
- Old logs are properly managed per backupCount setting
- No log data loss during rotation

### 3. Complex Configuration Tests (Unit Tests)

**Scope**: Test complex and edge case configuration scenarios

**Test Cases Required**:
- Nested configurations:
  - Deeply nested plugin configurations (3+ levels)
  - Arrays within nested structures
  - Mixed types in complex structures
- Environment variable overrides:
  - `AG_` prefixed overrides for nested values
  - Override precedence testing
  - Invalid override attempts
- Path resolution in configs:
  - Relative paths in nested configs
  - Home directory expansion in all path fields
  - Circular path references
- Edge cases:
  - Empty configuration sections
  - Null vs missing values
  - Unicode in configuration values
  - Very large configuration files

**Success Criteria**:
- All configuration edge cases handled gracefully
- Clear error messages for invalid configurations
- Consistent behavior across platforms

### 4. Concurrent Request Tests (Integration Tests)

**Scope**: Test Watchgate's behavior under concurrent load

**Test Cases Required**:
- Basic concurrency:
  - 10 simultaneous requests
  - 50 simultaneous requests
  - 100 simultaneous requests
- Request ordering:
  - Verify request/response pairs match correctly
  - Test FIFO processing order preservation
- Plugin state isolation:
  - Ensure plugins don't share mutable state
  - Test for race conditions in plugin execution
- Resource management:
  - Memory usage under load
  - File descriptor limits
  - Connection cleanup after requests
- Error scenarios:
  - Upstream server delays/timeouts under load
  - Plugin failures during concurrent processing
  - Client disconnections during processing

**Success Criteria**:
- No race conditions or deadlocks
- Consistent performance up to 100 concurrent requests
- Proper resource cleanup
- Graceful degradation under extreme load

### 5. Notification Support Research & Testing

**Scope**: Research and document approach for testing notification support

**Requirements**:
- Research existing MCP servers that send notifications
- Document findings on notification-capable servers
- If no suitable server exists, design mock server approach
- Create plan for notification test implementation

**Success Criteria**:
- Clear documentation of notification testing approach
- Identified or created test infrastructure for notifications
- Plan approved before implementation

## Implementation Priority

1. **High Priority**:
   - CLI debug commands tests (affects developer experience)
   - Concurrent request tests (production stability)

2. **Medium Priority**:
   - Complex configuration tests (robustness)
   - Log rotation tests (operational concerns)

3. **Low Priority**:
   - Notification support research (feature not widely used yet)

## Testing Standards

All tests must follow Watchgate's testing standards:
- Use pytest framework
- Follow existing test patterns
- Include both positive and negative test cases
- Mock external dependencies appropriately
- Maintain fast test execution (<5 seconds per test file)
- Use descriptive test names that explain the scenario

## Acceptance Criteria

- All test files run successfully with `pytest tests/`
- No test warnings or deprecations
- Code coverage increases for affected modules
- Tests are maintainable and well-documented
- Tests run on all supported platforms (Linux, macOS, Windows)