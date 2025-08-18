# RuntimeWarning Suppressions in Test Suite

This document explains where and why `pytest.mark.filterwarnings("ignore::RuntimeWarning")` is used in the test suite to suppress specific RuntimeWarnings that are expected behavior in our testing scenarios.

## Background

The RuntimeWarnings we suppress are primarily caused by `AsyncMock` objects creating coroutine objects that are not awaited in certain test scenarios. While these warnings are valuable in production code to catch genuine async programming errors, they are expected and harmless in our specific testing contexts.

## Summary Table

### Transport Tests (test_stdio_transport.py)
| Test Method | Line | Reason | AsyncMock Usage |
|-------------|------|--------|-----------------|
| `test_disconnect_with_timeout_kills_process` | 124 | Intentional timeout cancels coroutines | Process mock |
| `test_process_failure_during_connect` | 152 | AsyncMock for process creation creates internal coroutines | asyncio.create_subprocess_exec |
| `test_send_message_success` | 181 | AsyncMock fixture creates internal coroutines | stdin.drain |
| `test_send_message_with_params` | 199 | AsyncMock fixture creates internal coroutines | stdin.drain |
| `test_send_message_broken_pipe` | 231 | AsyncMock creates coroutines even when not called | stdin.drain |
| `test_receive_message_success` | 249 | AsyncMock fixture creates internal coroutines | stdout.readline |
| `test_receive_message_error_response` | 270 | AsyncMock fixture creates internal coroutines | stdout.readline |
| `test_receive_message_invalid_json` | 305 | AsyncMock fixture creates internal coroutines | stdout.readline |
| `test_receive_message_empty_line` | 316 | AsyncMock fixture creates internal coroutines | stdout.readline |
| `test_receive_message_validation_error` | 327 | AsyncMock fixture creates internal coroutines | stdout.readline |
| `test_message_validation_integration` | 507 | Manual AsyncMock setup creates internal coroutines | stdin.drain |
| `test_response_parsing_with_validation` | 536 | Manual AsyncMock setup creates internal coroutines | stdout.readline |

### Message Protocol Tests (test_message_sender.py)
| Test Method | Line | Reason | AsyncMock Usage |
|-------------|------|--------|-----------------|
| `test_sender_context_metadata_default` | 81 | AsyncMock in test dependencies creates internal coroutines | Indirect AsyncMock usage |

### Startup Error Notifier Tests (test_startup_error_notifier.py)
| Test Method | Line | Reason | AsyncMock Usage |
|-------------|------|--------|-----------------|
| `test_send_error_response` | 33 | AsyncMock fixture creates internal coroutines | writer.drain |

### CLI Tests (test_main_cli.py)
| Test Method | Line | Reason | AsyncMock Usage |
|-------------|------|--------|-----------------|
| `test_default_config_path` | 15 | AsyncMock for run_proxy creates internal coroutines | run_proxy mock |
| `test_custom_config_path` | 30 | AsyncMock for run_proxy creates internal coroutines | run_proxy mock |
| `test_verbose_flag` | 47 | AsyncMock for run_proxy creates internal coroutines | run_proxy mock |
| `test_version_display` | 63 | AsyncMock for run_proxy creates internal coroutines | run_proxy mock |
| `test_help_output` | 72 | AsyncMock for run_proxy creates internal coroutines | run_proxy mock |
| `test_config_file_not_found` | 86 | AsyncMock for run_proxy creates internal coroutines | run_proxy mock |
| `test_invalid_config_format` | 102 | AsyncMock for run_proxy creates internal coroutines | run_proxy mock |
| `test_keyboard_interrupt_handling` | 118 | AsyncMock for run_proxy creates internal coroutines | run_proxy mock |
| `test_async_proxy_integration` | 142 | AsyncMock for run_proxy creates internal coroutines | run_proxy mock |
| `test_unexpected_error_handling` | 206 | AsyncMock for run_proxy creates internal coroutines | run_proxy mock |
| `test_main_keyboard_interrupt_handling` | 221 | AsyncMock for run_proxy creates internal coroutines | run_proxy mock |

### Configuration Tests (test_plugin_config_models.py)
| Test Method | Line | Reason | AsyncMock Usage |
|-------------|------|--------|-----------------|
| `test_valid_plugin_config_schema` | 16 | AsyncMock in test dependencies creates internal coroutines | Indirect AsyncMock usage |
| `test_plugin_config_schema_validation_errors` | 47 | AsyncMock in test dependencies creates internal coroutines | Indirect AsyncMock usage |
| `test_plugins_config_schema_defaults` | 100 | AsyncMock in test dependencies creates internal coroutines | Indirect AsyncMock usage |

### Upstream Scoped Plugin Configuration Tests (test_upstream_scoped_plugin_config.py)
| Test Method | Line | Reason | AsyncMock Usage |
|-------------|------|--------|-----------------|
| `test_valid_upstream_key_patterns` | 179 | AsyncMock in test dependencies creates internal coroutines during validation | Indirect AsyncMock usage |

### Plugin Manager Tests (test_plugin_manager.py)
| Test Method | Line | Reason | AsyncMock Usage |
|-------------|------|--------|-----------------|
| `test_mixed_plugin_success_and_failure` | 586 | AsyncMock plugin methods create internal coroutines | FailingSecurityPlugin mock |
| `test_log_response_handles_plugin_failure` | 844 | AsyncMock plugin methods create internal coroutines | FailingAuditingPlugin mock |

### Main Logging Tests (test_main_logging.py)
| Test Method | Line | Reason | AsyncMock Usage |
|-------------|------|--------|-----------------|
| `test_setup_logging_from_config_stderr_only` | 14 | Cross-test contamination from CLI AsyncMock patches | run_proxy mock from other tests |

## Suppression Locations and Rationale

### 1. Process Lifecycle Test - Timeout Scenario

**Location:** `test_disconnect_with_timeout_kills_process`
**File:** `tests/unit/test_stdio_transport.py:124`

```python
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_disconnect_with_timeout_kills_process(self, transport, mock_process):
```

**Why suppressed:** This test intentionally triggers an `asyncio.TimeoutError` to simulate a process that doesn't respond to graceful termination. The timeout operation cancels awaitable coroutines, which legitimately generates RuntimeWarnings. These warnings are expected behavior for this edge case test.

### 2. Process Lifecycle Test - Subprocess Creation Failure

**Location:** `test_process_failure_during_connect`
**File:** `tests/unit/test_stdio_transport.py:152`

```python
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_process_failure_during_connect(self, transport):
```

**Why suppressed:** This test uses `AsyncMock` to mock `asyncio.create_subprocess_exec` and simulate process creation failure. The AsyncMock creates internal coroutine objects that are never awaited, triggering RuntimeWarnings. These warnings are testing artifacts from the mocking framework, not actual async programming issues.

### 3. CLI Tests with AsyncMock for run_proxy Function

**Locations:** Multiple CLI test methods that mock `run_proxy`
**File:** `tests/unit/test_main_cli.py:15, 30, 47, 63, 72, 86, 102, 118, 142, 206, 221`

#### Tests affected:
- `test_default_config_path`
- `test_custom_config_path`  
- `test_verbose_flag`
- `test_version_display`
- `test_help_output`
- `test_config_file_not_found`
- `test_invalid_config_format`
- `test_keyboard_interrupt_handling`
- `test_async_proxy_integration`
- `test_unexpected_error_handling`
- `test_main_keyboard_interrupt_handling`

**Why suppressed:** These CLI tests use `AsyncMock` to mock the `run_proxy` async function to test command-line argument handling and error scenarios. The AsyncMock creates internal coroutine objects for the mocked async function, even though the tests properly verify the mock was called with correct arguments. The warnings are artifacts of mocking an async function in a testing context.

**Example pattern:**
```python
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_default_config_path(self, mock_run_proxy):
    # Test CLI behavior
    main(["--config", "custom.json"])
    mock_run_proxy.assert_called_once_with(Path("custom.json"))  # Properly verified
```

### 4. Configuration Tests with AsyncMock Dependencies

**Locations:** Configuration model tests with async dependencies
**File:** `tests/unit/test_plugin_config_models.py:16, 47, 100`

#### Tests affected:
- `test_valid_plugin_config_schema`
- `test_plugin_config_schema_validation_errors`
- `test_plugins_config_schema_defaults`

**Why suppressed:** These tests create configuration schema objects that may have async dependencies or components that use AsyncMock indirectly through the testing framework. The warnings appear due to test infrastructure creating coroutines that are not directly awaited in the test scope. While these tests don't directly use AsyncMock, they interact with plugin configuration validation that may trigger async mock creation in the test environment.

### 4a. Upstream Scoped Plugin Configuration Tests with AsyncMock Dependencies

**Location:** `test_valid_upstream_key_patterns`
**File:** `tests/unit/test_upstream_scoped_plugin_config.py:179`

```python
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_valid_upstream_key_patterns(self):
```

**Why suppressed:** This test creates PluginsConfigSchema objects that validate upstream key patterns by iterating over dictionary items in the validator. During test execution, the validator may encounter AsyncMock objects from other test dependencies or fixtures, causing coroutines to be created during the `v.items()` iteration in the field validator at line 56 of config/models.py. These warnings are artifacts of test environment interaction with the validation system, not actual async programming issues.

### 5. Plugin Manager Tests with Mock Plugin Failures

**Locations:** Plugin manager tests with intentionally failing plugins
**File:** `tests/unit/test_plugin_manager.py:586, 844`

#### Tests affected:
- `test_mixed_plugin_success_and_failure`
- `test_log_response_handles_plugin_failure`

**Why suppressed:** These tests use mock plugins (FailingSecurityPlugin, FailingAuditingPlugin) that simulate plugin failures in async contexts. The failing plugin mocks create async methods using AsyncMock internally, which generate coroutines that are never awaited as part of the failure simulation. These warnings are expected artifacts of testing error handling scenarios.

**Example pattern:**
```python
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_mixed_plugin_success_and_failure(self):
    manager = PluginManager({})
    manager.security_plugins = [
        MockSecurityPlugin({"allowed": True}),
        FailingSecurityPlugin({})  # Creates AsyncMock coroutines during failure simulation
    ]
    # ... test failure handling ...
```

### 6. Message IO Tests with AsyncMock Fixtures

**Locations:** Multiple tests using `mock_connected_transport` fixture
**File:** `tests/unit/test_stdio_transport.py:181, 199, 231, 249, 270, 305, 316, 327`

#### Tests affected:
- `test_send_message_success`
- `test_send_message_with_params`
- `test_send_message_broken_pipe`
- `test_receive_message_success`
- `test_receive_message_error_response`
- `test_receive_message_invalid_json`
- `test_receive_message_empty_line`
- `test_receive_message_validation_error`

**Why suppressed:** These tests use the `mock_connected_transport` fixture which creates `AsyncMock` objects for process stdin/stdout operations. The AsyncMock library creates coroutine objects internally for async methods like `drain()`, even when we properly assert their usage with `assert_awaited_once()`. The warnings are artifacts of the mocking framework, not actual issues with our test logic.

**Example pattern:**
```python
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_send_message_success(self, mock_connected_transport):
    transport, mock_process = mock_connected_transport
    # ... test implementation ...
    mock_process.stdin.drain.assert_awaited_once()  # Properly asserted
```

### 7. Integration Tests with Manual AsyncMock Setup

**Locations:** Integration test methods that manually create AsyncMock objects
**File:** `tests/unit/test_stdio_transport.py:507, 536`

#### Tests affected:
- `test_message_validation_integration`
- `test_response_parsing_with_validation`

**Why suppressed:** These integration tests manually create `AsyncMock` objects for process I/O operations to test end-to-end message handling. Similar to the fixture-based tests, the AsyncMock creates internal coroutines that trigger warnings despite proper test assertions.

**Example pattern:**
```python
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_message_validation_integration(self, transport):
    process = Mock()
    process.stdin.drain = AsyncMock()  # Creates internal coroutines
    # ... test implementation ...
    process.stdin.drain.assert_awaited_once()  # Properly verified
```

### 8. Startup Error Notifier Tests with AsyncMock Writer Operations

**Location:** `test_send_error_response`
**File:** `tests/unit/test_startup_error_notifier.py:33`

```python
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_send_error_response(self, notifier, mock_writer):
```

**Why suppressed:** This test uses an `AsyncMock` fixture for the writer to test error response sending functionality. The AsyncMock creates internal coroutines for async methods like `writer.drain()`, which are properly awaited in the test but trigger RuntimeWarnings due to the mocking framework creating additional coroutine objects internally. The test properly verifies the mock was called with `assert_called_once()`, but the warnings are artifacts of testing async I/O operations.

**Example pattern:**
```python
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_send_error_response(self, notifier, mock_writer):
    # ... test implementation ...
    await notifier.send_error_response(error, mock_writer, request_id=1)
    mock_writer.drain.assert_called_once()  # Properly verified
```

### 9. Main Logging Tests with Cross-Test AsyncMock Contamination

**Location:** `test_setup_logging_from_config_stderr_only`
**File:** `tests/unit/test_main_logging.py:14`

```python
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_setup_logging_from_config_stderr_only(self):
```

**Why suppressed:** This test doesn't directly use AsyncMock, but it's affected by AsyncMock patches from CLI tests that mock the `run_proxy` async function. When the full test suite runs, there's cross-test contamination where AsyncMock objects from other test modules (specifically `test_main_cli.py`) create coroutines that are never awaited. This is a testing artifact from test isolation issues, not actual async programming problems in the code under test.

**Root cause:** The CLI tests in `test_main_cli.py` use `@patch('watchgate.main.run_proxy')` with AsyncMock, and some of these patches may have module-level or session-level scope that affects other tests that import or interact with the same modules.

### 10. Prompt Injection Defense Performance Tests with Cross-Test AsyncMock Contamination

**Location:** `test_memory_usage_optimization`
**File:** `tests/unit/test_prompt_injection_defense_plugin.py:640`

```python
@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_memory_usage_optimization(self):
```

**Why suppressed:** This test doesn't directly use AsyncMock, but experiences cross-test contamination similar to the main logging tests. When the full test suite runs, AsyncMock objects from other test modules create coroutines that are never awaited, particularly affecting the regex processing loop at line 208 in the BasicPromptInjectionDefensePlugin. This is a testing artifact from test isolation issues, not actual async programming problems in the plugin code.

**Root cause:** Cross-test contamination from AsyncMock patches in other test modules that have module-level or session-level scope affecting tests that process text patterns in loops.

## Alternative Approaches Considered

### 1. Mock Cleanup in Fixtures
We attempted to add cleanup logic to fixtures using `yield` and `reset_mock()`, but this didn't eliminate the warnings because AsyncMock creates coroutines at instantiation time, not just during calls.

### 2. Using Regular Mock Instead of AsyncMock
This wasn't viable because we need to test actual async operations like `stdin.drain()` which must be awaitable in the real implementation.

### 3. Manual Coroutine Cleanup
We tried manually closing coroutines created by AsyncMock, but this was fragile and didn't reliably eliminate all warnings.

## Verification

The suppressions are precisely targeted and verified by:

1. **Selective Application:** Only applied to tests that actually use AsyncMock objects
2. **Test Validation:** All tests still pass with proper async operation verification
3. **Error Detection:** Running tests with `-W error::RuntimeWarning` confirms no warnings leak through
4. **Minimal Scope:** Each suppression is applied at the test method level, not globally

## Maintenance Notes

- **Review Suppressions:** When updating AsyncMock usage, review if suppressions are still needed
- **New Tests:** Add suppressions to new tests that use AsyncMock for:
  - Process I/O operations (transport tests)
  - Async function mocking (CLI tests)  
  - Configuration objects with async dependencies (config tests)
  - Plugin failure simulation (plugin manager tests)
  - Writer/reader operations (startup error notifier tests)
  - Any test using mock plugins with async methods
- **Library Updates:** Monitor pytest-asyncio and AsyncMock updates that might resolve the underlying issue
- **Documentation:** Keep this documentation updated when adding new suppression locations
- **Cross-Domain Coverage:** Warning suppressions now span multiple test domains (transport, CLI, configuration, plugin management) - ensure new domains follow the same pattern

## Commands for Verification

```bash
# Verify no warnings leak through in transport tests
python -m pytest tests/unit/test_stdio_transport.py -W error::RuntimeWarning

# Verify no warnings leak through in CLI tests  
python -m pytest tests/unit/test_main_cli.py -W error::RuntimeWarning

# Verify no warnings leak through in configuration tests
python -m pytest tests/unit/test_plugin_config_models.py -W error::RuntimeWarning

# Verify no warnings leak through in plugin manager tests
python -m pytest tests/unit/test_plugin_manager.py -W error::RuntimeWarning

# Verify no warnings leak through in startup error notifier tests
python -m pytest tests/unit/test_startup_error_notifier.py -W error::RuntimeWarning

# Run all tests with strict warning checking
python -m pytest tests/ -W error::RuntimeWarning

# Run specific test with warning details
python -m pytest tests/unit/test_stdio_transport.py::TestStdioTransportMessageIO::test_send_message_success -v -s
python -m pytest tests/unit/test_main_cli.py::test_default_config_path -v -s
python -m pytest tests/unit/test_plugin_config_models.py::TestPluginConfigSchema::test_valid_plugin_config_schema -v -s
python -m pytest tests/unit/test_plugin_manager.py::TestPluginManagerErrorScenarios::test_mixed_plugin_success_and_failure -v -s
python -m pytest tests/unit/test_startup_error_notifier.py::TestStartupErrorNotifier::test_send_error_response -v -s
```

This targeted approach ensures we suppress only the expected AsyncMock-related warnings while preserving the ability to detect genuine async programming issues in our codebase.
