# PytestUnraisableExceptionWarning Suppressions

This document explains the global suppression of `PytestUnraisableExceptionWarning` in our test suite and identifies the specific scenarios where these warnings occur. The warning is globally suppressed in `pyproject.toml` because it represents a well-understood limitation of testing asyncio subprocesses with pytest, not bugs in our application code.

## Configuration

The warning is globally suppressed in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
filterwarnings = [
    "ignore::pytest.PytestUnraisableExceptionWarning",
]
```

## Why Global Suppression?

After careful analysis, we chose global suppression over per-test decorators for the following reasons:

1. **Consistent and Known Issue**: The warning only occurs in specific, well-understood scenarios (asyncio subprocess cleanup) that are not indicative of bugs
2. **Cleaner Test Code**: Eliminates the need for decorators on individual test methods
3. **Easier Maintenance**: Single point of configuration that can be easily removed when/if Python fixes the underlying issue
4. **Low Risk**: `PytestUnraisableExceptionWarning` is specific enough that global suppression is unlikely to hide unrelated issues

### Trade-offs Considered

- **Pro**: Simpler configuration and cleaner test code
- **Pro**: No risk of forgetting suppressions on new tests
- **Con**: Less granular - can't immediately see which tests trigger the warning
- **Con**: Could theoretically hide future unraisable exceptions (though unlikely given the specific nature of this warning)

## Tests That Trigger This Warning

While the warning is globally suppressed, these are the specific tests and scenarios that actually trigger it:

| File | Test(s) | Root Cause |
| :--- | :--- | :--- |
| `tests/integration/test_real_mcp_server.py` | Multiple | `asyncio` subprocess cleanup race conditions with the `pytest` event loop |
| `tests/integration/test_transport_integration.py` | Multiple | Same `asyncio` subprocess cleanup issue as above |
| `tests/unit/test_file_auditing_plugin.py` | `test_log_request_handles_logging_error_non_critical` | Test intentionally swallows an exception to verify non-critical plugin behavior |

---

## Detailed Rationale for Active Suppressions

### 1. `asyncio` Subprocess Integration Tests

- **Files Affected**:
    - `tests/integration/test_real_mcp_server.py`
    - `tests/integration/test_transport_integration.py`
- **Reason**: These integration tests launch real subprocesses using `asyncio`. A known issue exists where `pytest-asyncio` closes the event loop before Python's garbage collector cleans up the `asyncio` transport object for the subprocess. The transport's destructor (`__del__`) then attempts to access the closed loop, raising a `RuntimeError` that cannot be handled, which `pytest` reports as a `PytestUnraisableExceptionWarning`.
- **Conclusion**: This is a well-understood limitation of testing `asyncio` subprocesses and not a bug in our code. The suppression is necessary to avoid noisy, un-actionable warnings.

### 2. Intentional Exception Swallowing in Unit Tests

- **File Affected**: `tests/unit/test_file_auditing_plugin.py`
- **Test Affected**: `test_log_request_handles_logging_error_non_critical`
- **Reason**: This test's purpose is to verify that when a *non-critical* auditing plugin fails to log, it does *not* crash the application. To do this, the test mocks the logger to raise an exception and asserts that the plugin correctly catches and swallows it. The warning is a side effect of `pytest` detecting an exception that was raised but not re-raised or explicitly caught with `pytest.raises`.
- **Conclusion**: The warning is expected due to the specific nature of the test. Suppressing it is appropriate as the test is validating the intended "swallowing" behavior.

---

## Formerly Suppressed Warnings (Now Removed)

As part of a recent review, several unnecessary suppressions were identified and removed from the codebase. In these cases, the underlying issues that caused the warnings no longer exist, or the warnings were not reproducible.

Removing these suppressions improves code hygiene and ensures that we are not masking potential future issues.

The following files no longer suppress `PytestUnraisableExceptionWarning`:

-   `tests/unit/test_plugin_sequencing.py`
-   `tests/unit/test_cli_diagnostic_commands.py`
-   `tests/unit/test_config_loader_logging.py`

This cleanup was validated by running the entire `pytest` suite, which passed without any of these warnings reoccurring.

---

## Future Considerations

### Monitoring for Fixes

The underlying issue is in Python's asyncio library. We should periodically check if updates to Python or pytest have resolved the root cause:

```bash
# To test if the suppression is still needed:
# 1. Temporarily remove the filterwarnings from pyproject.toml
# 2. Run the affected tests
python -m pytest tests/integration/test_real_mcp_server.py -v
python -m pytest tests/integration/test_transport_integration.py -v
python -m pytest tests/unit/test_file_auditing_plugin.py::test_log_request_handles_logging_error_non_critical -v
```

### When to Reconsider

Consider reverting to targeted suppressions if:
- New types of unraisable exceptions appear that we need to investigate
- The team prefers more explicit documentation at the test level
- Python/pytest updates fix the asyncio subprocess cleanup issue

### Adding Comments to Affected Tests

While we use global suppression, consider adding brief comments to test files that trigger this warning to help future maintainers:

```python
# Note: Tests in this file may trigger PytestUnraisableExceptionWarning due to
# asyncio subprocess cleanup. This is globally suppressed in pyproject.toml.
```