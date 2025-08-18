# Test Coverage Gaps Implementation Prompt

## Context

You are implementing tests to address coverage gaps in the Watchgate codebase. The requirements are detailed in `requirements.md` in this directory. Watchgate follows strict Test-Driven Development (TDD) practices.

## CRITICAL: TDD Methodology

**YOU MUST FOLLOW TDD STRICTLY**:

1. **RED Phase**: Write failing tests FIRST
   - Write test cases that fail because the functionality doesn't exist or isn't properly tested
   - Ensure tests actually run and fail (not skip or error due to imports)
   - "No tests found" is NOT acceptable - fix test discovery issues

2. **GREEN Phase**: Make tests pass with minimal code
   - Only write enough code to make the failing tests pass
   - Don't add extra functionality not required by tests

3. **REFACTOR Phase**: Improve code while keeping tests green
   - Clean up implementation
   - Ensure all tests still pass

## ABSOLUTE REQUIREMENTS

### 🚨 NO TASK IS COMPLETE WITH FAILING TESTS 🚨

- **Run `pytest tests/` after EVERY change**
- **ALL tests must pass before moving to next task**
- **If ANY test fails, you MUST fix it immediately**
- **Do NOT declare success with failing tests**
- **Do NOT commit with failing tests**

### Test Execution Verification

Before considering any task complete:
```bash
# Run full test suite
pytest tests/

# If testing specific area
pytest tests/unit/test_cli.py -v
pytest tests/integration/test_concurrent_requests.py -v

# Check coverage
pytest --cov=watchgate tests/
```

## Implementation Tasks

### Task 1: CLI Debug Commands Tests

1. **RED Phase**:
   - Create `tests/unit/test_cli_debug_commands.py`
   - Write comprehensive test cases for all debug subcommands
   - Mock `WatchgateServer` and other dependencies
   - Ensure tests fail initially

2. **GREEN Phase**:
   - Fix any missing CLI command implementations
   - Add proper error handling where needed
   - Make all tests pass

3. **REFACTOR Phase**:
   - Improve error messages
   - Ensure consistent command behavior

**Key Test Areas**:
- `debug config --validate`
- `debug plugins --list-available`
- `debug plugins --validate-priorities`
- `debug plugins --validate-config`

### Task 2: Log Rotation Tests

1. **RED Phase**:
   - Create `tests/integration/test_log_rotation.py`
   - Write tests that trigger rotation by exceeding maxBytes
   - Test backup file creation and cleanup

2. **GREEN Phase**:
   - Ensure log rotation configuration is properly applied
   - Fix any rotation behavior issues

3. **REFACTOR Phase**:
   - Optimize rotation performance
   - Improve error handling during rotation

**Key Test Scenarios**:
- Basic rotation at size limit
- Multiple rotation cycles
- Concurrent writes during rotation
- Permission and disk space errors

### Task 3: Complex Configuration Tests

1. **RED Phase**:
   - Enhance `tests/unit/test_config.py` or create new test file
   - Add tests for deeply nested configurations
   - Test environment variable overrides
   - Test configuration edge cases

2. **GREEN Phase**:
   - Fix configuration parsing for complex scenarios
   - Implement missing override functionality
   - Add validation for edge cases

3. **REFACTOR Phase**:
   - Improve configuration error messages
   - Optimize configuration parsing

**Key Test Areas**:
- 3+ level nested configurations
- `AG_` environment variable overrides
- Empty sections and null values
- Unicode and special characters

### Task 4: Concurrent Request Tests

1. **RED Phase**:
   - Create `tests/integration/test_concurrent_requests.py`
   - Write tests using asyncio to send multiple simultaneous requests
   - Test request/response ordering
   - Test for race conditions

2. **GREEN Phase**:
   - Fix any concurrency issues found
   - Ensure proper request isolation
   - Add necessary synchronization

3. **REFACTOR Phase**:
   - Optimize concurrent performance
   - Improve resource management

**Key Test Scenarios**:
- 10, 50, and 100 simultaneous requests
- Request/response pair matching
- Plugin state isolation
- Resource cleanup

### Task 5: Notification Support Research

1. **Research Phase**:
   - Search for MCP servers that send notifications
   - Document findings in `docs/todos/test-coverage-gaps/notification-testing-approach.md`
   - If no suitable server exists, design a mock notification server

2. **Documentation Phase**:
   - Create clear plan for notification testing
   - Include example notification messages
   - Define test scenarios

## Working With Existing Tests

- Study existing test patterns in the codebase
- Use similar mocking strategies
- Follow naming conventions
- Reuse test utilities where appropriate

## Common Pitfalls to Avoid

1. **Don't skip TDD phases** - Write tests first!
2. **Don't ignore test failures** - Fix them immediately
3. **Don't use global state** - Tests must be isolated
4. **Don't make tests too slow** - Mock external dependencies
5. **Don't forget edge cases** - Test error conditions

## Success Criteria

Your implementation is complete when:
1. All new tests pass (`pytest tests/` shows 100% success)
2. No new warnings introduced
3. Code coverage improved for tested modules
4. Tests run quickly (<5 seconds per test file)
5. Tests work on Linux, macOS, and Windows

## Final Checklist

Before declaring the task complete:
- [ ] All tests written following TDD methodology
- [ ] `pytest tests/` runs with 100% success
- [ ] No test warnings or errors
- [ ] Code coverage increased
- [ ] Tests are well-documented
- [ ] Implementation follows Watchgate coding standards
- [ ] All edge cases covered

Remember: **YOU MUST NOT STOP UNTIL ALL TESTS PASS!** If you encounter failing tests, debug and fix them. The task is not complete until every single test passes.